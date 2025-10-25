using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using Newtonsoft.Json;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Bridge between Warbler's strategic analysis and School's experimental pipeline
    /// 
    /// PURPOSE: Preserve Warbler's decision-making context so it flows through:
    /// Warbler (analysis) → School pipeline → Claims → Final Report (recommendations)
    /// 
    /// This ensures the final output has "strategic continuity" with 70% of the
    /// intelligent reasoning that went into the original analysis.
    /// </summary>
    public class WarblerContextBridge
    {
        private const string WARBLER_CONTEXT_DIR = "Assets/experiments/school/warbler_context/";
        private const string ACTIVE_ANALYSIS_FILE = "Assets/experiments/school/warbler_context/active_analysis.json";
        private const string ANALYSIS_HISTORY_DIR = "Assets/experiments/school/warbler_context/history/";

        /// <summary>
        /// Represents Warbler's analysis in a format that School pipeline can consume
        /// </summary>
        [System.Serializable]
        public class WarblerContext
        {
            public string analysis_id = "";
            public DateTime analysis_timestamp = DateTime.Now;
            public string original_request = "";
            
            // Core analysis fields (from ProjectAnalysis)
            public string game_type = "";
            public string complexity_level = "";
            public string[] required_systems = System.Array.Empty<string>();
            public string[] recommended_folders = System.Array.Empty<string>();
            public string estimated_dev_time = "";
            public string[] key_mechanics = System.Array.Empty<string>();
            public string[] technical_considerations = System.Array.Empty<string>();
            public string suggested_architecture = "";
            public string warbler_insights = "";
            
            // Enhancement strategy (high-level recommendations)
            public string[] development_milestones = System.Array.Empty<string>();
            public string[] testing_strategy = System.Array.Empty<string>();
            public string[] suggested_tldl_tags = System.Array.Empty<string>();
            
            // Provider info
            public string ai_provider_used = "";
            public string[] providers_tried = System.Array.Empty<string>();
            public bool github_copilot_enhanced = false;
            
            // Hypothesis generation hints (for School stage 1)
            public string[] strategic_hypotheses = System.Array.Empty<string>();
            public string[] critical_validation_points = System.Array.Empty<string>();
            public string[] success_metrics = System.Array.Empty<string>();
        }

        /// <summary>
        /// Captures Warbler's ProjectAnalysis and saves it to School context
        /// Called from WarblerIntelligentOrchestrator after analysis completes
        /// </summary>
        public static bool SaveWarblerAnalysis(
            dynamic projectAnalysis,
            string originalRequest,
            string aiProvider = "unknown")
        {
            try
            {
                // Ensure directory exists
                if (!Directory.Exists(WARBLER_CONTEXT_DIR))
                {
                    Directory.CreateDirectory(WARBLER_CONTEXT_DIR);
                }

                // Create context from ProjectAnalysis
                var context = new WarblerContext
                {
                    analysis_id = $"warbler_{DateTime.Now:yyyyMMdd_HHmmss}",
                    analysis_timestamp = DateTime.Now,
                    original_request = originalRequest,
                    
                    game_type = projectAnalysis.game_type ?? "",
                    complexity_level = projectAnalysis.complexity_level ?? "",
                    required_systems = projectAnalysis.required_systems ?? System.Array.Empty<string>(),
                    recommended_folders = projectAnalysis.recommended_folders ?? System.Array.Empty<string>(),
                    estimated_dev_time = projectAnalysis.estimated_dev_time ?? "",
                    key_mechanics = projectAnalysis.key_mechanics ?? System.Array.Empty<string>(),
                    technical_considerations = projectAnalysis.technical_considerations ?? System.Array.Empty<string>(),
                    suggested_architecture = projectAnalysis.suggested_architecture ?? "",
                    warbler_insights = projectAnalysis.warbler_insights ?? "",
                    
                    ai_provider_used = aiProvider,
                    providers_tried = projectAnalysis.providers_tried ?? System.Array.Empty<string>(),
                    github_copilot_enhanced = projectAnalysis.github_copilot_enhanced
                };

                // Extract enhancement strategy
                if (projectAnalysis.warbler_enhancement != null)
                {
                    context.development_milestones = projectAnalysis.warbler_enhancement.development_milestones ?? System.Array.Empty<string>();
                    context.testing_strategy = projectAnalysis.warbler_enhancement.testing_strategy ?? System.Array.Empty<string>();
                    context.suggested_tldl_tags = projectAnalysis.warbler_enhancement.suggested_tldl_tags ?? System.Array.Empty<string>();
                }

                // Generate hypotheses from strategic analysis
                context.strategic_hypotheses = GenerateStrategicHypotheses(context);
                context.critical_validation_points = GenerateValidationPoints(context);
                context.success_metrics = GenerateSuccessMetrics(context);

                // Save as active analysis
                string jsonContent = JsonConvert.SerializeObject(context, Formatting.Indented);
                File.WriteAllText(ACTIVE_ANALYSIS_FILE, jsonContent);

                // Also save to history
                if (!Directory.Exists(ANALYSIS_HISTORY_DIR))
                {
                    Directory.CreateDirectory(ANALYSIS_HISTORY_DIR);
                }
                
                string historyPath = Path.Combine(ANALYSIS_HISTORY_DIR, $"{context.analysis_id}.json");
                File.WriteAllText(historyPath, jsonContent);

                Debug.Log($"✅ Warbler analysis saved: {context.analysis_id}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"❌ Failed to save Warbler analysis: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Load the active Warbler analysis
        /// </summary>
        public static WarblerContext LoadActiveAnalysis()
        {
            try
            {
                if (!File.Exists(ACTIVE_ANALYSIS_FILE))
                    return null;

                string jsonContent = File.ReadAllText(ACTIVE_ANALYSIS_FILE);
                return JsonConvert.DeserializeObject<WarblerContext>(jsonContent);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"⚠️ Failed to load Warbler context: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Generates strategic hypotheses from Warbler analysis
        /// These become the foundation for School experiments
        /// </summary>
        private static string[] GenerateStrategicHypotheses(WarblerContext context)
        {
            var hypotheses = new List<string>();

            // Architecture hypothesis
            if (!string.IsNullOrEmpty(context.suggested_architecture))
            {
                hypotheses.Add($"Architecture: {context.suggested_architecture} is optimal for {context.game_type}");
            }

            // Complexity hypothesis
            if (!string.IsNullOrEmpty(context.complexity_level))
            {
                hypotheses.Add($"Complexity: {context.game_type} at {context.complexity_level} level can be delivered in {context.estimated_dev_time}");
            }

            // System hypothesis
            foreach (var system in context.required_systems.Take(3))
            {
                hypotheses.Add($"Critical System: {system} is essential for {context.game_type} functionality");
            }

            // Mechanic hypothesis
            foreach (var mechanic in context.key_mechanics.Take(3))
            {
                hypotheses.Add($"Core Mechanic: {mechanic} must be implemented first for game feel validation");
            }

            return hypotheses.ToArray();
        }

        /// <summary>
        /// Generates critical validation points that School should test
        /// </summary>
        private static string[] GenerateValidationPoints(WarblerContext context)
        {
            var points = new List<string>();

            points.Add($"Game Type Recognition: Can team correctly identify and execute {context.game_type} requirements?");
            points.Add($"Complexity Assessment: Is {context.complexity_level} complexity level accurate?");
            points.Add($"Timeline Validation: Can {context.estimated_dev_time} estimate be met with proposed architecture?");
            points.Add($"Architecture Viability: Does {context.suggested_architecture} pattern actually work for this use case?");
            
            foreach (var consideration in context.technical_considerations.Take(3))
            {
                points.Add($"Technical: {consideration}");
            }

            return points.ToArray();
        }

        /// <summary>
        /// Generates measurable success metrics from analysis
        /// </summary>
        private static string[] GenerateSuccessMetrics(WarblerContext context)
        {
            var metrics = new List<string>
            {
                $"✓ Project matches {context.game_type} pattern requirements",
                $"✓ Architecture follows {context.suggested_architecture} design",
                $"✓ All required systems ({context.required_systems.Length}) implemented",
                $"✓ Timeline estimate within ±25% of {context.estimated_dev_time}",
                $"✓ All key mechanics ({context.key_mechanics.Length}) validated",
            };

            return metrics.ToArray();
        }

        /// <summary>
        /// Creates a TLDL entry from Warbler analysis for continuity
        /// </summary>
        public static void CreateTLDLFromWarbler(WarblerContext context)
        {
            try
            {
                var tldlContent = new
                {
                    title = $"Warbler Analysis: {context.game_type}",
                    analysis_id = context.analysis_id,
                    timestamp = context.analysis_timestamp,
                    original_request = context.original_request,
                    
                    summary = new
                    {
                        game_type = context.game_type,
                        complexity = context.complexity_level,
                        timeline = context.estimated_dev_time,
                        architecture = context.suggested_architecture,
                    },
                    
                    strategic_recommendations = context.development_milestones,
                    testing_focus = context.testing_strategy,
                    key_mechanics = context.key_mechanics,
                    required_systems = context.required_systems,
                };

                string tldlPath = $"TLDL/entries/warbler_{context.analysis_id}.json";
                string jsonContent = JsonConvert.SerializeObject(tldlContent, Formatting.Indented);
                
                // Ensure TLDL directory exists
                Directory.CreateDirectory(Path.GetDirectoryName(tldlPath));
                File.WriteAllText(tldlPath, jsonContent);

                Debug.Log($"📜 Created TLDL entry: {tldlPath}");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"⚠️ Failed to create TLDL entry: {ex.Message}");
            }
        }
    }
}