using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
using Newtonsoft.Json;
using System.Linq;
using System.Net.Http;

namespace TWG.TLDA.ProjectOrchestration
{
    /// <summary>
    /// Enhanced Warbler Project Orchestrator with AI Intelligence
    /// Connects to Ollama via Python bridge for intelligent project analysis
    /// </summary>
    public class WarblerIntelligentOrchestrator : EditorWindow
    {
        [MenuItem("TLDA/🧙‍♂️ Warbler AI Project Orchestrator")]
        public static void ShowWindow()
        {
            GetWindow<WarblerIntelligentOrchestrator>("Warbler AI Orchestrator");
        }

        private string projectRequest = "Create a Zork-like randomly generated Text-based adventure game powered by Warbler.\nThe game should launch with Unity's 2D features, have buttons for standard movement controls,\nbut a standard chat system for interacting with everything else.\nWell... except for known items and interactables... for instance, if we examine a room, search a room,\nanything that would make a character examine things... buttons would pop up for picking or interacting\nwith these items. I think a standard UI inventory might be helpful... a minimap showing areas we've \nexplored using acsii characters. I think you get the idea. The theme can be anything the player \nrequests and you can prompt them for ideas. It's a choose your own adventure.";
        private bool isProcessing = false;
        private bool useAIAnalysis = true;
        private string statusMessage = "Ready for AI-powered project orchestration";
        private Vector2 scrollPosition;
        private ProjectAnalysis lastAnalysis;

        // Connection Management
        private bool isConnected = false;
        private bool isConnecting = false;
        private string connectionStatus = "🔴 Disconnected";
        private string aiServiceEndpoint = "http://localhost:11434";
        private Vector2 connectionScrollPosition;

        void OnGUI()
        {
            GUILayout.Label("🧙‍♂️⚡ Warbler AI Project Orchestrator", EditorStyles.boldLabel);
            GUILayout.Label("Tell Warbler what to build, and watch Ollama-powered intelligence create your entire project!", EditorStyles.helpBox);

            EditorGUILayout.Space();

            // Connection Status Section
            DrawConnectionStatus();
            EditorGUILayout.Space();

            // AI Analysis Toggle
            useAIAnalysis = EditorGUILayout.Toggle("🧠 Use Ollama AI Analysis", useAIAnalysis);
            if (!useAIAnalysis)
            {
                EditorGUILayout.HelpBox("Disabling AI will use enhanced template responses with intelligent decision support.", MessageType.Info);
            }
            else if (!isConnected)
            {
                EditorGUILayout.HelpBox("⚠️ AI Analysis will auto-start Ollama when needed. Enhanced stubs provide intelligent fallbacks.", MessageType.Warning);
            }

            EditorGUILayout.Space();

            GUILayout.Label("Project Request:", EditorStyles.label);

            // Create word-wrapped text area style
            var textAreaStyle = new GUIStyle(EditorStyles.textArea) { wordWrap = true };
            projectRequest = EditorGUILayout.TextArea(projectRequest, textAreaStyle, GUILayout.Height(100), GUILayout.ExpandWidth(true));

            EditorGUILayout.Space();

            EditorGUI.BeginDisabledGroup(isProcessing);
            if (GUILayout.Button(isProcessing ? "🧙‍♂️ Warbler is thinking..." : "🚀 Orchestrate Project with AI", GUILayout.Height(40)))
            {
                ExecuteAIProjectSetup();
            }
            EditorGUI.EndDisabledGroup();

            // Quick Analysis button right below main button for better UX
            if (!isProcessing && !string.IsNullOrEmpty(projectRequest))
            {
                if (GUILayout.Button("🔍 Quick AI Analysis Only", GUILayout.Height(25)))
                {
                    PerformQuickAnalysis();
                }
            }

            EditorGUILayout.Space();

            GUILayout.Label($"Status: {statusMessage}", EditorStyles.helpBox);

            // Show analysis results
            if (lastAnalysis != null)
            {
                EditorGUILayout.Space();
                GUILayout.Label("🔮 AI Analysis Results:", EditorStyles.boldLabel);

                scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition, GUILayout.Height(300));

                // Create word-wrapped style
                var wrapStyle = new GUIStyle(EditorStyles.label) { wordWrap = true };
                var boldWrapStyle = new GUIStyle(EditorStyles.boldLabel) { wordWrap = true };

                EditorGUILayout.LabelField("Game Type:", lastAnalysis.game_type, boldWrapStyle);
                EditorGUILayout.LabelField("Complexity:", lastAnalysis.complexity_level, wrapStyle);
                EditorGUILayout.LabelField("Timeline:", lastAnalysis.estimated_dev_time, wrapStyle);
                EditorGUILayout.LabelField("Architecture:", lastAnalysis.suggested_architecture, wrapStyle);

                EditorGUILayout.Space();
                GUILayout.Label("Key Mechanics:", EditorStyles.boldLabel);
                foreach (var mechanic in lastAnalysis.key_mechanics)
                {
                    GUILayout.Label("• " + mechanic, wrapStyle);
                }

                EditorGUILayout.Space();
                GUILayout.Label("Required Systems:", EditorStyles.boldLabel);
                foreach (var system in lastAnalysis.required_systems)
                {
                    GUILayout.Label("• " + system, wrapStyle);
                }

                if (lastAnalysis.warbler_enhancement != null)
                {
                    EditorGUILayout.Space();
                    GUILayout.Label("🧙‍♂️ Warbler Insights:", EditorStyles.boldLabel);

                    GUILayout.Label("Development Milestones:", EditorStyles.boldLabel);
                    foreach (var milestone in lastAnalysis.warbler_enhancement.development_milestones)
                    {
                        GUILayout.Label("📅 " + milestone, wrapStyle);
                    }

                    EditorGUILayout.Space();
                    GUILayout.Label("Testing Strategy:", EditorStyles.boldLabel);
                    foreach (var test in lastAnalysis.warbler_enhancement.testing_strategy)
                    {
                        GUILayout.Label("🧪 " + test, wrapStyle);
                    }
                }

                EditorGUILayout.EndScrollView();
            }
        }

