#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles template/issue creation for the TLDL Scribe
    /// </summary>
    public class ScribeTemplateManager
    {
        private readonly ScribeFileOperations.StatusUpdateDelegate _statusCallback;
        private List<TemplateInfo> _templates = null;
        private int _selectedTemplateIndex = 0;

        public ScribeTemplateManager(ScribeFileOperations.StatusUpdateDelegate statusCallback)
        {
            _statusCallback = statusCallback;
        }

        public void DrawIssueCreator()
        {
            EditorGUILayout.LabelField("Issue Creator", EditorStyles.boldLabel);
            EnsureTemplatesLoaded();
            
            if (_templates == null || _templates.Count == 0)
            {
                EditorGUILayout.HelpBox("No templates found. Ensure templates/comments/registry.yaml exists at project root.", MessageType.Warning);
                return;
            }

            var items = new string[_templates.Count];
            for (int i = 0; i < _templates.Count; i++)
            {
                items[i] = string.IsNullOrEmpty(_templates[i].Title) ? _templates[i].Key : _templates[i].Title;
            }
            
            _selectedTemplateIndex = EditorGUILayout.Popup("Template", _selectedTemplateIndex, items);

            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Load Template → Editor"))
                {
                    LoadTemplate(_templates[_selectedTemplateIndex]);
                }
                
                if (GUILayout.Button("Create Issue From Template"))
                {
                    CreateIssueFromTemplate(_templates[_selectedTemplateIndex]);
                }
            }
        }

        private void EnsureTemplatesLoaded()
        {
            if (_templates != null) return;
            
            try
            {
                _templates = new List<TemplateInfo>();
                // Placeholder template
                _templates.Add(new TemplateInfo 
                { 
                    Key = "default", 
                    Title = "Default Template", 
                    File = "default.md",
                    AbsPath = string.Empty
                });
            }
            catch (Exception ex)
            {
                _statusCallback?.Invoke($"Failed to load templates: {ex.Message}");
            }
        }

        private void LoadTemplate(TemplateInfo template)
        {
            _statusCallback?.Invoke($"Loading template: {template.Title}");
            // TODO: Implement template loading
        }

        private void CreateIssueFromTemplate(TemplateInfo template)
        {
            _statusCallback?.Invoke($"Creating issue from template: {template.Title}");
            // TODO: Implement issue creation
        }
    }
}
#endif
