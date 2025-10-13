using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Diagnostics;
using UnityEngine;
using UnityEditor;
using System.Text;
using System.Linq;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Unity Editor window for School experiment execution
    /// KeeperNote: Stage 3 - Deterministic experiment runner with Unity 6 & GH integration
    /// </summary>
    public class ExperimentRunner : EditorWindow
    {
        private Vector2 scrollPosition;
        private List<ExperimentManifest> availableManifests;
        private bool isExecuting = false;
        private string executionProgress = "";
        private DateTime lastExecutionTime;
        private int experimentsCompleted = 0;
        private bool showLogs = false;
        private readonly StringBuilder executionLogs = new();
        
        // Paths and settings
        private const string MANIFESTS_DIR = "assets/experiments/school/manifests/";
        private const string OUTPUTS_DIR = "assets/experiments/school/outputs/runs/";
        private const string PYTHON_HARNESS_PATH = "engine/experiment_harness.py";
        
        [MenuItem("Tools/School/Run Experiments")]
        public static void ShowWindow()
        {
            var window = GetWindow<ExperimentRunner>("Experiment Runner");
            window.minSize = new Vector2(600, 800);
            window.Show();
        }
        
        private void OnEnable()
        {
            LoadAvailableManifests();
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawManifestSection();
            DrawExecutionSection();
            DrawResultsSection();
            DrawLogsSection();
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.Space(10);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("School Experiment Runner - Stage 3", EditorStyles.largeLabel);
            EditorGUILayout.LabelField("Deterministic Experiment Execution with Unity 6 & GitHub Integration", EditorStyles.miniLabel);
            EditorGUILayout.Space(5);
            
            var style = new GUIStyle(EditorStyles.label) { wordWrap = true };
            EditorGUILayout.LabelField("Executes experiment manifests generated in Stage 2, capturing results and artifacts for analysis.", style);
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.Space(10);
        }
        
        private void DrawManifestSection()
        {
            EditorGUILayout.LabelField("Available Experiment Manifests", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (GUILayout.Button("Refresh Manifests"))
            {
                LoadAvailableManifests();
            }
            
            EditorGUILayout.Space(5);
            
            if (availableManifests == null || availableManifests.Count == 0)
            {
                EditorGUILayout.LabelField("No experiment manifests found.");
                EditorGUILayout.LabelField("Please run Stage 2 (Experiment Manifest Generator) first.");
            }
            else
            {
                EditorGUILayout.LabelField($"Found {availableManifests.Count} experiment manifests:");
                
                EditorGUILayout.BeginVertical(EditorStyles.textArea);
                foreach (var manifest in availableManifests.Take(10)) // Show first 10
                {
                    EditorGUILayout.BeginHorizontal();
                    EditorGUILayout.LabelField($"• {manifest.Name}", GUILayout.Width(300));
                    EditorGUILayout.LabelField($"({manifest.HypothesisType})", EditorStyles.miniLabel, GUILayout.Width(100));
                    EditorGUILayout.LabelField($"Confidence: {manifest.Confidence:F2}", EditorStyles.miniLabel, GUILayout.Width(100));
                    EditorGUILayout.EndHorizontal();
                }
                
                if (availableManifests.Count > 10)
                {
                    EditorGUILayout.LabelField($"... and {availableManifests.Count - 10} more");
                }
                EditorGUILayout.EndVertical();
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawExecutionSection()
        {
            EditorGUILayout.LabelField("Experiment Execution", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (availableManifests != null && availableManifests.Count > 0)
            {
                EditorGUILayout.LabelField($"Ready to execute {availableManifests.Count} experiments");
                
                EditorGUILayout.Space(5);
                
                GUI.enabled = !isExecuting;
                if (GUILayout.Button("Execute All Experiments", GUILayout.Height(40)))
                {
                    ExecuteAllExperiments();
                }
                GUI.enabled = true;
                
                if (isExecuting)
                {
                    EditorGUILayout.Space(5);
                    EditorGUILayout.LabelField("Execution Status:", EditorStyles.boldLabel);
                    EditorGUILayout.LabelField(executionProgress);
                    
                    // Progress bar
                    var progressValue = availableManifests.Count > 0 ? 
                        (float)experimentsCompleted / availableManifests.Count : 0f;
                    Rect progressRect = EditorGUILayout.GetControlRect();
                    EditorGUI.ProgressBar(progressRect, progressValue, 
                        $"{experimentsCompleted}/{availableManifests.Count} experiments completed");
                }
            }
            else
            {
                EditorGUILayout.LabelField("No experiments available to execute.");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawResultsSection()
        {
            EditorGUILayout.LabelField("Execution Results", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (lastExecutionTime != default)
            {
                EditorGUILayout.LabelField($"Last Execution: {lastExecutionTime:yyyy-MM-dd HH:mm:ss}");
                EditorGUILayout.LabelField($"Experiments Completed: {experimentsCompleted}");
                
                EditorGUILayout.Space(5);
                
                if (GUILayout.Button("Open Results Directory"))
                {
                    var fullPath = Path.GetFullPath(OUTPUTS_DIR);
                    EditorUtility.RevealInFinder(fullPath);
                }
                
                if (GUILayout.Button("View GitHub Integration Data"))
                {
                    ShowGitHubIntegrationData();
                }
            }
            else
            {
                EditorGUILayout.LabelField("No execution results yet.");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawLogsSection()
        {
            EditorGUILayout.LabelField("Execution Logs", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            showLogs = EditorGUILayout.Foldout(showLogs, "Show Detailed Logs");
            
            if (showLogs && executionLogs.Length > 0)
            {
                EditorGUILayout.BeginVertical(EditorStyles.textArea);
                EditorGUILayout.SelectableLabel(executionLogs.ToString(), EditorStyles.wordWrappedLabel, 
                    GUILayout.Height(200));
                EditorGUILayout.EndVertical();
                
                if (GUILayout.Button("Clear Logs"))
                {
                    executionLogs.Clear();
                }
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void LoadAvailableManifests()
        {
            availableManifests = new List<ExperimentManifest>();
            
            if (!Directory.Exists(MANIFESTS_DIR))
            {
                LogMessage($"Manifests directory not found: {MANIFESTS_DIR}");
                return;
            }
            
            var manifestFiles = Directory.GetFiles(MANIFESTS_DIR, "*.yaml");
            LogMessage($"Found {manifestFiles.Length} manifest files");
            
            foreach (var file in manifestFiles)
            {
                try
                {
                    var manifest = LoadManifestFromFile(file);
                    if (manifest != null)
                    {
                        availableManifests.Add(manifest);
                    }
                }
                catch (Exception ex)
                {
                    LogMessage($"Error loading manifest {file}: {ex.Message}");
                }
            }
            
            LogMessage($"Successfully loaded {availableManifests.Count} manifests");
        }
        
        private ExperimentManifest LoadManifestFromFile(string filePath)
        {
            var content = File.ReadAllText(filePath);
            var lines = content.Split('\n');
            
            var manifest = new ExperimentManifest
            {
                FilePath = filePath,
                FileName = Path.GetFileName(filePath)
            };
            
            // Simple YAML parsing for key fields
            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (trimmed.StartsWith("name:"))
                {
                    manifest.Name = trimmed[ 5.. ].Trim().Trim('"');
                }
                else if (trimmed.StartsWith("hypothesis_type:"))
                {
                    manifest.HypothesisType = trimmed[ 16.. ].Trim();
                }
                else if (trimmed.StartsWith("hypothesis_id:"))
                {
                    manifest.HypothesisId = trimmed[ 14.. ].Trim();
                }
                else if (trimmed.StartsWith("- metric: \"hypothesis_validation_score\""))
                {
                    // Look for the threshold in the next line
                    var nextLine = lines.Where(l => l.Trim().StartsWith("threshold:")).FirstOrDefault();
                    if (nextLine != null)
                    {
                        if (float.TryParse(nextLine.Split(':')[1].Trim(), out float confidence))
                        {
                            manifest.Confidence = confidence;
                        }
                    }
                }
            }
            
            return manifest;
        }
        
        private async void ExecuteAllExperiments()
        {
            if (availableManifests == null || availableManifests.Count == 0)
            {
                LogMessage("No experiments to execute");
                return;
            }
            
            isExecuting = true;
            experimentsCompleted = 0;
            executionProgress = "Starting experiment execution...";
            lastExecutionTime = DateTime.Now;
            
            try
            {
                // Ensure output directory exists
                Directory.CreateDirectory(OUTPUTS_DIR);
                
                LogMessage($"Starting execution of {availableManifests.Count} experiments");
                
                foreach (var manifest in availableManifests)
                {
                    executionProgress = $"Executing: {manifest.Name}";
                    Repaint();
                    
                    await ExecuteSingleExperiment(manifest);
                    
                    experimentsCompleted++;
                    LogMessage($"Completed experiment: {manifest.Name} ({experimentsCompleted}/{availableManifests.Count})");
                    
                    // Small delay to allow Unity to update
                    await Task.Delay(100);
                }
                
                executionProgress = $"All experiments completed! ({experimentsCompleted}/{availableManifests.Count})";
                LogMessage("All experiments completed successfully");
                
                // Generate GitHub integration metadata
                await GenerateGitHubIntegrationData();
            }
            catch (Exception ex)
            {
                executionProgress = $"Execution failed: {ex.Message}";
                LogMessage($"Execution failed: {ex.Message}");
                UnityEngine.Debug.LogError($"Experiment execution failed: {ex}");
            }
            finally
            {
                isExecuting = false;
                Repaint();
            }
        }
        
        private async Task ExecuteSingleExperiment(ExperimentManifest manifest)
        {
            var runId = Guid.NewGuid().ToString("N")[..8];
            var outputDir = Path.Combine(OUTPUTS_DIR, $"run_{runId}_{DateTime.Now:yyyyMMdd_HHmmss}");
            Directory.CreateDirectory(outputDir);
            
            LogMessage($"Executing experiment: {manifest.Name}");
            LogMessage($"Output directory: {outputDir}");
            
            try
            {
                // Copy original manifest to run directory
                var originalManifestCopy = Path.Combine(outputDir, "unity_manifest.yaml");
                File.Copy(manifest.FilePath, originalManifestCopy);
                
                // Convert Unity manifest to Python harness format
                var convertedManifest = ManifestConverter.ConvertToHarnessFormat(manifest.FilePath);
                var harnessManifestPath = Path.Combine(outputDir, "harness_manifest.yaml");
                File.WriteAllText(harnessManifestPath, convertedManifest);
                
                LogMessage("Manifest converted to Python harness format");
                
                // Execute Python experiment harness with converted manifest
                var result = await ExecutePythonHarness(harnessManifestPath, outputDir);
                
                // Generate run metadata
                var metadata = CreateRunMetadata(manifest, runId, result);
                var metadataPath = Path.Combine(outputDir, "run_metadata.json");
                File.WriteAllText(metadataPath, JsonUtility.ToJson(metadata, true));
                
                LogMessage($"Experiment completed: {manifest.Name}");
            }
            catch (Exception ex)
            {
                LogMessage($"Error executing experiment {manifest.Name}: {ex.Message}");
                
                // Write error to run directory
                var errorPath = Path.Combine(outputDir, "error.txt");
                File.WriteAllText(errorPath, $"Error: {ex.Message}\nStack Trace: {ex.StackTrace}");
                
                throw;
            }
        }
        
        private async Task<ProcessResult> ExecutePythonHarness(string manifestPath, string outputDir) // @copilot - CS0618 -> Fixed by using proper async pattern
        {
            var processInfo = new ProcessStartInfo
            {
                FileName = "python3",
                Arguments = $"{PYTHON_HARNESS_PATH} run --manifest \"{manifestPath}\" --output-dir \"{outputDir}\"",
                WorkingDirectory = Application.dataPath + "/..",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            
            LogMessage($"Executing: {processInfo.FileName} {processInfo.Arguments}");

            using var process = new Process { StartInfo = processInfo };
            var outputBuilder = new StringBuilder();
            var errorBuilder = new StringBuilder();

            process.OutputDataReceived += (sender, e) =>
            {
                if (e.Data != null)
                {
                    outputBuilder.AppendLine(e.Data);
                    LogMessage($"[Python] {e.Data}");
                }
            };

            process.ErrorDataReceived += (sender, e) =>
            {
                if (e.Data != null)
                {
                    errorBuilder.AppendLine(e.Data);
                    LogMessage($"[Python Error] {e.Data}");
                }
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            // Use async version for proper async method
            await Task.Run(() =>
            {
                // Wait for process completion with timeout
                var completed = process.WaitForExit(300000); // 5 minutes timeout

                if (!completed)
                {
                    process.Kill();
                    throw new TimeoutException("Python harness execution timed out");
                }
            });

            return new ProcessResult
            {
                ExitCode = process.ExitCode,
                Output = outputBuilder.ToString(),
                Error = errorBuilder.ToString()
            };
        }
        
        private ExperimentRunMetadata CreateRunMetadata(ExperimentManifest manifest, string runId, ProcessResult result)
        {
            return new ExperimentRunMetadata
            {
                RunId = runId,
                ExperimentName = manifest.Name,
                HypothesisId = manifest.HypothesisId,
                HypothesisType = manifest.HypothesisType,
                ManifestFile = manifest.FileName,
                ExecutionTime = DateTime.UtcNow.ToString("O"),
                UnityVersion = Application.unityVersion,
                ProjectPath = Application.dataPath,
                GitCommit = GetGitCommitHash(),
                GitBranch = GetGitBranch(),
                ExitCode = result.ExitCode,
                Success = result.ExitCode == 0,
                Stage = "3",
                Workflow = "school"
            };
        }
        
        private Task GenerateGitHubIntegrationData() // Fixed CS1998 by removing async and returning Task.CompletedTask
        {
            var integrationData = new ExperimentRunnerGitHubData
            {
                Timestamp = DateTime.UtcNow.ToString("O"),
                UnityVersion = Application.unityVersion,
                ProjectPath = Application.dataPath,
                GitCommit = GetGitCommitHash(),
                GitBranch = GetGitBranch(),
                ExperimentsExecuted = experimentsCompleted,
                OutputDirectory = OUTPUTS_DIR,
                ArtifactPaths = GetArtifactPaths(),
                Stage = "3",
                Workflow = "school"
            };
            
            var integrationPath = Path.Combine(OUTPUTS_DIR, "github_integration.json");
            File.WriteAllText(integrationPath, JsonUtility.ToJson(integrationData, true));
            
            LogMessage($"GitHub integration data written to: {integrationPath}");
            
            return Task.CompletedTask;
        }
        
        private List<string> GetArtifactPaths()
        {
            var paths = new List<string>();
            
            if (Directory.Exists(OUTPUTS_DIR))
            {
                var runDirs = Directory.GetDirectories(OUTPUTS_DIR, "run_*");
                foreach (var dir in runDirs)
                {
                    var files = Directory.GetFiles(dir, "*", SearchOption.AllDirectories);
                    paths.AddRange(files.Select(f => Path.GetRelativePath(Application.dataPath + "/..", f)));
                }
            }
            
            return paths;
        }
        
        private string GetGitCommitHash()
        {
            try
            {
                var processInfo = new ProcessStartInfo
                {
                    FileName = "git",
                    Arguments = "rev-parse HEAD",
                    WorkingDirectory = Application.dataPath + "/..",
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = Process.Start(processInfo);
                var output = process.StandardOutput.ReadToEnd().Trim();
                process.WaitForExit();
                return process.ExitCode == 0 ? output : "unknown";
            }
            catch
            {
                return "unknown";
            }
        }
        
        private string GetGitBranch()
        {
            try
            {
                var processInfo = new ProcessStartInfo
                {
                    FileName = "git",
                    Arguments = "rev-parse --abbrev-ref HEAD",
                    WorkingDirectory = Application.dataPath + "/..",
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = Process.Start(processInfo);
                var output = process.StandardOutput.ReadToEnd().Trim();
                process.WaitForExit();
                return process.ExitCode == 0 ? output : "unknown";
            }
            catch
            {
                return "unknown";
            }
        }
        
        private void ShowGitHubIntegrationData()
        {
            var integrationPath = Path.Combine(OUTPUTS_DIR, "github_integration.json");
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
                    "No integration data found. Run experiments first.", "OK");
            }
        }
        
        private void LogMessage(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var logEntry = $"[{timestamp}] {message}";
            executionLogs.AppendLine(logEntry);
            UnityEngine.Debug.Log($"[ExperimentRunner] {message}");
        }
    }
    
    [Serializable]
    public class ExperimentManifest
    {
        public string Name;
        public string HypothesisId;
        public string HypothesisType;
        public string FilePath;
        public string FileName;
        public float Confidence;
    }
    
    [Serializable]
    public class ProcessResult
    {
        public int ExitCode;
        public string Output;
        public string Error;
    }
    
    [Serializable]
    public class ExperimentRunMetadata
    {
        public string RunId;
        public string ExperimentName;
        public string HypothesisId;
        public string HypothesisType;
        public string ManifestFile;
        public string ExecutionTime;
        public string UnityVersion;
        public string ProjectPath;
        public string GitCommit;
        public string GitBranch;
        public int ExitCode;
        public bool Success;
        public string Stage;
        public string Workflow;
    }
    
    [Serializable]
    public class ExperimentRunnerGitHubData
    {
        public string Timestamp;
        public string UnityVersion;
        public string ProjectPath;
        public string GitCommit;
        public string GitBranch;
        public int ExperimentsExecuted;
        public string OutputDirectory;
        public List<string> ArtifactPaths;
        public string Stage;
        public string Workflow;
    }
}
