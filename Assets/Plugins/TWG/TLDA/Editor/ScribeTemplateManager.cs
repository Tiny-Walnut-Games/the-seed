using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;

namespace LivingDevAgent.Editor.Scribe
{
    /// <summary>
    /// Template management for issue creation
    /// KeeperNote: This is the "template forge" - manages reusable documentation patterns
    /// </summary>
    public class ScribeTemplateManager
    {
        public class Template
        {
            public string Key { get; set; }
            public string Title { get; set; }
            public string FilePath { get; set; }
            public string Content { get; set; }
        }
        
        private List<Template> _templates;
        private readonly string _templatesDirectory;
        
        public List<Template> Templates
        {
            get
            {
                if (_templates == null)
                    LoadTemplates();
                return _templates;
            }
        }
        
        public ScribeTemplateManager()
        {
            var projectRoot = Directory.GetParent(Application.dataPath).FullName;
            _templatesDirectory = Path.Combine(projectRoot, "templates", "comments");
        }
        
        void LoadTemplates()
        {
            _templates = new List<Template>();
            
            var registryPath = Path.Combine(_templatesDirectory, "registry.yaml");
            if (!File.Exists(registryPath))
            {
                Debug.LogWarning($"[ScribeTemplates] Registry not found: {registryPath}");
                return;
            }
            
            try
            {
                ParseRegistry(registryPath);
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[ScribeTemplates] Failed to load templates: {e.Message}");
            }
        }
        
        void ParseRegistry(string registryPath)
        {
            var lines = File.ReadAllLines(registryPath);
            bool inTemplates = false;
            
            Template current = null;
            
            foreach (var rawLine in lines)
            {
                var line = rawLine.TrimEnd();
                
                // Look for templates section
                if (line.Trim() == "templates:")
                {
                    inTemplates = true;
                    continue;
                }
                
                if (!inTemplates)
                    continue;
                
                // Template key (2 spaces indent)
                var keyMatch = Regex.Match(line, @"^  ([A-Za-z0-9_-]+):\s*$");
                if (keyMatch.Success)
                {
                    // Save previous template if exists
                    if (current != null && !string.IsNullOrEmpty(current.FilePath))
                    {
                        LoadTemplateContent(current);
                        _templates.Add(current);
                    }
                    
                    current = new Template
                    {
                        Key = keyMatch.Groups[1].Value
                    };
                    continue;
                }
                
                // File property (4 spaces indent)
                var fileMatch = Regex.Match(line, @"^    file:\s*(.+)$");
                if (fileMatch.Success && current != null)
                {
                    current.FilePath = Path.Combine(_templatesDirectory, fileMatch.Groups[1].Value.Trim());
                    continue;
                }
                
                // Title property (4 spaces indent)
                var titleMatch = Regex.Match(line, @"^    title:\s*""?([^""]+)""?$");
                if (titleMatch.Success && current != null)
                {
                    current.Title = titleMatch.Groups[1].Value.Trim();
                    continue;
                }
            }
            
            // Save last template
            if (current != null && !string.IsNullOrEmpty(current.FilePath))
            {
                LoadTemplateContent(current);
                _templates.Add(current);
            }
        }
        
        void LoadTemplateContent(Template template)
        {
            if (!File.Exists(template.FilePath))
            {
                Debug.LogWarning($"[ScribeTemplates] Template file not found: {template.FilePath}");
                return;
            }
            
            try
            {
                // Extract markdown content from YAML template
                var lines = File.ReadAllLines(template.FilePath);
                var contentBuilder = new StringBuilder();
                bool inTemplate = false;
                
                foreach (var line in lines)
                {
                    if (!inTemplate)
                    {
                        if (Regex.IsMatch(line, @"^\s*template:\s*\|"))
                        {
                            inTemplate = true;
                            continue;
                        }
                    }
                    else
                    {
                        // Check if we've exited the template block
                        if (line.Length > 0 && !char.IsWhiteSpace(line[0]))
                            break;
                        
                        // Remove YAML indentation (typically 2 spaces)
                        var content = line.StartsWith("  ") ? line[2..] : line;
                        contentBuilder.AppendLine(content);
                    }
                }
                
                template.Content = contentBuilder.ToString();
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[ScribeTemplates] Failed to load template content: {e.Message}");
            }
        }
        
