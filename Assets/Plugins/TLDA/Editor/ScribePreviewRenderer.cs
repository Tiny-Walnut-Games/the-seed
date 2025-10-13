#if UNITY_EDITOR
using System;
using System.Text.RegularExpressions;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;
using TinyWalnutGames.TLDA.Editor.Unity;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles markdown preview rendering for the TLDL Scribe
    /// </summary>
    public class ScribePreviewRenderer
    {
        private readonly ScribeImageManager _imageManager;
        private Vector2 _previewScroll;
        
        // GUI Styles
        private GUIStyle _bodyWrap;
        private GUIStyle _listItem;
        private GUIStyle _h1, _h2, _h3;
        private GUIStyle _codeBlock;

        public ScribePreviewRenderer(ScribeImageManager imageManager)
        {
            _imageManager = imageManager;
            InitializeStyles();
        }

        private void InitializeStyles()
        {
            _bodyWrap = new GUIStyle(EditorStyles.label) { wordWrap = true, richText = true };
            _listItem = new GUIStyle(EditorStyles.label) { wordWrap = true, richText = true };
            _h1 = new GUIStyle(EditorStyles.boldLabel) { fontSize = 16, richText = true, wordWrap = true };
            _h2 = new GUIStyle(EditorStyles.boldLabel) { fontSize = 14, richText = true, wordWrap = true };
            _h3 = new GUIStyle(EditorStyles.boldLabel) { fontSize = 12, richText = true, wordWrap = true };
            
            _codeBlock = new GUIStyle(EditorStyles.textArea) 
            { 
                font = CreateSafeFont("Consolas", 12), 
                wordWrap = false 
            };
        }

        private static Font CreateSafeFont(string family, int size)
        {
            try 
            { 
                return Font.CreateDynamicFontFromOSFont(family, size); 
            } 
            catch 
            { 
                return EditorStyles.textArea.font; 
            }
        }

        public void DrawPreview(string rawContent, ScribeFormData formData, Vector2 windowPosition)
        {
            // Always render from raw if available, otherwise from form
            var md = !string.IsNullOrEmpty(rawContent) ? rawContent : 
                ScribeMarkdownGenerator.BuildMarkdown(formData, DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss 'UTC'"));

            // Improved viewport height calculation for preview
            var baseOffset = 220f;
            var viewportHeight = Math.Max(120f, windowPosition.height - baseOffset);
            
            _previewScroll = EditorGUILayout.BeginScrollView(_previewScroll, GUILayout.Height(viewportHeight), GUILayout.ExpandHeight(true));
            
            GUILayout.Label("Markdown Preview (rendered)", EditorStyles.boldLabel);
            RenderMarkdown(md);
            
            EditorGUILayout.EndScrollView();
        }

        private void RenderMarkdown(string md)
        {
            if (string.IsNullOrEmpty(md)) return;
            
            var lines = md.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);
            var inCode = false;
            var codeBuffer = new System.Text.StringBuilder();
            
            foreach (var raw in lines)
            {
                var line = raw;
                
                if (line.StartsWith("```"))
                {
                    if (!inCode)
                    {
                        inCode = true;
                        codeBuffer.Length = 0;
                    }
                    else
                    {
                        EditorGUILayout.TextArea(codeBuffer.ToString(), _codeBlock, GUILayout.ExpandWidth(true));
                        inCode = false;
                    }
                    continue;
                }
                
                if (inCode)
                {
                    codeBuffer.AppendLine(line);
                    continue;
                }

                // Markdown image: ![alt](path)
                var imgMatch = Regex.Match(line, @"^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$");
                if (imgMatch.Success)
                {
                    var alt = imgMatch.Groups[1].Value;
                    var path = imgMatch.Groups[2].Value;
                    RenderImage(path, alt);
                    continue;
                }

                // Checkbox list items: - [ ] and - [x]
                if (Regex.IsMatch(line, @"^\s*[-*]\s\[( |x|X)\]\s"))
                {
                    var isChecked = line.IndexOf("[x]", StringComparison.OrdinalIgnoreCase) >= 0;
                    var text = Regex.Replace(line, @"^\s*[-*]\s\[( |x|X)\]\s", "");
                    EditorGUI.BeginDisabledGroup(true);
                    EditorGUILayout.ToggleLeft(ApplyInlineFormatting(text), isChecked);
                    EditorGUI.EndDisabledGroup();
                    continue;
                }

                // Headers
                if (line.StartsWith("### "))
                {
                    EditorGUILayout.LabelField(line[4..], _h3);
                }
                else if (line.StartsWith("## "))
                {
                    EditorGUILayout.LabelField(line[3..], _h2);
                }
                else if (line.StartsWith("# "))
                {
                    EditorGUILayout.LabelField(line[2..], _h1);
                }
                else if (line.StartsWith("- ") || line.StartsWith("* "))
                {
                    EditorGUILayout.LabelField("• " + ApplyInlineFormatting(line[2..]), _listItem);
                }
                else if (string.IsNullOrWhiteSpace(line))
                {
                    GUILayout.Space(4);
                }
                else
                {
                    EditorGUILayout.LabelField(ApplyInlineFormatting(line), _bodyWrap);
                }
            }
        }

        private void RenderImage(string refPath, string alt)
        {
            // For now, just show a placeholder since we need currentFilePath and activeFolder
            EditorGUILayout.HelpBox($"Image: {alt} - {refPath}", MessageType.None);
            
            // TODO: Implement full image rendering when we have access to file paths
            // _imageManager.RenderImage(refPath, alt, currentFilePath, activeFolder, maxWidth);
        }

        private string ApplyInlineFormatting(string input)
        {
            if (string.IsNullOrEmpty(input)) return string.Empty;
            
            var s = input;
            s = s.Replace("<", "&lt;").Replace(">", "&gt;");
            s = Regex.Replace(s, "`([^`]+)`", m => $"<color=#c8e1ff><b>{m.Groups[1].Value}</b></color>");
            s = Regex.Replace(s, @"\*\*([^*]+)\*\*", m => $"<b>{m.Groups[1].Value}</b>");
            s = Regex.Replace(s, @"(?<!\*)\*([^*]+)\*(?!\*)", m => $"<i>{m.Groups[1].Value}</i>");
            s = Regex.Replace(s, @"_([^_]+)_", m => $"<i>{m.Groups[1].Value}</i>");
            s = Regex.Replace(s, @"\[([^\]]+)\]\(([^)]+)\)", m => $"<color=#4ea1ff><u>{m.Groups[1].Value}</u></color>");
            
            return s;
        }
    }
}
#endif
