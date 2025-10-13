using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Unity Editor window for School experiment manifest generation
    /// KeeperNote: Stage 2 - Experiment manifest generation for hypothesis-driven experiments
    /// </summary>
    public class ExperimentManifestGenerator : EditorWindow
    {
        private Vector2 scrollPosition;
        private HypothesisDrafts loadedHypotheses;
        private bool isGenerating = false;
        private string generationProgress = "";
        private DateTime lastGenerationTime;
        private int manifestsGenerated = 0;
        
        // Input/Output settings
        private const string INPUT_PATH = "assets/experiments/school/hypothesis_drafts.json";
        private const string OUTPUT_DIR = "assets/experiments/school/manifests/";
        
        [MenuItem("Tools/School/Generate Experiment Manifests")]
        public static void ShowWindow()
        {
            var window = GetWindow<ExperimentManifestGenerator>("Experiment Manifest Generator");
            window.minSize = new Vector2(500, 700);
            window.Show();
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawInputSection();
            DrawGenerationSection();
            DrawResultsSection();
            DrawOutputSection();
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.Space(10);
            GUILayout.Label("🧪 Experiment Manifest Generator", EditorStyles.largeLabel);
            GUILayout.Label("Stage 2: Generate YAML manifests for each hypothesis", EditorStyles.helpBox);
            EditorGUILayout.Space(10);
        }
        
        private void DrawInputSection()
        {
            EditorGUILayout.LabelField("Input Configuration", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("Hypothesis Drafts File:", INPUT_PATH);
            
            if (File.Exists(INPUT_PATH))
            {
                EditorGUILayout.LabelField("✓ Input file found", EditorStyles.miniLabel);
                
                if (GUILayout.Button("Load Hypotheses", GUILayout.Height(30)))
                {
                    LoadHypotheses();
                }
            }
            else
            {
                EditorGUILayout.LabelField("✗ Input file not found. Run Stage 1 first.", EditorStyles.miniLabel);
            }
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.Space(10);
        }
        
        private void DrawGenerationSection()
        {
            EditorGUILayout.LabelField("Manifest Generation", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (loadedHypotheses != null)
            {
                EditorGUILayout.LabelField($"Loaded {loadedHypotheses.Hypotheses.Count} hypotheses");
                EditorGUILayout.LabelField($"From: {loadedHypotheses.Timestamp}");
                EditorGUILayout.LabelField($"Unity Version: {loadedHypotheses.UnityVersion}");
                
                EditorGUILayout.Space(5);
                
                GUI.enabled = !isGenerating;
                if (GUILayout.Button("Generate Experiment Manifests", GUILayout.Height(40)))
                {
                    GenerateManifests();
                }
                GUI.enabled = true;
                
                if (isGenerating)
                {
                    EditorGUILayout.LabelField("Status:", generationProgress);
                    EditorUtility.DisplayProgressBar("Generating Manifests", generationProgress, 0.5f);
                }
            }
            else
            {
                EditorGUILayout.LabelField("No hypotheses loaded. Load input file first.");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawResultsSection()
        {
            EditorGUILayout.LabelField("Generation Results", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (manifestsGenerated > 0)
            {
                EditorGUILayout.LabelField($"✓ Generated {manifestsGenerated} manifest files");
                EditorGUILayout.LabelField($"Last generation: {lastGenerationTime}");
            }
            else
            {
                EditorGUILayout.LabelField("No manifests generated yet.");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawOutputSection()
        {
            EditorGUILayout.LabelField("Output Configuration", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("Output Directory:", OUTPUT_DIR);
            
            if (Directory.Exists(OUTPUT_DIR))
            {
                var files = Directory.GetFiles(OUTPUT_DIR, "experiment_*.yaml");
                EditorGUILayout.LabelField($"Current manifest files: {files.Length}");
                
                if (GUILayout.Button("Open Output Directory"))
                {
                    EditorUtility.RevealInFinder(OUTPUT_DIR);
                }
            }
            else
            {
                EditorGUILayout.LabelField("Output directory will be created during generation.");
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void LoadHypotheses()
        {
            try
            {
                var json = File.ReadAllText(INPUT_PATH);
                loadedHypotheses = JsonUtility.FromJson<HypothesisDrafts>(json);
                Debug.Log($"[ExperimentManifestGenerator] Loaded {loadedHypotheses.Hypotheses.Count} hypotheses from {INPUT_PATH}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ExperimentManifestGenerator] Failed to load hypotheses: {ex.Message}");
                EditorUtility.DisplayDialog("Load Error", $"Failed to load hypotheses:\n{ex.Message}", "OK");
            }
        }
        
        private async void GenerateManifests()
        {
            if (loadedHypotheses == null || loadedHypotheses.Hypotheses.Count == 0)
            {
                EditorUtility.DisplayDialog("Generation Error", "No hypotheses loaded. Please load the input file first.", "OK");
                return;
            }
            
            isGenerating = true;
            manifestsGenerated = 0;
            
            try
            {
                // Ensure output directory exists
                if (!Directory.Exists(OUTPUT_DIR))
                {
                    Directory.CreateDirectory(OUTPUT_DIR);
                }
                
                generationProgress = "Generating experiment manifests...";
                
                for (int i = 0; i < loadedHypotheses.Hypotheses.Count; i++)
                {
                    var hypothesis = loadedHypotheses.Hypotheses[i];
                    generationProgress = $"Processing hypothesis {i + 1}/{loadedHypotheses.Hypotheses.Count}: {hypothesis.Title}";
                    
                    await GenerateManifestForHypothesis(hypothesis);
                    manifestsGenerated++;
                    
                    // Allow UI to update
                    await Task.Delay(10);
                }
                
                lastGenerationTime = DateTime.Now;
                generationProgress = $"Completed! Generated {manifestsGenerated} manifests.";
                
                Debug.Log($"[ExperimentManifestGenerator] Generated {manifestsGenerated} experiment manifests in {OUTPUT_DIR}");
                
                EditorUtility.DisplayDialog("Generation Complete", 
                    $"Successfully generated {manifestsGenerated} experiment manifests.\n\nOutput directory: {OUTPUT_DIR}", "OK");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ExperimentManifestGenerator] Generation failed: {ex.Message}");
                EditorUtility.DisplayDialog("Generation Error", $"Failed to generate manifests:\n{ex.Message}", "OK");
            }
            finally
            {
                isGenerating = false;
                EditorUtility.ClearProgressBar();
            }
        }
        
        private async Task GenerateManifestForHypothesis(Hypothesis hypothesis)
        {
            var manifest = CreateExperimentManifest(hypothesis);
            var filename = $"experiment_{hypothesis.Id}.yaml";
            var filepath = Path.Combine(OUTPUT_DIR, filename);
            
            await File.WriteAllTextAsync(filepath, manifest);
        }
        
        private string CreateExperimentManifest(Hypothesis hypothesis)
        {
            // Map hypothesis priority to experiment parameters
            var (modelType, corpusSize, batchSize) = GetExperimentParametersFromHypothesis(hypothesis);
            
            // Generate deterministic seed from hypothesis ID
            var seed = GenerateSeedFromId(hypothesis.Id);
            
            // Create experiment tags based on hypothesis type and priority
            var tags = GenerateExperimentTags(hypothesis);
            
            // Map confidence to intervention threshold
            var interventionThreshold = Math.Max(0.3f, Math.Min(0.9f, hypothesis.Confidence));
            
            var manifest = $@"metadata:
  name: ""{hypothesis.Title}""
  description: ""{hypothesis.Description}""
  version: ""1.0.0""
  author: ""School Experiment Framework""
  tags: [{string.Join(", ", tags.ConvertAll(t => $"\"{t}\""))}]
  hypothesis_id: ""{hypothesis.Id}""
  faculty_surface: ""{hypothesis.FacultySurfacePath}""
  hypothesis_type: ""{hypothesis.Type}""

model:
  type: ""{modelType}""
  instance_config:
    enable_intervention_tracking: true
    intervention_threshold: {interventionThreshold:F2}
    faculty_surface_focus: ""{hypothesis.FacultySurfacePath}""
  performance_profile: ""experiment""

conditions:
  hypothesis_types:
    - ""{hypothesis.Type}""
  priority_levels:
    - ""{hypothesis.Priority}""
  confidence_ranges:
    - {hypothesis.Confidence:F2}
  effort_estimates:
    - ""{hypothesis.EstimatedEffort}""

corpus:
  type: ""synthetic""
  size: {corpusSize}
  seed: {seed}
  focus_assets:
    - ""{hypothesis.FacultySurfacePath}""

processing:
  batch_size: {batchSize}
  parallel_execution: true
  checkpoint_interval: 10
  
validation:
  success_criteria:
    - metric: ""hypothesis_validation_score""
      threshold: {hypothesis.Confidence:F2}
    - metric: ""faculty_surface_coverage""
      threshold: 0.8
  expected_duration: ""{hypothesis.EstimatedEffort}""
  
reporting:
  output_format: ""yaml""
  include_metrics:
    - ""execution_time""
    - ""resource_usage""
    - ""validation_score""
    - ""faculty_surface_impact""
  dashboard_integration: true

# Experiment-specific metadata
experiment_context:
  source_inventory_hash: ""{loadedHypotheses.SourceInventoryHash}""
  generation_timestamp: ""{DateTime.UtcNow:yyyy-MM-ddTHH:mm:ss.ffffffZ}""
  unity_version: ""{loadedHypotheses.UnityVersion}""
  project_path: ""{loadedHypotheses.ProjectPath}""
  stage: ""2""
  workflow: ""school""
";

            return manifest;
        }
        
        private (string modelType, int corpusSize, int batchSize) GetExperimentParametersFromHypothesis(Hypothesis hypothesis)
        {
            // Map hypothesis characteristics to experiment parameters
            string modelType = "behavioral_governance";
            int corpusSize = 100;
            int batchSize = 10;
            
            // Adjust based on hypothesis type
            switch (hypothesis.Type)
            {
                case "CapabilityAssertion":
                    modelType = "behavioral_governance";
                    corpusSize = 150;
                    break;
                case "ImprovementTarget":
                    modelType = "batch_evaluation";
                    corpusSize = 200;
                    break;
            }
            
            // Adjust based on priority
            switch (hypothesis.Priority)
            {
                case "High":
                    corpusSize *= 2;
                    batchSize = 20;
                    break;
                case "Medium":
                    corpusSize = (int)(corpusSize * 1.5);
                    batchSize = 15;
                    break;
                case "Low":
                    // Keep default values
                    break;
            }
            
            // Adjust based on confidence
            if (hypothesis.Confidence > 0.8f)
            {
                corpusSize = (int)(corpusSize * 1.2);
            }
            else if (hypothesis.Confidence < 0.5f)
            {
                corpusSize = (int)(corpusSize * 0.8);
            }
            
            return (modelType, corpusSize, batchSize);
        }
        
        private int GenerateSeedFromId(string hypothesisId)
        {
            // Generate deterministic seed from hypothesis ID hash
            var hash = hypothesisId.GetHashCode();
            return Math.Abs(hash % 10000) + 1000; // Ensure positive seed between 1000-10999
        }
        
        private List<string> GenerateExperimentTags(Hypothesis hypothesis)
        {
            var tags = new List<string> { "school", "hypothesis" };
            
            // Add type-based tags
            switch (hypothesis.Type)
            {
                case "CapabilityAssertion":
                    tags.AddRange(new[] { "capability", "assertion" });
                    break;
                case "ImprovementTarget":
                    tags.AddRange(new[] { "improvement", "optimization" });
                    break;
            }
            
            // Add priority tag
            tags.Add(hypothesis.Priority.ToLower());
            
            // Add faculty surface type tag
            tags.Add(hypothesis.FacultySurfaceType.ToLower());
            
            // Add confidence level tag
            if (hypothesis.Confidence >= 0.8f)
                tags.Add("high-confidence");
            else if (hypothesis.Confidence >= 0.6f)
                tags.Add("medium-confidence");
            else
                tags.Add("low-confidence");
            
            return tags;
        }
    }
}