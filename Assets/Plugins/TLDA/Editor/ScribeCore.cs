#if UNITY_EDITOR
using System;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;
using TinyWalnutGames.TLDA.Editor.Unity;

// 🔥 WARBLER COMPATIBILITY - Use facade types instead of real Unity types
using UnityDebug = TinyWalnutGames.TLDA.Editor.Unity.Debug;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Core TLDL Scribe window - orchestrates all the components
    /// </summary>
    public class ScribeCore : EditorWindow
    {
        // Core data
        private ScribeFormData _formData = new();
        private string _rawContent = string.Empty;
        private string _currentFilePath = "";
        private string _statusLine = "Ready";

        // Component managers
        private ScribeImageManager _imageManager;
        private ScribeNavigator _navigator;
        private ScribeFormBuilder _formBuilder;
        private ScribeEditor _editor;
        private ScribePreviewRenderer _previewRenderer;
        private ScribeTemplateManager _templateManager;

        // UI state
        private Vector2 _scroll;
        private int _tab = 0; // 0=Form, 1=Editor, 2=Preview
        private bool _rawDirty = false;
        private string _rawGeneratedSnapshot = null;
        private string _lastFormSnapshot = null;
        private bool _autoSyncEditor = false;

        // Constants
        private const string EditorPrefsRootKey = "LDA_TLDL_ROOT";

        #region Unity Lifecycle

        [MenuItem("Tools/Living Dev Agent/The Scribe")]
        public static void OpenScribe()
        {
            OpenWindow("The Scribe");
        }

        [MenuItem("Tools/Living Dev Agent/TLDL Wizard (Deprecated)")]
        public static void OpenDeprecated()
        {
            OpenWindow("The Scribe (Deprecated)");
        }

        // Back-compat: keep old entry point name but route to Scribe
        public static void ShowWindow()
        {
            OpenWindow("The Scribe");
        }

        static void OpenWindow(string title)
        {
            var wnd = GetWindow<ScribeCore>(true, title, true);
            wnd.minSize = new Vector2(900, 600);
            wnd.Show();
        }

        public override void OnEnable()
        {
            InitializeComponents();
            LoadSettings();
        }

        private void OnDisable()
        {
            _imageManager?.Dispose();
        }

        public override void OnGUI()
        {
            try
            {
                DrawTopToolbar();
                EditorGUILayout.Space(2);

                using (new EditorGUILayout.HorizontalScope())
                {
                    _navigator?.DrawNavigatorPanel(260);

                    using (new EditorGUILayout.VerticalScope())
                    {
                        DrawTabBar();
                        EditorGUILayout.Space(6);

                        switch (_tab)
                        {
                            case 0: _formBuilder?.DrawForm(_formData, position); break;
                            case 1: _editor?.DrawRawEditor(ref _rawContent, ref _rawDirty, _rawGeneratedSnapshot, position); break;
                            case 2: _previewRenderer?.DrawPreview(_rawContent, _formData, position); break;
                        }
                    }
                }

                EditorGUILayout.Space(4);
                EditorGUILayout.HelpBox(_statusLine, MessageType.None);

                HandleAutoSync();
            }
            catch (Exception ex)
            {
                EditorGUILayout.HelpBox($"Error in OnGUI: {ex.Message}", MessageType.Error);
                UnityDebug.LogError($"[The Scribe] OnGUI Error: {ex}");
            }
        }

        #endregion

        #region Initialization

        private void InitializeComponents()
        {
            _imageManager = new ScribeImageManager();
            _navigator = new ScribeNavigator(UpdateStatus, LoadFileCallback);
            _formBuilder = new ScribeFormBuilder(_imageManager, UpdateStatus);
            _editor = new ScribeEditor(_imageManager, UpdateStatus);
            _previewRenderer = new ScribePreviewRenderer(_imageManager);
            _templateManager = new ScribeTemplateManager(UpdateStatus);
        }

        private void LoadSettings()
        {
            var rootPath = EditorPrefs.GetString(EditorPrefsRootKey, string.Empty);
            _navigator?.SetRootPath(rootPath);
        }

        #endregion

        #region UI Drawing

        private void DrawTopToolbar()
        {
            using (new EditorGUILayout.HorizontalScope(EditorStyles.toolbar))
            {
                // Navigator controls
                if (GUILayout.Button("Choose Root…", EditorStyles.toolbarButton, GUILayout.Width(110)))
                {
                    _navigator?.ChooseRootFolder();
                    SaveSettings();
                }

                if (GUILayout.Button("Refresh", EditorStyles.toolbarButton, GUILayout.Width(70)))
                {
                    _navigator?.RefreshNavigator();
                }

                GUILayout.Space(8);

                // File operations
                if (GUILayout.Button("Load File…", EditorStyles.toolbarButton, GUILayout.Width(90)))
                {
                    LoadFileDialog();
                }

                using (new EditorGUI.DisabledScope(string.IsNullOrEmpty(_rawContent)))
                {
                    if (GUILayout.Button("Save Raw", EditorStyles.toolbarButton, GUILayout.Width(80)))
                    {
                        SaveRaw();
                    }
                    if (GUILayout.Button("Save Raw As…", EditorStyles.toolbarButton, GUILayout.Width(100)))
                    {
                        SaveRawAs();
                    }
                }

                GUILayout.FlexibleSpace();

                // Form operations
                if (GUILayout.Button("Generate From Form → Editor", EditorStyles.toolbarButton))
                {
                    if (WarnOverwriteRawIfDirty())
                    {
                        GenerateFromForm();
                        _tab = 1; // jump to Editor
                    }
                }

                if (GUILayout.Button("Create TLDL File", EditorStyles.toolbarButton))
                {
                    CreateTLDLFile();
                }
            }
        }

        private void DrawTabBar()
        {
            var tabs = new[] { "Form", "Editor", "Preview" };
            _tab = GUILayout.Toolbar(_tab, tabs);
        }

        #endregion

        #region Core Operations

        private void GenerateFromForm()
        {
            var createdTs = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss 'UTC'");
            var md = ScribeMarkdownGenerator.BuildMarkdown(_formData, createdTs);
            _rawContent = md;
            _rawGeneratedSnapshot = md;
            _rawDirty = false;
            _lastFormSnapshot = BuildFormSnapshot();
            UpdateStatus("Generated content from form into Editor");
        }

        private void CreateTLDLFile()
        {
            var activeFolder = _navigator?.GetActiveFolder() ?? GetDefaultFolder();
            var result = ScribeFileOperations.CreateTLDLFile(_formData, activeFolder, UpdateStatus);
            
            if (result.Success)
            {
                _currentFilePath = result.FilePath;
                var createdTs = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss 'UTC'");
                _rawContent = ScribeMarkdownGenerator.BuildMarkdown(_formData, createdTs);
                _rawGeneratedSnapshot = _rawContent;
                _rawDirty = false;
                _navigator?.RefreshNavigator();
            }
        }

        private void LoadFileDialog()
        {
            var dir = _navigator?.GetActiveFolder() ?? GetDefaultFolder();
            // 🔥 WARBLER COMPATIBILITY FIX - Convert string array to proper filter format
            var filters = new[] { "All", "*.*", "Markdown", "md,markdown", "Text", "txt,log", "XML", "xml" };
            var picked = EditorUtility.OpenFilePanelWithFilters("Open Document", dir, string.Join(",", filters));
            
            if (!string.IsNullOrEmpty(picked))
            {
                LoadFileCallback(picked);
            }
        }

        private void LoadFileCallback(string absPath)
        {
            var result = ScribeFileOperations.LoadFile(absPath);
            if (result.Success)
            {
                _currentFilePath = result.FilePath;
                _rawContent = result.Content;
                _rawGeneratedSnapshot = result.Content;
                _rawDirty = false;
                
                // Apply parsed metadata to form
                if (result.ParsedMetadata != null)
                {
                    ApplyMetadataToForm(result.ParsedMetadata);
                }
                
                UpdateStatus($"Loaded: {ScribeFileOperations.MakeProjectRelative(absPath)}");
                _tab = 1; // Editor
            }
            else
            {
                UpdateStatus($"Failed to load file: {result.ErrorMessage}");
            }
        }

        private void SaveRaw()
        {
            if (!string.IsNullOrEmpty(_currentFilePath))
            {
                var result = ScribeFileOperations.SaveFile(_currentFilePath, _rawContent, UpdateStatus);
                if (result.Success)
                {
                    _navigator?.RefreshNavigator();
                }
            }
            else
            {
                SaveRawAs();
            }
        }

        private void SaveRawAs()
        {
            var dir = _navigator?.GetActiveFolder() ?? GetDefaultFolder();
            var suggested = $"TLDL-{DateTime.UtcNow:yyyy-MM-dd}-Entry.md";
            var picked = EditorUtility.SaveFilePanel("Save Document As", dir, suggested, "md");
            
            if (!string.IsNullOrEmpty(picked))
            {
                var result = ScribeFileOperations.SaveFile(picked, _rawContent, UpdateStatus);
                if (result.Success)
                {
                    _currentFilePath = result.FilePath;
                    _navigator?.RefreshNavigator();
                }
            }
        }

        #endregion

        #region Helpers

        private void UpdateStatus(string message)
        {
            _statusLine = message;
            Repaint();
        }

        private bool WarnOverwriteRawIfDirty()
        {
            if (!_rawDirty) return true;
            return EditorUtility.DisplayDialog("Overwrite Raw Editor?", 
                "You have unsaved manual edits in the raw editor. Overwrite with regenerated content?", 
                "Overwrite", "Cancel");
        }

        private void HandleAutoSync()
        {
            if (_autoSyncEditor)
            {
                var snap = BuildFormSnapshot();
                if (snap != _lastFormSnapshot)
                {
                    if (_rawDirty)
                    {
                        UpdateStatus("Auto-sync skipped (raw editor has manual edits)");
                    }
                    else
                    {
                        GenerateFromForm();
                        UpdateStatus("Editor auto-synced from form");
                    }
                }
            }
        }

        private string BuildFormSnapshot()
        {
            // Simple hash of form data to detect changes
            return _formData.Title + "|" + _formData.Author + "|" + _formData.Context + "|" + _formData.Summary;
        }

        private void ApplyMetadataToForm(ScribeMetadata metadata)
        {
            if (!string.IsNullOrEmpty(metadata.Author)) _formData.Author = metadata.Author;
            if (!string.IsNullOrEmpty(metadata.Summary)) _formData.Summary = metadata.Summary;
            if (!string.IsNullOrEmpty(metadata.Context)) _formData.Context = metadata.Context;
            if (!string.IsNullOrEmpty(metadata.TagsCsv)) _formData.TagsCsv = metadata.TagsCsv;
        }

        private string GetDefaultFolder()
        {
            return System.IO.Path.Combine(Application.dataPath, "Plugins/TLDA/docs");
        }

        private void SaveSettings()
        {
            var rootPath = _navigator?.GetRootPath();
            if (!string.IsNullOrEmpty(rootPath))
            {
                EditorPrefs.SetString(EditorPrefsRootKey, rootPath);
            }
        }

        #endregion
    }
}
#endif
