using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Unity Editor window for School experiment hypothesis extraction
    /// KeeperNote: Stage 1 - Hypothesis extraction for faculty surfaces capability assessment
    /// </summary>
    public class HypothesisExtractor : EditorWindow
    {
        private Vector2 scrollPosition;
        private HypothesisDrafts lastHypotheses;
        private bool isExtracting = false;
        private string extractionProgress = "";
        private DateTime lastExtractionTime;
        private InventoryData loadedInventory;

        // Input/Output settings
        private const string INPUT_PATH = "Assets/experiments/school/inventory.json";
        private const string OUTPUT_PATH = "Assets/experiments/school/hypothesis_drafts.json";

        [MenuItem("Tools/School/Extract Hypotheses")]
        public static void ShowWindow()
        {
            var window = GetWindow<HypothesisExtractor>("Hypothesis Extractor");
            window.minSize = new Vector2(500, 700);
            window.Show();
        }

        /// <summary>
        /// Run hypothesis extraction without opening any windows. Returns number of hypotheses generated.
        /// </summary>
        public static async Task<int> RunHeadless(string inputPath = null, string outputPath = null)
        {
            var temp = CreateInstance<HypothesisExtractor>();
            try
            {
                string invPath = inputPath ?? INPUT_PATH;
                string outPath = outputPath ?? OUTPUT_PATH;

                if (!File.Exists(invPath))
                {
                    throw new FileNotFoundException($"Inventory not found: {invPath}");
                }

                var invJson = await File.ReadAllTextAsync(invPath);
                temp.loadedInventory = JsonUtility.FromJson<InventoryData>(invJson);

                var hypotheses = new HypothesisDrafts
                {
                    Timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.ffffffZ"),
                    Status = "draft",
                    UnityVersion = Application.unityVersion,
                    ProjectPath = Application.dataPath,
                    SourceInventoryHash = temp.loadedInventory.Hash,
                    Hypotheses = new List<Hypothesis>()
                };

                await temp.ExtractHypothesesFromSurfaces(hypotheses);

                var outDir = Path.GetDirectoryName(outPath);
                if (!Directory.Exists(outDir)) Directory.CreateDirectory(outDir);
                var json = JsonUtility.ToJson(hypotheses, true);
                await File.WriteAllTextAsync(outPath, json);

                return hypotheses.Hypotheses.Count;
            }
            finally
            {
                if (!Application.isPlaying)
                {
                    DestroyImmediate(temp);
                }
            }
        }

        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            DrawHeader();
            DrawInventorySection();
            DrawExtractionSection();
            DrawResultsSection();
            DrawOutputSection();

            EditorGUILayout.EndScrollView();
        }

        private void DrawHeader()
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("🧪 School Experiment - Stage 1", EditorStyles.largeLabel);
            EditorGUILayout.LabelField("Hypothesis Extraction for Faculty Surfaces", EditorStyles.label);
            EditorGUILayout.Space();

            EditorGUILayout.HelpBox(
                "Stage 1: Extract hypotheses (capability assertions, improvement targets) from faculty surfaces identified in Stage 0.\n\n" +
                "This tool processes the inventory.json file and generates hypothesis drafts for each faculty surface based on Unity context and metadata.",
                MessageType.Info);

            EditorGUILayout.Space();
        }

        private void DrawInventorySection()
        {
            EditorGUILayout.LabelField("📋 Inventory Input", EditorStyles.boldLabel);

            EditorGUILayout.LabelField($"Input Path: {INPUT_PATH}");

            bool inventoryExists = File.Exists(INPUT_PATH);
            if (inventoryExists)
            {
                EditorGUILayout.LabelField("✅ Inventory file found", EditorStyles.miniLabel);

                if (loadedInventory != null)
                {
                    EditorGUILayout.LabelField($"📊 Loaded: {loadedInventory.FacultySurfaces.Count} faculty surfaces");
                    EditorGUILayout.LabelField($"🕐 Generated: {loadedInventory.Timestamp}");
                }
                else
                {
                    if (GUILayout.Button("🔄 Load Inventory"))
                    {
                        LoadInventory();
                    }
                }
            }
            else
            {
                EditorGUILayout.HelpBox(
                    "Inventory file not found. Please run Stage 0 (Tools > School > Generate Inventory) first.",
                    MessageType.Warning);
            }

            EditorGUILayout.Space();
        }

        private void DrawExtractionSection()
        {
            EditorGUILayout.LabelField("🧠 Hypothesis Extraction", EditorStyles.boldLabel);

            if (isExtracting)
            {
                EditorGUILayout.LabelField("Status: " + extractionProgress);
                EditorGUI.ProgressBar(EditorGUILayout.GetControlRect(), 0.5f, "Extracting hypotheses...");
            }
            else
            {
                bool canExtract = loadedInventory != null && loadedInventory.FacultySurfaces.Count > 0;

                EditorGUI.BeginDisabledGroup(!canExtract);
                if (GUILayout.Button("🚀 Extract Hypotheses", GUILayout.Height(30)))
                {
                    PerformHypothesisExtraction();
                }
                EditorGUI.EndDisabledGroup();

                if (!canExtract && loadedInventory == null)
                {
                    EditorGUILayout.HelpBox("Load inventory first before extracting hypotheses.", MessageType.Info);
                }
            }

            EditorGUILayout.Space();
        }

        private void DrawResultsSection()
        {
            if (lastHypotheses == null) return;

            EditorGUILayout.LabelField("📈 Extraction Results", EditorStyles.boldLabel);

            EditorGUILayout.LabelField($"Total Hypotheses: {lastHypotheses.Hypotheses.Count}");
            EditorGUILayout.LabelField($"Status: {lastHypotheses.Status}");
            EditorGUILayout.LabelField($"Generated: {lastHypotheses.Timestamp}");

            EditorGUILayout.Space();

            // Hypothesis type breakdown
            EditorGUILayout.LabelField("🔬 Hypothesis Type Breakdown", EditorStyles.boldLabel);

            var typeGroups = lastHypotheses.Hypotheses.GroupBy(h => h.Type).ToList();
            foreach (var group in typeGroups)
            {
                EditorGUILayout.LabelField($"  {group.Key}: {group.Count()}");
            }

            EditorGUILayout.Space();

            // Surface coverage
            EditorGUILayout.LabelField("📊 Faculty Surface Coverage", EditorStyles.boldLabel);
            var surfaceGroups = lastHypotheses.Hypotheses.GroupBy(h => h.FacultySurfaceType).ToList();
            foreach (var group in surfaceGroups)
            {
                EditorGUILayout.LabelField($"  {group.Key}: {group.Count()} hypotheses");
            }

            EditorGUILayout.Space();
        }

        private void DrawOutputSection()
        {
            EditorGUILayout.LabelField("💾 Output", EditorStyles.boldLabel);

            EditorGUILayout.LabelField($"Output Path: {OUTPUT_PATH}");

            bool outputExists = File.Exists(OUTPUT_PATH);
            EditorGUILayout.LabelField(outputExists ? "✅ Output file exists" : "❌ No output file", EditorStyles.miniLabel);

            if (outputExists)
            {
                if (GUILayout.Button("📂 Show in Explorer"))
                {
                    EditorUtility.RevealInFinder(OUTPUT_PATH);
                }
            }

            EditorGUILayout.Space();
        }

        private async void LoadInventory()
        {
            try
            {
                extractionProgress = "Loading inventory...";
                Repaint();

                if (!File.Exists(INPUT_PATH))
                {
                    Debug.LogError($"[HypothesisExtractor] Inventory file not found: {INPUT_PATH}");
                    EditorUtility.DisplayDialog("Error", "Inventory file not found. Please run Stage 0 first.", "OK");
                    return;
                }

                var json = await File.ReadAllTextAsync(INPUT_PATH);
                loadedInventory = JsonUtility.FromJson<InventoryData>(json);

                Debug.Log($"[HypothesisExtractor] Loaded inventory with {loadedInventory.FacultySurfaces.Count} faculty surfaces");

                extractionProgress = "";
                Repaint();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[HypothesisExtractor] Failed to load inventory: {ex.Message}");
                EditorUtility.DisplayDialog("Error", $"Failed to load inventory: {ex.Message}", "OK");
                extractionProgress = "";
                Repaint();
            }
        }

        private async void PerformHypothesisExtraction()
        {
            if (loadedInventory == null)
            {
                Debug.LogError("[HypothesisExtractor] No inventory loaded");
                return;
            }

            isExtracting = true;

            try
            {
                extractionProgress = "Initializing extraction...";
                Repaint();

                var hypotheses = new HypothesisDrafts
                {
                    Timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.ffffffZ"),
                    Status = "draft",
                    UnityVersion = Application.unityVersion,
                    ProjectPath = Application.dataPath,
                    SourceInventoryHash = loadedInventory.Hash,
                    Hypotheses = new List<Hypothesis>()
                };

                await ExtractHypothesesFromSurfaces(hypotheses);

                // Save to JSON
                extractionProgress = "Saving hypotheses...";
                Repaint();

                await SaveHypothesesJson(hypotheses);

                lastHypotheses = hypotheses;
                lastExtractionTime = DateTime.Now;

                Debug.Log($"[HypothesisExtractor] Hypothesis extraction complete: {hypotheses.Hypotheses.Count} hypotheses generated");
                EditorUtility.DisplayDialog("Extraction Complete",
                    $"Generated {hypotheses.Hypotheses.Count} hypotheses.\\nSaved to {OUTPUT_PATH}",
                    "OK");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[HypothesisExtractor] Extraction failed: {ex.Message}");
                EditorUtility.DisplayDialog("Error", $"Extraction failed: {ex.Message}", "OK");
            }
            finally
            {
                isExtracting = false;
                extractionProgress = "";
                Repaint();
            }
        }

        private async Task ExtractHypothesesFromSurfaces(HypothesisDrafts hypotheses)
        {
            var totalSurfaces = loadedInventory.FacultySurfaces.Count;

            for (int i = 0; i < totalSurfaces; i++)
            {
                var surface = loadedInventory.FacultySurfaces[i];

                extractionProgress = $"Processing surface {i + 1}/{totalSurfaces}: {Path.GetFileName(surface.Path)}";
                Repaint();

                // Generate hypotheses for this faculty surface
                var surfaceHypotheses = await GenerateHypothesesForSurface(surface);
                hypotheses.Hypotheses.AddRange(surfaceHypotheses);

                // Yield control to prevent freezing
                await Task.Yield();
            }
        }

        private async Task<List<Hypothesis>> GenerateHypothesesForSurface(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>();

            // Generate hypotheses based on surface type and metadata
            switch (surface.Type)
            {
                case "Script":
                    hypotheses.AddRange(await GenerateScriptHypotheses(surface));
                    break;
                case "Prefab":
                    hypotheses.AddRange(await GeneratePrefabHypotheses(surface));
                    break;
                case "Material":
                    hypotheses.AddRange(await GenerateMaterialHypotheses(surface));
                    break;
                case "Texture":
                    hypotheses.AddRange(await GenerateTextureHypotheses(surface));
                    break;
                case "Shader":
                    hypotheses.AddRange(await GenerateShaderHypotheses(surface));
                    break;
                case "Scene":
                    hypotheses.AddRange(await GenerateSceneHypotheses(surface));
                    break;
                case "Audio":
                    hypotheses.AddRange(await GenerateAudioHypotheses(surface));
                    break;
                case "Mesh":
                    hypotheses.AddRange(await GenerateMeshHypotheses(surface));
                    break;
                default:
                    hypotheses.Add(await GenerateGenericHypothesis(surface));
                    break;
            }

            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateScriptHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>();

            // Capability assessment based on script tags
            if (surface.Tags.Contains("EditorTool"))
            {
                hypotheses.Add(new Hypothesis
                {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "CapabilityAssertion",
                    Title = "Editor Tool Enhancement Potential",
                    Description = "This editor tool can be enhanced with additional workflow automation and UI improvements",
                    Evidence = $"Script tagged as EditorTool, file size: {surface.FileSize} bytes",
                    Priority = "Medium",
                    Confidence = 0.7f,
                    EstimatedEffort = "2-4 hours",
                    PotentialImpact = "Improved developer workflow efficiency"
                });
            }

            if (surface.Tags.Contains("Component"))
            {
                hypotheses.Add(new Hypothesis
                {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "ImprovementTarget",
                    Title = "Component Performance Optimization",
                    Description = "MonoBehaviour component can be optimized for better runtime performance",
                    Evidence = $"Script tagged as Component, potential for Update() loop optimization",
                    Priority = "Low",
                    Confidence = 0.5f,
                    EstimatedEffort = "1-3 hours",
                    PotentialImpact = "Better runtime performance and frame rate"
                });
            }

            if (surface.Tags.Contains("DataAsset"))
            {
                hypotheses.Add(new Hypothesis
                {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "CapabilityAssertion",
                    Title = "Data Structure Extensibility",
                    Description = "ScriptableObject data structure can be extended with additional fields and validation",
                    Evidence = $"Script tagged as DataAsset, extensible architecture",
                    Priority = "Medium",
                    Confidence = 0.8f,
                    EstimatedEffort = "1-2 hours",
                    PotentialImpact = "Enhanced data management and validation capabilities"
                });
            }

            // File size based assessment
            if (surface.FileSize > 10000)
            {
                hypotheses.Add(new Hypothesis
                {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "ImprovementTarget",
                    Title = "Large Script Refactoring Opportunity",
                    Description = "Large script file could benefit from refactoring into smaller, focused components",
                    Evidence = $"File size: {surface.FileSize} bytes (above 10KB threshold)",
                    Priority = "Medium",
                    Confidence = 0.6f,
                    EstimatedEffort = "4-8 hours",
                    PotentialImpact = "Improved code maintainability and testability"
                });
            }

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GeneratePrefabHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>();

            // Extract component count from tags
            var componentTag = surface.Tags.FirstOrDefault(t => t.StartsWith("Components:"));
            if (componentTag != null && int.TryParse(componentTag.Split(':')[1], out int componentCount))
            {
                if (componentCount > 5)
                {
                    hypotheses.Add(new Hypothesis
                    {
                        Id = Guid.NewGuid().ToString(),
                        FacultySurfacePath = surface.Path,
                        FacultySurfaceType = surface.Type,
                        Type = "ImprovementTarget",
                        Title = "Complex Prefab Simplification",
                        Description = "Prefab with many components could be simplified or broken into smaller prefabs",
                        Evidence = $"Prefab has {componentCount} components",
                        Priority = "Low",
                        Confidence = 0.4f,
                        EstimatedEffort = "2-4 hours",
                        PotentialImpact = "Improved prefab maintainability and performance"
                    });
                }

                hypotheses.Add(new Hypothesis
                {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "CapabilityAssertion",
                    Title = "Prefab Variant Creation Potential",
                    Description = "Prefab can be used as base for creating specialized variants",
                    Evidence = $"Well-structured prefab with {componentCount} components",
                    Priority = "Medium",
                    Confidence = 0.7f,
                    EstimatedEffort = "1-2 hours",
                    PotentialImpact = "Reusable asset creation and workflow efficiency"
                });
            }

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateMaterialHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>
            {
                new() {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "CapabilityAssertion",
                    Title = "Material Optimization Potential",
                    Description = "Material can be optimized for target platform performance",
                    Evidence = "Material asset available for shader optimization",
                    Priority = "Low",
                    Confidence = 0.6f,
                    EstimatedEffort = "30 minutes - 1 hour",
                    PotentialImpact = "Better rendering performance on target platforms"
                }
            };

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateTextureHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>
            {
                new() {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "ImprovementTarget",
                    Title = "Texture Compression Optimization",
                    Description = "Texture can be optimized with appropriate compression settings for target platforms",
                    Evidence = "Texture asset available for compression optimization",
                    Priority = "Low",
                    Confidence = 0.8f,
                    EstimatedEffort = "15-30 minutes",
                    PotentialImpact = "Reduced memory usage and improved loading times"
                }
            };

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateShaderHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>
            {
                new() {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "CapabilityAssertion",
                    Title = "Shader Variant Creation Potential",
                    Description = "Custom shader can be extended with additional features and variants",
                    Evidence = "Custom shader asset with extensible architecture",
                    Priority = "Medium",
                    Confidence = 0.7f,
                    EstimatedEffort = "2-6 hours",
                    PotentialImpact = "Enhanced visual effects and rendering capabilities"
                }
            };

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateSceneHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>
            {
                new() {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "ImprovementTarget",
                    Title = "Scene Performance Optimization",
                    Description = "Scene can be optimized for better loading times and runtime performance",
                    Evidence = "Scene asset available for optimization analysis",
                    Priority = "Medium",
                    Confidence = 0.6f,
                    EstimatedEffort = "1-4 hours",
                    PotentialImpact = "Improved loading times and frame rate"
                }
            };

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateAudioHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>
            {
                new() {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "ImprovementTarget",
                    Title = "Audio Compression Optimization",
                    Description = "Audio clip can be optimized with appropriate compression settings",
                    Evidence = "Audio asset available for compression optimization",
                    Priority = "Low",
                    Confidence = 0.7f,
                    EstimatedEffort = "15-30 minutes",
                    PotentialImpact = "Reduced build size and memory usage"
                }
            };

            await Task.Yield();
            return hypotheses;
        }

        private async Task<List<Hypothesis>> GenerateMeshHypotheses(FacultySurface surface)
        {
            var hypotheses = new List<Hypothesis>
            {
                new() {
                    Id = Guid.NewGuid().ToString(),
                    FacultySurfacePath = surface.Path,
                    FacultySurfaceType = surface.Type,
                    Type = "ImprovementTarget",
                    Title = "Mesh Optimization Potential",
                    Description = "3D mesh can be optimized for polygon count and memory usage",
                    Evidence = "Mesh asset available for optimization analysis",
                    Priority = "Low",
                    Confidence = 0.6f,
                    EstimatedEffort = "30 minutes - 2 hours",
                    PotentialImpact = "Better rendering performance and reduced memory usage"
                }
            };

            await Task.Yield();
            return hypotheses;
        }

        private async Task<Hypothesis> GenerateGenericHypothesis(FacultySurface surface)
        {
            await Task.Yield();

            return new Hypothesis
            {
                Id = Guid.NewGuid().ToString(),
                FacultySurfacePath = surface.Path,
                FacultySurfaceType = surface.Type,
                Type = "CapabilityAssertion",
                Title = "Asset Integration Potential",
                Description = "Asset can be further integrated into project workflow and optimization pipeline",
                Evidence = $"Asset of type {surface.Type} available for integration",
                Priority = "Low",
                Confidence = 0.4f,
                EstimatedEffort = "30 minutes - 1 hour",
                PotentialImpact = "Enhanced asset utilization and workflow integration"
            };
        }

        private async Task SaveHypothesesJson(HypothesisDrafts hypotheses)
        {
            var outputDir = Path.GetDirectoryName(OUTPUT_PATH);
            if (!Directory.Exists(outputDir))
            {
                Directory.CreateDirectory(outputDir);
            }

            var json = JsonUtility.ToJson(hypotheses, true);
            await File.WriteAllTextAsync(OUTPUT_PATH, json);

            Debug.Log($"[HypothesisExtractor] Hypotheses saved to {OUTPUT_PATH}");
        }
    }

    /// <summary>
    /// Data structure for hypothesis drafts output
    /// </summary>
    [Serializable]
    public class HypothesisDrafts
    {
        public string Timestamp;
        public string Status;
        public string UnityVersion;
        public string ProjectPath;
        public string SourceInventoryHash;
        public List<Hypothesis> Hypotheses = new List<Hypothesis>();
    }

    /// <summary>
    /// Individual hypothesis (capability assertion or improvement target)
    /// </summary>
    [Serializable]
    public class Hypothesis
    {
        public string Id;
        public string FacultySurfacePath;
        public string FacultySurfaceType;
        public string Type; // "CapabilityAssertion" or "ImprovementTarget"
        public string Title;
        public string Description;
        public string Evidence;
        public string Priority; // "Low", "Medium", "High"
        public float Confidence; // 0.0 to 1.0
        public string EstimatedEffort;
        public string PotentialImpact;
    }
}
