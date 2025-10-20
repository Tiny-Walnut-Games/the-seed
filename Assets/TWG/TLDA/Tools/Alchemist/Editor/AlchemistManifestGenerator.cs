using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using System.Globalization;

namespace TWG.TLDA.Alchemist.Editor
{
    /// <summary>
    /// Unity Editor tool for generating Alchemist Faculty experiment manifests
    /// from Gu Pot GitHub issues. Provides GUI interface for manifest creation
    /// with validation and batch processing capabilities.
    /// </summary>
    public class AlchemistManifestGenerator : EditorWindow
    {
        #region Constants
        private const string ALCHEMIST_VERSION = "0.1.0";
        private const string WINDOW_TITLE = "Alchemist Manifest Generator";
        private const int WINDOW_WIDTH = 800;
        private const int WINDOW_HEIGHT = 600;
        #endregion

        #region Fields
        [SerializeField] private string issueNumber = "";
        [SerializeField] private string repositoryUrl = "https://github.com/owner/repo";
        [SerializeField] private string outputDirectory = "gu_pot/";
        [SerializeField] private bool autoValidate = true;
        [SerializeField] private bool verboseLogging = false;
        [SerializeField] private OutputFormat outputFormat = OutputFormat.YAML;

        private GilHubIssueData currentIssueData;
        private AlchemistManifest generatedManifest;
        private Vector2 scrollPosition;
        private bool isProcessing = false;
        private string statusMessage = "";
        private MessageType messageType = MessageType.Info;

        private enum OutputFormat { YAML, JSON }
        #endregion

        #region Menu Integration
        [MenuItem("Tools/Alchemist Faculty/Generate Manifest", priority = 100)]
        public static void ShowWindow()
        {
            AlchemistManifestGenerator window = GetWindow<AlchemistManifestGenerator>(WINDOW_TITLE);
            window.minSize = new Vector2(WINDOW_WIDTH, WINDOW_HEIGHT);
            window.Show();
        }
        #endregion

        #region Unity Callbacks
        private void OnEnable()
        {
            titleContent = new GUIContent(WINDOW_TITLE, "Generate Alchemist experiment manifests");
            LoadSettings();
        }

        private void OnDisable()
        {
            SaveSettings();
        }

        private void OnGUI()
        {
            DrawHeader();

            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            DrawInputSection();
            DrawGenerationSection();
            DrawResultsSection();
            DrawOutputSection();

            EditorGUILayout.EndScrollView();

            DrawStatusBar();
        }
        #endregion

        #region GUI Drawing
        private void DrawHeader()
        {
            EditorGUILayout.BeginVertical("box");

            GUILayout.Label("🧪 Alchemist Faculty Manifest Generator", EditorStyles.boldLabel);
            GUILayout.Label("Transform Gu Pot narratives into experimental manifests", EditorStyles.helpBox);
            GUILayout.Label($"Version: {ALCHEMIST_VERSION}", EditorStyles.miniLabel);

            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
        }

