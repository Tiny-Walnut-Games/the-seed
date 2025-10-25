using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Single, modular window that guides the user through the full School/Warbler experiment workflow.
    /// Stages: 0 Inventory -> 1 Hypotheses -> 2 Manifests -> 3 Run -> 4 Validate -> 5 Report
    /// This provides a unified tabbed/wizard UI over the existing stage tools.
    /// </summary>
    public class SchoolExperimentWorkbench : EditorWindow
    {
        private enum Stage
        {
            Inventory = 0,
            Hypotheses = 1,
            Manifests = 2,
            Run = 3,
            Validate = 4,
            Report = 5
        }

        // Known pipeline paths (mirrors stage windows)
        private const string INVENTORY_PATH = "assets/experiments/school/inventory.json";
        private const string HYPOTHESES_PATH = "assets/experiments/school/hypothesis_drafts.json";
        private const string MANIFESTS_DIR = "assets/experiments/school/manifests/";
        private const string RUNS_DIR = "assets/experiments/school/outputs/runs/";
        private const string CLAIMS_DIR = "assets/experiments/school/claims/";
        private const string REPORTS_DIR = "assets/experiments/school/reports/";

        private Stage currentStage = Stage.Inventory;
        private Vector2 scroll;

        private GUIStyle _titleStyle;
        private GUIStyle _helpStyle;
        private GUIStyle _stageTitleStyle;

        [MenuItem("Tools/School/Workbench")]
        public static void ShowWindow()
        {
            var window = GetWindow<SchoolExperimentWorkbench>("School Workbench");
            window.minSize = new Vector2(780, 600);
            window.Show();
        }

        private void OnEnable()
        {
            _titleStyle = new GUIStyle(EditorStyles.boldLabel) { fontSize = 16 };
            _helpStyle = new GUIStyle(EditorStyles.helpBox) { wordWrap = true };
            _stageTitleStyle = new GUIStyle(EditorStyles.boldLabel) { fontSize = 13 };
        }

        private void OnGUI()
        {
            scroll = EditorGUILayout.BeginScrollView(scroll);

            DrawHeader();
            DrawStageTabs();
            EditorGUILayout.Space(8);

            switch (currentStage)
            {
                case Stage.Inventory: DrawStageInventory(); break;
                case Stage.Hypotheses: DrawStageHypotheses(); break;
                case Stage.Manifests: DrawStageManifests(); break;
                case Stage.Run: DrawStageRun(); break;
                case Stage.Validate: DrawStageValidate(); break;
                case Stage.Report: DrawStageReport(); break;
            }

            EditorGUILayout.Space(8);
            DrawNavBar();

            EditorGUILayout.EndScrollView();
        }

        private void DrawHeader()
        {
            EditorGUILayout.Space(6);
            EditorGUILayout.LabelField("🏫 Schoolhouse / Warbler Workbench", _titleStyle);
            EditorGUILayout.LabelField("Single window, step-by-step through the experiment pipeline.", _helpStyle);
            EditorGUILayout.Space(6);
        }

        private void DrawStageTabs()
        {
            var labels = new[]
            {
                "0 • Inventory",
                "1 • Hypotheses",
                "2 • Manifests",
                "3 • Run",
                "4 • Validate",
                "5 • Report"
            };

            int selected = (int)currentStage;
            selected = GUILayout.Toolbar(selected, labels);
            currentStage = (Stage)Mathf.Clamp(selected, 0, labels.Length - 1);
        }

        private void DrawNavBar()
        {
            EditorGUILayout.Space(6);
            EditorGUILayout.BeginHorizontal();

            GUI.enabled = currentStage != Stage.Inventory;
            if (GUILayout.Button("◀ Back", GUILayout.Width(100)))
                currentStage = (Stage)Mathf.Max(0, (int)currentStage - 1);
            GUI.enabled = true;

            GUILayout.FlexibleSpace();

            GUI.enabled = currentStage != Stage.Report;
            if (GUILayout.Button("Next ▶", GUILayout.Width(100)))
                currentStage = (Stage)Mathf.Min((int)Stage.Report, (int)currentStage + 1);
            GUI.enabled = true;

            EditorGUILayout.EndHorizontal();
        }

        private void DrawStageInventory()
        {
            EditorGUILayout.LabelField("Stage 0 — Inventory", _stageTitleStyle);
            EditorGUILayout.LabelField("Scan project to collect faculty surfaces.", EditorStyles.miniLabel);
            EditorGUILayout.Space(4);

            DrawFileStatus(INVENTORY_PATH, "Inventory JSON");

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Run Stage 0 (Generate Inventory)", GUILayout.Height(28)))
            {
                // Use existing tool via menu to minimize code changes
                EditorApplication.ExecuteMenuItem("Tools/School/Generate Inventory");
            }
            if (GUILayout.Button("Open Output", GUILayout.Width(120)))
            {
                Reveal(INVENTORY_PATH);
            }
            EditorGUILayout.EndHorizontal();

            // Preview
            if (File.Exists(INVENTORY_PATH))
            {
                try
                {
                    var json = File.ReadAllText(INVENTORY_PATH);
                    var data = JsonUtility.FromJson<InventoryData>(json);
                    if (data != null)
                    {
                        EditorGUILayout.Space(6);
                        EditorGUILayout.LabelField($"Surfaces: {data.FacultySurfaces?.Count ?? 0}");
                        EditorGUILayout.LabelField($"Hash: {data.Hash}");
                        EditorGUILayout.LabelField($"Timestamp: {data.Timestamp}");
                    }
                }
                catch (Exception ex)
                {
                    EditorGUILayout.HelpBox($"Failed to preview inventory: {ex.Message}", MessageType.Warning);
                }
            }
        }

        private void DrawStageHypotheses()
        {
            EditorGUILayout.LabelField("Stage 1 — Hypotheses", _stageTitleStyle);
            EditorGUILayout.LabelField("Extract hypotheses from the inventory.", EditorStyles.miniLabel);
            EditorGUILayout.Space(4);

            EditorGUILayout.LabelField($"Requires: {INVENTORY_PATH}", EditorStyles.miniLabel);
            DrawFileStatus(HYPOTHESES_PATH, "Hypothesis Drafts JSON");

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Run Stage 1 (Extract Hypotheses)", GUILayout.Height(28)))
            {
                EditorApplication.ExecuteMenuItem("Tools/School/Extract Hypotheses");
            }
            if (GUILayout.Button("Open Output", GUILayout.Width(120)))
            {
                Reveal(HYPOTHESES_PATH);
            }
            EditorGUILayout.EndHorizontal();

            // Preview
            if (File.Exists(HYPOTHESES_PATH))
            {
                try
                {
                    var json = File.ReadAllText(HYPOTHESES_PATH);
                    var data = JsonUtility.FromJson<HypothesisDrafts>(json);
                    if (data != null)
                    {
                        EditorGUILayout.Space(6);
                        EditorGUILayout.LabelField($"Hypotheses: {data.Hypotheses?.Count ?? 0}");
                        EditorGUILayout.LabelField($"Unity: {data.UnityVersion} | Timestamp: {data.Timestamp}");
                    }
                }
                catch (Exception ex)
                {
                    EditorGUILayout.HelpBox($"Failed to preview hypotheses: {ex.Message}", MessageType.Warning);
                }
            }
        }

        private void DrawStageManifests()
        {
            EditorGUILayout.LabelField("Stage 2 — Manifests", _stageTitleStyle);
            EditorGUILayout.LabelField("Generate experiment manifests from hypotheses.", EditorStyles.miniLabel);
            EditorGUILayout.Space(4);

            EditorGUILayout.LabelField($"Requires: {HYPOTHESES_PATH}", EditorStyles.miniLabel);
            DrawDirStatus(MANIFESTS_DIR, "Experiment Manifests", pattern: "experiment_*.yaml");

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Run Stage 2 (Generate Manifests)", GUILayout.Height(28)))
            {
                EditorApplication.ExecuteMenuItem("Tools/School/Generate Experiment Manifests");
            }
            if (GUILayout.Button("Open Output", GUILayout.Width(120)))
            {
                RevealDir(MANIFESTS_DIR);
            }
            EditorGUILayout.EndHorizontal();
        }

        private void DrawStageRun()
        {
            EditorGUILayout.LabelField("Stage 3 — Run", _stageTitleStyle);
            EditorGUILayout.LabelField("Execute manifests and collect outputs.", EditorStyles.miniLabel);
            EditorGUILayout.Space(4);

            EditorGUILayout.LabelField($"Requires: {MANIFESTS_DIR}", EditorStyles.miniLabel);
            DrawDirStatus(RUNS_DIR, "Run Outputs", pattern: "*");

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Run Stage 3 (Execute Experiments)", GUILayout.Height(28)))
            {
                EditorApplication.ExecuteMenuItem("Tools/School/Run Experiments");
            }
            if (GUILayout.Button("Open Output", GUILayout.Width(120)))
            {
                RevealDir(RUNS_DIR);
            }
            EditorGUILayout.EndHorizontal();
        }

        private void DrawStageValidate()
        {
            EditorGUILayout.LabelField("Stage 4 — Validate", _stageTitleStyle);
            EditorGUILayout.LabelField("Validate run outputs and synthesize claims.", EditorStyles.miniLabel);
            EditorGUILayout.Space(4);

            EditorGUILayout.LabelField($"Requires: {RUNS_DIR}", EditorStyles.miniLabel);
            DrawDirStatus(CLAIMS_DIR, "Claims", pattern: "*.json");

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Run Stage 4 (Validate Results)", GUILayout.Height(28)))
            {
                EditorApplication.ExecuteMenuItem("Tools/School/Validate Results");
            }
            if (GUILayout.Button("Open Output", GUILayout.Width(120)))
            {
                RevealDir(CLAIMS_DIR);
            }
            EditorGUILayout.EndHorizontal();
        }

        private void DrawStageReport()
        {
            EditorGUILayout.LabelField("Stage 5 — Report", _stageTitleStyle);
            EditorGUILayout.LabelField("Build reports and optionally push to GitHub.", EditorStyles.miniLabel);
            EditorGUILayout.Space(4);

            DrawDirStatus(REPORTS_DIR, "Reports", pattern: "*.md");

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Run Stage 5 (Build Report)", GUILayout.Height(28)))
            {
                EditorApplication.ExecuteMenuItem("Tools/School/Build Report");
            }
            if (GUILayout.Button("Open Output", GUILayout.Width(120)))
            {
                RevealDir(REPORTS_DIR);
            }
            EditorGUILayout.EndHorizontal();
        }

        private void DrawFileStatus(string path, string label)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField(label, EditorStyles.boldLabel);
            EditorGUILayout.LabelField($"Path: {path}", EditorStyles.miniLabel);

            if (File.Exists(path))
            {
                var info = new FileInfo(path);
                EditorGUILayout.LabelField($"Status: ✓ Found  •  Size: {info.Length} bytes  •  Modified: {info.LastWriteTime:yyyy-MM-dd HH:mm:ss}");
            }
            else
            {
                EditorGUILayout.LabelField("Status: ✗ Not found", EditorStyles.miniLabel);
            }
            EditorGUILayout.EndVertical();
        }

        private void DrawDirStatus(string dir, string label, string pattern = "*")
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField(label, EditorStyles.boldLabel);
            EditorGUILayout.LabelField($"Directory: {dir}", EditorStyles.miniLabel);

            if (Directory.Exists(dir))
            {
                int count = 0;
                try
                {
                    count = Directory.GetFiles(dir, pattern, SearchOption.AllDirectories).Length;
                }
                catch (Exception ex)
                {
                    EditorGUILayout.HelpBox($"Failed to enumerate directory: {ex.Message}", MessageType.Warning);
                }
                EditorGUILayout.LabelField($"Status: ✓ Exists  •  Files matching '{pattern}': {count}");
            }
            else
            {
                EditorGUILayout.LabelField("Status: ✗ Directory not found", EditorStyles.miniLabel);
            }
            EditorGUILayout.EndVertical();
        }

        private void Reveal(string path)
        {
            try
            {
                if (File.Exists(path))
                {
                    EditorUtility.RevealInFinder(Path.GetFullPath(path));
                }
                else
                {
                    EditorUtility.DisplayDialog("Not Found", $"File not found:\n{path}", "OK");
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[SchoolExperimentWorkbench] Reveal failed: {ex.Message}");
            }
        }

        private void RevealDir(string dir)
        {
            try
            {
                string full = Path.GetFullPath(dir);
                if (!Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }
                EditorUtility.RevealInFinder(full);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[SchoolExperimentWorkbench] RevealDir failed: {ex.Message}");
            }
        }
    }
}
