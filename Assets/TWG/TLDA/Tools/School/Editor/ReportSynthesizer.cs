using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Linq;
using UnityEngine;
using UnityEditor;
using System.Text;
using UnityEngine.Networking;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Unity Editor window for School experiment report synthesis
    /// KeeperNote: Stage 5 - Report synthesis & actionable intel with Unity 6 & GH integration
    /// </summary>
    public class ReportSynthesizer : EditorWindow
    {
        private Vector2 scrollPosition;
        private List<ClaimData> loadedClaims;
        private bool isGenerating = false;
        private string generationProgress = "";
        private DateTime lastGenerationTime;
        private ReportMetadata lastReportMetadata;
        private bool showLogs = false;
        private readonly StringBuilder generationLogs = new();
        private bool enableGitHubIntegration = false;
        private string gitHubToken = "";
        private string targetRepository = "";
        
        // Paths and settings
        private const string CLAIMS_DIR = "assets/experiments/school/claims/";
        private const string VALIDATED_CLAIMS_DIR = "assets/experiments/school/claims/validated/";
        private const string HYPOTHESES_CLAIMS_DIR = "assets/experiments/school/claims/hypotheses/";
        private const string REGRESSIONS_CLAIMS_DIR = "assets/experiments/school/claims/regressions/";
        private const string ANOMALIES_CLAIMS_DIR = "assets/experiments/school/claims/anomalies/";
        private const string IMPROVEMENTS_CLAIMS_DIR = "assets/experiments/school/claims/improvements/";
        private const string NEW_PHENOMENA_CLAIMS_DIR = "assets/experiments/school/claims/new_phenomena/";
        private const string REPORTS_DIR = "assets/experiments/school/reports/";
        private const string GITHUB_INTEGRATION_PATH = "assets/experiments/school/claims/github_integration.json";
        
        [MenuItem("Tools/School/Build Report")]
        public static void ShowWindow()
        {
            var window = GetWindow<ReportSynthesizer>("Report Synthesizer");
            window.minSize = new Vector2(700, 900);
            window.Show();
        }
        
        private void OnEnable()
        {
            LoadValidatedClaims();
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            // Header
            EditorGUILayout.Space(10);
            var titleStyle = new GUIStyle(EditorStyles.boldLabel) { fontSize = 16 };
            EditorGUILayout.LabelField("🧙‍♂️ School Experiment Report Synthesizer", titleStyle);
            EditorGUILayout.LabelField("Stage 5: Generate actionable intelligence reports from validated claims", EditorStyles.helpBox);
            EditorGUILayout.Space(10);
            
            // Claims loading section
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("📋 Claims Data", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("🔄 Refresh Claims", GUILayout.Width(150)))
            {
                LoadValidatedClaims();
            }
            
            if (loadedClaims != null)
            {
                EditorGUILayout.LabelField($"Loaded {loadedClaims.Count} claims");
            }
            else
            {
                EditorGUILayout.LabelField("No claims loaded", EditorStyles.helpBox);
            }
            EditorGUILayout.EndHorizontal();
            
            if (loadedClaims != null && loadedClaims.Count > 0)
            {
                // Claims summary with enhanced categories
                var validated = loadedClaims.Where(c => c.ClaimType == "validated").Count();
                var hypotheses = loadedClaims.Where(c => c.ClaimType == "hypothesis").Count();
                var regressions = loadedClaims.Where(c => c.ClaimType == "regression").Count();
                var anomalies = loadedClaims.Where(c => c.ClaimType == "anomaly").Count();
                var improvements = loadedClaims.Where(c => c.ClaimType == "improvement").Count();
                var newPhenomena = loadedClaims.Where(c => c.ClaimType == "new_phenomenon").Count();
                var avgConfidence = loadedClaims.Average(c => c.ConfidenceScore);
                
                EditorGUILayout.LabelField($"✅ Validated: {validated} | 🔬 Hypotheses: {hypotheses} | ⚠️ Regressions: {regressions}");
                EditorGUILayout.LabelField($"🔍 Anomalies: {anomalies} | 📈 Improvements: {improvements} | 🆕 New Phenomena: {newPhenomena}");
                EditorGUILayout.LabelField($"📊 Average Confidence: {avgConfidence:F2}");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
            
            // Report generation section
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("📄 Report Generation", EditorStyles.boldLabel);
            
            EditorGUI.BeginDisabledGroup(isGenerating || loadedClaims == null || loadedClaims.Count == 0);
            
            if (GUILayout.Button("🚀 Generate Report", GUILayout.Height(30)))
            {
                _ = GenerateReport();
            }
            
            EditorGUI.EndDisabledGroup();
            
            if (isGenerating)
            {
                EditorGUILayout.LabelField("⚡ Generating...", EditorStyles.helpBox);
                EditorGUILayout.LabelField(generationProgress);
                
                // Progress indicator
                var rect = EditorGUILayout.GetControlRect();
                EditorGUI.ProgressBar(rect, 0.5f, "Building Report...");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
            
            // GitHub Integration section
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("🐙 GitHub Integration (Optional)", EditorStyles.boldLabel);
            
            enableGitHubIntegration = EditorGUILayout.Toggle("Enable GitHub Integration", enableGitHubIntegration);
            
            if (enableGitHubIntegration)
            {
                EditorGUILayout.LabelField("⚠️ GitHub integration requires valid token and repository", EditorStyles.helpBox);
                gitHubToken = EditorGUILayout.PasswordField("GitHub Token:", gitHubToken);
                targetRepository = EditorGUILayout.TextField("Target Repository:", targetRepository);
                EditorGUILayout.LabelField("Format: owner/repository (e.g., jmeyer1980/TWG-TLDA)", EditorStyles.miniLabel);
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
            
            // Results section
            if (lastReportMetadata != null)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.LabelField("📊 Last Report Generation", EditorStyles.boldLabel);
                
                EditorGUILayout.LabelField($"🕒 Generated: {lastGenerationTime:yyyy-MM-dd HH:mm:ss}");
                EditorGUILayout.LabelField($"📁 Report Path: {lastReportMetadata.ReportPath}");
                EditorGUILayout.LabelField($"📋 Claims Processed: {lastReportMetadata.ClaimsProcessed}");
                EditorGUILayout.LabelField($"⭐ Avg Confidence: {lastReportMetadata.AverageConfidence:F2}");
                
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("📂 Open Report", GUILayout.Width(120)))
                {
                    if (File.Exists(lastReportMetadata.ReportPath))
                    {
                        Application.OpenURL("file://" + Path.GetFullPath(lastReportMetadata.ReportPath));
                    }
                    else
                    {
                        LogMessage("❌ Report file not found");
                    }
                }
                
                if (GUILayout.Button("📂 Open Reports Folder", GUILayout.Width(150)))
                {
                    var reportsPath = Path.GetFullPath(REPORTS_DIR);
                    if (Directory.Exists(reportsPath))
                    {
                        EditorUtility.RevealInFinder(reportsPath);
                    }
                    else
                    {
                        LogMessage("❌ Reports directory not found");
                    }
                }
                EditorGUILayout.EndHorizontal();
                
                EditorGUILayout.EndVertical();
                EditorGUILayout.Space(10);
            }
            
            // Logs section
            showLogs = EditorGUILayout.Foldout(showLogs, "📝 Generation Logs");
            if (showLogs)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                var logContent = generationLogs.ToString();
                if (string.IsNullOrEmpty(logContent))
                {
                    EditorGUILayout.LabelField("No logs available", EditorStyles.centeredGreyMiniLabel);
                }
                else
                {
                    EditorGUILayout.TextArea(logContent, GUILayout.MaxHeight(200));
                }
                
                if (GUILayout.Button("Clear Logs", GUILayout.Width(100)))
                {
                    generationLogs.Clear();
                }
                EditorGUILayout.EndVertical();
            }
            
            EditorGUILayout.EndScrollView();
        }
        
        private void LoadValidatedClaims()
        {
            loadedClaims = new List<ClaimData>();
            generationProgress = "Loading claims...";
            
            try
            {
                LoadClaimsFromDirectory(VALIDATED_CLAIMS_DIR);
                LoadClaimsFromDirectory(HYPOTHESES_CLAIMS_DIR);
                LoadClaimsFromDirectory(REGRESSIONS_CLAIMS_DIR);
                LoadClaimsFromDirectory(ANOMALIES_CLAIMS_DIR);
                LoadClaimsFromDirectory(IMPROVEMENTS_CLAIMS_DIR);
                LoadClaimsFromDirectory(NEW_PHENOMENA_CLAIMS_DIR);
                
                LogMessage($"🧙‍♂️ Loaded {loadedClaims.Count} claims from all categories");
                generationProgress = $"Loaded {loadedClaims.Count} claims";
            }
            catch (Exception ex)
            {
                LogMessage($"❌ Failed to load claims: {ex.Message}");
                generationProgress = "Failed to load claims";
            }
        }
        
        private void LoadClaimsFromDirectory(string directory)
        {
            if (!Directory.Exists(directory)) return;
            
            var claimFiles = Directory.GetFiles(directory, "*.json");
            foreach (var file in claimFiles)
            {
                try
                {
                    var json = File.ReadAllText(file);
                    var claim = JsonUtility.FromJson<ClaimData>(json);
                    if (claim != null)
                    {
                        loadedClaims.Add(claim);
                    }
                }
                catch (Exception ex)
                {
                    LogMessage($"⚠️ Failed to parse claim file {file}: {ex.Message}");
                }
            }
        }
        
        private async Task GenerateReport()
        {
            isGenerating = true;
            generationProgress = "Initializing report generation...";
            
            try
            {
                LogMessage("🚀 Starting report generation...");
                
                // Ensure reports directory exists
                Directory.CreateDirectory(REPORTS_DIR);
                
                // Generate report content
                var reportContent = GenerateMarkdownReport();
                
                // Save report
                var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                var reportFileName = $"school_experiment_report_{timestamp}.md";
                var reportPath = Path.Combine(REPORTS_DIR, reportFileName);

                await File.WriteAllTextAsync(reportPath, reportContent);
                
                // Also generate HTML version
                var htmlContent = ConvertMarkdownToHTML(reportContent);
                var htmlFileName = $"school_experiment_report_{timestamp}.html";
                var htmlPath = Path.Combine(REPORTS_DIR, htmlFileName);
                await File.WriteAllTextAsync(htmlPath, htmlContent);
                
                // Create metadata
                lastReportMetadata = new ReportMetadata
                {
                    ReportPath = reportPath,
                    ClaimsProcessed = loadedClaims.Count,
                    AverageConfidence = loadedClaims.Average(c => c.ConfidenceScore),
                    GenerationTime = DateTime.Now
                };
                
                lastGenerationTime = DateTime.Now;
                
                LogMessage($"✅ Report generated successfully: {reportPath}");
                
                // Optional GitHub integration
                if (enableGitHubIntegration && !string.IsNullOrEmpty(gitHubToken) && !string.IsNullOrEmpty(targetRepository))
                {
                    await PushToGitHub(reportContent, reportFileName);
                }
                
                generationProgress = "Report generation completed!";
            }
            catch (Exception ex)
            {
                LogMessage($"❌ Report generation failed: {ex.Message}");
                generationProgress = "Report generation failed";
            }
            finally
            {
                isGenerating = false;
            }
        }
        
        private string GenerateMarkdownReport()
        {
            var report = new StringBuilder();
            var timestamp = DateTime.Now;
            
            // Report header
            report.AppendLine("# School Experiment Report");
            report.AppendLine($"**Generated:** {timestamp:yyyy-MM-dd HH:mm:ss}");
            report.AppendLine($"**Total Claims:** {loadedClaims.Count}");
            report.AppendLine();
            
            // Summary section
            var validated = loadedClaims.Where(c => c.ClaimType == "validated").ToList();
            var hypotheses = loadedClaims.Where(c => c.ClaimType == "hypothesis").ToList();
            var regressions = loadedClaims.Where(c => c.ClaimType == "regression").ToList();
            var avgConfidence = loadedClaims.Average(c => c.ConfidenceScore);
            
            report.AppendLine("## Executive Summary");
            report.AppendLine();
            report.AppendLine($"- ✅ **Validated Claims:** {validated.Count}");
            report.AppendLine($"- 🔬 **Hypotheses:** {hypotheses.Count}");
            report.AppendLine($"- ⚠️ **Regressions:** {regressions.Count}");
            report.AppendLine($"- 📊 **Average Confidence:** {avgConfidence:F1}%");
            report.AppendLine();
            
            // Validated claims (highest priority)
            if (validated.Any())
            {
                report.AppendLine("## ✅ Validated Claims (Ready for Action)");
                report.AppendLine();
                GenerateClaimsSection(report, validated, "These claims have high confidence scores and are recommended for immediate implementation.");
            }
            
            // Hypotheses (medium priority)
            if (hypotheses.Any())
            {
                report.AppendLine("## 🔬 Hypotheses (Further Investigation Needed)");
                report.AppendLine();
                GenerateClaimsSection(report, hypotheses, "These findings show promise but require additional validation before implementation.");
            }
            
            // Regressions (attention required)
            if (regressions.Any())
            {
                report.AppendLine("## ⚠️ Regressions (Attention Required)");
                report.AppendLine();
                GenerateClaimsSection(report, regressions, "These areas show potential performance degradation and should be investigated.");
            }
            
            // GitHub integration metadata
            if (File.Exists(GITHUB_INTEGRATION_PATH))
            {
                try
                {
                    var integrationData = File.ReadAllText(GITHUB_INTEGRATION_PATH);
                    var integration = JsonUtility.FromJson<GitHubIntegrationData>(integrationData);
                    
                    report.AppendLine("## 🔗 Integration Metadata");
                    report.AppendLine();
                    report.AppendLine($"- **Unity Version:** {integration.UnityVersion}");
                    report.AppendLine($"- **Git Commit:** {integration.GitCommit}");
                    report.AppendLine($"- **Git Branch:** {integration.GitBranch}");
                    report.AppendLine($"- **Baseline Delta:** {integration.BaselineDelta}%");
                    report.AppendLine();
                }
                catch (Exception ex)
                {
                    LogMessage($"⚠️ Failed to load GitHub integration data: {ex.Message}");
                }
            }
            
            report.AppendLine("---");
            report.AppendLine("*Generated by TWG Living Dev Agent - School Experiment Workflow Stage 5*");
            
            return report.ToString();
        }
        
        private void GenerateClaimsSection(StringBuilder report, List<ClaimData> claims, string description)
        {
            report.AppendLine(description);
            report.AppendLine();
            
            foreach (var claim in claims.OrderByDescending(c => c.ConfidenceScore))
            {
                report.AppendLine($"### {claim.ExperimentName}");
                report.AppendLine();
                
                // What
                report.AppendLine($"**What:** {GetClaimDescription(claim)}");
                
                // Why
                report.AppendLine($"**Why:** {GetClaimRationale(claim)}");
                
                // Evidence links
                report.AppendLine($"**Evidence:** [Run {claim.RunId}](../outputs/runs/{claim.RunId}/) | Hypothesis: `{claim.HypothesisId}`");
                
                // Impact
                report.AppendLine($"**Impact:** {GetClaimImpact(claim)}");
                
                // Action
                report.AppendLine($"**Recommended Action:** {GetRecommendedAction(claim)}");
                
                // Confidence
                var confidenceBar = GenerateConfidenceBar(claim.ConfidenceScore);
                report.AppendLine($"**Confidence:** {claim.ConfidenceScore:F1}% {confidenceBar}");
                
                if (!string.IsNullOrEmpty(claim.BaselineComparison) && claim.BaselineComparison != "pending")
                {
                    report.AppendLine($"**Baseline Comparison:** {claim.BaselineComparison}");
                }
                
                report.AppendLine($"**Validation Time:** {claim.ValidationTime}");
                report.AppendLine();
            }
        }
        
        private string GetClaimDescription(ClaimData claim)
        {
            return claim.Success 
                ? $"Experiment '{claim.ExperimentName}' completed successfully with {claim.ConfidenceScore:F1}% confidence."
                : $"Experiment '{claim.ExperimentName}' identified potential issues requiring attention.";
        }
        
        private string GetClaimRationale(ClaimData claim)
        {
            return claim.ClaimType switch
            {
                "validated" => "High confidence score indicates reliable findings that can guide development decisions.",
                "hypothesis" => "Moderate confidence suggests promising direction that warrants further investigation.",
                "regression" => "Low confidence or negative indicators suggest potential performance degradation.",
                "anomaly" => "Unusual patterns detected that deviate from expected behavior - requires analysis to determine if expected or concerning.",
                "improvement" => "Significant positive changes detected that represent measurable enhancements to the system.",
                "new_phenomenon" => "Novel patterns or behaviors identified that haven't been observed before - potential breakthrough discovery.",
                _ => "Experimental findings provide insights into development opportunities."
            };
        }
        
        private string GetClaimImpact(ClaimData claim)
        {
            var impact = claim.ConfidenceScore switch
            {
                >= 0.8f => "High impact - significant improvement opportunity",
                >= 0.6f => "Medium impact - notable optimization potential", 
                >= 0.4f => "Low impact - minor enhancement possibility",
                _ => "Minimal impact - investigation or mitigation needed"
            };
            
            return claim.Success ? impact : "Potential negative impact - requires investigation";
        }
        
        private string GetRecommendedAction(ClaimData claim)
        {
            return claim.ClaimType switch
            {
                "validated" when claim.Success => "Implement changes based on validated findings. Proceed with development.",
                "hypothesis" when claim.Success => "Conduct additional experiments to increase confidence before implementation.",
                "regression" => "Investigate root cause and implement fixes to prevent performance degradation.",
                "anomaly" => claim.Classification?.IsExpectedAnomaly == true 
                    ? "Monitor expected anomaly patterns and ensure they align with anticipated behavior." 
                    : "Investigate unexpected anomaly to determine cause and potential impact.",
                "improvement" => "Document improvement patterns and consider applying similar optimizations elsewhere.",
                "new_phenomenon" => "Study new phenomenon thoroughly - potential breakthrough that merits deeper investigation and documentation.",
                _ => "Review experimental results and determine if additional validation is needed."
            };
        }
        
        private string GenerateConfidenceBar(float confidence)
        {
            var percentage = (int)(confidence * 100);
            var filled = percentage / 10;
            var empty = 10 - filled;
            
            return $"[{'█'.ToString().PadLeft(filled, '█')}{'░'.ToString().PadLeft(empty, '░')}] {percentage}%";
        }
        
        private string ConvertMarkdownToHTML(string markdown)
        {
            // Simple markdown to HTML conversion
            var html = new StringBuilder();
            
            html.AppendLine("<!DOCTYPE html>");
            html.AppendLine("<html><head>");
            html.AppendLine("<title>School Experiment Report</title>");
            html.AppendLine("<style>");
            html.AppendLine("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }");
            html.AppendLine("h1, h2, h3 { color: #333; } h1 { border-bottom: 2px solid #007acc; } h2 { border-bottom: 1px solid #ddd; }");
            html.AppendLine("pre, code { background: #f8f8f8; padding: 10px; border-radius: 4px; }");
            html.AppendLine(".confidence-bar { font-family: monospace; background: #f0f0f0; padding: 2px 4px; border-radius: 2px; }");
            html.AppendLine(".emoji { font-size: 1.2em; }");
            html.AppendLine("</style>");
            html.AppendLine("</head><body>");
            
            // Convert markdown content to HTML
            var lines = markdown.Split('\n');
            foreach (var line in lines)
            {
                var htmlLine = line
                    .Replace("# ", "<h1>").Replace("## ", "<h2>").Replace("### ", "<h3>")
                    .Replace("**", "<strong>").Replace("*", "<em>")
                    .Replace("[█", "<span class='confidence-bar'>[█")
                    .Replace("]", "]</span>");
                
                if (htmlLine.StartsWith("<h1>") || htmlLine.StartsWith("<h2>") || htmlLine.StartsWith("<h3>"))
                {
                    html.AppendLine(htmlLine + (htmlLine.StartsWith("<h1>") ? "</h1>" : htmlLine.StartsWith("<h2>") ? "</h2>" : "</h3>"));
                }
                else if (string.IsNullOrWhiteSpace(htmlLine))
                {
                    html.AppendLine("<br>");
                }
                else
                {
                    html.AppendLine("<p>" + htmlLine + "</p>");
                }
            }
            
            html.AppendLine("</body></html>");
            return html.ToString();
        }
        
        private async Task PushToGitHub(string reportContent, string fileName)
        {
            try
            {
                LogMessage("🐙 Attempting GitHub integration...");
                
                if (string.IsNullOrEmpty(gitHubToken))
                {
                    LogMessage("❌ GitHub token not provided");
                    return;
                }
                
                if (string.IsNullOrEmpty(targetRepository))
                {
                    LogMessage("❌ Target repository not specified");
                    return;
                }
                
                // Validate repository format (owner/repo)
                if (!targetRepository.Contains("/") || targetRepository.Split('/').Length != 2)
                {
                    LogMessage("❌ Invalid repository format. Use: owner/repository");
                    return;
                }
                
                // Create GitHub issue with the report
                var apiUrl = $"https://api.github.com/repos/{targetRepository}/issues";
                
                // Prepare issue data - NOW USING THE FILENAME!
                var issueTitle = $"School Experiment Report - {DateTime.Now:yyyy-MM-dd HH:mm} ({fileName})";
                var issueBody = FormatReportForGitHub(reportContent, fileName);
                
                // Create JSON payload manually since Unity's JsonUtility has limitations
                var jsonPayload = CreateGitHubIssueJson(issueTitle, issueBody);
                var jsonBytes = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
                
                LogMessage($"📤 Creating GitHub issue at: {apiUrl}");
                LogMessage($"📄 Issue title: {issueTitle}");
                LogMessage($"📁 Report file: {fileName}");

                using var request = new UnityWebRequest(apiUrl, "POST");
                request.uploadHandler = new UploadHandlerRaw(jsonBytes);
                request.downloadHandler = new DownloadHandlerBuffer();

                // Set required headers
                request.SetRequestHeader("Authorization", $"Bearer {gitHubToken}");
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("Accept", "application/vnd.github.v3+json");
                request.SetRequestHeader("User-Agent", "Unity-School-Experiment-Reporter/1.0");

                // Send request and wait for completion
                var operation = request.SendWebRequest();

                // Wait for completion with progress updates
                while (!operation.isDone)
                {
                    await Task.Delay(100);
                    // Update progress to keep UI responsive
                    if (isGenerating)
                    {
                        generationProgress = $"Uploading to GitHub... {(operation.progress * 100):F0}%";
                        Repaint();
                    }
                }

                // Handle response
                if (request.result == UnityWebRequest.Result.Success)
                {
                    LogMessage("✅ GitHub issue created successfully");

                    // Parse response to get issue details
                    try
                    {
                        var responseText = request.downloadHandler.text;
                        var issueUrl = ExtractIssueUrlFromResponse(responseText);
                        var issueNumber = ExtractIssueNumberFromResponse(responseText);

                        if (!string.IsNullOrEmpty(issueUrl))
                        {
                            LogMessage($"🔗 Issue created: {issueUrl}");
                            LogMessage($"📋 Issue number: #{issueNumber}");
                            LogMessage($"📁 Report source: {fileName}");

                            // Optional: Open the issue in browser
                            if (EditorUtility.DisplayDialog("GitHub Issue Created",
                                $"Successfully created GitHub issue #{issueNumber}\nReport: {fileName}\n\nWould you like to open it in your browser?",
                                "Open Issue", "Close"))
                            {
                                Application.OpenURL(issueUrl);
                            }
                        }
                        else
                        {
                            LogMessage("✅ Issue created but couldn't extract URL from response");
                        }
                    }
                    catch (Exception parseEx)
                    {
                        LogMessage($"⚠️ Issue created but response parsing failed: {parseEx.Message}");
                    }
                }
                else
                {
                    // Handle various error types
                    var errorMsg = request.error ?? "Unknown error";
                    var responseCode = request.responseCode;
                    var responseText = request.downloadHandler?.text ?? "";

                    LogMessage($"❌ GitHub API error ({responseCode}): {errorMsg}");

                    // Provide specific guidance based on error code
                    if (responseCode == 401)
                    {
                        LogMessage("🔑 Authentication failed. Check your GitHub token permissions.");
                        LogMessage("💡 Token needs 'repo' scope for private repos or 'public_repo' for public repos.");
                    }
                    else if (responseCode == 404)
                    {
                        LogMessage("🔍 Repository not found. Check repository name and token permissions.");
                    }
                    else if (responseCode == 422)
                    {
                        LogMessage("📝 Invalid request data. Check issue content format.");
                    }
                    else if (responseCode == 403)
                    {
                        LogMessage("🚫 Forbidden. Check token permissions and repository access.");
                    }

                    if (!string.IsNullOrEmpty(responseText))
                    {
                        LogMessage($"📄 Response details: {responseText}");
                    }
                }
            }
            catch (Exception ex)
            {
                LogMessage($"❌ GitHub integration failed: {ex.Message}");
                LogMessage($"🔧 Stack trace: {ex.StackTrace}");
            }
        }
        
        private string FormatReportForGitHub(string markdownReport, string fileName)
        {
            var formatted = new StringBuilder();
            
            formatted.AppendLine("## 🧙‍♂️ Automated School Experiment Report");
            formatted.AppendLine();
            formatted.AppendLine("*This issue was automatically generated by the School Experiment Workflow Stage 5 - Report Synthesizer*");
            formatted.AppendLine();
            formatted.AppendLine($"**📁 Report File:** `{fileName}`");
            formatted.AppendLine($"**🕒 Generated:** {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC");
            formatted.AppendLine();
            formatted.AppendLine("---");
            formatted.AppendLine();
            
            // Add the full report as a collapsible section to keep the issue clean
            formatted.AppendLine("<details>");
            formatted.AppendLine("<summary>📊 Full Experiment Report (Click to expand)</summary>");
            formatted.AppendLine();
            formatted.AppendLine("```markdown");
            formatted.AppendLine(markdownReport);
            formatted.AppendLine("```");
            formatted.AppendLine();
            formatted.AppendLine("</details>");
            formatted.AppendLine();
            
            // Add summary section for quick viewing
            if (lastReportMetadata != null)
            {
                formatted.AppendLine("## 📋 Quick Summary");
                formatted.AppendLine();
                formatted.AppendLine($"- **Claims Processed**: {lastReportMetadata.ClaimsProcessed}");
                formatted.AppendLine($"- **Average Confidence**: {lastReportMetadata.AverageConfidence:F1}%");
                formatted.AppendLine($"- **Generated**: {lastReportMetadata.GenerationTime:yyyy-MM-dd HH:mm:ss} UTC");
                formatted.AppendLine($"- **Source File**: `{fileName}`");
                formatted.AppendLine();
            }
            
            formatted.AppendLine("## 🎯 Next Steps");
            formatted.AppendLine();
            formatted.AppendLine("1. Review the validated claims for immediate implementation opportunities");
            formatted.AppendLine("2. Investigate any regressions identified in the report");
            formatted.AppendLine("3. Plan additional experiments for hypotheses requiring further validation");
            formatted.AppendLine("4. Update baseline metrics based on validated improvements");
            formatted.AppendLine();
            
            formatted.AppendLine("## 📁 Report Details");
            formatted.AppendLine();
            formatted.AppendLine($"- **Local File**: `{fileName}`");
            formatted.AppendLine($"- **Report Directory**: `{REPORTS_DIR}`");
            formatted.AppendLine($"- **Generated by**: Unity School Experiment Workflow Stage 5");
            formatted.AppendLine();
            
            formatted.AppendLine("---");
            formatted.AppendLine("*Generated by TWG Living Dev Agent - Unity School Experiment Workflow*");
            
            return formatted.ToString();
        }
        
        private string CreateGitHubIssueJson(string title, string body)
        {
            // Manually create JSON since Unity's JsonUtility doesn't handle arrays well
            var escapedTitle = EscapeJsonString(title);
            var escapedBody = EscapeJsonString(body);
            
            return $@"{{
    ""title"": ""{escapedTitle}"",
    ""body"": ""{escapedBody}"",
    ""labels"": [""experiment-report"", ""automated"", ""school-workflow"", ""unity""]
}}";
        }
        
        private string EscapeJsonString(string str)
        {
            if (string.IsNullOrEmpty(str))
                return "";
            
            return str
                .Replace("\\", "\\\\")  // Escape backslashes first
                .Replace("\"", "\\\"")  // Escape quotes
                .Replace("\r", "\\r")   // Escape carriage returns
                .Replace("\n", "\\n")   // Escape newlines
                .Replace("\t", "\\t");  // Escape tabs
        }
        
        private string ExtractIssueUrlFromResponse(string responseJson)
        {
            try
            {
                // Simple extraction - look for html_url field
                var htmlUrlStart = responseJson.IndexOf("\"html_url\":\"");
                if (htmlUrlStart == -1) return null;
                
                htmlUrlStart += 12; // Length of "\"html_url\":\""
                var htmlUrlEnd = responseJson.IndexOf("\"", htmlUrlStart);
                if (htmlUrlEnd == -1) return null;
                
                return responseJson[ htmlUrlStart..htmlUrlEnd ];
            }
            catch
            {
                return null;
            }
        }
        
        private string ExtractIssueNumberFromResponse(string responseJson)
        {
            try
            {
                // Simple extraction - look for number field
                var numberStart = responseJson.IndexOf("\"number\":");
                if (numberStart == -1) return "unknown";
                
                numberStart += 9; // Length of "\"number\":":
                var numberEnd = responseJson.IndexOf(",", numberStart);
                if (numberEnd == -1) numberEnd = responseJson.IndexOf("}", numberStart);
                if (numberEnd == -1) return "unknown";
                
                return responseJson[ numberStart..numberEnd ].Trim();
            }
            catch
            {
                return "unknown";
            }
        }
        
        private void LogMessage(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var logEntry = $"[{timestamp}] {message}";
            generationLogs.AppendLine(logEntry);
            Debug.Log($"[ReportSynthesizer] {message}");
        }
        
        /// <summary>
        /// CLI entry point for automated report generation
        /// Usage: Unity -batchmode -executeMethod TWG.TLDA.School.Editor.ReportSynthesizer.GenerateReportCLI
        /// </summary>
        public static void GenerateReportCLI()
        {
            Debug.Log("[ReportSynthesizer] Starting CLI report generation...");
            
            try
            {
                var synthesizer = CreateInstance<ReportSynthesizer>();
                synthesizer.LoadValidatedClaims();
                
                if (synthesizer.loadedClaims == null || synthesizer.loadedClaims.Count == 0)
                {
                    Debug.LogWarning("[ReportSynthesizer] No claims found for report generation");
                    return;
                }
                
                // Generate report synchronously for CLI
                Directory.CreateDirectory(REPORTS_DIR);
                var reportContent = synthesizer.GenerateMarkdownReport();
                
                var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                var reportFileName = $"school_experiment_report_{timestamp}.md";
                var reportPath = Path.Combine(REPORTS_DIR, reportFileName);
                
                File.WriteAllText(reportPath, reportContent);
                
                Debug.Log($"[ReportSynthesizer] ✅ CLI report generated: {reportPath}");
                Debug.Log($"[ReportSynthesizer] 📊 Processed {synthesizer.loadedClaims.Count} claims");
                
                // Optional GitHub integration via command line args
                var args = System.Environment.GetCommandLineArgs();
                var githubToken = GetCommandLineArg(args, "-github-token");
                var githubRepo = GetCommandLineArg(args, "-github-repo");
                
                if (!string.IsNullOrEmpty(githubToken) && !string.IsNullOrEmpty(githubRepo))
                {
                    Debug.Log("[ReportSynthesizer] 🐙 GitHub integration detected in CLI mode");
                    // Note: Actual GitHub integration would be implemented here
                    Debug.Log($"[ReportSynthesizer] Target repository: {githubRepo}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ReportSynthesizer] ❌ CLI report generation failed: {ex.Message}");
            }
        }
        
        private static string GetCommandLineArg(string[] args, string argName)
        {
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == argName)
                {
                    return args[i + 1];
                }
            }
            return null;
        }
    }
    
    // Data structures
    [System.Serializable]
    public class ClaimData
    {
        public string RunId;
        public string ExperimentName;
        public string HypothesisId;
        public float ConfidenceScore;
        public string ClaimType;
        public string ValidationTime;
        public bool Success;
        public string BaselineComparison;
        
        // Enhanced classification metadata
        public ClassificationMetadata Classification;
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
    
    [System.Serializable]
    public class ReportMetadata
    {
        public string ReportPath;
        public int ClaimsProcessed;
        public float AverageConfidence;
        public DateTime GenerationTime;
    }
    
    [System.Serializable]
    public class GitHubIntegrationData
    {
        public string UnityVersion;
        public string GitCommit;
        public string GitBranch;
        public float BaselineDelta;
    }
}