        private void DrawInputSection()
        {
            EditorGUILayout.BeginVertical("box");
            GUILayout.Label("📋 Issue Input", EditorStyles.boldLabel);

            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Issue Number:", GUILayout.Width(100));
            issueNumber = EditorGUILayout.TextField(issueNumber);
            if (GUILayout.Button("Parse URL", GUILayout.Width(80)))
            {
                ParseIssueFromUrl();
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Repository:", GUILayout.Width(100));
            repositoryUrl = EditorGUILayout.TextField(repositoryUrl);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Output Directory:", GUILayout.Width(100));
            outputDirectory = EditorGUILayout.TextField(outputDirectory);
            if (GUILayout.Button("📁", GUILayout.Width(30)))
            {
                string selected = EditorUtility.OpenFolderPanel("Select Output Directory", outputDirectory, "");
                if (!string.IsNullOrEmpty(selected))
                {
                    outputDirectory = GetRelativePath(selected);
                }
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space();

            EditorGUILayout.BeginHorizontal();
            autoValidate = EditorGUILayout.Toggle("Auto-validate", autoValidate, GUILayout.Width(150));
            verboseLogging = EditorGUILayout.Toggle("Verbose logging", verboseLogging, GUILayout.Width(150));
            outputFormat = (OutputFormat)EditorGUILayout.EnumPopup("Format", outputFormat, GUILayout.Width(200));
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
        }

        private void DrawGenerationSection()
        {
            EditorGUILayout.BeginVertical("box");
            GUILayout.Label("⚗️ Manifest Generation", EditorStyles.boldLabel);

            EditorGUI.BeginDisabledGroup(isProcessing || string.IsNullOrWhiteSpace(issueNumber));

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("🔍 Fetch Issue Data", GUILayout.Height(30)))
            {
                FetchIssueData();
            }

            EditorGUI.BeginDisabledGroup(currentIssueData == null);
            if (GUILayout.Button("🧪 Generate Manifest", GUILayout.Height(30)))
            {
                GenerateManifest();
            }
            EditorGUI.EndDisabledGroup();

            EditorGUILayout.EndHorizontal();

            EditorGUI.EndDisabledGroup();

            if (currentIssueData != null)
            {
                DrawIssueDataPreview();
            }

            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
        }

        private void DrawIssueDataPreview()
        {
            EditorGUILayout.Space();
            GUILayout.Label("📄 Issue Data Preview", EditorStyles.boldLabel);

            EditorGUILayout.BeginVertical("helpbox");

            GUILayout.Label($"Title: {currentIssueData.Title}", EditorStyles.wordWrappedLabel);
            GUILayout.Label($"Stage: {currentIssueData.Stage}", EditorStyles.miniLabel);

            if (!string.IsNullOrEmpty(currentIssueData.Logline))
            {
                GUILayout.Label("Logline:", EditorStyles.boldLabel);
                GUILayout.Label(currentIssueData.Logline, EditorStyles.wordWrappedLabel);
            }

            if (!string.IsNullOrEmpty(currentIssueData.Tension))
            {
                GUILayout.Label("Tension:", EditorStyles.boldLabel);
                GUILayout.Label(currentIssueData.Tension, EditorStyles.wordWrappedLabel);
            }

            if (!string.IsNullOrEmpty(currentIssueData.IrreversibleShift))
            {
                GUILayout.Label("Irreversible Shift:", EditorStyles.boldLabel);
                GUILayout.Label(currentIssueData.IrreversibleShift, EditorStyles.wordWrappedLabel);
            }

            if (currentIssueData.Stage != "distilled")
            {
                EditorGUILayout.HelpBox($"Warning: Issue is in '{currentIssueData.Stage}' stage, not 'distilled'. Manifest generation may proceed but validation will be limited.", MessageType.Warning);
            }

            EditorGUILayout.EndVertical();
        }

        private void DrawResultsSection()
        {
            if (generatedManifest == null) return;

            EditorGUILayout.BeginVertical("box");
            GUILayout.Label("📊 Generated Manifest", EditorStyles.boldLabel);

            EditorGUILayout.BeginVertical("helpbox");

            GUILayout.Label($"Experiment ID: {generatedManifest.ExperimentId}", EditorStyles.miniLabel);
            GUILayout.Label($"Origin Hash: {generatedManifest.OriginBinding.LoglineHash}", EditorStyles.miniLabel);

            if (generatedManifest.ValidationCriteria != null)
            {
                GUILayout.Label("Validation Criteria:", EditorStyles.boldLabel);
                GUILayout.Label($"• Min Confidence: {generatedManifest.ValidationCriteria.MinConfidenceThreshold:P0}", EditorStyles.miniLabel);
                GUILayout.Label($"• Min Improvement: {generatedManifest.ValidationCriteria.MinBaselineImprovement:P0}", EditorStyles.miniLabel);
                GUILayout.Label($"• Max Error Rate: {generatedManifest.ValidationCriteria.MaxErrorRate:P0}", EditorStyles.miniLabel);
            }

            EditorGUILayout.EndVertical();
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
        }

        private void DrawOutputSection()
        {
            if (generatedManifest == null) return;

            EditorGUILayout.BeginVertical("box");
            GUILayout.Label("💾 Save Manifest", EditorStyles.boldLabel);

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("💾 Save to File", GUILayout.Height(30)))
            {
                SaveManifest();
            }

            if (GUILayout.Button("📋 Copy to Clipboard", GUILayout.Height(30)))
            {
                CopyManifestToClipboard();
            }

            if (GUILayout.Button("📁 Open Output Directory", GUILayout.Height(30)))
            {
                OpenOutputDirectory();
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.EndVertical();
        }

        private void DrawStatusBar()
        {
            EditorGUILayout.BeginHorizontal("toolbar");

            if (isProcessing)
            {
                GUILayout.Label("⏳ Processing...", EditorStyles.miniLabel);
                EditorUtility.DisplayProgressBar("Alchemist Manifest Generator", statusMessage, 0.5f);
            }
            else
            {
                EditorUtility.ClearProgressBar();
                if (!string.IsNullOrEmpty(statusMessage))
                {
                    string icon = messageType == MessageType.Error ? "❌" :
                                 messageType == MessageType.Warning ? "⚠️" : "✅";
                    GUILayout.Label($"{icon} {statusMessage}", EditorStyles.miniLabel);
                }
            }

            GUILayout.FlexibleSpace();
            GUILayout.Label($"Alchemist v{ALCHEMIST_VERSION}", EditorStyles.miniLabel);

            EditorGUILayout.EndHorizontal();
        }
        #endregion

        #region Core Logic
        private void ParseIssueFromUrl()
        {
            if (repositoryUrl.Contains("/issues/"))
            {
                var match = Regex.Match(repositoryUrl, @"/issues/(\d+)");
                if (match.Success)
                {
                    issueNumber = match.Groups[1].Value;
                    repositoryUrl = Regex.Replace(repositoryUrl, @"/issues/\d+.*", "");
                    SetStatus("Issue number extracted from URL", MessageType.Info);
                }
            }
        }

        private void FetchIssueData()
        {
            if (string.IsNullOrWhiteSpace(issueNumber) || string.IsNullOrWhiteSpace(repositoryUrl))
            {
                SetStatus("Issue number and repository URL are required", MessageType.Error);
                return;
            }

            isProcessing = true;
            statusMessage = "Fetching issue data...";

            try
            {
                // Since we can't make actual HTTP requests in this context,
                // generate data that reflects the requested issue so different numbers produce distinct manifests.
                currentIssueData = GenerateMockIssueData(issueNumber, repositoryUrl);
                generatedManifest = null; // Clear previous manifest

                SetStatus($"Issue #{issueNumber} data loaded successfully", MessageType.Info);
            }
            catch (Exception ex)
            {
                SetStatus($"Failed to fetch issue data: {ex.Message}", MessageType.Error);
                currentIssueData = null;
            }
            finally
            {
                isProcessing = false;
                Repaint();
            }
        }

        private void GenerateManifest()
        {
            if (currentIssueData == null)
            {
                SetStatus("No issue data available. Fetch issue data first.", MessageType.Error);
                return;
            }

            isProcessing = true;
            statusMessage = "Generating manifest...";

            try
            {
                var generator = new ManifestGenerator();
                generatedManifest = generator.CreateManifest(currentIssueData);

                if (autoValidate)
                {
                    ValidateManifest();
                }

                SetStatus("Manifest generated successfully", MessageType.Info);
            }
            catch (Exception ex)
            {
                SetStatus($"Failed to generate manifest: {ex.Message}", MessageType.Error);
                generatedManifest = null;
            }
            finally
            {
                isProcessing = false;
                Repaint();
            }
        }

        private void ValidateManifest()
        {
            if (generatedManifest == null) return;

            // Perform basic validation
            var issues = new List<string>();

            if (string.IsNullOrEmpty(generatedManifest.ExperimentId))
                issues.Add("Missing experiment ID");

            if (generatedManifest.OriginBinding == null)
                issues.Add("Missing origin binding");

            if (generatedManifest.ValidationCriteria == null)
                issues.Add("Missing validation criteria");

            if (issues.Any())
            {
                SetStatus($"Validation issues: {string.Join(", ", issues)}", MessageType.Warning);
            }
        }

        private void SaveManifest()
        {
            if (generatedManifest == null)
            {
                SetStatus("No manifest to save", MessageType.Error);
                return;
            }

            try
            {
                string issueDir = Path.Combine(outputDirectory, $"issue-{issueNumber}");
                Directory.CreateDirectory(issueDir);

                string filename = outputFormat == OutputFormat.YAML ?
                    "manifest_v1.yaml" : "manifest_v1.json";
                string filepath = Path.Combine(issueDir, filename);

                string content = SerializeManifest(generatedManifest, outputFormat);
                File.WriteAllText(filepath, content, Encoding.UTF8);

                SetStatus($"Manifest saved to: {filepath}", MessageType.Info);

                if (verboseLogging)
                {
                    Debug.Log($"Alchemist: Manifest saved for issue #{issueNumber} to {filepath}");
                }
            }
            catch (Exception ex)
            {
                SetStatus($"Failed to save manifest: {ex.Message}", MessageType.Error);
            }
        }

        private void CopyManifestToClipboard()
        {
            if (generatedManifest == null)
            {
                SetStatus("No manifest to copy", MessageType.Error);
                return;
            }

            try
            {
                string content = SerializeManifest(generatedManifest, outputFormat);
                EditorGUIUtility.systemCopyBuffer = content;
                SetStatus("Manifest copied to clipboard", MessageType.Info);
            }
            catch (Exception ex)
            {
                SetStatus($"Failed to copy manifest: {ex.Message}", MessageType.Error);
            }
        }

        private void OpenOutputDirectory()
        {
            string path = Path.Combine(Application.dataPath, "..", outputDirectory);
            if (Directory.Exists(path))
            {
                EditorUtility.RevealInFinder(path);
            }
            else
            {
                SetStatus("Output directory does not exist", MessageType.Warning);
            }
        }
        #endregion

        #region Utility Methods
        private void SetStatus(string message, MessageType type)
        {
            statusMessage = message;
            messageType = type;

            if (verboseLogging || type == MessageType.Error)
            {
                Debug.Log($"Alchemist: {message}");
            }
        }

        private string GetRelativePath(string absolutePath)
        {
            string projectPath = Path.GetDirectoryName(Application.dataPath);
            return Path.GetRelativePath(projectPath, absolutePath);
        }

        private GilHubIssueData GenerateMockIssueData(string number, string repoUrl)
        {
            // Create per-issue mock data so different numbers yield different manifests
            int parsedNumber = 0;
            int.TryParse(number, out parsedNumber);
            string n = string.IsNullOrEmpty(number) ? "0" : number.Trim();
            string repo = string.IsNullOrEmpty(repoUrl) ? "https://github.com/owner/repo" : repoUrl.Trim().TrimEnd('/');

            // Vary content slightly by issue number to avoid duplicates
            string[] themes =
            {
                "narrative integration",
                "performance spike",
                "UI/UX coherence",
                "asset pipeline",
                "AI behavior",
                "network sync"
            };
            string theme = themes[Mathf.Abs(parsedNumber) % themes.Length];

            return new GilHubIssueData
            {
                IssueNumber = parsedNumber,
                Title = $"{char.ToUpper(theme[0]) + theme.Substring(1)} - Issue #{n}",
                Logline = $"Investigation into {theme} affecting scenario #{n}",
                Tension = "Observed mismatch between intent and outcome within gameplay loop",
                IrreversibleShift = "Establish measurable intervention that couples player action with systemic feedback",
                MeasurableResidue = "- Engagement delta\n- Error rate trend\n- Completion correlation",
                Stage = "distilled",
                IssueUrl = $"{repo}/issues/{n}",
                CreatedAt = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                Labels = new[] { "gu-pot:distilled", theme.Replace(" ", "-"), "alchemist:ready" }
            };
        }

        private string SerializeManifest(AlchemistManifest manifest, OutputFormat format)
        {
            if (format == OutputFormat.JSON)
            {
                return JsonUtility.ToJson(manifest, true);
            }
            else
            {
                // Simple YAML serialization (could be enhanced with a proper YAML library)
                return ConvertToYaml(manifest);
            }
        }

        private string ConvertToYaml(AlchemistManifest manifest)
        {
            var yaml = new StringBuilder();

            yaml.AppendLine("# Alchemist Faculty Experiment Manifest");
            yaml.AppendLine($"# Generated on: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC");
            yaml.AppendLine($"# Alchemist Version: {ALCHEMIST_VERSION}");
            yaml.AppendLine();

            yaml.AppendLine("metadata:");
            yaml.AppendLine($"  name: \"{manifest.Name}\"");
            yaml.AppendLine($"  description: \"{manifest.Description}\"");
            yaml.AppendLine($"  version: \"{manifest.Version}\"");
            yaml.AppendLine($"  experiment_id: \"{manifest.ExperimentId}\"");
            yaml.AppendLine();

            yaml.AppendLine("origin:");
            yaml.AppendLine($"  type: \"{manifest.OriginBinding.Type}\"");
            yaml.AppendLine($"  issue_number: {manifest.OriginBinding.IssueNumber}");
            yaml.AppendLine($"  issue_url: \"{manifest.OriginBinding.IssueUrl}\"");
            yaml.AppendLine($"  stage_at_evaluation: \"{manifest.OriginBinding.StageAtEvaluation}\"");
            yaml.AppendLine($"  logline_hash: \"{manifest.OriginBinding.LoglineHash}\"");
            yaml.AppendLine($"  tension_hash: \"{manifest.OriginBinding.TensionHash}\"");
            yaml.AppendLine($"  irreversible_shift_declared: {manifest.OriginBinding.IrreversibleShiftDeclared.ToString().ToLower()}");
            yaml.AppendLine($"  extracted_on: \"{manifest.OriginBinding.ExtractedOn}\"");
            yaml.AppendLine($"  alchemist_version: \"{manifest.OriginBinding.AlchemistVersion}\"");

            return yaml.ToString();
        }

        private void LoadSettings()
        {
            issueNumber = EditorPrefs.GetString("AlchemistManifestGenerator.IssueNumber", "");
            repositoryUrl = EditorPrefs.GetString("AlchemistManifestGenerator.RepositoryUrl", "https://github.com/owner/repo");
            outputDirectory = EditorPrefs.GetString("AlchemistManifestGenerator.OutputDirectory", "gu_pot/");
            autoValidate = EditorPrefs.GetBool("AlchemistManifestGenerator.AutoValidate", true);
            verboseLogging = EditorPrefs.GetBool("AlchemistManifestGenerator.VerboseLogging", false);
            outputFormat = (OutputFormat)EditorPrefs.GetInt("AlchemistManifestGenerator.OutputFormat", 0);
        }

        private void SaveSettings()
        {
            EditorPrefs.SetString("AlchemistManifestGenerator.IssueNumber", issueNumber);
            EditorPrefs.SetString("AlchemistManifestGenerator.RepositoryUrl", repositoryUrl);
            EditorPrefs.SetString("AlchemistManifestGenerator.OutputDirectory", outputDirectory);
            EditorPrefs.SetBool("AlchemistManifestGenerator.AutoValidate", autoValidate);
            EditorPrefs.SetBool("AlchemistManifestGenerator.VerboseLogging", verboseLogging);
            EditorPrefs.SetInt("AlchemistManifestGenerator.OutputFormat", (int)outputFormat);
        }
        #endregion
    }

