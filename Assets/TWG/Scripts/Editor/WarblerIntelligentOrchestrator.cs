#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using System;
using System.IO;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace LivingDevAgent.Editor.Warbler
{
    /// <summary>
    /// 🧠 Warbler Intelligent Project Orchestrator - Unity Editor Integration
    /// Sacred Mission: Bridge Unity Editor with AI-powered project intelligence
    /// 
    /// Provides Unity developers with AI-assisted project structure generation,
    /// intelligent code suggestions, and automated development workflow guidance.
    /// Handles Ollama connectivity with proper timeout management and fallback strategies.
    /// 
    /// Author: Bootstrap Sentinel & Living Dev Agent
    /// Chronicle: Unity integration component of the Warbler AI Project Orchestrator
    /// </summary>
    public class WarblerIntelligentOrchestrator : EditorWindow
    {
        // Connection settings
        [SerializeField] private string ollamaUrl = "http://localhost:11434";
        [SerializeField] private string model = "llama2";
        
        // UI state
        private string projectDescription = "Create a simple 2D platformer game";
        private string projectType = "unity_2d_game";
        private string targetPlatform = "pc";
        private string complexity = "simple";
        private List<string> additionalRequirements = new List<string>();
        private string newRequirement = "";
        
        // Connection status
        private ConnectionStatus connectionStatus = ConnectionStatus.Unknown;
        private string connectionMessage = "Not tested";
        private DateTime lastConnectionTest = DateTime.MinValue;
        
        // Generation state
        private bool isGenerating = false;
        private string generationProgress = "";
        private ProjectAnalysisResult lastResult = null;
        
        // UI control
        private Vector2 scrollPosition;
        private bool showAdvancedSettings = false;
        private bool showConnectionDetails = false;
        private bool showLastResult = false;
        
        // Process management
        private Process currentProcess = null;
        
        private enum ConnectionStatus
        {
            Unknown,
            Connected,
            Disconnected,
            Testing,
            Error
        }
        
        [Serializable]
        public class ProjectAnalysisResult
        {
            public bool success;
            public string project_name;
            public string description;
            public List<ProjectStructureItem> structure;
            public List<ScriptInfo> scripts;
            public List<AssetInfo> assets_needed;
            public List<string> setup_instructions;
            public List<string> development_notes;
            public float generation_time;
            public bool ai_generated;
            public bool fallback_used;
            public string error_message;
        }
        
        [Serializable]
        public class ProjectStructureItem
        {
            public string path;
            public string type;
            public string content;
            public string description;
            public bool is_generated;
        }
        
        [Serializable]
        public class ScriptInfo
        {
            public string name;
            public string path;
            public string description;
            public string content;
        }
        
        [Serializable]
        public class AssetInfo
        {
            public string type;
            public string name;
            public string description;
        }
        
        [MenuItem("TWG/Warbler AI/Intelligent Project Orchestrator")]
        public static void ShowWindow()
        {
            var window = GetWindow<WarblerIntelligentOrchestrator>("🧠 Warbler AI");
            window.minSize = new Vector2(450, 600);
            window.Show();
        }
        
        private void OnEnable()
        {
            // Load settings from EditorPrefs
            LoadSettings();
            
            // Auto-test connection on startup if not recently tested
            if ((DateTime.Now - lastConnectionTest).TotalMinutes > 5)
            {
                EditorApplication.delayCall += () => TestConnectionAsync();
            }
        }
        
        private void OnDisable()
        {
            // Clean up any running processes
            CleanupProcess();
            
            // Save settings
            SaveSettings();
        }
        
        private void LoadSettings()
        {
            ollamaUrl = EditorPrefs.GetString("WarblerAI.OllamaUrl", "http://localhost:11434");
            model = EditorPrefs.GetString("WarblerAI.Model", "llama2");
            projectDescription = EditorPrefs.GetString("WarblerAI.LastDescription", "Create a simple 2D platformer game");
            projectType = EditorPrefs.GetString("WarblerAI.ProjectType", "unity_2d_game");
            targetPlatform = EditorPrefs.GetString("WarblerAI.Platform", "pc");
            complexity = EditorPrefs.GetString("WarblerAI.Complexity", "simple");
        }
        
        private void SaveSettings()
        {
            EditorPrefs.SetString("WarblerAI.OllamaUrl", ollamaUrl);
            EditorPrefs.SetString("WarblerAI.Model", model);
            EditorPrefs.SetString("WarblerAI.LastDescription", projectDescription);
            EditorPrefs.SetString("WarblerAI.ProjectType", projectType);
            EditorPrefs.SetString("WarblerAI.Platform", targetPlatform);
            EditorPrefs.SetString("WarblerAI.Complexity", complexity);
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawConnectionStatus();
            DrawProjectConfiguration();
            DrawGenerationControls();
            
            if (showLastResult && lastResult != null)
            {
                DrawLastResult();
            }
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.Space(10);
            
            GUILayout.BeginHorizontal();
            GUILayout.FlexibleSpace();
            
            var headerStyle = new GUIStyle(EditorStyles.largeLabel)
            {
                fontSize = 18,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };
            
            GUILayout.Label("🧠 Warbler AI Project Orchestrator", headerStyle);
            GUILayout.FlexibleSpace();
            GUILayout.EndHorizontal();
            
            EditorGUILayout.Space(5);
            
            var subtitleStyle = new GUIStyle(EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.LabelField("AI-Powered Unity Project Intelligence", subtitleStyle);
            
            EditorGUILayout.Space(15);
        }
        
        private void DrawConnectionStatus()
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            GUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("🔌 AI Connection Status", EditorStyles.boldLabel);
            
            if (GUILayout.Button(showConnectionDetails ? "Hide Details" : "Show Details", GUILayout.Width(100)))
            {
                showConnectionDetails = !showConnectionDetails;
            }
            GUILayout.EndHorizontal();
            
            // Status indicator
            GUILayout.BeginHorizontal();
            
            Color statusColor = GetStatusColor();
            var originalColor = GUI.backgroundColor;
            GUI.backgroundColor = statusColor;
            
            string statusIcon = GetStatusIcon();
            string statusText = $"{statusIcon} {connectionStatus}";
            
            if (connectionStatus == ConnectionStatus.Testing)
            {
                statusText += "...";
            }
            
            EditorGUILayout.LabelField(statusText, GUILayout.Width(120));
            GUI.backgroundColor = originalColor;
            
            EditorGUILayout.LabelField(connectionMessage);
            
            if (GUILayout.Button("Test", GUILayout.Width(60)))
            {
                TestConnectionAsync();
            }
            
            GUILayout.EndHorizontal();
            
            if (showConnectionDetails)
            {
                EditorGUILayout.Space(5);
                
                EditorGUILayout.LabelField("Configuration:", EditorStyles.miniBoldLabel);
                
                EditorGUI.indentLevel++;
                ollamaUrl = EditorGUILayout.TextField("Ollama URL", ollamaUrl);
                model = EditorGUILayout.TextField("Model", model);
                
                if (lastConnectionTest != DateTime.MinValue)
                {
                    string lastTestText = $"Last tested: {lastConnectionTest:HH:mm:ss}";
                    EditorGUILayout.LabelField(lastTestText, EditorStyles.miniLabel);
                }
                EditorGUI.indentLevel--;
                
                if (GUI.changed)
                {
                    // Reset connection status when settings change
                    connectionStatus = ConnectionStatus.Unknown;
                    connectionMessage = "Settings changed - retest needed";
                }
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void DrawProjectConfiguration()
        {
            EditorGUILayout.Space(10);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            EditorGUILayout.LabelField("🎯 Project Configuration", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);
            
            // Project description
            EditorGUILayout.LabelField("Project Description:", EditorStyles.miniBoldLabel);
            projectDescription = EditorGUILayout.TextArea(projectDescription, GUILayout.Height(60));
            
            EditorGUILayout.Space(8);
            
            // Basic settings
            GUILayout.BeginHorizontal();
            
            GUILayout.BeginVertical();
            EditorGUILayout.LabelField("Type:", EditorStyles.miniLabel, GUILayout.Width(60));
            projectType = EditorGUILayout.Popup(GetProjectTypeIndex(), GetProjectTypeOptions(), GUILayout.Width(140));
            GUILayout.EndVertical();
            
            GUILayout.BeginVertical();
            EditorGUILayout.LabelField("Platform:", EditorStyles.miniLabel, GUILayout.Width(60));
            targetPlatform = EditorGUILayout.Popup(GetPlatformIndex(), GetPlatformOptions(), GUILayout.Width(100));
            GUILayout.EndVertical();
            
            GUILayout.BeginVertical();
            EditorGUILayout.LabelField("Complexity:", EditorStyles.miniLabel, GUILayout.Width(80));
            complexity = EditorGUILayout.Popup(GetComplexityIndex(), GetComplexityOptions(), GUILayout.Width(100));
            GUILayout.EndVertical();
            
            GUILayout.EndHorizontal();
            
            // Advanced settings toggle
            EditorGUILayout.Space(8);
            showAdvancedSettings = EditorGUILayout.Foldout(showAdvancedSettings, "Advanced Requirements");
            
            if (showAdvancedSettings)
            {
                EditorGUI.indentLevel++;
                
                // Additional requirements
                EditorGUILayout.LabelField("Additional Requirements:", EditorStyles.miniLabel);
                
                // Show existing requirements
                for (int i = 0; i < additionalRequirements.Count; i++)
                {
                    GUILayout.BeginHorizontal();
                    EditorGUILayout.LabelField($"• {additionalRequirements[i]}", EditorStyles.wordWrappedLabel);
                    if (GUILayout.Button("×", GUILayout.Width(20)))
                    {
                        additionalRequirements.RemoveAt(i);
                        i--;
                    }
                    GUILayout.EndHorizontal();
                }
                
                // Add new requirement
                GUILayout.BeginHorizontal();
                newRequirement = EditorGUILayout.TextField("New requirement:", newRequirement);
                if (GUILayout.Button("Add", GUILayout.Width(50)) && !string.IsNullOrWhiteSpace(newRequirement))
                {
                    additionalRequirements.Add(newRequirement.Trim());
                    newRequirement = "";
                }
                GUILayout.EndHorizontal();
                
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void DrawGenerationControls()
        {
            EditorGUILayout.Space(10);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            EditorGUILayout.LabelField("🚀 AI Generation", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);
            
            if (isGenerating)
            {
                // Show progress
                EditorGUILayout.LabelField("Status:", EditorStyles.miniBoldLabel);
                EditorGUILayout.LabelField(generationProgress, EditorStyles.wordWrappedLabel);
                
                EditorGUILayout.Space(5);
                
                // Progress bar (indeterminate)
                Rect progressRect = EditorGUILayout.GetControlRect();
                EditorGUI.ProgressBar(progressRect, Mathf.PingPong(Time.realtimeSinceStartup, 1.0f), "Generating...");
                
                EditorGUILayout.Space(5);
                
                if (GUILayout.Button("Cancel", GUILayout.Height(25)))
                {
                    CancelGeneration();
                }
            }
            else
            {
                // Generation buttons
                bool canGenerate = !string.IsNullOrWhiteSpace(projectDescription);
                
                GUI.enabled = canGenerate;
                
                if (GUILayout.Button("🤖 Generate with AI", GUILayout.Height(35)))
                {
                    GenerateProjectAsync(false);
                }
                
                if (GUILayout.Button("🛡️ Generate Fallback Template", GUILayout.Height(25)))
                {
                    GenerateProjectAsync(true);
                }
                
                GUI.enabled = true;
                
                if (!canGenerate)
                {
                    EditorGUILayout.HelpBox("Please enter a project description to generate.", MessageType.Info);
                }
                else if (connectionStatus == ConnectionStatus.Disconnected || connectionStatus == ConnectionStatus.Error)
                {
                    EditorGUILayout.HelpBox("AI is not available. Use fallback template or fix connection.", MessageType.Warning);
                }
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void DrawLastResult()
        {
            EditorGUILayout.Space(10);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            GUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("📊 Last Generation Result", EditorStyles.boldLabel);
            
            if (GUILayout.Button("Hide", GUILayout.Width(50)))
            {
                showLastResult = false;
            }
            GUILayout.EndHorizontal();
            
            EditorGUILayout.Space(5);
            
            if (lastResult.success)
            {
                EditorGUILayout.LabelField($"✅ {lastResult.project_name}", EditorStyles.boldLabel);
                EditorGUILayout.LabelField(lastResult.description, EditorStyles.wordWrappedLabel);
                
                EditorGUILayout.Space(5);
                
                string generationInfo = lastResult.ai_generated 
                    ? $"🤖 AI-generated in {lastResult.generation_time:F1}s"
                    : $"🛡️ Fallback template in {lastResult.generation_time:F1}s";
                    
                EditorGUILayout.LabelField(generationInfo, EditorStyles.miniLabel);
                
                if (lastResult.structure != null && lastResult.structure.Count > 0)
                {
                    EditorGUILayout.Space(5);
                    EditorGUILayout.LabelField($"📁 Structure ({lastResult.structure.Count} items):", EditorStyles.miniBoldLabel);
                    
                    EditorGUI.indentLevel++;
                    foreach (var item in lastResult.structure)
                    {
                        string icon = item.type == "directory" ? "📁" : "📄";
                        EditorGUILayout.LabelField($"{icon} {item.path}", EditorStyles.miniLabel);
                    }
                    EditorGUI.indentLevel--;
                }
                
                if (lastResult.scripts != null && lastResult.scripts.Count > 0)
                {
                    EditorGUILayout.Space(5);
                    EditorGUILayout.LabelField($"📜 Scripts ({lastResult.scripts.Count}):", EditorStyles.miniBoldLabel);
                    
                    EditorGUI.indentLevel++;
                    foreach (var script in lastResult.scripts)
                    {
                        EditorGUILayout.LabelField($"• {script.name}", EditorStyles.miniLabel);
                    }
                    EditorGUI.indentLevel--;
                }
                
                EditorGUILayout.Space(8);
                
                if (GUILayout.Button("📋 Export Project Files", GUILayout.Height(25)))
                {
                    ExportProjectFiles();
                }
            }
            else
            {
                EditorGUILayout.LabelField("❌ Generation Failed", EditorStyles.boldLabel);
                EditorGUILayout.LabelField(lastResult.error_message, EditorStyles.wordWrappedLabel);
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private Color GetStatusColor()
        {
            switch (connectionStatus)
            {
                case ConnectionStatus.Connected: return Color.green;
                case ConnectionStatus.Disconnected: return Color.red;
                case ConnectionStatus.Testing: return Color.yellow;
                case ConnectionStatus.Error: return Color.red;
                default: return Color.gray;
            }
        }
        
        private string GetStatusIcon()
        {
            switch (connectionStatus)
            {
                case ConnectionStatus.Connected: return "✅";
                case ConnectionStatus.Disconnected: return "❌";
                case ConnectionStatus.Testing: return "🔄";
                case ConnectionStatus.Error: return "⚠️";
                default: return "❓";
            }
        }
        
        private void TestConnectionAsync()
        {
            if (connectionStatus == ConnectionStatus.Testing) return;
            
            connectionStatus = ConnectionStatus.Testing;
            connectionMessage = "Testing connection...";
            lastConnectionTest = DateTime.Now;
            
            Task.Run(() =>
            {
                try
                {
                    string pythonPath = GetPythonPath();
                    string scriptPath = GetConnectionTestScriptPath();
                    
                    if (string.IsNullOrEmpty(pythonPath))
                    {
                        EditorApplication.delayCall += () =>
                        {
                            connectionStatus = ConnectionStatus.Error;
                            connectionMessage = "Python not found";
                        };
                        return;
                    }
                    
                    if (string.IsNullOrEmpty(scriptPath))
                    {
                        EditorApplication.delayCall += () =>
                        {
                            connectionStatus = ConnectionStatus.Error;
                            connectionMessage = "Connection test script not found";
                        };
                        return;
                    }
                    
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = pythonPath,
                        Arguments = $"\"{scriptPath}\" --url \"{ollamaUrl}\" --model \"{model}\" --quick --json",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    
                    using (var process = Process.Start(startInfo))
                    {
                        if (process != null)
                        {
                            process.WaitForExit(15000); // 15 second timeout
                            
                            string output = process.StandardOutput.ReadToEnd();
                            string error = process.StandardError.ReadToEnd();
                            
                            EditorApplication.delayCall += () =>
                            {
                                try
                                {
                                    if (process.ExitCode == 0 && !string.IsNullOrEmpty(output))
                                    {
                                        // Parse simple JSON manually for connection test
                                        bool success = output.Contains("\"success\": true");
                                        string message = "Connection test completed";
                                        
                                        // Extract message if possible
                                        int messageStart = output.IndexOf("\"message\": \"");
                                        if (messageStart >= 0)
                                        {
                                            messageStart += 12; // Length of "\"message\": \""
                                            int messageEnd = output.IndexOf("\"", messageStart);
                                            if (messageEnd > messageStart)
                                            {
                                                message = output.Substring(messageStart, messageEnd - messageStart);
                                            }
                                        }
                                        
                                        connectionStatus = success ? ConnectionStatus.Connected : ConnectionStatus.Disconnected;
                                        connectionMessage = message;
                                    }
                                    else
                                    {
                                        connectionStatus = ConnectionStatus.Error;
                                        connectionMessage = string.IsNullOrEmpty(error) ? "Connection test failed" : error;
                                    }
                                }
                                catch (Exception e)
                                {
                                    connectionStatus = ConnectionStatus.Error;
                                    connectionMessage = $"Test error: {e.Message}";
                                }
                            };
                        }
                    }
                }
                catch (Exception e)
                {
                    EditorApplication.delayCall += () =>
                    {
                        connectionStatus = ConnectionStatus.Error;
                        connectionMessage = e.Message;
                    };
                }
            });
        }
        
        private void GenerateProjectAsync(bool forceFallback)
        {
            if (isGenerating) return;
            
            isGenerating = true;
            generationProgress = "Initializing generation...";
            
            Task.Run(() =>
            {
                try
                {
                    string pythonPath = GetPythonPath();
                    string scriptPath = GetIntelligenceScriptPath();
                    
                    if (string.IsNullOrEmpty(pythonPath) || string.IsNullOrEmpty(scriptPath))
                    {
                        EditorApplication.delayCall += () =>
                        {
                            isGenerating = false;
                            generationProgress = "";
                            
                            EditorUtility.DisplayDialog("Error", 
                                "Required Python or script files not found. Please check your setup.", "OK");
                        };
                        return;
                    }
                    
                    // Build arguments
                    string args = $"\"{scriptPath}\" \"{projectDescription}\"";
                    args += $" --type {GetProjectTypeString()}";
                    args += $" --platform {GetPlatformString()}";
                    args += $" --complexity {GetComplexityString()}";
                    args += $" --ollama-url \"{ollamaUrl}\"";
                    args += $" --model \"{model}\"";
                    args += " --json";
                    
                    if (forceFallback)
                    {
                        args += " --force-fallback";
                    }
                    
                    if (additionalRequirements.Count > 0)
                    {
                        args += " --requirements";
                        foreach (string req in additionalRequirements)
                        {
                            args += $" \"{req}\"";
                        }
                    }
                    
                    EditorApplication.delayCall += () => { generationProgress = "Starting AI analysis..."; };
                    
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = pythonPath,
                        Arguments = args,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    
                    currentProcess = Process.Start(startInfo);
                    if (currentProcess != null)
                    {
                        EditorApplication.delayCall += () => { generationProgress = "AI processing request..."; };
                        
                        currentProcess.WaitForExit(180000); // 3 minute timeout
                        
                        string output = currentProcess.StandardOutput.ReadToEnd();
                        string error = currentProcess.StandardError.ReadToEnd();
                        
                        EditorApplication.delayCall += () =>
                        {
                            try
                            {
                                if (currentProcess.ExitCode == 0 && !string.IsNullOrEmpty(output))
                                {
                                    lastResult = JsonUtility.FromJson<ProjectAnalysisResult>(output);
                                    showLastResult = true;
                                    
                                    string resultType = lastResult.ai_generated ? "AI-generated" : "fallback template";
                                    EditorUtility.DisplayDialog("Success", 
                                        $"Project analysis completed using {resultType}!\n\nGenerated: {lastResult.project_name}", "OK");
                                }
                                else
                                {
                                    string errorMsg = string.IsNullOrEmpty(error) ? "Generation failed" : error;
                                    EditorUtility.DisplayDialog("Generation Failed", errorMsg, "OK");
                                }
                            }
                            catch (Exception e)
                            {
                                EditorUtility.DisplayDialog("Error", $"Failed to parse result: {e.Message}", "OK");
                            }
                            finally
                            {
                                isGenerating = false;
                                generationProgress = "";
                                currentProcess = null;
                            }
                        };
                    }
                }
                catch (Exception e)
                {
                    EditorApplication.delayCall += () =>
                    {
                        isGenerating = false;
                        generationProgress = "";
                        currentProcess = null;
                        
                        EditorUtility.DisplayDialog("Error", $"Generation failed: {e.Message}", "OK");
                    };
                }
            });
        }
        
        private void CancelGeneration()
        {
            CleanupProcess();
            isGenerating = false;
            generationProgress = "";
        }
        
        private void CleanupProcess()
        {
            if (currentProcess != null && !currentProcess.HasExited)
            {
                try
                {
                    currentProcess.Kill();
                }
                catch
                {
                    // Process may have already exited
                }
                currentProcess = null;
            }
        }
        
        private void ExportProjectFiles()
        {
            if (lastResult == null || !lastResult.success) return;
            
            string outputPath = EditorUtility.SaveFolderPanel("Export Project Files", "", lastResult.project_name);
            if (string.IsNullOrEmpty(outputPath)) return;
            
            try
            {
                // Create directories
                if (lastResult.structure != null)
                {
                    foreach (var item in lastResult.structure)
                    {
                        string fullPath = Path.Combine(outputPath, item.path);
                        
                        if (item.type == "directory")
                        {
                            Directory.CreateDirectory(fullPath);
                        }
                        else
                        {
                            Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
                            if (!string.IsNullOrEmpty(item.content))
                            {
                                File.WriteAllText(fullPath, item.content);
                            }
                        }
                    }
                }
                
                // Create scripts
                if (lastResult.scripts != null)
                {
                    foreach (var script in lastResult.scripts)
                    {
                        string scriptPath = Path.Combine(outputPath, script.path);
                        Directory.CreateDirectory(Path.GetDirectoryName(scriptPath));
                        File.WriteAllText(scriptPath, script.content);
                    }
                }
                
                // Create README
                string readmePath = Path.Combine(outputPath, "README.md");
                string readme = CreateReadmeContent();
                File.WriteAllText(readmePath, readme);
                
                EditorUtility.DisplayDialog("Export Complete", 
                    $"Project files exported to:\n{outputPath}", "OK");
                    
                // Open the folder
                EditorUtility.RevealInFinder(outputPath);
            }
            catch (Exception e)
            {
                EditorUtility.DisplayDialog("Export Failed", $"Failed to export files: {e.Message}", "OK");
            }
        }
        
        private string CreateReadmeContent()
        {
            var content = new System.Text.StringBuilder();
            
            content.AppendLine($"# {lastResult.project_name}");
            content.AppendLine();
            content.AppendLine(lastResult.description);
            content.AppendLine();
            
            if (lastResult.ai_generated)
            {
                content.AppendLine("*Generated using Warbler AI Project Intelligence*");
            }
            else
            {
                content.AppendLine("*Generated using functional fallback templates*");
            }
            content.AppendLine();
            
            if (lastResult.setup_instructions != null && lastResult.setup_instructions.Count > 0)
            {
                content.AppendLine("## Setup Instructions");
                content.AppendLine();
                for (int i = 0; i < lastResult.setup_instructions.Count; i++)
                {
                    content.AppendLine($"{i + 1}. {lastResult.setup_instructions[i]}");
                }
                content.AppendLine();
            }
            
            if (lastResult.development_notes != null && lastResult.development_notes.Count > 0)
            {
                content.AppendLine("## Development Notes");
                content.AppendLine();
                foreach (string note in lastResult.development_notes)
                {
                    content.AppendLine($"- {note}");
                }
                content.AppendLine();
            }
            
            content.AppendLine("---");
            content.AppendLine($"Generated on {DateTime.Now:yyyy-MM-dd HH:mm:ss} using Warbler AI Project Orchestrator");
            
            return content.ToString();
        }
        
        // Helper methods for UI dropdowns
        private string[] GetProjectTypeOptions()
        {
            return new[] { "Unity 2D Game", "Unity 3D Game", "Unity 2D Platformer" };
        }
        
        private int GetProjectTypeIndex()
        {
            switch (projectType)
            {
                case "unity_2d_game": return 0;
                case "unity_3d_game": return 1;
                case "unity_2d_platformer": return 2;
                default: return 0;
            }
        }
        
        private string GetProjectTypeString()
        {
            string[] types = { "unity_2d_game", "unity_3d_game", "unity_2d_platformer" };
            int index = GetProjectTypeIndex();
            return index < types.Length ? types[index] : "unity_2d_game";
        }
        
        private string[] GetPlatformOptions()
        {
            return new[] { "PC", "Mobile", "Web", "Console" };
        }
        
        private int GetPlatformIndex()
        {
            switch (targetPlatform)
            {
                case "pc": return 0;
                case "mobile": return 1;
                case "web": return 2;
                case "console": return 3;
                default: return 0;
            }
        }
        
        private string GetPlatformString()
        {
            string[] platforms = { "pc", "mobile", "web", "console" };
            int index = GetPlatformIndex();
            return index < platforms.Length ? platforms[index] : "pc";
        }
        
        private string[] GetComplexityOptions()
        {
            return new[] { "Simple", "Medium", "Complex" };
        }
        
        private int GetComplexityIndex()
        {
            switch (complexity)
            {
                case "simple": return 0;
                case "medium": return 1;
                case "complex": return 2;
                default: return 0;
            }
        }
        
        private string GetComplexityString()
        {
            string[] complexities = { "simple", "medium", "complex" };
            int index = GetComplexityIndex();
            return index < complexities.Length ? complexities[index] : "simple";
        }
        
        private string GetPythonPath()
        {
            // Try common Python paths
            string[] pythonPaths = { "python3", "python", "py" };
            
            foreach (string pythonCmd in pythonPaths)
            {
                try
                {
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = pythonCmd,
                        Arguments = "--version",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        CreateNoWindow = true
                    };
                    
                    using (var process = Process.Start(startInfo))
                    {
                        if (process != null)
                        {
                            process.WaitForExit(5000);
                            if (process.ExitCode == 0)
                            {
                                return pythonCmd;
                            }
                        }
                    }
                }
                catch
                {
                    // Continue to next option
                }
            }
            
            return null;
        }
        
        private string GetConnectionTestScriptPath()
        {
            // Look for the connection test script relative to project
            string projectPath = Application.dataPath.Replace("/Assets", "");
            string scriptPath = Path.Combine(projectPath, "scripts", "connection_test.py");
            
            return File.Exists(scriptPath) ? scriptPath : null;
        }
        
        private string GetIntelligenceScriptPath()
        {
            // Look for the intelligence script relative to project
            string projectPath = Application.dataPath.Replace("/Assets", "");
            string scriptPath = Path.Combine(projectPath, "scripts", "warbler_project_intelligence.py");
            
            return File.Exists(scriptPath) ? scriptPath : null;
        }
    }
}
#endif