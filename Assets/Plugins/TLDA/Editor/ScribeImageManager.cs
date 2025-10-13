#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using TinyWalnutGames.TLDA.Editor.Unity;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;

// 🔥 GLOBAL DESTRUCTORS - Import the global DestroyImmediate function
using static DestroyImmediateStub;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Manages image loading, caching, and operations for the TLDL Scribe
    /// </summary>
    public class ScribeImageManager
    {
        private readonly Dictionary<string, Texture2D> _imageCache = new();
        private readonly List<string> _imageCacheOrder = new(); // LRU order
        private const int ImageCacheMax = 128;

        public delegate void StatusUpdateDelegate(string message);

        /// <summary>
        /// Gets or loads an image texture from cache
        /// </summary>
        public Texture2D GetImageTexture(string absPath)
        {
            if (string.IsNullOrEmpty(absPath)) return null;

            if (_imageCache.TryGetValue(absPath, out var tex) && tex != null)
            {
                // Move to end of LRU order
                _imageCacheOrder.Remove(absPath);
                _imageCacheOrder.Add(absPath);
                return tex;
            }

            // Try to load the image
            return LoadImageTexture(absPath);
        }

        /// <summary>
        /// Loads an image from disk and adds to cache
        /// </summary>
        private Texture2D LoadImageTexture(string absPath)
        {
            try
            {
                if (!File.Exists(absPath)) return null;

                var bytes = File.ReadAllBytes(absPath);
                if (bytes == null || bytes.Length == 0) return null;

                var tex = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                if (tex.LoadImage(bytes))
                {
                    AddTextureToCache(absPath, tex);
                    return tex;
                }
                else
                {
                    DestroyImmediate(tex);
                    return null;
                }
            }
            catch
            {
                return null; // Ignore IO/format errors
            }
        }

        /// <summary>
        /// Adds texture to cache with LRU eviction
        /// </summary>
        private void AddTextureToCache(string key, Texture2D tex)
        {
            if (tex == null) return;

            _imageCache[key] = tex;
            _imageCacheOrder.Add(key);

            // LRU eviction
            if (_imageCacheOrder.Count > ImageCacheMax)
            {
                var oldest = _imageCacheOrder[0];
                _imageCacheOrder.RemoveAt(0);
                
                if (_imageCache.TryGetValue(oldest, out var oldTex) && oldTex != null)
                {
                    DestroyImmediate(oldTex);
                }
                _imageCache.Remove(oldest);
            }
        }

        /// <summary>
        /// Resolves relative image path to absolute path
        /// </summary>
        public string ResolveImageAbsolutePath(string refPath, string currentFilePath, string activeFolder)
        {
            if (string.IsNullOrEmpty(refPath)) return null;
            
            var norm = refPath.Replace('\\', '/');
            if (Path.IsPathRooted(refPath)) return refPath;

            // Resolve relative to current file directory or active folder
            var baseDir = string.IsNullOrEmpty(currentFilePath) ? activeFolder : Path.GetDirectoryName(currentFilePath);
            if (string.IsNullOrEmpty(baseDir)) baseDir = activeFolder;
            
            var abs = Path.GetFullPath(Path.Combine(baseDir, norm));
            if (File.Exists(abs)) return abs;

            // Try images subfolder under active folder
            var imgDir = EnsureImagesDirectory(baseDir);
            var tryAbs = Path.Combine(imgDir ?? baseDir, Path.GetFileName(norm));
            if (File.Exists(tryAbs)) return tryAbs;
            
            return abs;
        }

        /// <summary>
        /// Ensures images directory exists and returns its path
        /// </summary>
        public string EnsureImagesDirectory(string baseDir)
        {
            if (string.IsNullOrEmpty(baseDir)) return null;
            
            var imagesDir = Path.Combine(baseDir, "images");
            if (!Directory.Exists(imagesDir))
            {
                Directory.CreateDirectory(imagesDir);
            }
            return imagesDir;
        }

        /// <summary>
        /// Creates markdown image link for copying to clipboard
        /// </summary>
        public string CreateImageMarkdownLink(string absPath, string relPath)
        {
            if (string.IsNullOrEmpty(relPath)) return "";
            
            var alt = Path.GetFileNameWithoutExtension(absPath);
            return $"![{alt}]({relPath})";
        }

        /// <summary>
        /// Inserts image markdown at cursor position or appends to end
        /// </summary>
        public ScribeImageInsertResult InsertImageMarkdownAtCursor(string relPath, string rawContent, int cursorIndex)
        {
            var result = new ScribeImageInsertResult();
            var insert = $"![image]({relPath})";

            if (cursorIndex >= 0 && cursorIndex <= (rawContent?.Length ?? 0))
            {
                rawContent ??= string.Empty;
                bool needLeadingNewline = cursorIndex > 0 && rawContent[cursorIndex - 1] != '\n';
                bool needTrailingNewline = cursorIndex < rawContent.Length && rawContent[cursorIndex] != '\n';
                
                var prefix = rawContent[..cursorIndex];
                var suffix = rawContent[cursorIndex..];
                
                var newContent = prefix;
                if (needLeadingNewline) newContent += '\n';
                newContent += insert;
                if (needTrailingNewline) newContent += '\n';
                newContent += suffix;

                result.NewContent = newContent;
                result.NewCursorIndex = prefix.Length + (needLeadingNewline ? 1 : 0) + insert.Length + (needTrailingNewline ? 1 : 0);
                result.InsertedAtCursor = true;
            }
            else
            {
                // Append to end
                var content = rawContent ?? string.Empty;
                if (!content.EndsWith("\n") && content.Length > 0) content += "\n";
                
                result.NewContent = content + insert + "\n";
                result.NewCursorIndex = result.NewContent.Length;
                result.InsertedAtCursor = false;
            }

            return result;
        }

        /// <summary>
        /// Adds an image file to the project and returns the relative path
        /// </summary>
        public ScribeAddImageResult AddImageFile(string startDir, StatusUpdateDelegate statusCallback = null)
        {
            var result = new ScribeAddImageResult();
            
            try
            {
                // 🔥 WARBLER COMPATIBILITY FIX - Convert string array to proper filter format
                var filters = new[] { "Images", "png,jpg,jpeg,gif", "All", "*.*" };
                var picked = EditorUtility.OpenFilePanelWithFilters("Add Image", startDir, string.Join(",", filters));
                
                if (string.IsNullOrEmpty(picked))
                {
                    result.Success = false;
                    result.Cancelled = true;
                    return result;
                }

                var imagesDir = EnsureImagesDirectory(startDir);
                var copyResult = ScribeFileOperations.CopyImageToProject(picked, imagesDir);
                
                if (copyResult.Success)
                {
                    result.Success = true;
                    result.RelativePath = copyResult.RelativePath;
                    result.AbsolutePath = copyResult.DestinationPath;
                    statusCallback?.Invoke($"Image added: {copyResult.RelativePath}");
                }
                else
                {
                    result.Success = false;
                    result.ErrorMessage = copyResult.ErrorMessage;
                    statusCallback?.Invoke($"Failed to add image: {copyResult.ErrorMessage}");
                }

                return result;
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = ex.Message;
                statusCallback?.Invoke($"Failed to add image: {ex.Message}");
                return result;
            }
        }

        /// <summary>
        /// Renders an image in the GUI with size constraints
        /// </summary>
        public void RenderImage(string refPath, string alt, string currentFilePath, string activeFolder, float maxWidth)
        {
            var resolved = ResolveImageAbsolutePath(refPath, currentFilePath, activeFolder);
            if (string.IsNullOrEmpty(resolved))
            {
                EditorGUILayout.HelpBox($"Image not found: {refPath}", MessageType.None);
                return;
            }

            var tex = GetImageTexture(resolved);
            if (tex == null)
            {
                EditorGUILayout.HelpBox($"(missing image) {alt} - {refPath}", MessageType.Warning);
                return;
            }

            var aspect = (float)tex.width / System.Math.Max(1, tex.height);
            var width = System.Math.Min(maxWidth, tex.width);
            var height = width / System.Math.Max(0.01f, aspect);
            
            // Fallback: label with placeholder since facade GUIContent may differ
            EditorGUILayout.LabelField($"[img {alt}] {refPath}");
        }

        /// <summary>
        /// Renders a thumbnail with max size constraint
        /// </summary>
        public void RenderThumbnail(string absPath, float maxSize = 36f)
        {
            var tex = GetImageTexture(absPath);
            if (tex == null)
            {
                GUILayout.Space(4);
                return;
            }
            // Represent thumbnail with text placeholder (facade lack of direct texture label overload)
            GUILayout.Label($"[img]", GUILayout.Width(maxSize), GUILayout.Height(maxSize));
        }

        /// <summary>
        /// Clears the image cache and disposes all textures
        /// </summary>
        public void ClearCache()
        {
            foreach (var tex in _imageCache.Values)
            {
                if (tex != null) DestroyImmediate(tex);
            }
            _imageCache.Clear();
            _imageCacheOrder.Clear();
        }

        /// <summary>
        /// Disposes resources when the manager is no longer needed
        /// </summary>
        public void Dispose()
        {
            ClearCache();
        }
    }

    /// <summary>
    /// Result of inserting image markdown
    /// </summary>
    public class ScribeImageInsertResult
    {
        public string NewContent;
        public int NewCursorIndex;
        public bool InsertedAtCursor;
    }

    /// <summary>
    /// Result of adding an image file
    /// </summary>
    public class ScribeAddImageResult
    {
        public bool Success;
        public bool Cancelled;
        public string RelativePath;
        public string AbsolutePath;
        public string ErrorMessage;
    }
}
#endif