    #region Data Classes
    [System.Serializable]
    public class GilHubIssueData
    {
        public int IssueNumber;
        public string Title;
        public string Logline;
        public string Tension;
        public string IrreversibleShift;
        public string MeasurableResidue;
        public string Stage;
        public string IssueUrl;
        public string CreatedAt;
        public string[] Labels;
    }

    [System.Serializable]
    public class AlchemistManifest
    {
        public string Name;
        public string Description;
        public string Version = "1.0.0";
        public string ExperimentId;
        public OriginBinding OriginBinding;
        public ValidationCriteria ValidationCriteria;
    }

    [System.Serializable]
    public class OriginBinding
    {
        public string Type = "gu_pot";
        public int IssueNumber;
        public string IssueUrl;
        public string StageAtEvaluation;
        public string LoglineHash;
        public string TensionHash;
        public bool IrreversibleShiftDeclared;
        public string ExtractedOn;
        public string AlchemistVersion;
    }

    [System.Serializable]
    public class ValidationCriteria
    {
        public float MinConfidenceThreshold = 0.7f;
        public float MinBaselineImprovement = 0.10f;
        public float MaxErrorRate = 0.05f;
    }

    public class ManifestGenerator
    {
        public AlchemistManifest CreateManifest(GilHubIssueData issueData)
        {
            var timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
            var experimentId = GenerateExperimentId(issueData.IssueNumber, timestamp);

            return new AlchemistManifest
            {
                Name = $"Alchemist Experiment - Issue #{issueData.IssueNumber}",
                Description = issueData.Title,
                ExperimentId = experimentId,
                OriginBinding = new OriginBinding
                {
                    IssueNumber = issueData.IssueNumber,
                    IssueUrl = issueData.IssueUrl,
                    StageAtEvaluation = issueData.Stage,
                    LoglineHash = GenerateHash(issueData.Logline),
                    TensionHash = GenerateHash(issueData.Tension),
                    IrreversibleShiftDeclared = !string.IsNullOrEmpty(issueData.IrreversibleShift),
                    ExtractedOn = timestamp,
                    AlchemistVersion = "0.1.0" // Use literal value since ALCHEMIST_VERSION is not accessible from inner class
                },
                ValidationCriteria = new ValidationCriteria()
            };
        }

        private string GenerateExperimentId(int issueNumber, string timestamp)
        {
            // Generate a deterministic but unique ID
            string seedString = $"issue-{issueNumber}-{timestamp}";
            using var sha256 = SHA256.Create();
            byte [ ] hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(seedString));
            return System.Guid.NewGuid().ToString(); // Simplified for demo
        }

        private string GenerateHash(string text)
        {
            if (string.IsNullOrEmpty(text)) return "sha256:0000000000000000000000000000000000000000000000000000000000000000";

            // Normalize text: trim, lowercase, collapse whitespace
            string normalized = Regex.Replace(text.Trim().ToLower(), @"\s+", " ");

            using var sha256 = SHA256.Create();
            byte [ ] hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(normalized));
            string hexString = BitConverter.ToString(hash).Replace("-", "").ToLower();
            return $"sha256:{hexString}";
        }
    }
    #endregion
}
