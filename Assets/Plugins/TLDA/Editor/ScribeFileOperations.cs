#if UNITY_EDITOR
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles all file operations for the TLDL Scribe
    /// </summary>
    public static class ScribeFileOperations
    {
        public delegate void StatusUpdateDelegate(string message);

        /// <summary>
        /// Loads a file and returns its content with basic metadata parsing
        /// </summary>
        public static ScribeLoadResult LoadFile(string absPath)
        {
            var result = new ScribeLoadResult();
            try
            {
                result.Content = File.ReadAllText(absPath);
                result.FilePath = absPath;
                result.Success = true;
                
                // Parse basic metadata from the content
                result.ParsedMetadata = ParseBasicMetadata(result.Content);
                
                return result;
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = ex.Message;
                return result;
            }
        }

        /// <summary>
        /// Saves content to a file with UTF-8 encoding (no BOM)
        /// </summary>
        public static ScribeSaveResult SaveFile(string absPath, string content, StatusUpdateDelegate statusCallback = null)
        {
            var result = new ScribeSaveResult();
            try
            {
                File.WriteAllText(absPath, content ?? string.Empty, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
                PostWriteImport(absPath);
                result.Success = true;
                result.FilePath = absPath;
                statusCallback?.Invoke($"Saved: {MakeProjectRelative(absPath)}");
                return result;
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = ex.Message;
                statusCallback?.Invoke($"Failed to save: {ex.Message}");
                return result;
            }
        }

        /// <summary>
        /// Creates a TLDL file with generated content
        /// </summary>
        public static ScribeSaveResult CreateTLDLFile(ScribeFormData formData, string targetFolder, StatusUpdateDelegate statusCallback = null)
        {
            try
            {
                var date = DateTime.UtcNow.ToString("yyyy-MM-dd");
                var safeTitle = ScribeUtils.SanitizeTitle(formData.Title);
                if (string.IsNullOrEmpty(safeTitle)) safeTitle = "Entry";
                
                var fileName = $"TLDL-{date}-{safeTitle}.md";
                
                if (!Directory.Exists(targetFolder)) 
                    Directory.CreateDirectory(targetFolder);
                
                var absPath = Path.Combine(targetFolder, fileName);
                var createdTs = DateTime.UtcNow.ToString(format: "yyyy-MM-dd HH:mm:ss 'UTC'");
                var md = ScribeMarkdownGenerator.BuildMarkdown(formData, createdTs, date, safeTitle);
                
                return SaveFile(absPath, md, statusCallback);
            }
            catch (Exception ex)
            {
                var result = new ScribeSaveResult
                {
                    Success = false,
                    ErrorMessage = ex.Message
                };
                statusCallback?.Invoke($"Error creating file: {ex.Message}");
                return result;
            }
        }

        /// <summary>
        /// Duplicates a file with automatic naming (Copy, Copy 2, etc.)
        /// </summary>
        public static ScribeSaveResult DuplicateFile(string srcPath)
        {
            var result = new ScribeSaveResult();
            try
            {
                if (string.IsNullOrEmpty(srcPath) || !File.Exists(srcPath))
                    throw new FileNotFoundException("Source file not found", srcPath);

                var target = GenerateUniqueCopyPath(srcPath);
                File.Copy(srcPath, target, overwrite: false);
                PostWriteImport(target);
                
                result.Success = true;
                result.FilePath = target;
                return result;
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = ex.Message;
                return result;
            }
        }

        /// <summary>
        /// Copies an image to the images directory and returns the relative path
        /// </summary>
        public static ScribeImageCopyResult CopyImageToProject(string sourcePath, string imagesDirectory)
        {
            var result = new ScribeImageCopyResult();
            try
            {
                if (!Directory.Exists(imagesDirectory))
                    Directory.CreateDirectory(imagesDirectory);

                var fileName = Path.GetFileName(sourcePath);
                var dest = Path.Combine(imagesDirectory, fileName);
                var uniqueDest = dest;
                int i = 1;
                
                while (File.Exists(uniqueDest))
                {
                    var nameWithoutExt = Path.GetFileNameWithoutExtension(fileName);
                    var ext = Path.GetExtension(fileName);
                    uniqueDest = Path.Combine(imagesDirectory, $"{nameWithoutExt}_{i}{ext}");
                    i++;
                }

                File.Copy(sourcePath, uniqueDest, overwrite: false);
                PostWriteImport(uniqueDest);

                result.Success = true;
                result.DestinationPath = uniqueDest;
                result.RelativePath = $"images/{Path.GetFileName(uniqueDest)}".Replace('\\', '/');
                
                return result;
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = ex.Message;
                return result;
            }
        }

        /// <summary>
        /// Parses basic metadata from markdown content
        /// </summary>
        public static ScribeMetadata ParseBasicMetadata(string md)
        {
            var metadata = new ScribeMetadata();
            if (string.IsNullOrEmpty(md)) return metadata;
            
            try
            {
                using var reader = new StringReader(md);
                string line;
                while ((line = reader.ReadLine()) != null)
                {
                    if (line.StartsWith("**Author:"))
                    {
                        var value = line["**Author:**".Length..].Trim();
                        if (!string.IsNullOrEmpty(value)) metadata.Author = value;
                    }
                    else if (line.StartsWith("**Summary:"))
                    {
                        var value = line["**Summary:**".Length..].Trim();
                        if (!string.IsNullOrEmpty(value)) metadata.Summary = value;
                    }
                    else if (line.StartsWith("**Context:"))
                    {
                        var value = line["**Context:**".Length..].Trim();
                        if (!string.IsNullOrEmpty(value)) metadata.Context = value;
                    }
                    else if (line.StartsWith("**Tags"))
                    {
                        var idx = line.IndexOf(':');
                        if (idx >= 0)
                        {
                            var value = line[(idx + 1)..].Trim();
                            if (!string.IsNullOrEmpty(value))
                            {
                                metadata.TagsCsv = value.Replace('#', ' ').Replace("  ", " ").Trim().Replace(' ', ',');
                            }
                        }
                    }
                }
            }
            catch
            {
                // Ignore parsing errors
            }
            
            return metadata;
        }

        /// <summary>
        /// Generates a unique copy path (Name Copy.ext, Name Copy 2.ext, etc.)
        /// </summary>
        private static string GenerateUniqueCopyPath(string srcPath)
        {
            var dir = Path.GetDirectoryName(srcPath) ?? "";
            var name = Path.GetFileNameWithoutExtension(srcPath);
            var ext = Path.GetExtension(srcPath);

            var candidate = Path.Combine(dir, $"{name} Copy{ext}");
            int i = 2;
            while (File.Exists(candidate))
            {
                candidate = Path.Combine(dir, $"{name} Copy {i}{ext}");
                i++;
            }
            return candidate;
        }

        /// <summary>
        /// Converts absolute path to project-relative path
        /// </summary>
        public static string MakeProjectRelative(string absPath)
        {
            var projectRoot = Directory.GetParent(Application.dataPath)?.FullName.Replace('\\', '/');
            if (string.IsNullOrEmpty(projectRoot)) return absPath;
            
            var norm = absPath.Replace('\\', '/');
            if (norm.StartsWith(projectRoot))
            {
                return norm[(projectRoot.Length + 1)..];
            }
            return absPath;
        }

        /// <summary>
        /// Imports asset if it's within the Unity project
        /// </summary>
        private static void PostWriteImport(string absPath)
        {
            if (string.IsNullOrEmpty(absPath)) return;
            var unityPath = MakeUnityPath(absPath);
            if (!string.IsNullOrEmpty(unityPath))
            {
                AssetDatabase.ImportAsset(unityPath, ImportAssetOptions.ForceSynchronousImport);
            }
        }

        /// <summary>
        /// Converts absolute path to Unity asset path (Assets/...)
        /// </summary>
        private static string MakeUnityPath(string absPath)
        {
            var norm = absPath.Replace('\\', '/');
            var dataPath = Application.dataPath.Replace('\\', '/');
            if (norm.StartsWith(dataPath, StringComparison.OrdinalIgnoreCase))
            {
                return "Assets" + norm[dataPath.Length..];
            }
            return null;
        }
    }

    /// <summary>
    /// Result of loading a file
    /// </summary>
    public class ScribeLoadResult
    {
        public bool Success;
        public string Content;
        public string FilePath;
        public string ErrorMessage;
        public ScribeMetadata ParsedMetadata;
    }

    /// <summary>
    /// Result of saving a file
    /// </summary>
    public class ScribeSaveResult
    {
        public bool Success;
        public string FilePath;
        public string ErrorMessage;
    }

    /// <summary>
    /// Result of copying an image
    /// </summary>
    public class ScribeImageCopyResult
    {
        public bool Success;
        public string DestinationPath;
        public string RelativePath;
        public string ErrorMessage;
    }

    /// <summary>
    /// Parsed metadata from a markdown file
    /// </summary>
    public class ScribeMetadata
    {
        public string Author = "";
        public string Summary = "";
        public string Context = "";
        public string TagsCsv = "";
    }
}
#endif
