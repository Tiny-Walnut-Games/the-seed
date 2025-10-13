#if UNITY_EDITOR
using TinyWalnutGames.TLDA.Editor.Unity.Editor;
using TinyWalnutGames.TLDA.Editor.Unity;
using System.Collections.Generic;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles the form-based documentation builder for the TLDL Scribe
    /// </summary>
    public class ScribeFormBuilder
    {
        private readonly ScribeImageManager _imageManager;
        private readonly ScribeFileOperations.StatusUpdateDelegate _statusCallback;
        private Vector2 _scroll; // persistent scroll position

        public ScribeFormBuilder(ScribeImageManager imageManager, ScribeFileOperations.StatusUpdateDelegate statusCallback)
        {
            _imageManager = imageManager;
            _statusCallback = statusCallback;
            _scroll = new Vector2(0, 0);
        }

        public void DrawForm(ScribeFormData formData, Vector2 windowPosition)
        {
            // Placeholder implementation - will be filled with the full form UI
            var viewportHeight = System.Math.Max(140f, windowPosition.height - 220f);
            _scroll = EditorGUILayout.BeginScrollView(_scroll, GUILayout.Height(viewportHeight), GUILayout.ExpandHeight(true));

            // Header
            GUILayout.Label("Header", EditorStyles.boldLabel);
            formData.Title = EditorGUILayout.TextField("Title", formData.Title);
            formData.Author = EditorGUILayout.TextField("Author", formData.Author);
            formData.Context = EditorGUILayout.TextArea(formData.Context, GUILayout.MinHeight(40));
            formData.Summary = EditorGUILayout.TextArea(formData.Summary, GUILayout.MinHeight(40));
            formData.TagsCsv = EditorGUILayout.TextField("Tags", formData.TagsCsv);

            EditorGUILayout.Space(8);
            
            // Section toggles
            GUILayout.Label("Sections", EditorStyles.boldLabel);
            formData.IncludeDiscoveries = EditorGUILayout.ToggleLeft("Include Discoveries", formData.IncludeDiscoveries);
            formData.IncludeActions = EditorGUILayout.ToggleLeft("Include Actions Taken", formData.IncludeActions);
            formData.IncludeTechnicalDetails = EditorGUILayout.ToggleLeft("Include Technical Details", formData.IncludeTechnicalDetails);
            formData.IncludeTerminalProof = EditorGUILayout.ToggleLeft("Include Terminal Proof", formData.IncludeTerminalProof);
            formData.IncludeDependencies = EditorGUILayout.ToggleLeft("Include Dependencies", formData.IncludeDependencies);
            formData.IncludeLessons = EditorGUILayout.ToggleLeft("Include Lessons Learned", formData.IncludeLessons);
            formData.IncludeNextSteps = EditorGUILayout.ToggleLeft("Include Next Steps", formData.IncludeNextSteps);
            formData.IncludeReferences = EditorGUILayout.ToggleLeft("Include References", formData.IncludeReferences);
            formData.IncludeDevTimeTravel = EditorGUILayout.ToggleLeft("Include DevTimeTravel Context", formData.IncludeDevTimeTravel);
            formData.IncludeMetadata = EditorGUILayout.ToggleLeft("Include Metadata", formData.IncludeMetadata);
            formData.IncludeImages = EditorGUILayout.ToggleLeft("Include Images", formData.IncludeImages);

            // Placeholder for the detailed form sections
            if (formData.IncludeDiscoveries)
            {
                DrawDiscoveriesSection(formData);
            }

            if (formData.IncludeActions)
            {
                DrawActionsSection(formData);
            }

            EditorGUILayout.EndScrollView();
        }

        private void DrawDiscoveriesSection(ScribeFormData formData)
        {
            EditorGUILayout.BeginVertical("box");
            GUILayout.Label("Discoveries", EditorStyles.boldLabel);
            
            for (int i = 0; i < formData.Discoveries.Count; i++)
            {
                var d = formData.Discoveries[i];
                EditorGUILayout.BeginVertical("frameBox");
                d.Foldout = EditorGUILayout.Foldout(d.Foldout, string.IsNullOrEmpty(d.Category) ? $"Discovery {i + 1}" : d.Category, true);
                if (d.Foldout)
                {
                    d.Category = EditorGUILayout.TextField("Category/Title", d.Category);
                    d.KeyFinding = EditorGUILayout.TextArea(d.KeyFinding, GUILayout.MinHeight(40));
                    d.Impact = EditorGUILayout.TextArea(d.Impact, GUILayout.MinHeight(40));
                }
                EditorGUILayout.EndVertical();
            }

            if (GUILayout.Button("+ Add Discovery"))
            {
                formData.Discoveries.Add(new Discovery { Category = $"Discovery {formData.Discoveries.Count + 1}" });
            }
            EditorGUILayout.EndVertical();
        }

        private void DrawActionsSection(ScribeFormData formData)
        {
            EditorGUILayout.BeginVertical("box");
            GUILayout.Label("Actions Taken", EditorStyles.boldLabel);
            for (int i = 0; i < formData.Actions.Count; i++)
            {
                var a = formData.Actions[i];
                EditorGUILayout.BeginVertical("frameBox");
                a.Foldout = EditorGUILayout.Foldout(a.Foldout, string.IsNullOrEmpty(a.Name) ? $"Action {i + 1}" : a.Name, true);
                if (a.Foldout)
                {
                    a.Name = EditorGUILayout.TextField("Action Name", a.Name);
                    a.What = EditorGUILayout.TextArea(a.What, GUILayout.MinHeight(40));
                    a.Why = EditorGUILayout.TextArea(a.Why, GUILayout.MinHeight(40));
                }
                EditorGUILayout.EndVertical();
            }
            if (GUILayout.Button("+ Add Action"))
            {
                formData.Actions.Add(new ActionItem { Name = $"Action {formData.Actions.Count + 1}" });
            }
            EditorGUILayout.EndVertical();
        }
    }
}
#endif
