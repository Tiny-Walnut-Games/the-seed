#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;
using TinyWalnutGames.TLDA.Editor.Unity;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles the file browser/navigator panel for the TLDL Scribe
    /// </summary>
    public class ScribeNavigator
    {
        private string _rootPath;
        private string _activeDirPath;
        private readonly Dictionary<string, bool> _folderExpanded = new();
        private Vector2 _navScroll;
        
        private readonly ScribeFileOperations.StatusUpdateDelegate _statusCallback;
        private readonly Action<string> _loadFileCallback;

        public ScribeNavigator(ScribeFileOperations.StatusUpdateDelegate statusCallback, Action<string> loadFileCallback)
        {
            _statusCallback = statusCallback;
            _loadFileCallback = loadFileCallback;
        }

        public void SetRootPath(string rootPath)
        {
            _rootPath = rootPath;
            if (!string.IsNullOrEmpty(_rootPath) && Directory.Exists(_rootPath))
            {
                if (string.IsNullOrEmpty(_activeDirPath)) 
                    _activeDirPath = _rootPath;
            }
        }

        public string GetRootPath() => _rootPath;
        public string GetActiveFolder() => _activeDirPath ?? _rootPath;

        public void DrawNavigatorPanel(float width)
        {
            // Placeholder implementation - will be filled with the full navigator logic
            using (new EditorGUILayout.VerticalScope("box", GUILayout.MaxWidth(width), GUILayout.MinWidth(width)))
            {
                GUILayout.Label("Sudo-GitBook", EditorStyles.boldLabel);
                
                using (new EditorGUILayout.HorizontalScope())
                {
                    EditorGUILayout.TextField("Root", string.IsNullOrEmpty(_rootPath) ? "(not set)" : _rootPath);
                }

                _navScroll = EditorGUILayout.BeginScrollView(_navScroll, GUILayout.ExpandHeight(true));
                
                if (string.IsNullOrEmpty(_rootPath))
                {
                    EditorGUILayout.HelpBox("Choose a root folder to begin.", MessageType.Info);
                }
                else if (!Directory.Exists(_rootPath))
                {
                    EditorGUILayout.HelpBox("Root folder not found. Please choose a new root.", MessageType.Warning);
                }
                else
                {
                    DrawDirectoryNode(_rootPath, 0);
                }
                
                EditorGUILayout.EndScrollView();

                // Active dir indicator
                using (new EditorGUI.DisabledScope(true))
                {
                    EditorGUILayout.TextField("Active Directory", string.IsNullOrEmpty(_activeDirPath) ? "(none)" : _activeDirPath);
                }
            }
        }

        private void DrawDirectoryNode(string path, int depth)
        {
            if (string.IsNullOrEmpty(path) || !Directory.Exists(path)) return;

            string folderName = Path.GetFileName(path);
            if (string.IsNullOrEmpty(folderName)) folderName = path;
            
            if (!_folderExpanded.ContainsKey(path)) 
                _folderExpanded[path] = depth <= 1;

            using (new EditorGUILayout.HorizontalScope())
            {
                _folderExpanded[path] = EditorGUILayout.Foldout(_folderExpanded[path], folderName, true);
                if (GUILayout.Button("Select", GUILayout.Width(60)))
                {
                    _activeDirPath = path;
                    _statusCallback?.Invoke($"Active directory set: {path}");
                }
            }

            if (!_folderExpanded[path]) return;

            try
            {
                // Sort subdirectories
                var subDirs = Directory.GetDirectories(path);
                Array.Sort(subDirs, StringComparer.OrdinalIgnoreCase);
                foreach (var d in subDirs)
                {
                    EditorGUI.indentLevel++;
                    DrawDirectoryNode(d, depth + 1);
                    EditorGUI.indentLevel--;
                }

                // Sort files
                var files = Directory.GetFiles(path);
                Array.Sort(files, StringComparer.OrdinalIgnoreCase);
                foreach (var f in files)
                {
                    var ext = Path.GetExtension(f);
                    if (!ScribeFileFilters.AllowedExts.Contains(ext)) continue;

                    using (new EditorGUILayout.HorizontalScope())
                    {
                        EditorGUI.indentLevel++;
                        var fileName = Path.GetFileName(f);
                        
                        if (GUILayout.Button(fileName, EditorStyles.label))
                        {
                            _loadFileCallback?.Invoke(f);
                        }
                        
                        if (GUILayout.Button("Open", GUILayout.Width(50)))
                        {
                            _loadFileCallback?.Invoke(f);
                        }
                        
                        EditorGUI.indentLevel--;
                    }
                }
            }
            catch (Exception e)
            {
                EditorGUILayout.HelpBox($"Error reading directory: {e.Message}", MessageType.Warning);
            }
        }

        public void ChooseRootFolder()
        {
            var start = string.IsNullOrEmpty(_rootPath) ? Application.dataPath : _rootPath;
            var picked = EditorUtility.OpenFolderPanel("Choose Sudo-GitBook Root", start, "");
            
            if (!string.IsNullOrEmpty(picked))
            {
                _rootPath = picked;
                _activeDirPath = _rootPath;
                _statusCallback?.Invoke($"Root set to: {_rootPath}");
                RefreshNavigator();
            }
        }

        public void RefreshNavigator()
        {
            // Just trigger a repaint for now
        }
    }
}
#endif