        public string CreateIssueFromTemplate(Template template, ScribeDataManager data)
        {
            var issuesDir = GetIssuesDirectory();
            if (!Directory.Exists(issuesDir))
            {
                Directory.CreateDirectory(issuesDir);
                CreateIssuesReadme(issuesDir);
            }
            
            var fileName = GenerateIssueFileName(data.Title);
            var filePath = Path.Combine(issuesDir, fileName);
            
            var content = GenerateIssueContent(template, data);
            
            try
            {
                File.WriteAllText(filePath, content, new UTF8Encoding(false));
                ImportIfInAssets(filePath);
                
                Debug.Log($"[ScribeTemplates] Created issue: {filePath}");
                return filePath;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[ScribeTemplates] Failed to create issue: {e.Message}");
                return null;
            }
        }
        
        string GenerateIssueContent(Template template, ScribeDataManager data)
        {
            var sb = new StringBuilder();
            
            // Header
            sb.AppendLine($"# Issue: {data.Title}");
            sb.AppendLine($"**Created:** {System.DateTime.UtcNow:yyyy-MM-dd HH:mm:ss 'UTC'}");
            
            if (!string.IsNullOrWhiteSpace(data.Context))
                sb.AppendLine($"**Context:** {data.Context}");
            
            if (!string.IsNullOrWhiteSpace(data.Summary))
                sb.AppendLine($"**Summary:** {data.Summary}");
            
            sb.AppendLine();
            
            // Template content
            if (!string.IsNullOrEmpty(template.Content))
            {
                sb.Append(template.Content);
            }
            
            return sb.ToString();
        }
        
        string GenerateIssueFileName(string title)
        {
            var safeTitle = SanitizeTitle(title);
            if (string.IsNullOrEmpty(safeTitle))
                safeTitle = "Issue";
            
            return $"Issue-{System.DateTime.UtcNow:yyyy-MM-dd}-{safeTitle}.md";
        }
        
        string SanitizeTitle(string title)
        {
            if (string.IsNullOrWhiteSpace(title))
                return "";
            
            var invalid = Path.GetInvalidFileNameChars();
            var result = title;
            
            foreach (var c in invalid)
            {
                result = result.Replace(c.ToString(), "");
            }
            
            return result.Replace(" ", "-");
        }
        
        string GetIssuesDirectory()
        {
            var projectRoot = Directory.GetParent(Application.dataPath).FullName;
            return Path.Combine(projectRoot, "TLDL", "issues");
        }
        
        void CreateIssuesReadme(string issuesDir)
        {
            var readmePath = Path.Combine(issuesDir, "README.md");
            if (File.Exists(readmePath))
                return;
            
            var content = @"# TLDL Issues Directory

This directory contains all issues created using The Scribe.

**Location**: `Root/TLDL/issues/`  
Where `Root/` is the project root containing Assets and Packages directories.

**Important**: Do not rename this directory - automation and CI flows depend on this canonical path.

## Issue Naming Convention
Issues follow the pattern: `Issue-YYYY-MM-DD-Title.md`

## Templates
Issues are created from templates defined in `templates/comments/registry.yaml`
";
            
            File.WriteAllText(readmePath, content, new UTF8Encoding(false));
        }
        
        void ImportIfInAssets(string path)
        {
            var dataPath = Application.dataPath.Replace('\\', '/');
            var normalizedPath = path.Replace('\\', '/');
            
            if (normalizedPath.StartsWith(dataPath))
            {
                var assetPath = "Assets" + normalizedPath[dataPath.Length..];
                UnityEditor.AssetDatabase.ImportAsset(assetPath);
            }
        }
    }
}
