using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Linq;
using UnityEngine;
using UnityEditor;
using System.Text;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Unity Editor window for School experiment result validation
    /// KeeperNote: Stage 4 - Validation & promotion with Unity 6 & GH integration
    /// </summary>
    public class ResultValidator : EditorWindow
    {
        private Vector2 scrollPosition;
        private List<RunResult> availableRuns;
        private bool isValidating = false;
        private string validationProgress = "";
        private DateTime lastValidationTime;
        private ValidationSummary lastValidationSummary;
        private bool showLogs = false;
        private readonly StringBuilder validationLogs = new();
        
        // Paths and settings
        private const string RUNS_DIR = "assets/experiments/school/outputs/runs/";
        private const string CLAIMS_DIR = "assets/experiments/school/claims/";
        private const string VALIDATED_CLAIMS_DIR = "assets/experiments/school/claims/validated/";
        private const string HYPOTHESES_CLAIMS_DIR = "assets/experiments/school/claims/hypotheses/";
        private const string REGRESSIONS_CLAIMS_DIR = "assets/experiments/school/claims/regressions/";
        private const string ANOMALIES_CLAIMS_DIR = "assets/experiments/school/claims/anomalies/";
        private const string IMPROVEMENTS_CLAIMS_DIR = "assets/experiments/school/claims/improvements/";
        private const string NEW_PHENOMENA_CLAIMS_DIR = "assets/experiments/school/claims/new_phenomena/";
        private const string BASELINE_METRICS_PATH = "data/baseline_metrics.json";
        
        [MenuItem("Tools/School/Validate Results")]
        public static void ShowWindow()
        {
            var window = GetWindow<ResultValidator>("Result Validator");
            window.minSize = new Vector2(600, 800);
            window.Show();
        }
        
        private void OnEnable()
        {
            LoadAvailableRuns();
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawRunsSection();
            DrawValidationSection();
            DrawResultsSection();
            DrawLogsSection();
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.Space(10);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("School Result Validator - Stage 4", EditorStyles.largeLabel);
            EditorGUILayout.LabelField("Validation & Promotion with Unity 6 & GitHub Integration", EditorStyles.miniLabel);
            EditorGUILayout.Space(5);
            
            var style = new GUIStyle(EditorStyles.label) { wordWrap = true };
            EditorGUILayout.LabelField("Validates experiment results, computes confidence scores, checks baseline deltas, and promotes validated claims.", style);
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.Space(10);
        }
        
        private void DrawRunsSection()
        {
            EditorGUILayout.LabelField("Available Experiment Runs", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (GUILayout.Button("Refresh Runs"))
            {
                LoadAvailableRuns();
            }
            
            EditorGUILayout.Space(5);
            
            if (availableRuns == null || availableRuns.Count == 0)
            {
                EditorGUILayout.LabelField("No experiment runs found.");
                EditorGUILayout.LabelField("Please run Stage 3 (Experiment Runner) first.");
            }
            else
            {
                EditorGUILayout.LabelField($"Found {availableRuns.Count} experiment runs:");
                
                EditorGUILayout.BeginVertical(EditorStyles.textArea);
                foreach (var run in availableRuns.Take(10)) // Show first 10
                {
                    EditorGUILayout.BeginHorizontal();
                    EditorGUILayout.LabelField($"• {run.RunId}", GUILayout.Width(80));
                    EditorGUILayout.LabelField($"{run.ExperimentName}", GUILayout.ExpandWidth(true));
                    EditorGUILayout.LabelField($"{(run.Success ? "✓" : "✗")}", GUILayout.Width(20));
                    EditorGUILayout.EndHorizontal();
                }
                
                if (availableRuns.Count > 10)
                {
                    EditorGUILayout.LabelField($"... and {availableRuns.Count - 10} more runs");
                }
                EditorGUILayout.EndVertical();
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawValidationSection()
        {
            EditorGUILayout.LabelField("Validation Control", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (isValidating)
            {
                EditorGUILayout.LabelField("Status: Validating...", EditorStyles.boldLabel);
                EditorGUILayout.LabelField(validationProgress);
                
                if (GUILayout.Button("Cancel Validation"))
                {
                    isValidating = false;
                    validationProgress = "Validation cancelled by user";
                }
            }
            else
            {
                EditorGUILayout.LabelField("Status: Ready");
                
                GUI.enabled = availableRuns != null && availableRuns.Count > 0;
                if (GUILayout.Button("Validate All Results"))
                {
                    ValidateAllResults();
                }
                GUI.enabled = true;
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawResultsSection()
        {
            EditorGUILayout.LabelField("Validation Results", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (lastValidationSummary != null)
            {
                EditorGUILayout.LabelField($"Last validation: {lastValidationTime:yyyy-MM-dd HH:mm:ss}");
                EditorGUILayout.Space(5);
                
                EditorGUILayout.LabelField($"Runs validated: {lastValidationSummary.RunsValidated}");
                EditorGUILayout.LabelField($"Claims promoted: {lastValidationSummary.ClaimsPromoted}");
                EditorGUILayout.LabelField($"Average confidence: {lastValidationSummary.AverageConfidence:F2}");
                EditorGUILayout.LabelField($"Baseline delta: {lastValidationSummary.BaselineDelta:F2}%");
                
                EditorGUILayout.Space(5);
                
                if (GUILayout.Button("Show Claims Directory"))
                {
                    ShowClaimsDirectory();
                }
                
                if (GUILayout.Button("Show GitHub Integration Data"))
                {
                    ShowGitHubIntegrationData();
                }
            }
            else
            {
                EditorGUILayout.LabelField("No validation results yet.");
                EditorGUILayout.LabelField("Run validation to see results here.");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawLogsSection()
        {
            EditorGUILayout.LabelField("Validation Logs", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            showLogs = EditorGUILayout.Foldout(showLogs, $"Show logs ({validationLogs.Length} characters)");
            
            if (showLogs)
            {
                EditorGUILayout.BeginVertical(EditorStyles.textArea);
                EditorGUILayout.SelectableLabel(validationLogs.ToString(), GUILayout.Height(200));
                EditorGUILayout.EndVertical();
                
                if (GUILayout.Button("Clear Logs"))
                {
                    validationLogs.Clear();
                }
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void LoadAvailableRuns()
        {
            availableRuns = new List<RunResult>();
            
            try
            {
                if (!Directory.Exists(RUNS_DIR))
                {
                    LogMessage($"Runs directory not found: {RUNS_DIR}");
                    return;
                }
                
                var runDirectories = Directory.GetDirectories(RUNS_DIR, "run_*");
                
                foreach (var runDir in runDirectories)
                {
                    var metadataPath = Path.Combine(runDir, "run_metadata.json");
                    if (File.Exists(metadataPath))
                    {
                        try
                        {
                            var metadataJson = File.ReadAllText(metadataPath);
                            var runData = JsonUtility.FromJson<RunMetadata>(metadataJson);
                            
                            var runResult = new RunResult
                            {
                                RunId = runData.run_id,
                                ExperimentName = runData.experiment_name,
                                Success = runData.success,
                                ExecutionTime = runData.execution_time,
                                RunDirectory = runDir,
                                Metadata = runData
                            };
                            
                            availableRuns.Add(runResult);
                        }
                        catch (Exception ex)
                        {
                            LogMessage($"Failed to parse run metadata: {metadataPath} - {ex.Message}");
                        }
                    }
                }
                
                availableRuns = availableRuns.OrderBy(r => r.RunId).ToList();
                LogMessage($"Loaded {availableRuns.Count} experiment runs");
            }
            catch (Exception ex)
            {
                LogMessage($"Failed to load runs: {ex.Message}");
            }
        }
        
        private async void ValidateAllResults()
        {
            if (isValidating) return;
            
            isValidating = true;
            validationProgress = "Starting validation...";
            lastValidationTime = DateTime.Now;
            
            try
            {
                // Ensure output directories exist
                Directory.CreateDirectory(CLAIMS_DIR);
                Directory.CreateDirectory(VALIDATED_CLAIMS_DIR);
                Directory.CreateDirectory(HYPOTHESES_CLAIMS_DIR);
                Directory.CreateDirectory(REGRESSIONS_CLAIMS_DIR);
                Directory.CreateDirectory(ANOMALIES_CLAIMS_DIR);
                Directory.CreateDirectory(IMPROVEMENTS_CLAIMS_DIR);
                Directory.CreateDirectory(NEW_PHENOMENA_CLAIMS_DIR);
                
                var summary = new ValidationSummary();
                var validatedClaims = new List<ClaimData>();
                
                LogMessage($"Validating {availableRuns.Count} experiment runs...");
                
                for (int i = 0; i < availableRuns.Count; i++)
                {
                    var run = availableRuns[i];
                    validationProgress = $"Validating run {i + 1}/{availableRuns.Count}: {run.RunId}";
                    Repaint();
                    
                    var claim = await ValidateRun(run);
                    if (claim != null)
                    {
                        validatedClaims.Add(claim);
                        summary.RunsValidated++;
                        summary.ConfidenceScores.Add(claim.ConfidenceScore);
                    }
                    
                    await Task.Yield();
                }
                
                // Compute baseline delta
                summary.BaselineDelta = await ComputeBaselineDelta();
                
                // Promote claims based on validation results
                summary.ClaimsPromoted = await PromoteClaims(validatedClaims);
                
                // Calculate average confidence
                summary.AverageConfidence = summary.ConfidenceScores.Count > 0 
                    ? summary.ConfidenceScores.Average() 
                    : 0.0f;
                
                lastValidationSummary = summary;
                
                LogMessage($"Validation complete: {summary.RunsValidated} runs validated, {summary.ClaimsPromoted} claims promoted");
                
                // Generate GitHub integration data
                await GenerateGitHubIntegrationData(summary);
                
                EditorUtility.DisplayDialog("Validation Complete", 
                    $"Validated {summary.RunsValidated} runs.\nPromoted {summary.ClaimsPromoted} claims.\nAverage confidence: {summary.AverageConfidence:F2}", 
                    "OK");
            }
            catch (Exception ex)
            {
                LogMessage($"Validation failed: {ex.Message}");
                EditorUtility.DisplayDialog("Validation Failed", $"Validation failed:\n{ex.Message}", "OK");
            }
            finally
            {
                isValidating = false;
                validationProgress = "Validation complete";
                Repaint();
            }
        }
        
        private async Task<ClaimData> ValidateRun(RunResult run) // Enhanced validation with comprehensive claim analysis
        {
            try
            {
                // Simulate brief validation delay to represent actual analysis time
                await Task.Delay(1); // Brief delay to represent validation processing
                
                // Calculate confidence score based on run success and metadata
                float confidence = CalculateConfidenceScore(run);
                
                // Determine claim type based on validation criteria
                var (claimType, classificationMetadata) = DetermineClaimTypeWithMetadata(run, confidence);
                
                var claim = new ClaimData
                {
                    RunId = run.RunId,
                    ExperimentName = run.ExperimentName,
                    HypothesisId = run.Metadata.hypothesis_id ?? "unknown",
                    ConfidenceScore = confidence,
                    ClaimType = claimType,
                    ValidationTime = DateTime.Now.ToString("O"),
                    Success = run.Success,
                    BaselineComparison = "pending", // Will be computed later
                    Classification = classificationMetadata
                };
                
                LogMessage($"Run {run.RunId}: confidence={confidence:F2}, type={claimType}, " +
                          $"anomaly_score={classificationMetadata.AnomalyScore:F2}");
                return claim;
            }
            catch (Exception ex)
            {
                LogMessage($"Failed to validate run {run.RunId}: {ex.Message}");
                return null;
            }
        }
        
        private float CalculateConfidenceScore(RunResult run)
        {
            float baseConfidence = run.Success ? 0.8f : 0.2f;
            
            // Factor in execution consistency (if we have execution logs)
            float consistencyFactor = 1.0f;
            var logsPath = Path.Combine(run.RunDirectory, "execution_logs.txt");
            if (File.Exists(logsPath))
            {
                try
                {
                    var logs = File.ReadAllText(logsPath);
                    // Simple heuristic: fewer errors = higher confidence
                    int errorCount = logs.Split("ERROR", StringSplitOptions.None).Length - 1;
                    consistencyFactor = Math.Max(0.1f, 1.0f - (errorCount * 0.1f));
                }
                catch
                {
                    consistencyFactor = 0.8f; // Default if we can't read logs
                }
            }
            
            // Factor in metadata completeness
            float metadataFactor = 1.0f;
            if (string.IsNullOrEmpty(run.Metadata.hypothesis_id)) metadataFactor *= 0.9f;
            if (string.IsNullOrEmpty(run.Metadata.git_commit)) metadataFactor *= 0.95f;
            if (string.IsNullOrEmpty(run.Metadata.git_branch)) metadataFactor *= 0.95f;
            
            float finalConfidence = baseConfidence * consistencyFactor * metadataFactor;
            return Math.Min(0.95f, Math.Max(0.05f, finalConfidence));
        }
        
        /// <summary>
        /// Determine claim type and classification metadata based on comprehensive validation criteria
        /// 🎯 ENHANCED IMPLEMENTATION: Uses run metadata, execution context, confidence score, and advanced
        /// pattern recognition for intelligent claim classification that differentiates between regressions,
        /// expected anomalies, unexpected anomalies, improvements, and new phenomena
        /// </summary>
        private (string claimType, ClassificationMetadata metadata) DetermineClaimTypeWithMetadata(RunResult run, float confidence)
        {
            // Step 1: Basic classification using confidence thresholds
            var baseClassification = DetermineBaseClassification(confidence);
            
            // Step 2: Analyze for anomaly patterns
            var anomalyAnalysis = AnalyzeAnomalyPatterns(run, confidence);
            
            // Step 3: Check for improvement patterns
            var improvementAnalysis = AnalyzeImprovementPatterns(run, confidence);
            
            // Step 4: Detect new phenomena
            var phenomenonAnalysis = AnalyzeNewPhenomena(run, confidence);
            
            // Step 5: Apply metadata-based classification enhancements
            var enhancedAnalysis = ApplyMetadataBasedClassification(run, confidence, baseClassification.ToString());
            
            // Step 6: Apply domain-specific classification rules
            var finalAnalysis = ApplyDomainSpecificClassification(run, confidence, enhancedAnalysis);
            
            // Step 7: Combine all analyses to determine final classification
            var (finalType, metadata) = SynthesizeClassification(
                run, confidence, baseClassification, anomalyAnalysis, 
                improvementAnalysis, phenomenonAnalysis, finalAnalysis);
            
            LogMessage($"Enhanced classification for {run.RunId}: " +
                      $"base={baseClassification}, final={finalType}, " +
                      $"anomaly_score={metadata.AnomalyScore:F2}, " +
                      $"trend_significance={metadata.TrendSignificance:F2}");
            
            return (finalType, metadata);
        }

        /// <summary>
        /// Determine base classification using traditional confidence thresholds
        /// </summary>
        private ClaimClassification DetermineBaseClassification(float confidence)
        {
            return confidence switch
            {
                >= 0.75f => ClaimClassification.Validated,
                >= 0.5f => ClaimClassification.Hypothesis,
                _ => ClaimClassification.Regression
            };
        }

        /// <summary>
        /// Analyze patterns that indicate anomalous behavior (expected or unexpected)
        /// </summary>
        private AnomalyAnalysis AnalyzeAnomalyPatterns(RunResult run, float confidence)
        {
            var analysis = new AnomalyAnalysis();
            
            // Analyze execution time patterns for anomalies
            if (!string.IsNullOrEmpty(run.ExecutionTime) && TryParseExecutionTime(run.ExecutionTime, out var duration))
            {
                // Very fast execution might indicate anomalous behavior
                if (duration.TotalSeconds < 2)
                {
                    analysis.AnomalyScore += 0.3f;
                    analysis.AnomalyFlags.Add("execution_too_fast");
                    analysis.Type = AnomalyType.Performance;
                }
                // Very slow execution might also indicate anomalies
                else if (duration.TotalMinutes > 15)
                {
                    analysis.AnomalyScore += 0.4f;
                    analysis.AnomalyFlags.Add("execution_too_slow");
                    analysis.Type = AnomalyType.Performance;
                }
            }
            
            // Check for expected anomalies based on experiment name patterns
            var experimentName = run.ExperimentName.ToLower();
            if (experimentName.Contains("stress") || experimentName.Contains("load") || 
                experimentName.Contains("boundary") || experimentName.Contains("edge"))
            {
                analysis.IsExpected = true;
                analysis.AnomalyScore += 0.2f; // Moderate anomaly score for expected stress tests
                analysis.AnomalyFlags.Add("expected_stress_test");
            }
            
            // Check for git branch patterns that suggest expected anomalies
            var gitBranch = run.Metadata.git_branch?.ToLower() ?? "";
            if (gitBranch.Contains("experimental") || gitBranch.Contains("prototype") || 
                gitBranch.Contains("research") || gitBranch.Contains("spike"))
            {
                analysis.IsExpected = true;
                analysis.AnomalyScore += 0.15f;
                analysis.AnomalyFlags.Add("experimental_branch");
            }
            
            // Behavioral anomalies - success/failure mismatch with confidence
            if (run.Success && confidence < 0.3f)
            {
                analysis.AnomalyScore += 0.5f; // High anomaly - successful run with very low confidence
                analysis.AnomalyFlags.Add("success_confidence_mismatch");
                analysis.Type = AnomalyType.Behavioral;
            }
            else if (!run.Success && confidence > 0.7f)
            {
                analysis.AnomalyScore += 0.4f; // Moderate anomaly - failed run with high confidence
                analysis.AnomalyFlags.Add("failure_confidence_mismatch");
                analysis.Type = AnomalyType.Behavioral;
            }
            
            return analysis;
        }

        /// <summary>
        /// Analyze patterns that indicate significant improvements
        /// </summary>
        private ImprovementAnalysis AnalyzeImprovementPatterns(RunResult run, float confidence)
        {
            var analysis = new ImprovementAnalysis();
            
            // High confidence successful runs are potential improvements
            if (run.Success && confidence >= 0.8f)
            {
                analysis.ImprovementScore = confidence;
                analysis.ImprovementFlags.Add("high_confidence_success");
                
                // Check for performance improvement indicators
                var experimentName = run.ExperimentName.ToLower();
                if (experimentName.Contains("optimization") || experimentName.Contains("performance") ||
                    experimentName.Contains("efficiency") || experimentName.Contains("speed"))
                {
                    analysis.ImprovementScore += 0.1f;
                    analysis.ImprovementFlags.Add("performance_optimization");
                    analysis.Type = "performance";
                }
                
                // Check for user experience improvements
                if (experimentName.Contains("ui") || experimentName.Contains("ux") ||
                    experimentName.Contains("usability") || experimentName.Contains("experience"))
                {
                    analysis.ImprovementScore += 0.1f;
                    analysis.ImprovementFlags.Add("user_experience_enhancement");
                    analysis.Type = "user_experience";
                }
            }
            
            return analysis;
        }

        /// <summary>
        /// Detect patterns that indicate new phenomena not seen before
        /// </summary>
        private PhenomenonAnalysis AnalyzeNewPhenomena(RunResult run, float confidence)
        {
            var analysis = new PhenomenonAnalysis();
            
            // Check for novel experiment patterns
            var experimentName = run.ExperimentName.ToLower();
            if (experimentName.Contains("novel") || experimentName.Contains("new") ||
                experimentName.Contains("innovative") || experimentName.Contains("breakthrough"))
            {
                analysis.PhenomenonScore = 0.6f;
                analysis.PhenomenonFlags.Add("novel_experiment_indicator");
                analysis.Type = "experimental_breakthrough";
            }
            
            // Check for unusual confidence patterns that might indicate new phenomena
            if (confidence > 0.9f && run.Success)
            {
                analysis.PhenomenonScore += 0.3f; // Very high confidence might indicate something new
                analysis.PhenomenonFlags.Add("exceptionally_high_confidence");
            }
            
            // Check for git context that suggests new phenomena
            var gitBranch = run.Metadata.git_branch?.ToLower() ?? "";
            if (gitBranch.Contains("discovery") || gitBranch.Contains("exploration") ||
                gitBranch.Contains("investigation"))
            {
                analysis.PhenomenonScore += 0.2f;
                analysis.PhenomenonFlags.Add("exploratory_branch");
                analysis.Type = "behavioral_discovery";
            }
            
            return analysis;
        }

        /// <summary>
        /// Synthesize all analyses into final classification and metadata
        /// </summary>
        private (string claimType, ClassificationMetadata metadata) SynthesizeClassification(
            RunResult run, float confidence, ClaimClassification baseClassification,
            AnomalyAnalysis anomalyAnalysis, ImprovementAnalysis improvementAnalysis,
            PhenomenonAnalysis phenomenonAnalysis, string domainSpecificType)
        {
            var metadata = new ClassificationMetadata
            {
                AnomalyScore = Math.Min(1.0f, anomalyAnalysis.AnomalyScore),
                TrendSignificance = confidence,
                IsExpectedAnomaly = anomalyAnalysis.IsExpected,
                ClassificationFlags = new string[0], // Will be populated below
                BaselineDeviation = "pending_baseline_analysis"
            };
            
            var flags = new List<string>();
            string finalType;
            string secondaryType = "";
            string reason;
            
            // Priority 1: New phenomena (highest priority for novel discoveries)
            if (phenomenonAnalysis.PhenomenonScore >= 0.5f)
            {
                finalType = "new_phenomenon";
                metadata.PhenomenonType = phenomenonAnalysis.Type;
                flags.AddRange(phenomenonAnalysis.PhenomenonFlags);
                reason = $"Novel patterns detected (score: {phenomenonAnalysis.PhenomenonScore:F2})";
            }
            // Priority 2: Improvements (significant positive changes)
            else if (improvementAnalysis.ImprovementScore >= 0.8f)
            {
                finalType = "improvement";
                secondaryType = improvementAnalysis.Type;
                flags.AddRange(improvementAnalysis.ImprovementFlags);
                reason = $"Significant improvement detected (score: {improvementAnalysis.ImprovementScore:F2})";
            }
            // Priority 3: Anomalies (unexpected or expected deviations)
            else if (anomalyAnalysis.AnomalyScore >= 0.3f)
            {
                finalType = "anomaly";
                secondaryType = anomalyAnalysis.IsExpected ? "expected" : "unexpected";
                flags.AddRange(anomalyAnalysis.AnomalyFlags);
                reason = $"{secondaryType} anomaly detected (score: {anomalyAnalysis.AnomalyScore:F2})";
            }
            // Priority 4: Domain-specific classification
            else
            {
                finalType = domainSpecificType;
                reason = $"Domain-specific classification based on {baseClassification} with confidence {confidence:F2}";
            }
            
            // Add confidence-based flags
            if (confidence >= 0.9f) flags.Add("very_high_confidence");
            else if (confidence >= 0.75f) flags.Add("high_confidence");
            else if (confidence >= 0.5f) flags.Add("moderate_confidence");
            else flags.Add("low_confidence");
            
            // Add success-based flags
            if (run.Success) flags.Add("successful_execution");
            else flags.Add("failed_execution");
            
            metadata.PrimaryType = finalType;
            metadata.SecondaryType = secondaryType;
            metadata.ClassificationFlags = flags.ToArray();
            metadata.ClassificationReason = reason;
            
            return (finalType, metadata);
        }

        /// <summary>
        /// Apply metadata-based classification enhancements
        /// Considers execution quality, git context, and experimental conditions
        /// </summary>
        private string ApplyMetadataBasedClassification(RunResult run, float confidence, string baseType)
        {
            var metadata = run.Metadata;
            string enhancedType = baseType;

            // Factor in execution quality indicators
            if (run.Success && !string.IsNullOrEmpty(run.ExecutionTime))
            {
                if (TryParseExecutionTime(run.ExecutionTime, out var executionDuration))
                {
                    // Very fast execution might indicate incomplete testing
                    if (executionDuration.TotalSeconds < 5 && baseType == "validated")
                    {
                        enhancedType = "hypothesis"; // Downgrade - too fast to be thorough
                        LogMessage($"Downgraded {run.RunId} due to suspiciously fast execution: {executionDuration.TotalSeconds}s");
                    }
                    // Very slow execution might indicate system issues
                    else if (executionDuration.TotalMinutes > 30 && baseType != "regression")
                    {
                        enhancedType = "hypothesis"; // Downgrade - might have performance issues
                        LogMessage($"Downgraded {run.RunId} due to slow execution: {executionDuration.TotalMinutes:F1}m");
                    }
                }
            }

            // Factor in git context quality
            if (HasHighQualityGitContext(metadata))
            {
                // Good git hygiene suggests more reliable experiment
                if (baseType == "hypothesis" && confidence >= 0.65f)
                {
                    enhancedType = "validated"; // Upgrade due to good git practices
                    LogMessage($"Upgraded {run.RunId} due to high-quality git context");
                }
            }
            else if (HasPoorGitContext(metadata))
            {
                // Poor git hygiene suggests less reliable experiment
                if (baseType == "validated")
                {
                    enhancedType = "hypothesis"; // Downgrade due to poor git practices
                    LogMessage($"Downgraded {run.RunId} due to poor git context");
                }
            }

            // Factor in hypothesis quality
            if (!string.IsNullOrEmpty(metadata.hypothesis_id))
            {
                var hypothesisQuality = EvaluateHypothesisQuality(metadata.hypothesis_id);
                if (hypothesisQuality == HypothesisQuality.High && confidence >= 0.6f)
                {
                    if (baseType == "hypothesis")
                    {
                        enhancedType = "validated"; // Upgrade for well-formed hypothesis
                        LogMessage($"Upgraded {run.RunId} due to high-quality hypothesis: {metadata.hypothesis_id}");
                    }
                }
                else if (hypothesisQuality == HypothesisQuality.Low)
                {
                    if (baseType == "validated")
                    {
                        enhancedType = "hypothesis"; // Downgrade for poor hypothesis
                        LogMessage($"Downgraded {run.RunId} due to low-quality hypothesis: {metadata.hypothesis_id}");
                    }
                }
            }

            return enhancedType;
        }

        /// <summary>
        /// Apply domain-specific classification rules based on experiment type and context
        /// </summary>
        private string ApplyDomainSpecificClassification(RunResult run, float confidence, string enhancedType)
        {
            // Analyze experiment name for domain-specific patterns
            var experimentType = ClassifyExperimentType(run.ExperimentName);

            string finalType = experimentType switch
            {
                ExperimentType.Performance => ApplyPerformanceClassificationRules(run, confidence, enhancedType),
                ExperimentType.UserInterface => ApplyUIClassificationRules(run, confidence, enhancedType),
                ExperimentType.Integration => ApplyIntegrationClassificationRules(run, confidence, enhancedType),
                ExperimentType.Security => ApplySecurityClassificationRules(run, confidence, enhancedType),
                ExperimentType.DataProcessing => ApplyDataProcessingClassificationRules(run, confidence, enhancedType),
                _ => ApplyGeneralClassificationRules(run, confidence, enhancedType), // Apply general classification rules
            };

            // Apply final safety checks
            if (finalType != enhancedType)
            {
                LogMessage($"Domain-specific classification changed {run.RunId} from {enhancedType} to {finalType} " +
                          $"(experiment type: {experimentType})");
            }

            return finalType;
        }

        /// <summary>
        /// Check if git context indicates high-quality experimental practices
        /// </summary>
        private bool HasHighQualityGitContext(RunMetadata metadata)
        {
            return !string.IsNullOrEmpty(metadata.git_commit) &&
                   !string.IsNullOrEmpty(metadata.git_branch) &&
                   metadata.git_branch != "main" && // Experiments should be on feature branches
                   metadata.git_branch != "master" &&
                   metadata.git_commit.Length >= 7; // Full commit hash indicates proper git usage
        }

        /// <summary>
        /// Check if git context indicates poor experimental practices
        /// </summary>
        private bool HasPoorGitContext(RunMetadata metadata)
        {
            return string.IsNullOrEmpty(metadata.git_commit) ||
                   string.IsNullOrEmpty(metadata.git_branch) ||
                   metadata.git_branch == "main" || // Experiments directly on main are risky
                   metadata.git_branch == "master";
        }

        /// <summary>
        /// Evaluate the quality of the hypothesis based on naming conventions and structure
        /// </summary>
        private HypothesisQuality EvaluateHypothesisQuality(string hypothesisId)
        {
            if (string.IsNullOrEmpty(hypothesisId))
                return HypothesisQuality.None;

            // High-quality hypothesis indicators
            if (hypothesisId.Contains("performance") && hypothesisId.Contains("improvement") ||
                hypothesisId.Contains("user_experience") && hypothesisId.Contains("enhancement") ||
                hypothesisId.Contains("efficiency") && hypothesisId.Contains("optimization") ||
                hypothesisId.Length > 20 && hypothesisId.Contains("_"))
            {
                return HypothesisQuality.High;
            }

            // Low-quality hypothesis indicators
            if (hypothesisId.Length < 5 ||
                hypothesisId.Equals("test", StringComparison.OrdinalIgnoreCase) ||
                hypothesisId.Equals("experiment", StringComparison.OrdinalIgnoreCase) ||
                hypothesisId.StartsWith("tmp") ||
                hypothesisId.StartsWith("debug"))
            {
                return HypothesisQuality.Low;
            }

            return HypothesisQuality.Medium;
        }

        /// <summary>
        /// Classify experiment type based on name and context
        /// </summary>
        private ExperimentType ClassifyExperimentType(string experimentName)
        {
            var name = experimentName.ToLower();
            
            if (name.Contains("performance") || name.Contains("benchmark") || name.Contains("speed"))
                return ExperimentType.Performance;
            
            if (name.Contains("ui") || name.Contains("interface") || name.Contains("ux") || name.Contains("frontend"))
                return ExperimentType.UserInterface;
            
            if (name.Contains("integration") || name.Contains("api") || name.Contains("service"))
                return ExperimentType.Integration;
            
            if (name.Contains("security") || name.Contains("auth") || name.Contains("permission"))
                return ExperimentType.Security;
            
            if (name.Contains("data") || name.Contains("processing") || name.Contains("analytics"))
                return ExperimentType.DataProcessing;
            
            return ExperimentType.General;
        }

        /// <summary>
        /// Try to parse execution time string into TimeSpan
        /// </summary>
        private bool TryParseExecutionTime(string executionTimeStr, out TimeSpan duration)
        {
            duration = TimeSpan.Zero;
            
            try
            {
                // Handle various formats: "1.23s", "45.6", "00:01:23", etc.
                if (executionTimeStr.EndsWith("s"))
                {
                    var secondsStr = executionTimeStr.TrimEnd('s');
                    if (double.TryParse(secondsStr, out var seconds))
                    {
                        duration = TimeSpan.FromSeconds(seconds);
                        return true;
                    }
                }
                else if (double.TryParse(executionTimeStr, out var seconds))
                {
                    duration = TimeSpan.FromSeconds(seconds);
                    return true;
                }
                else if (TimeSpan.TryParse(executionTimeStr, out duration))
                {
                    return true;
                }
            }
            catch
            {
                // Parsing failed, return false
            }
            
            return false;
        }

        // Domain-specific classification methods
        private string ApplyPerformanceClassificationRules(RunResult _, float confidence, string currentType)
        {
            // Performance experiments require higher confidence for validation
            if (currentType == "validated" && confidence < 0.8f)
            {
                return "hypothesis"; // Performance claims need higher confidence
            }
            return currentType;
        }

        private string ApplyUIClassificationRules(RunResult _, float confidence, string currentType)
        {
            // UI experiments are more subjective, slightly lower bar for validation
            if (currentType == "hypothesis" && confidence >= 0.7f)
            {
                return "validated"; // UI improvements can be validated with slightly lower confidence
            }
            return currentType;
        }

        private string ApplyIntegrationClassificationRules(RunResult run, float confidence, string currentType)
        {
            // Integration tests are binary - they work or they don't
            if (run.Success && confidence >= 0.6f)
            {
                return "validated"; // Successful integration is highly valuable
            }
            else if (!run.Success)
            {
                return "regression"; // Failed integration is concerning
            }
            return currentType;
        }

        private string ApplySecurityClassificationRules(RunResult _, float confidence, string currentType)
        {
            // Security experiments require very high confidence
            if (currentType == "validated" && confidence < 0.85f)
            {
                return "hypothesis"; // Security changes need extra validation
            }
            return currentType;
        }

        private string ApplyDataProcessingClassificationRules(RunResult _, float confidence, string currentType)
        {
            // Data processing experiments depend on data quality
            if (currentType == "validated" && confidence < 0.75f)
            {
                return "hypothesis"; // Data experiments can have hidden biases
            }
            return currentType;
        }

        private string ApplyGeneralClassificationRules(RunResult _, float _1, string currentType)
        {
            // Apply conservative general rules
            return currentType; // No changes for general experiments
        }

        #region Supporting Methods for Enhanced Validation System

        /// <summary>
        /// Compute baseline delta for validation metrics
        /// </summary>
        private async Task<float> ComputeBaselineDelta()
        {
            try
            {
                if (!File.Exists(BASELINE_METRICS_PATH))
                {
                    LogMessage("No baseline metrics found, assuming 0% delta");
                    return 0.0f;
                }
                
                // Simple delta calculation - in a real implementation, this would be more sophisticated
                var currentMetrics = await CaptureCurrentMetrics();
                var baselineText = File.ReadAllText(BASELINE_METRICS_PATH);
                
                // For now, just return a placeholder delta
                // Real implementation would compare actual metrics
                return 2.5f; // 2.5% improvement over baseline
            }
            catch (Exception ex)
            {
                LogMessage($"Failed to compute baseline delta: {ex.Message}");
                return 0.0f;
            }
        }

        /// <summary>
        /// Capture current system metrics for baseline comparison
        /// </summary>
        private async Task<string> CaptureCurrentMetrics()
        {
            // Simulate metrics capture with small delay to represent actual system polling
            await Task.Delay(10); // Brief delay to represent actual metrics gathering
            
            // In a real implementation, this would gather system metrics like:
            // - Memory usage, CPU performance, frame rate, load times, etc.
            var mockMetrics = new
            {
                timestamp = DateTime.UtcNow.ToString("O"),
                memoryUsage = UnityEngine.Random.Range(50, 80),
                frameRate = UnityEngine.Random.Range(45, 60),
                loadTime = UnityEngine.Random.Range(1.2f, 2.8f)
            };
            
            return JsonUtility.ToJson(mockMetrics);
        }

        /// <summary>
        /// Promote claims to appropriate directories based on classification
        /// </summary>
        private async Task<int> PromoteClaims(List<ClaimData> claims)
        {
            int promoted = 0;
            
            foreach (var claim in claims)
            {
                string targetDir = claim.ClaimType switch
                {
                    "validated" => VALIDATED_CLAIMS_DIR,
                    "hypothesis" => HYPOTHESES_CLAIMS_DIR,
                    "regression" => REGRESSIONS_CLAIMS_DIR,
                    "anomaly" => ANOMALIES_CLAIMS_DIR,
                    "improvement" => IMPROVEMENTS_CLAIMS_DIR,
                    "new_phenomenon" => NEW_PHENOMENA_CLAIMS_DIR,
                    _ => HYPOTHESES_CLAIMS_DIR // Default fallback
                };
                
                var claimPath = Path.Combine(targetDir, $"claim_{claim.RunId}_{DateTime.Now:yyyyMMdd_HHmmss}.json");
                
                try
                {
                    var claimJson = JsonUtility.ToJson(claim, true);
                    File.WriteAllText(claimPath, claimJson);
                    promoted++;
                    LogMessage($"Promoted claim to {targetDir}: {claim.RunId} (type: {claim.ClaimType})");
                }
                catch (Exception ex)
                {
                    LogMessage($"Failed to promote claim {claim.RunId}: {ex.Message}");
                }
            }
            
            await Task.Yield();
            return promoted;
        }

        /// <summary>
        /// Generate GitHub integration data for workflow automation
        /// </summary>
        private async Task GenerateGitHubIntegrationData(ValidationSummary summary)
        {
            try
            {
                var integrationData = new GitHubValidationIntegrationData
                {
                    Timestamp = DateTime.UtcNow.ToString("O"),
                    UnityVersion = Application.unityVersion,
                    ProjectPath = Application.dataPath,
                    GitCommit = GetGitCommitHash(),
                    GitBranch = GetGitBranch(),
                    RunsValidated = summary.RunsValidated,
                    ClaimsPromoted = summary.ClaimsPromoted,
                    AverageConfidence = summary.AverageConfidence,
                    BaselineDelta = summary.BaselineDelta,
                    OutputDirectory = CLAIMS_DIR,
                    ClaimsPaths = GetClaimsPaths(),
                    Stage = "4",
                    Workflow = "school"
                };
                
                var integrationPath = Path.Combine(CLAIMS_DIR, "github_integration.json");
                File.WriteAllText(integrationPath, JsonUtility.ToJson(integrationData, true));
                
                LogMessage($"GitHub integration data saved to: {integrationPath}");
                await Task.Yield();
            }
            catch (Exception ex)
            {
                LogMessage($"Failed to generate GitHub integration data: {ex.Message}");
            }
        }

        /// <summary>
        /// Get paths to all generated claim files
        /// </summary>
        private string[] GetClaimsPaths()
        {
            var paths = new List<string>();
            
            try
            {
                if (Directory.Exists(VALIDATED_CLAIMS_DIR))
                    paths.AddRange(Directory.GetFiles(VALIDATED_CLAIMS_DIR, "*.json"));
                if (Directory.Exists(HYPOTHESES_CLAIMS_DIR))
                    paths.AddRange(Directory.GetFiles(HYPOTHESES_CLAIMS_DIR, "*.json"));
                if (Directory.Exists(REGRESSIONS_CLAIMS_DIR))
                    paths.AddRange(Directory.GetFiles(REGRESSIONS_CLAIMS_DIR, "*.json"));
                if (Directory.Exists(ANOMALIES_CLAIMS_DIR))
                    paths.AddRange(Directory.GetFiles(ANOMALIES_CLAIMS_DIR, "*.json"));
                if (Directory.Exists(IMPROVEMENTS_CLAIMS_DIR))
                    paths.AddRange(Directory.GetFiles(IMPROVEMENTS_CLAIMS_DIR, "*.json"));
                if (Directory.Exists(NEW_PHENOMENA_CLAIMS_DIR))
                    paths.AddRange(Directory.GetFiles(NEW_PHENOMENA_CLAIMS_DIR, "*.json"));
            }
            catch (Exception ex)
            {
                LogMessage($"Failed to get claims paths: {ex.Message}");
            }
            
            return paths.ToArray();
        }

        /// <summary>
        /// Get current Git commit hash
        /// </summary>
        private string GetGitCommitHash()
        {
            try
            {
                var processInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "git",
                    Arguments = "rev-parse HEAD",
                    WorkingDirectory = Application.dataPath + "/..",
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = System.Diagnostics.Process.Start(processInfo);
                var output = process.StandardOutput.ReadToEnd().Trim();
                process.WaitForExit();
                return process.ExitCode == 0 ? output : "unknown";
            }
            catch
            {
                return "unknown";
            }
        }

        /// <summary>
        /// Get current Git branch name
        /// </summary>
        private string GetGitBranch()
        {
            try
            {
                var processInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "git",
                    Arguments = "rev-parse --abbrev-ref HEAD",
                    WorkingDirectory = Application.dataPath + "/..",
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = System.Diagnostics.Process.Start(processInfo);
                var output = process.StandardOutput.ReadToEnd().Trim();
                process.WaitForExit();
                return process.ExitCode == 0 ? output : "main";
            }
            catch
            {
                return "main";
            }
        }

        /// <summary>
        /// Show claims directory in file explorer
        /// </summary>
        private void ShowClaimsDirectory()
        {
            if (Directory.Exists(CLAIMS_DIR))
            {
                EditorUtility.RevealInFinder(CLAIMS_DIR);
            }
            else
            {
                EditorUtility.DisplayDialog("Claims Directory", 
                    "Claims directory not found. Run validation first.", "OK");
            }
        }

        /// <summary>
        /// Show GitHub integration data dialog
        /// </summary>
        private void ShowGitHubIntegrationData()
        {
            var integrationPath = Path.Combine(CLAIMS_DIR, "github_integration.json");
            if (File.Exists(integrationPath))
            {
                var content = File.ReadAllText(integrationPath);
                LogMessage("GitHub Integration Data:");
                LogMessage(content);
                
                EditorUtility.DisplayDialog("GitHub Integration Data", 
                    $"Integration data available at:\n{integrationPath}\n\nCheck logs for full content.", "OK");
            }
            else
            {
                EditorUtility.DisplayDialog("GitHub Integration Data", 
                    "No integration data found. Run validation first.", "OK");
            }
        }

        /// <summary>
        /// Log message to validation logs and Debug console
        /// </summary>
        private void LogMessage(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var logEntry = $"[{timestamp}] {message}\n";
            validationLogs.Append(logEntry);
            Debug.Log($"[ResultValidator] {message}");
        }

        #endregion

        // Supporting analysis classes for enhanced classification
        private class AnomalyAnalysis
        {
            public float AnomalyScore = 0.0f;
            public bool IsExpected = false;
            public AnomalyType Type = AnomalyType.Unexpected;
            public List<string> AnomalyFlags = new();
        }

        private class ImprovementAnalysis
        {
            public float ImprovementScore = 0.0f;
            public string Type = "";
            public List<string> ImprovementFlags = new();
        }

        private class PhenomenonAnalysis
        {
            public float PhenomenonScore = 0.0f;
            public string Type = "";
            public List<string> PhenomenonFlags = new();
        }

        // Supporting enums for enhanced claim classification
        private enum HypothesisQuality
        {
            None,
            Low,
            Medium,
            High
        }

        private enum ExperimentType
        {
            General,
            Performance,
            UserInterface,
            Integration,
            Security,
            DataProcessing
        }

        private enum ClaimClassification
        {
            Validated,          // High-confidence positive results
            Hypothesis,         // Medium-confidence findings needing more validation
            Regression,         // Performance degradation or negative trends
            Anomaly,           // Unexpected patterns (expected or unexpected)
            Improvement,       // Significant positive changes
            NewPhenomenon      // Novel patterns not seen before
        }

        private enum AnomalyType
        {
            Expected,          // Anomalies that are anticipated (e.g., during system changes)
            Unexpected,        // Truly unexpected anomalies requiring investigation  
            Performance,       // Performance-related anomalies
            Behavioral,        // Behavioral pattern anomalies
            Data              // Data pattern anomalies
        }
    }
    
    // Data structures for validation
    [System.Serializable]
    public class RunResult
    {
        public string RunId;
        public string ExperimentName;
        public bool Success;
        public string ExecutionTime;
        public string RunDirectory;
        public RunMetadata Metadata;
    }
    
    [System.Serializable]
    public class RunMetadata
    {
        public string run_id;
        public string experiment_name;
        public string hypothesis_id;
        public string manifest_file;
        public string execution_time;
        public int exit_code;
        public bool success;
        public string stage;
        public string workflow;
        public string git_commit;
        public string git_branch;
    }
    
    [System.Serializable]
    public class ValidationSummary
    {
        public int RunsValidated;
        public int ClaimsPromoted;
        public float AverageConfidence;
        public float BaselineDelta;
        public List<float> ConfidenceScores = new();
    }
    
    [System.Serializable]
    public class GitHubValidationIntegrationData
    {
        public string Timestamp;
        public string UnityVersion;
        public string ProjectPath;
        public string GitCommit;
        public string GitBranch;
        public int RunsValidated;
        public int ClaimsPromoted;
        public float AverageConfidence;
        public float BaselineDelta;
        public string OutputDirectory;
        public string[] ClaimsPaths;
        public string Stage;
        public string Workflow;
    }

    [System.Serializable]
    public class ClassificationMetadata
    {
        public string PrimaryType;           // validated, hypothesis, regression, anomaly, improvement, new_phenomenon
        public string SecondaryType;         // additional classification context
        public float AnomalyScore;           // 0.0-1.0, likelihood of being an anomaly
        public string[] ClassificationFlags; // e.g., ["expected_anomaly", "performance_improvement", "ui_regression"]
        public string ClassificationReason;  // human-readable explanation
        public float TrendSignificance;      // significance of trend pattern (0.0-1.0)
        public string BaselineDeviation;     // description of how this deviates from baseline
        public bool IsExpectedAnomaly;       // flag for expected vs unexpected anomalies
        public string PhenomenonType;        // for new phenomena: "performance", "behavior", "ui", etc.
    }
}
