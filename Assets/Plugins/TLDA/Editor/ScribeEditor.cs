#if UNITY_EDITOR
using TinyWalnutGames.TLDA.Editor.Unity.Editor;
using TinyWalnutGames.TLDA.Editor.Unity;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles the raw markdown editor for the TLDL Scribe
    /// </summary>
    public class ScribeEditor
    {
        private readonly ScribeImageManager _imageManager;
        private readonly ScribeFileOperations.StatusUpdateDelegate _statusCallback;
        
        private bool _rawWrap = true;
        private Vector2 _rawScroll;
        private readonly string _rawEditorControlName = "TLDL_RAW_EDITOR";

        public ScribeEditor(ScribeImageManager imageManager, ScribeFileOperations.StatusUpdateDelegate statusCallback)
        {
            _imageManager = imageManager;
            _statusCallback = statusCallback;
            _rawScroll = new Vector2(0, 0);
        }

        public void DrawRawEditor(ref string rawContent, ref bool rawDirty, string rawGeneratedSnapshot, Vector2 windowPosition)
        {
            GUILayout.Label("Editor", EditorStyles.boldLabel);
            _rawWrap = EditorGUILayout.ToggleLeft("Wrap lines", _rawWrap);

            var rawStyle = new GUIStyle(EditorStyles.textArea) { wordWrap = _rawWrap };
            var baseOffset = 240f;
            var viewportHeight = System.Math.Max(140f, windowPosition.height - baseOffset);
            _rawScroll = EditorGUILayout.BeginScrollView(_rawScroll, GUILayout.Height(viewportHeight), GUILayout.ExpandHeight(true));
            GUI.SetNextControlName(_rawEditorControlName);
            var edited = EditorGUILayout.TextArea(rawContent ?? string.Empty, rawStyle, GUILayout.ExpandHeight(true));
            if (edited != rawContent)
            {
                if (rawGeneratedSnapshot != null && edited != rawGeneratedSnapshot)
                    rawDirty = true;
                rawContent = edited;
            }
            EditorGUILayout.EndScrollView();

            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Load File…", GUILayout.Width(110)))
                {
                    LoadFileDialog(ref rawContent, ref rawDirty);
                }
                using (new EditorGUI.DisabledScope(string.IsNullOrEmpty(rawContent)))
                {
                    if (GUILayout.Button("Save Raw")) SaveRaw(rawContent);
                    if (GUILayout.Button("Save Raw As…")) SaveRawAs(rawContent);
                }
                if (GUILayout.Button("Insert Image…", GUILayout.Width(120)))
                {
                    AddImageAndInsertAtCursor(ref rawContent);
                }
            }
        }

        private void LoadFileDialog(ref string rawContent, ref bool rawDirty)
        {
            var filters = new[] { "All", "*.*", "Markdown", "md,markdown", "Text", "txt,log", "XML", "xml" };
            var picked = EditorUtility.OpenFilePanelWithFilters("Open Document", "", string.Join(",", filters));
            if (!string.IsNullOrEmpty(picked))
            {
                var result = ScribeFileOperations.LoadFile(picked);
                if (result.Success)
                {
                    rawContent = result.Content;
                    rawDirty = false;
                    _statusCallback?.Invoke($"Loaded: {ScribeFileOperations.MakeProjectRelative(picked)}");
                }
                else
                {
                    _statusCallback?.Invoke($"Failed to load file: {result.ErrorMessage}");
                }
            }
        }

        private void SaveRaw(string rawContent)
        {
            var picked = EditorUtility.SaveFilePanel("Save Document", "", "document.md", "md");
            if (!string.IsNullOrEmpty(picked))
            {
                ScribeFileOperations.SaveFile(picked, rawContent, _statusCallback);
            }
        }

        private void SaveRawAs(string rawContent)
        {
            var picked = EditorUtility.SaveFilePanel("Save Document As", "", "document.md", "md");
            if (!string.IsNullOrEmpty(picked))
            {
                ScribeFileOperations.SaveFile(picked, rawContent, _statusCallback);
            }
        }

        private void AddImageAndInsertAtCursor(ref string rawContent)
        {
            // Wrap status callback to image manager delegate type
            var result = _imageManager.AddImageFile("", msg => _statusCallback?.Invoke(msg));
            if (result.Success && !string.IsNullOrEmpty(result.RelativePath))
            {
                var insertResult = _imageManager.InsertImageMarkdownAtCursor(result.RelativePath, rawContent, -1);
                rawContent = insertResult.NewContent;
                _statusCallback?.Invoke($"Inserted image: {result.RelativePath}");
            }
        }
    }
}
#endif
