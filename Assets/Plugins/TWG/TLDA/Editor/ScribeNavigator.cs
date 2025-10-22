using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEditor;

namespace LivingDevAgent.Editor.Scribe
{
    /// <summary>
    /// 🔧 ENHANCEMENT READY - Advanced file navigator with script support and selection state
    /// Current: Basic markdown navigator with folder traversal
    /// Enhancement path: Multi-format support, selection persistence, script editing integration
    /// Sacred Mission: Transform into the legendary "Spellsmith" script browser!
    /// </summary>
    public class ScribeNavigator
    {
        private readonly ScribeFileOperations _fileOps;
        private string _rootPath = "";
        private string _activePath = "";
        private string _selectedFilePath = ""; // 🔧 Track selected file for blue highlighting
        private readonly Dictionary<string, bool> _folderExpanded = new();
        private Vector2 _scrollPosition;
        
        // 🔧 ENHANCEMENT READY - Multi-format file support for Spellsmith integration
        private readonly Dictionary<string, Color> _fileTypeColors = new()
        {
            { ".md", new Color(0.4f, 0.8f, 1f) },      // Light blue - readable
            { ".py", new Color(0.5f, 1f, 0.5f) },      // Light green - readable  
            { ".sh", new Color(1f, 1f, 0.4f) },        // Light yellow - readable
            { ".js", new Color(0.6f, 0.8f, 1f) },      // Light blue - readable
            { ".mjs", new Color(0.6f, 0.8f, 1f) },     // Light blue - readable
            { ".cs", new Color(0.8f, 0.6f, 1f) },      // Light purple - readable
            { ".yaml", new Color(1f, 0.6f, 1f) },      // Light magenta - readable
            { ".yml", new Color(1f, 0.6f, 1f) },       // Light magenta - readable
            { ".json", new Color(1f, 0.8f, 0.4f) },    // Light orange - readable
            // 🖼️ Image file support
            { ".png", new Color(0.9f, 0.9f, 0.5f) },   // Light yellow for images
            { ".jpg", new Color(0.9f, 0.9f, 0.5f) },   // Light yellow for images
            { ".jpeg", new Color(0.9f, 0.9f, 0.5f) },  // Light yellow for images
            { ".gif", new Color(0.9f, 0.9f, 0.5f) },   // Light yellow for images
            { ".bmp", new Color(0.9f, 0.9f, 0.5f) },   // Light yellow for images
            { ".tga", new Color(0.9f, 0.9f, 0.5f) }    // Light yellow for images
        };
        
        // 🖼️ Image thumbnail cache for performance
        private readonly Dictionary<string, Texture2D> _thumbnailCache = new();
        private const int ThumbnailSize = 32;
        
        // Events
        public event System.Action<string> OnFileSelected;
        public event System.Action<string> OnDirectorySelected;
        
        public ScribeNavigator(ScribeFileOperations fileOps)
        {
            _fileOps = fileOps;
            LoadRootPath();
        }
        
        public void SetSelectedFile(string filePath)
        {
            _selectedFilePath = filePath;
        }
        
        public void Draw(float width)
        {
            EditorGUILayout.BeginVertical(GUILayout.Width(width));
            {
                DrawHeader();
                DrawNavigatorTree();
                DrawFooter();
            }
            EditorGUILayout.EndVertical();
        }
        
        void DrawHeader()
        {
            GUILayout.Label("📁 Spellsmith Navigator", EditorStyles.boldLabel);
            
            if (GUILayout.Button("Choose Root..."))
            {
                ChooseRootFolder();
            }
            
            EditorGUILayout.TextField("Root", _rootPath);
            
            // 🔧 Quick access buttons for common locations
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("📜 Docs", GUILayout.Width(50)))
                {
                    var docsPath = Path.Combine(Application.dataPath, "../docs");
                    if (Directory.Exists(docsPath))
                    {
                        _rootPath = Path.GetFullPath(docsPath);
                        SaveRootPath();
                    }
                }
                