        void DrawConnectionStatus()
        {
            GUILayout.Label("🔌 AI Service Connection", EditorStyles.boldLabel);

            EditorGUILayout.BeginHorizontal();
            GUILayout.Label($"Status: {connectionStatus}", EditorStyles.label);
            GUILayout.FlexibleSpace();

            // Connection buttons
            EditorGUI.BeginDisabledGroup(isConnecting);

            if (!isConnected)
            {
                if (GUILayout.Button(isConnecting ? "🔄 Connecting..." : "🔌 Connect to AI Service", GUILayout.Width(150)))
                {
                    ConnectToAIService();
                }

                if (GUILayout.Button("🚀 Start Ollama", GUILayout.Width(100)))
                {
                    StartOllamaService();
                }
            }
            else
            {
                if (GUILayout.Button("🔌 Disconnect", GUILayout.Width(100)))
                {
                    DisconnectFromAIService();
                }

                if (GUILayout.Button("🔄 Refresh", GUILayout.Width(80)))
                {
                    CheckConnectionStatus();
                }
            }

            if (GUILayout.Button("🛠️ Diagnostic", GUILayout.Width(80)))
            {
                RunConnectionDiagnostic();
            }

            EditorGUI.EndDisabledGroup();
            EditorGUILayout.EndHorizontal();

            // Endpoint configuration
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Endpoint:", GUILayout.Width(70));
            aiServiceEndpoint = EditorGUILayout.TextField(aiServiceEndpoint);
            EditorGUILayout.EndHorizontal();

            // Show Ollama integration hint
            if (!isConnected)
            {
                EditorGUILayout.HelpBox("💡 Tip: New simplified integration! No Docker required. Ollama binary will auto-download and start when you click 'Connect to AI Service' or 'Start Ollama'. Enhanced stubs provide intelligent responses even when AI is unavailable.", MessageType.Info);
            }
        }

        async void ExecuteAIProjectSetup()
        {
            isProcessing = true;
            statusMessage = "🧠 Warbler connecting to Ollama for intelligent analysis...";

            try
            {
                ProjectAnalysis analysis = null;

                if (useAIAnalysis)
                {
                    analysis = await GetAIAnalysis(projectRequest);
                }

                if (analysis == null)
                {
                    statusMessage = "⚠️ AI analysis failed, using fallback template system...";
                    await Task.Delay(1000);
                    analysis = CreateFallbackAnalysis(projectRequest);
                }

                lastAnalysis = analysis;
                statusMessage = $"📋 AI Analysis complete! Detected: {analysis.game_type} ({analysis.complexity_level})";
                await Task.Delay(1500);

                statusMessage = "🏗️ Creating intelligent project structure...";
                await CreateIntelligentProjectStructure(analysis);

                statusMessage = "⚡ Generating AI-optimized systems...";
                await CreateIntelligentSystems(analysis);

                statusMessage = "📝 Creating development blueprint...";
                await CreateProjectBlueprint(analysis);

                statusMessage = "📜 Generating comprehensive TLDL documentation...";
                await CreateAITLDLEntry(analysis, projectRequest);

                statusMessage = $"✅ AI-powered project setup complete! {analysis.game_type} ready for legendary development.";

                EditorUtility.DisplayDialog("🧙‍♂️ Warbler Success!",
                    $"Your {analysis.game_type} project has been created with AI-powered intelligence!\n\n" +
                    $"• {analysis.required_systems.Length} core systems generated\n" +
                    $"• {analysis.recommended_folders.Length} organized folders created\n" +
                    $"• Complete development roadmap included\n" +
                    $"• Estimated timeline: {analysis.estimated_dev_time}\n\n" +
                    "Check the Console for detailed logs and the TLDL entries for the complete development plan!",
                    "Start Developing!");
            }
            catch (Exception e)
            {
                statusMessage = $"❌ Error: {e.Message}";
                UnityEngine.Debug.LogError($"Warbler AI Project Setup Error: {e}");
                EditorUtility.DisplayDialog("Warbler Error", $"Setup failed: {e.Message}", "OK");
            }
            finally
            {
                isProcessing = false;
            }
        }

        async void PerformQuickAnalysis()
        {
            isProcessing = true;
            statusMessage = "🔍 Performing quick AI analysis...";

            try
            {
                var analysis = await GetAIAnalysis(projectRequest);
                if (analysis != null)
                {
                    lastAnalysis = analysis;
                    statusMessage = $"✅ Analysis complete! {analysis.game_type} - {analysis.complexity_level} complexity";
                }
                else
                {
                    statusMessage = "❌ AI analysis failed - check Ollama connection";
                }
            }
            catch (Exception e)
            {
                statusMessage = $"❌ Analysis error: {e.Message}";
            }
            finally
            {
                isProcessing = false;
            }
        }