                if (GUILayout.Button("⚗️ Scripts", GUILayout.Width(60)))
                {
                    var scriptsPath = Path.Combine(Application.dataPath, "../scripts");
                    if (Directory.Exists(scriptsPath))
                    {
                        _rootPath = Path.GetFullPath(scriptsPath);
                        SaveRootPath();
                    }
                }
                
                if (GUILayout.Button("📦 Src", GUILayout.Width(40)))
                {
                    var srcPath = Path.Combine(Application.dataPath, "../src");
                    if (Directory.Exists(srcPath))
                    {
                        _rootPath = Path.GetFullPath(srcPath);
                        SaveRootPath();
                    }
                }
            }
            EditorGUILayout.EndHorizontal();
        }
        
        void DrawNavigatorTree()
        {
            // 🔧 CRITICAL FIX: Ensure proper scrollbar display with explicit style
            _scrollPosition = EditorGUILayout.BeginScrollView(
                _scrollPosition, 
                GUILayout.ExpandHeight(true),
                GUILayout.ExpandWidth(true)
            );
            {
                if (!string.IsNullOrEmpty(_rootPath) && Directory.Exists(_rootPath))
                {
                    EditorGUILayout.BeginVertical();
                    {
                        DrawDirectoryNode(_rootPath, 0);
                    }
                    EditorGUILayout.EndVertical();
                }
                else
                {
                    EditorGUILayout.HelpBox("Choose a root folder to begin the adventure", MessageType.Info);
                }
            }
            EditorGUILayout.EndScrollView();
        }
        
        void DrawDirectoryNode(string path, int depth)
        {
            // KeeperNote: Recursive directory traversal with state preservation
            var dirName = Path.GetFileName(path);
            if (string.IsNullOrEmpty(dirName)) dirName = path;
            
            if (!_folderExpanded.ContainsKey(path))
                _folderExpanded[path] = depth <= 1;
            
            EditorGUILayout.BeginHorizontal();
            {
                GUILayout.Space(depth * 20);
                
                _folderExpanded[path] = EditorGUILayout.Foldout(
                    _folderExpanded[path], 
                    $"📁 {dirName}", 
                    true
                );
                
                if (GUILayout.Button("Select", GUILayout.Width(60)))
                {
                    _activePath = path;
                    OnDirectorySelected?.Invoke(path);
                }
            }
            EditorGUILayout.EndHorizontal();
            
            if (_folderExpanded[path])
            {
                // Draw subdirectories
                var dirs = Directory.GetDirectories(path);
                System.Array.Sort(dirs);
                foreach (var dir in dirs)
                {
                    DrawDirectoryNode(dir, depth + 1);
                }
                
                // 🔧 ENHANCEMENT READY - Multi-format file support
                // Current: Text files and images
                // Enhancement path: All development-related files with proper thumbnails
                var supportedExtensions = new[] { 
                    "*.asset", "*.md", "*.py", "*.sh", "*.js", "*.mjs", "*.cs", "*.yaml", "*.yml", "*.json", "*.txt",
                    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.tga" // 🖼️ Image files
                };
                var allFiles = new List<string>();
                
                foreach (var pattern in supportedExtensions)
                {
                    var files = Directory.GetFiles(path, pattern);
                    allFiles.AddRange(files);
                }
                
                System.Array.Sort(allFiles.ToArray());
                foreach (var file in allFiles)
                {
                    DrawFileNode(file, depth + 1);
                }
            }
        }
        
        void DrawFileNode(string path, int depth)
        {
            var fileName = Path.GetFileName(path);
            var extension = Path.GetExtension(path).ToLower();
            var isSelected = _selectedFilePath == path;
            var isImage = IsImageFile(extension);
            
            // Get file type icon and color
            var icon = GetFileIcon(extension);
            var color = _fileTypeColors.ContainsKey(extension) ? _fileTypeColors[extension] : Color.white;
            
            EditorGUILayout.BeginHorizontal();
            {
                GUILayout.Space(depth * 20);
                
                // 🖼️ LEGENDARY - Image thumbnail display
                if (isImage)
                {
                    DrawImageFileNode(path, fileName, isSelected, icon, color);
                }
                else
                {
                    DrawRegularFileNode(path, fileName, isSelected, icon, color);
                }
            }
            EditorGUILayout.EndHorizontal();
        }
        
        /// <summary>
        /// 🖼️ LEGENDARY - Image file display with thumbnail preview
        /// Sacred Vision: Visual file browser with actual image previews!
        /// </summary>
        void DrawImageFileNode(string path, string fileName, bool isSelected, string icon, Color color)
        {
            var thumbnail = GetOrCreateThumbnail(path);
            
            var buttonStyle = isSelected ? EditorStyles.selectionRect : EditorStyles.label;
            var originalColor = GUI.color;
            GUI.color = isSelected ? Color.white : color;
            
            EditorGUILayout.BeginHorizontal();
            {
                // Thumbnail preview
                if (thumbnail != null)
                {
                    var thumbnailRect = GUILayoutUtility.GetRect(ThumbnailSize, ThumbnailSize, GUILayout.Width(ThumbnailSize), GUILayout.Height(ThumbnailSize));
                    GUI.DrawTexture(thumbnailRect, thumbnail, ScaleMode.ScaleToFit);
                    
                    // Click on thumbnail to select
                    if (Event.current.type == EventType.MouseDown && thumbnailRect.Contains(Event.current.mousePosition))
                    {
                        _selectedFilePath = path;
                        OnFileSelected?.Invoke(path);
                        Debug.Log($"🖼️ Image selected: {fileName}");
                        Event.current.Use();
                    }
                }
                else
                {
                    GUILayout.Box(icon, GUILayout.Width(ThumbnailSize), GUILayout.Height(ThumbnailSize));
                }
                
                // File name
                if (GUILayout.Button(fileName, buttonStyle, GUILayout.ExpandWidth(true)))
                {
                    _selectedFilePath = path;
                    OnFileSelected?.Invoke(path);
                    Debug.Log($"🖼️ Image selected: {fileName}");
                }
            }
            EditorGUILayout.EndHorizontal();
            
            GUI.color = originalColor;
        }
        
        /// <summary>
        /// 🔧 Regular file display (non-images)
        /// </summary>
        void DrawRegularFileNode(string path, string fileName, bool isSelected, string icon, Color color)
        {
            var buttonStyle = isSelected ? EditorStyles.selectionRect : EditorStyles.label;
            var originalColor = GUI.color;
            
            // Apply file type color but make it readable
            GUI.color = isSelected ? Color.white : color;
            
            if (GUILayout.Button($"{icon} {fileName}", buttonStyle, GUILayout.ExpandWidth(true)))
            {
                _selectedFilePath = path;
                OnFileSelected?.Invoke(path);
                Debug.Log($"🔵 File selected: {fileName}");
            }
            
            GUI.color = originalColor;
        }
        
        /// <summary>
        /// 🖼️ Get or create thumbnail for image files
        /// </summary>
        Texture2D GetOrCreateThumbnail(string imagePath)
        {
            if (_thumbnailCache.TryGetValue(imagePath, out var cached))
            {
                return cached;
            }
            
            try
            {
                if (File.Exists(imagePath))
                {
                    var imageBytes = File.ReadAllBytes(imagePath);
                    var originalTexture = new Texture2D(2, 2);
                    
                    if (originalTexture.LoadImage(imageBytes))
                    {
                        // Create thumbnail
                        var thumbnail = CreateThumbnail(originalTexture);
                        _thumbnailCache[imagePath] = thumbnail;
                        
                        // Clean up original
                        Object.DestroyImmediate(originalTexture);
                        
                        return thumbnail;
                    }
                    else
                    {
                        Object.DestroyImmediate(originalTexture);
                    }
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"Failed to create thumbnail for {imagePath}: {e.Message}");
            }
            
            return null;
        }
        
        /// <summary>
        /// 🖼️ Create a thumbnail from full-size texture
        /// </summary>
        Texture2D CreateThumbnail(Texture2D original)
        {
            var thumbnail = new Texture2D(ThumbnailSize, ThumbnailSize, TextureFormat.RGBA32, false);
            
            // Simple nearest-neighbor scaling for thumbnail
            var scaleX = (float)original.width / ThumbnailSize;
            var scaleY = (float)original.height / ThumbnailSize;
            
            for (int y = 0; y < ThumbnailSize; y++)
            {
                for (int x = 0; x < ThumbnailSize; x++)
                {
                    var sourceX = Mathf.FloorToInt(x * scaleX);
                    var sourceY = Mathf.FloorToInt(y * scaleY);
                    
                    sourceX = Mathf.Clamp(sourceX, 0, original.width - 1);
                    sourceY = Mathf.Clamp(sourceY, 0, original.height - 1);
                    
                    var color = original.GetPixel(sourceX, sourceY);
                    thumbnail.SetPixel(x, y, color);
                }
            }
            
            thumbnail.Apply();
            return thumbnail;
        }
        
        /// <summary>
        /// 🖼️ Check if file is an image
        /// </summary>
        bool IsImageFile(string extension)
        {
            return extension switch
            {
                ".png" or ".jpg" or ".jpeg" or ".gif" or ".bmp" or ".tga" => true,
                _ => false
            };
        }
        
        void ChooseRootFolder()
        {
            var picked = EditorUtility.OpenFolderPanel(
                "Choose Documentation Root", 
                _rootPath, 
                ""
            );
            
            if (!string.IsNullOrEmpty(picked))
            {
                _rootPath = picked;
                _activePath = _rootPath;
                SaveRootPath();
            }
        }
        
        void LoadRootPath()
        {
            _rootPath = EditorPrefs.GetString("LDA_SCRIBE_ROOT", "");
            if (string.IsNullOrEmpty(_rootPath))
            {
                // Default to TLDA docs folder
                var defaultPath = Path.Combine(Application.dataPath, "Plugins/TLDA/docs");
                if (Directory.Exists(defaultPath))
                {
                    _rootPath = defaultPath;
                }
            }
        }
        
        void SaveRootPath()
        {
            EditorPrefs.SetString("LDA_SCRIBE_ROOT", _rootPath);
        }
        
        void DrawFooter()
        {
            EditorGUILayout.TextField("Active", _activePath);
            
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("Refresh"))
                {
                    // Force refresh
                    _folderExpanded.Clear();
                }
                
                if (GUILayout.Button("New Folder"))
                {
                    CreateNewFolder();
                }
            }
            EditorGUILayout.EndHorizontal();
        }
        
        void CreateNewFolder()
        {
            // Implementation for creating new folder
            var folderName = EditorUtility.SaveFolderPanel(
                "Create New Folder",
                _activePath,
                "NewFolder"
            );
            
            if (!string.IsNullOrEmpty(folderName))
            {
                Directory.CreateDirectory(folderName);
                _folderExpanded.Clear(); // Force refresh
            }
        }
        
        string GetFileIcon(string extension)
        {
            return extension switch
            {
                ".md" => "📜",
                ".py" => "🐍",
                ".sh" => "⚡",
                ".js" or ".mjs" => "📜",
                ".cs" => "🔷",
                ".yaml" or ".yml" => "⚙️",
                ".json" => "📋",
                // 🖼️ Image file icons
                ".png" or ".jpg" or ".jpeg" => "🖼️",
                ".gif" => "🎬",
                ".bmp" or ".tga" => "🖼️",
                _ => "📄"
            };
        }
    }
}