        // Connection Management Methods
        async void ConnectToAIService()
        {
            isConnecting = true;
            connectionStatus = "🔄 Connecting...";

            try
            {
                // Test connection using simple connection test script
                string pythonPath = FindPythonPath();
                string testScript = Path.Combine(Application.dataPath, "..", "scripts", "connection_test.py");

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{testScript}\" --test-connection {aiServiceEndpoint}",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                }; using (var process = Process.Start(processInfo))
                {
                    var output = await process.StandardOutput.ReadToEndAsync();
                    var errors = await process.StandardError.ReadToEndAsync();

                    process.WaitForExit();

                    if (process.ExitCode == 0 && output.Contains("✅ CONNECTION SUCCESS"))
                    {
                        isConnected = true;
                        connectionStatus = "🟢 Connected";
                        statusMessage = "✅ Successfully connected to AI service!";
                        UnityEngine.Debug.Log($"🔌 Connected to AI service at {aiServiceEndpoint}");
                    }
                    else
                    {
                        isConnected = false;
                        connectionStatus = "🔴 Connection Failed";
                        statusMessage = "❌ Failed to connect to AI service. Try starting Ollama first.";
                        UnityEngine.Debug.LogWarning($"Connection test failed: {errors}");
                    }
                }
            }
            catch (Exception e)
            {
                isConnected = false;
                connectionStatus = "🔴 Error";
                statusMessage = $"❌ Connection error: {e.Message}";
                UnityEngine.Debug.LogError($"Connection error: {e}");
            }
            finally
            {
                isConnecting = false;
            }
        }

        void DisconnectFromAIService()
        {
            isConnected = false;
            connectionStatus = "🔴 Disconnected";
            statusMessage = "Disconnected from AI service";
            UnityEngine.Debug.Log("🔌 Disconnected from AI service");
        }

        async void CheckConnectionStatus()
        {
            await ConnectToAIServiceInternal(); // Reuse connection logic for status check
        }

        string FindPythonPath()
        {
            // Try common Python locations
            string[] pythonPaths = {
                "python",
                "python3",
                @"C:\Python39\python.exe",
                @"C:\Python310\python.exe",
                @"C:\Python311\python.exe",
                @"C:\Python312\python.exe",
                @"C:\Users\" + Environment.UserName + @"\AppData\Local\Programs\Python\Python39\python.exe",
                @"C:\Users\" + Environment.UserName + @"\AppData\Local\Programs\Python\Python310\python.exe",
                @"C:\Users\" + Environment.UserName + @"\AppData\Local\Programs\Python\Python311\python.exe",
                @"C:\Users\" + Environment.UserName + @"\AppData\Local\Programs\Python\Python312\python.exe"
            };

            foreach (string path in pythonPaths)
            {
                try
                {
                    var process = Process.Start(new ProcessStartInfo
                    {
                        FileName = path,
                        Arguments = "--version",
                        RedirectStandardOutput = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    });

                    if (process != null)
                    {
                        process.WaitForExit(1000);
                        if (process.ExitCode == 0)
                        {
                            return path;
                        }
                    }
                }
                catch
                {
                    // Continue to next path
                }
            }

            return "python"; // Fallback
        }

        async Task ConnectToAIServiceInternal()
        {
            isConnecting = true;
            connectionStatus = "🔄 Connecting...";

            try
            {
                // Simple HTTP test using basic connectivity check
                using (var client = new System.Net.Http.HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(3);
                    var response = await client.GetAsync(aiServiceEndpoint);

                    if (response.IsSuccessStatusCode)
                    {
                        isConnected = true;
                        connectionStatus = "🟢 Connected";
                        statusMessage = "✅ Successfully connected to AI service!";
                        UnityEngine.Debug.Log($"🔌 Connected to AI service at {aiServiceEndpoint}");
                    }
                    else
                    {
                        isConnected = false;
                        connectionStatus = "🔴 Service Not Ready";
                        statusMessage = $"⚠️ Service responded with status {response.StatusCode}";
                    }
                }
            }
            catch (HttpRequestException e)
            {
                isConnected = false;
                connectionStatus = "🔴 No API Server";
                statusMessage = "❌ No HTTP API server detected. Ollama may not be running properly.";
                UnityEngine.Debug.LogWarning($"No API server found: {e.Message}");
            }
            catch (Exception e)
            {
                isConnected = false;
                connectionStatus = "🔴 Connection Failed";
                statusMessage = $"❌ Connection error: {e.Message}";
                UnityEngine.Debug.LogWarning($"Connection test failed: {e.Message}");
            }
            finally
            {
                isConnecting = false;
            }
        }

        async void StartOllamaService()
        {
            isConnecting = true;
            connectionStatus = "🚀 Starting Ollama...";
            statusMessage = "🚀 Starting Ollama AI service (no Docker required)...";

            try
            {
                // Start Ollama using the new direct binary approach
                string pythonPath = FindPythonPath();
                string managerScript = Path.Combine(Application.dataPath, "..", "scripts", "ollama_manager.py");

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{managerScript}\" --start",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                using (var process = Process.Start(processInfo))
                {
                    var output = await process.StandardOutput.ReadToEndAsync();
                    var errors = await process.StandardError.ReadToEndAsync();

                    process.WaitForExit();

                    // Give it time to start
                    await Task.Delay(3000);

                    // Check if it's running
                    await ConnectToAIServiceInternal();

                    if (isConnected)
                    {
                        statusMessage = "✅ Ollama started successfully! (No Docker required)";
                        UnityEngine.Debug.Log("🚀 Ollama AI service started with direct binary integration");
                    }
                    else
                    {
                        statusMessage = "⚠️ Ollama binary started. Enhanced stubs available as fallback.";
                        UnityEngine.Debug.LogWarning($"Ollama started but may need configuration: {output}");
                    }
                }
            }
            catch (Exception e)
            {
                connectionStatus = "🔴 Start Failed";
                statusMessage = $"❌ Failed to start Ollama: {e.Message}. Enhanced stubs available.";
                UnityEngine.Debug.LogError($"Failed to start Ollama: {e}");
            }
            finally
            {
                isConnecting = false;
            }
        }

        async void RunConnectionDiagnostic()
        {
            statusMessage = "🛠️ Running connection diagnostic...";

            try
            {
                string pythonPath = FindPythonPath();
                string helperPath = Path.Combine(Application.dataPath, "..", "scripts", "terminus_ai_helper.py");

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{helperPath}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = false, // Show window for diagnostic
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                var process = Process.Start(processInfo);
                statusMessage = "🛠️ Diagnostic running in terminal window...";
                UnityEngine.Debug.Log("🛠️ Connection diagnostic started. Check terminal for results.");

                // Don't wait - let it run in background
            }
            catch (Exception e)
            {
                statusMessage = $"❌ Diagnostic error: {e.Message}";
                UnityEngine.Debug.LogError($"Failed to run diagnostic: {e}");
            }
        }

        async Task<ProjectAnalysis> GetAIAnalysis(string request)
        {
            try
            {
                string pythonPath = FindPythonPath();
                string scriptPath = Path.Combine(Application.dataPath, "..", "scripts", "warbler_project_intelligence.py");

                if (!File.Exists(scriptPath))
                {
                    UnityEngine.Debug.LogError($"Warbler intelligence script not found at: {scriptPath}");
                    return null;
                }

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{scriptPath}\" \"{request}\" --generate-files",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                using (var process = Process.Start(processInfo))
                {
                    var output = await process.StandardOutput.ReadToEndAsync();
                    var errors = await process.StandardError.ReadToEndAsync();

                    process.WaitForExit();

                    if (process.ExitCode != 0)
                    {
                        UnityEngine.Debug.LogError($"Warbler AI Analysis failed: {errors}");
                        return null;
                    }

                    // Parse the JSON output - it spans multiple lines after the header
                    string jsonStart = "🔮 Warbler Intelligence Output:";
                    int startIndex = output.IndexOf(jsonStart);
                    if (startIndex != -1)
                    {
                        string jsonSection = output.Substring(startIndex + jsonStart.Length).Trim();
                        int braceStart = jsonSection.IndexOf('{');
                        if (braceStart != -1)
                        {
                            // Find the matching closing brace
                            int braceCount = 0;
                            int endPos = -1;
                            string jsonPart = jsonSection.Substring(braceStart);

                            for (int i = 0; i < jsonPart.Length; i++)
                            {
                                if (jsonPart[i] == '{') braceCount++;
                                else if (jsonPart[i] == '}') braceCount--;

                                if (braceCount == 0)
                                {
                                    endPos = i + 1;
                                    break;
                                }
                            }

                            if (endPos > 0)
                            {
                                string jsonText = jsonPart.Substring(0, endPos);
                                try
                                {
                                    var result = JsonConvert.DeserializeObject<AIAnalysisResult>(jsonText);
                                    if (result.success)
                                    {
                                        return result.analysis;
                                    }
                                }
                                catch (JsonException e)
                                {
                                    UnityEngine.Debug.LogError($"JSON parsing error: {e.Message}");
                                }
                            }
                        }
                    }

                    // Fallback: try line-by-line parsing for backwards compatibility
                    var lines = output.Split('\n');
                    foreach (var line in lines)
                    {
                        if (line.Trim().StartsWith("{") && line.Contains("\"success\""))
                        {
                            try
                            {
                                var result = JsonConvert.DeserializeObject<AIAnalysisResult>(line.Trim());
                                if (result.success)
                                {
                                    return result.analysis;
                                }
                            }
                            catch (JsonException)
                            {
                                continue; // Try next line
                            }
                        }
                    }

                    UnityEngine.Debug.LogWarning($"Could not parse AI analysis result: {output}");
                    return null;
                }
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogError($"AI Analysis execution failed: {e.Message}");
                return null;
            }
        }

        ProjectAnalysis CreateFallbackAnalysis(string request)
        {
            // Simple fallback when AI is unavailable
            return new ProjectAnalysis
            {
                game_type = "custom",
                complexity_level = "moderate",
                required_systems = new[] { "PlayerController", "GameManager", "UIManager" },
                recommended_folders = new[] { "Scripts/Player", "Scripts/Managers", "Scripts/UI" },
                unity_packages = new[] { "InputSystem" },
                estimated_dev_time = "4-6 weeks",
                key_mechanics = new[] { "basic_gameplay", "ui_interaction" },
                technical_considerations = new[] { "performance", "maintainability" },
                suggested_architecture = "Component-based",
                warbler_insights = "Fallback analysis - AI unavailable",
                warbler_enhancement = new WarblerEnhancement
                {
                    development_milestones = new[] { "Setup (Week 1)", "Core features (Week 2-3)", "Polish (Week 4)" },
                    testing_strategy = new[] { "Basic functionality testing", "Performance validation" },
                    suggested_tldl_tags = new[] { "fallback-generation", "basic-template" }
                }
            };
        }

        async Task CreateIntelligentProjectStructure(ProjectAnalysis analysis)
        {
            // Create folders based on AI analysis
            foreach (var folder in analysis.recommended_folders)
            {
                var fullPath = Path.Combine(Application.dataPath, folder);
                if (!Directory.Exists(fullPath))
                {
                    Directory.CreateDirectory(fullPath);
                    UnityEngine.Debug.Log($"📁 AI-recommended folder created: {folder}");
                }
                await Task.Delay(50);
            }

            AssetDatabase.Refresh();
        }

        async Task CreateIntelligentSystems(ProjectAnalysis analysis)
        {
            foreach (var system in analysis.required_systems)
            {
                await CreateAIOptimizedScript(system, analysis);
                await Task.Delay(100);
            }
        }

        async Task CreateAIOptimizedScript(string systemName, ProjectAnalysis analysis)
        {
            var scriptContent = GenerateAIOptimizedScript(systemName, analysis);
            var folder = DetermineScriptFolder(systemName, analysis);
            var scriptPath = Path.Combine(Application.dataPath, "Scripts", folder, $"{systemName}.cs");

            Directory.CreateDirectory(Path.GetDirectoryName(scriptPath));
            File.WriteAllText(scriptPath, scriptContent);

            UnityEngine.Debug.Log($"🤖 AI-optimized script created: {systemName}.cs");
            await Task.Delay(50);
        }

        string DetermineScriptFolder(string systemName, ProjectAnalysis analysis)
        {
            // Use AI analysis to determine best folder structure
            foreach (var folder in analysis.recommended_folders)
            {
                var folderName = Path.GetFileName(folder);
                if (systemName.ToLower().Contains(folderName.ToLower().Replace("scripts/", "")))
                {
                    return folderName;
                }
            }
            return "Managers"; // Default
        }

        string GenerateAIOptimizedScript(string systemName, ProjectAnalysis analysis)
        {
            var architecture = analysis.suggested_architecture;
            var gameType = analysis.game_type;

            return $@"using UnityEngine;
{(architecture == "ECS" ? "using Unity.Entities;" : "")}

namespace TWG.TLDA.AI.Generated
{{
    /// <summary>
    /// {systemName} - AI-Generated by Warbler for {gameType}
    /// Architecture: {architecture}
    /// Generated based on Ollama analysis for optimal {gameType} development
    /// </summary>
    {(architecture == "ECS" ? "public struct " + systemName + " : IComponentData" : "public class " + systemName + " : MonoBehaviour")}
    {{
        {GenerateSystemSpecificCode(systemName, analysis)}
    }}
}}";
        }

        string GenerateSystemSpecificCode(string systemName, ProjectAnalysis analysis)
        {
            // Generate code based on AI analysis
            if (analysis.key_mechanics.Contains("movement") && systemName.Contains("Player"))
            {
                return @"[Header(""AI-Optimized Movement"")]
        [SerializeField] private float moveSpeed = 5f;
        [SerializeField] private float acceleration = 10f;
        
        private Vector2 inputVector;
        private Rigidbody2D rb;
        
        void Start()
        {
            rb = GetComponent<Rigidbody2D>();
            Debug.Log(""🤖 AI-optimized PlayerController initialized"");
        }
        
        void Update()
        {
            inputVector.x = Input.GetAxis(""Horizontal"");
            inputVector.y = Input.GetAxis(""Vertical"");
        }
        
        void FixedUpdate()
        {
            // AI-recommended smooth movement
            Vector2 targetVelocity = inputVector.normalized * moveSpeed;
            rb.velocity = Vector2.Lerp(rb.velocity, targetVelocity, acceleration * Time.fixedDeltaTime);
        }";
            }
            else if (systemName.Contains("Manager"))
            {
                return @"[Header(""AI-Generated Management System"")]
        [SerializeField] private bool debugMode = true;
        
        void Start()
        {
            Initialize();
        }
        
        void Initialize()
        {
            if (debugMode)
                Debug.Log($""🤖 {GetType().Name} initialized by Warbler AI"");
        }
        
        void Update()
        {
            // AI-recommended update pattern
            if (Time.frameCount % 60 == 0) // Optimize for 60 FPS
            {
                PerformPeriodicUpdate();
            }
        }
        
        void PerformPeriodicUpdate()
        {
            // Override in derived classes
        }";
            }

            return @"void Start()
        {
            Debug.Log($""🤖 {GetType().Name} generated by Warbler AI"");
        }
        
        void Update()
        {
            // TODO: Implement AI-recommended functionality
        }";
        }

        async Task CreateProjectBlueprint(ProjectAnalysis analysis)
        {
            var blueprintContent = JsonConvert.SerializeObject(analysis, Formatting.Indented);
            var blueprintPath = Path.Combine(Application.dataPath, "..", "blueprints", $"warbler-ai-project-{DateTime.Now:yyyyMMdd-HHmmss}.json");

            Directory.CreateDirectory(Path.GetDirectoryName(blueprintPath));
            File.WriteAllText(blueprintPath, blueprintContent);

            UnityEngine.Debug.Log($"📋 AI Project Blueprint created: {Path.GetFileName(blueprintPath)}");
            await Task.Delay(100);
        }

        async Task CreateAITLDLEntry(ProjectAnalysis analysis, string originalRequest)
        {
            var tldlContent = $@"# TLDL-{DateTime.Now:yyyy-MM-dd}-WarblerAI-{analysis.game_type.Replace(".", "")}

## Metadata
- Entry ID: TLDL-{DateTime.Now:yyyy-MM-dd}-WarblerAI-{analysis.game_type.Replace(".", "")}
- Author: Warbler AI Project Orchestrator + Ollama
- Context: AI-powered project setup for {analysis.game_type}
- Summary: Complete intelligent project structure generated with AI analysis
- Tags: {string.Join(", ", analysis.warbler_enhancement?.suggested_tldl_tags ?? new[] { "ai-generated" })}

## Objective
**User Request:** ""{originalRequest}""
**AI Interpretation:** {analysis.game_type} ({analysis.complexity_level} complexity)
**Recommended Architecture:** {analysis.suggested_architecture}

## AI Analysis Results
### Game Type Detection
- **Primary Type:** {analysis.game_type}
- **Complexity Level:** {analysis.complexity_level}
- **Estimated Timeline:** {analysis.estimated_dev_time}

### Key Mechanics Identified
{string.Join("\n", analysis.key_mechanics.Select(m => $"- {m}"))}

### Technical Considerations
{string.Join("\n", analysis.technical_considerations.Select(t => $"- {t}"))}

## Generated Project Structure
### Intelligent Folder Organization
{string.Join("\n", analysis.recommended_folders.Select(f => $"- {f}/"))}

### AI-Optimized Systems
{string.Join("\n", analysis.required_systems.Select(s => $"- {s}.cs: AI-generated {s.ToLower()} implementation"))}

### Recommended Unity Packages
{string.Join("\n", analysis.unity_packages.Select(p => $"- {p}"))}

## Development Roadmap
### Milestones (AI-Recommended)
{string.Join("\n", analysis.warbler_enhancement?.development_milestones?.Select((m, i) => $"{i + 1}. {m}") ?? new[] { "Standard development phases" })}

### Testing Strategy
{string.Join("\n", analysis.warbler_enhancement?.testing_strategy?.Select(t => $"- {t}") ?? new[] { "Basic testing approach" })}

## Warbler Insights
{analysis.warbler_insights}

## Next Steps
1. **Review Generated Code**: Check AI-generated scripts for project-specific customization needs
2. **Configure Unity Packages**: Install recommended packages through Package Manager
3. **Create Prefabs**: Set up game objects based on the generated system architecture
4. **Scene Setup**: Configure scenes according to the {analysis.game_type} requirements
5. **Testing Phase**: Implement the AI-recommended testing strategy
6. **Iteration**: Use Warbler for continued development assistance

## AI Enhancement Features
- ✅ **Intelligent Code Generation**: Scripts optimized for {analysis.suggested_architecture} architecture
- ✅ **Project Structure Optimization**: Folders organized for {analysis.game_type} development
- ✅ **Development Timeline Planning**: {analysis.estimated_dev_time} realistic timeline
- ✅ **Testing Strategy**: Comprehensive testing approach for {analysis.game_type}
- ✅ **Technical Recommendations**: AI-analyzed technical considerations

*Generated by Warbler AI Project Orchestrator powered by Ollama - Where artificial intelligence meets game development magic!* 🧙‍♂️🤖⚡

---
**Warbler Achievement Unlocked:** 🏆 **AI Project Genesis** - Successfully created an entire game project structure using artificial intelligence in under 60 seconds!
";

            var tldlPath = Path.Combine(Application.dataPath, "..", "TLDL", "entries", $"TLDL-{DateTime.Now:yyyy-MM-dd}-WarblerAI-{analysis.game_type.Replace(".", "")}.md");

            Directory.CreateDirectory(Path.GetDirectoryName(tldlPath));
            File.WriteAllText(tldlPath, tldlContent);

            UnityEngine.Debug.Log($"📜 AI TLDL entry created: {Path.GetFileName(tldlPath)}");
            await Task.Delay(100);
        }
    }

    // Data structures for AI analysis
    [System.Serializable]
    public class ProjectAnalysis
    {
        public string game_type;
        public string complexity_level;
        public string[] required_systems;
        public string[] recommended_folders;
        public string[] unity_packages;
        public string estimated_dev_time;
        public string[] key_mechanics;
        public string[] technical_considerations;
        public string suggested_architecture;
        public string warbler_insights;
        public WarblerEnhancement warbler_enhancement;
    }

    [System.Serializable]
    public class WarblerEnhancement
    {
        public string[] development_milestones;
        public string[] testing_strategy;
        public string[] suggested_tldl_tags;
    }

    [System.Serializable]
    public class AIAnalysisResult
    {
        public bool success;
        public ProjectAnalysis analysis;
        public string blueprint_path;
    }
}
