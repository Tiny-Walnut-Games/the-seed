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
        private ProjectAnalysis lastAnalysis = null;

        // Connection Management
        private bool isConnected = false;
        private bool isConnecting = false;
        private string connectionStatus = "🔴 Disconnected";
        private string aiServiceEndpoint = "http://localhost:11434";
        private Vector2 connectionScrollPosition;

        // GitHub Copilot Integration
        private bool githubCopilotAvailable = false;
        private bool githubCopilotConnected = false;
        private bool githubCopilotAuthenticating = false;
        private string githubCopilotStatus = "🔒 Not Authenticated";
        private bool preferGitHubCopilot = true;  // Default to GitHub first
        private System.DateTime lastRefreshAll = System.DateTime.MinValue; // throttle refresh all
        private readonly string[] ollamaModelOptions = new[] {
            "llama3.2:1b",
            "llama3.2:3b",
            "phi3:mini",
            "gemma2:2b",
            "qwen2:1.5b",
            "mistral:7b",
            "llama3.1:8b"
        };
        private int selectedModelIndex = 0;
        // private System.Diagnostics.Process ollamaServeProcess = null;  // Reserved for 👀 future expansion
        private string ollamaLogPath = string.Empty;
        private System.Diagnostics.Process ollamaServeProcess = null;

        void OnGUI()
        {
            GUILayout.Label("🧙‍♂️⚡ Warbler AI Project Orchestrator", EditorStyles.boldLabel);
            GUILayout.Label("Tell Warbler what to build, and watch AI intelligence create your entire project!", EditorStyles.helpBox);

            EditorGUILayout.Space();

            // AI Provider Selection
            DrawAIProviderSelection();
            EditorGUILayout.Space();

            // Connection Status Section
            DrawConnectionStatus();
            EditorGUILayout.Space();

            // AI Analysis Toggle
            EditorGUILayout.BeginHorizontal();
            useAIAnalysis = EditorGUILayout.Toggle("🧠 Use AI Analysis", useAIAnalysis);

            if (useAIAnalysis)
            {
                GUILayout.Label("Provider:", GUILayout.Width(60));
                string providerLabel = preferGitHubCopilot ?
                    (githubCopilotConnected ? "🔐 GitHub Copilot" : "🔒 GitHub (Not Auth)") :
                    (isConnected ? "🟢 Ollama" : "🔴 Ollama (Offline)");

                if (GUILayout.Button(providerLabel, GUILayout.Width(140)))
                {
                    // Toggle provider preference
                    preferGitHubCopilot = !preferGitHubCopilot;
                    UpdateProviderStatus();
                }
            }
            EditorGUILayout.EndHorizontal();

            if (!useAIAnalysis)
            {
                EditorGUILayout.HelpBox("Disabling AI will use enhanced template responses with intelligent decision support.", MessageType.Info);
            }
            else if (!githubCopilotConnected && !isConnected)
            {
                EditorGUILayout.HelpBox("⚠️ AI Analysis will auto-start Ollama when needed. Enhanced stubs provide intelligent fallbacks.", MessageType.Warning);
            }
            else if (preferGitHubCopilot && !githubCopilotConnected)
            {
                EditorGUILayout.HelpBox("ℹ️ GitHub Copilot preferred but not connected. Will fallback to Ollama if available.", MessageType.Info);
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

        void DrawAIProviderSelection()
        {
            GUILayout.Label("🤖 AI Provider Selection", EditorStyles.boldLabel);

            EditorGUILayout.BeginHorizontal();

            // GitHub Copilot section
            EditorGUILayout.BeginVertical("box", GUILayout.Width(200));
            GUILayout.Label("🔐 GitHub Copilot", EditorStyles.boldLabel);
            GUILayout.Label($"Status: {githubCopilotStatus}");

            EditorGUI.BeginDisabledGroup(githubCopilotAuthenticating);
            if (!githubCopilotConnected)
            {
                if (GUILayout.Button(githubCopilotAuthenticating ? "🔄 Authenticating..." : "🔐 Connect GitHub Copilot"))
                {
                    AuthenticateGitHubCopilot();
                }
            }
            else
            {
                if (GUILayout.Button("✅ Connected"))
                {
                    // Maybe show connection details or allow disconnect
                }
            }
            EditorGUI.EndDisabledGroup();

            EditorGUILayout.EndVertical();

            GUILayout.Space(10);

            // Ollama section
            EditorGUILayout.BeginVertical("box", GUILayout.Width(200));
            GUILayout.Label("🦙 Ollama (Local)", EditorStyles.boldLabel);
            GUILayout.Label($"Status: {connectionStatus}");

            EditorGUI.BeginDisabledGroup(isConnecting);
            if (!isConnected)
            {
                if (GUILayout.Button(isConnecting ? "🔄 Connecting..." : "🔌 Connect Ollama"))
                {
                    ConnectToAIService();
                }
            }
            else
            {
                if (GUILayout.Button("✅ Connected"))
                {
                    // Maybe show connection details or allow disconnect
                }
            }
            EditorGUI.EndDisabledGroup();

            EditorGUILayout.EndVertical();

            EditorGUILayout.EndHorizontal();

            // Provider preference
            EditorGUILayout.Space();
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Preferred Provider:", GUILayout.Width(120));

            if (GUILayout.Toggle(preferGitHubCopilot, "GitHub Copilot First", GUILayout.Width(140)))
            {
                if (!preferGitHubCopilot)
                {
                    preferGitHubCopilot = true;
                    UpdateProviderStatus();
                }
            }

            if (GUILayout.Toggle(!preferGitHubCopilot, "Ollama First", GUILayout.Width(100)))
            {
                if (preferGitHubCopilot)
                {
                    preferGitHubCopilot = false;
                    UpdateProviderStatus();
                }
            }

            EditorGUILayout.EndHorizontal();
        }

        void DrawConnectionStatus()
        {
            GUILayout.Label("🔌 Connection Details", EditorStyles.boldLabel);

            EditorGUILayout.BeginHorizontal();
            GUILayout.Label($"Overall Status: {GetOverallConnectionStatus()}", EditorStyles.label);
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
                    _ = CheckConnectionStatus(); // Fire and forget with discard
                }
            }

            // Advanced connection tools
            if (GUILayout.Button("🔄 Refresh All", GUILayout.Width(100)))
            {
                var now = System.DateTime.UtcNow;
                if ((now - lastRefreshAll).TotalSeconds < 2)
                {
                    statusMessage = "⏳ Please wait a moment before refreshing again";
                    ShowNotification(new GUIContent("Please wait before refreshing again"));
                }
                else
                {
                    lastRefreshAll = now;
                    _ = CheckAllProviderStatus(); // fire and forget
                    ShowNotification(new GUIContent("Refreshing provider status…"));
                }
            }

            if (GUILayout.Button("🛠️ Diagnostic", GUILayout.Width(80)))
            {
                RunConnectionDiagnostic();
            }

            if (GUILayout.Button("🧪 Deep Diagnostic", GUILayout.Width(120)))
            {
                _ = RunDeepDiagnostic();
            }

            if (GUILayout.Button("🚀 Full Setup", GUILayout.Width(80)))
            {
                _ = RunFullSetup(); // fire and forget
            }

            if (GUILayout.Button("💬 Chat", GUILayout.Width(60)))
            {
                // Open the Warbler Chat window via reflection (assembly-safe)
                var chatType = Type.GetType("TWG.TLDA.Chat.WarblerChatWindow, Assembly-CSharp-Editor")
                               ?? Type.GetType("TWG.TLDA.Chat.WarblerChatWindow, Assembly-CSharp");
                if (chatType != null)
                {
                    EditorWindow.GetWindow(chatType, false, "Warbler Chat", true);
                }
                else
                {
                    statusMessage = "❌ Warbler Chat window type not found";
                    UnityEngine.Debug.LogWarning("Could not locate WarblerChatWindow type. Ensure the script exists in an Editor assembly.");
                }
            }

            if (GUILayout.Button("📄 Logs", GUILayout.Width(60)))
            {
                OpenOllamaLogs();
            }

            if (GUILayout.Button("❤️ Health", GUILayout.Width(70)))
            {
                _ = RunOllamaHealthCheckAsync();
            }

            if (GUILayout.Button("⏹ Stop", GUILayout.Width(60)))
            {
                _ = StopOllamaServiceAsync();
            }

            if (GUILayout.Button("📖 Help", GUILayout.Width(60)))
            {
                ShowProgressGuide();
            }

            EditorGUI.EndDisabledGroup();
            EditorGUILayout.EndHorizontal();

            // Endpoint configuration for Ollama
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Ollama Endpoint:", GUILayout.Width(100));
            aiServiceEndpoint = EditorGUILayout.TextField(aiServiceEndpoint);
            EditorGUILayout.EndHorizontal();

            // Model selection / actions
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("Model:", GUILayout.Width(60));
            selectedModelIndex = EditorGUILayout.Popup(selectedModelIndex, ollamaModelOptions, GUILayout.Width(140));
            if (GUILayout.Button("📥 Pull", GUILayout.Width(70)))
            {
                _ = PullModelAsync(ollamaModelOptions[selectedModelIndex], TimeSpan.FromMinutes(8));
                ShowNotification(new GUIContent($"Pulling {ollamaModelOptions[selectedModelIndex]}…"));
            }
            if (GUILayout.Button("🔁 Retry Connect", GUILayout.Width(120)))
            {
                _ = CheckConnectionStatus();
            }
            EditorGUILayout.EndHorizontal();

            // Show connection hints
            if (!githubCopilotConnected && !isConnected)
            {
                EditorGUILayout.HelpBox("💡 New! Enhanced progress feedback prevents operations from appearing to 'hang'. No Docker required - Ollama binary will auto-download and start when you click 'Connect to AI Service' or 'Start Ollama'. Enhanced stubs provide intelligent responses even when AI is unavailable.\n\n📖 See docs/WARBLER_PROGRESS_GUIDE.md for detailed setup instructions.", MessageType.Info);
            }
            else if (githubCopilotConnected)
            {
                EditorGUILayout.HelpBox("🔐 GitHub Copilot connected! Cloud-powered AI analysis available with secure authentication.", MessageType.Info);
            }
        }

        async void ExecuteAIProjectSetup()
        {
            isProcessing = true;
            string aiProvider = GetPreferredAIProvider();
            statusMessage = $"🧠 Warbler connecting to {aiProvider} for intelligent analysis...";

            try
            {
                ProjectAnalysis? analysis = null;

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
                string providerUsed = analysis.ai_provider_used ?? "fallback";
                statusMessage = $"📋 AI Analysis complete using {providerUsed}! Detected: {analysis.game_type} ({analysis.complexity_level})";
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

        // GitHub Copilot Integration Methods
        async void AuthenticateGitHubCopilot()
        {
            githubCopilotAuthenticating = true;
            githubCopilotStatus = "🔄 Authenticating...";
            statusMessage = "🔐 Starting GitHub Copilot authentication...";

            try
            {
                string pythonPath = FindPythonPath();
                string authScript = Path.Combine(Application.dataPath, "..", "scripts", "github_copilot_auth.py");

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{authScript}\" auth-progress",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                using (var process = Process.Start(processInfo))
                {
                    // Read output line by line for real-time progress
                    string line;
                    while ((line = await process.StandardOutput.ReadLineAsync()) != null)
                    {
                        if (line.StartsWith("PROGRESS:"))
                        {
                            var progressMsg = line.Substring(9).Trim();
                            statusMessage = $"🔄 {progressMsg}";
                            githubCopilotStatus = "🔄 Authenticating...";
                            UnityEngine.Debug.Log($"GitHub Progress: {progressMsg}");

                            // Show special messages for key steps
                            if (progressMsg.Contains("browser"))
                            {
                                githubCopilotStatus = "🌐 Browser Opening...";
                                statusMessage = "🌐 Browser opened - please complete GitHub authentication";
                            }
                            else if (progressMsg.Contains("Waiting for"))
                            {
                                githubCopilotStatus = "⏳ Waiting for User...";
                                statusMessage = "⏳ Please complete authentication in your browser";
                            }

                            // Force UI refresh
                            Repaint();
                        }
                        else if (line.StartsWith("AUTH_URL:"))
                        {
                            var authUrl = line.Substring(9).Trim();
                            statusMessage = "🌐 Browser authentication started. If browser didn't open, check console for URL.";
                            UnityEngine.Debug.Log($"GitHub Auth URL: {authUrl}");
                            UnityEngine.Debug.Log("If browser didn't open automatically, please visit the URL above to authenticate.");
                            // Offer manual open
                            Application.OpenURL(authUrl);
                        }
                        else if (line.StartsWith("SUCCESS:"))
                        {
                            var successMsg = line.Substring(8).Trim();
                            githubCopilotConnected = true;
                            githubCopilotStatus = "🟢 Authenticated";
                            statusMessage = $"✅ {successMsg}";
                            UnityEngine.Debug.Log($"GitHub Success: {successMsg}");
                        }
                        else if (line.StartsWith("ERROR:"))
                        {
                            var errorMsg = line.Substring(6).Trim();
                            githubCopilotConnected = false;
                            githubCopilotStatus = "🔴 Auth Failed";
                            statusMessage = $"❌ {errorMsg}";
                            UnityEngine.Debug.LogError($"GitHub Error: {errorMsg}");
                        }
                        else if (!string.IsNullOrWhiteSpace(line))
                        {
                            // Log other messages
                            UnityEngine.Debug.Log($"GitHub: {line}");
                        }
                    }

                    var errors = await process.StandardError.ReadToEndAsync();
                    process.WaitForExit();

                    if (process.ExitCode == 0 && !githubCopilotConnected)
                    {
                        // Final success check if not already set
                        githubCopilotConnected = true;
                        githubCopilotStatus = "🟢 Authenticated";
                        statusMessage = "✅ GitHub Copilot authentication successful!";
                        UnityEngine.Debug.Log("🔐 GitHub Copilot authenticated successfully");
                    }
                    else if (process.ExitCode != 0)
                    {
                        githubCopilotConnected = false;
                        githubCopilotStatus = "🔴 Auth Failed";
                        statusMessage = "❌ GitHub Copilot authentication failed. If the app is unverified, use the manual token flow (see console).";
                        UnityEngine.Debug.LogWarning($"GitHub authentication failed: {errors}");
                        UnityEngine.Debug.Log("Manual fallback: In scripts/github_copilot_auth.py, run the token flow directly from a terminal: 'python github_copilot_auth.py' and follow the browser flow. Then re-check from the Orchestrator.");
                    }
                }
            }
            catch (Exception e)
            {
                githubCopilotConnected = false;
                githubCopilotStatus = "🔴 Error";
                statusMessage = $"❌ GitHub authentication error: {e.Message}";
                UnityEngine.Debug.LogError($"GitHub authentication error: {e}");
            }
            finally
            {
                githubCopilotAuthenticating = false;
                UpdateProviderStatus();
                Repaint();
            }
        }

        void UpdateProviderStatus()
        {
            // Update status display based on connections and preferences
            if (preferGitHubCopilot && githubCopilotConnected)
            {
                statusMessage = "🔐 GitHub Copilot ready for AI analysis";
            }
            else if (!preferGitHubCopilot && isConnected)
            {
                statusMessage = "🦙 Ollama ready for AI analysis";
            }
            else if (githubCopilotConnected || isConnected)
            {
                statusMessage = "🤖 AI analysis available";
            }
            else
            {
                statusMessage = "⚠️ No AI providers connected";
            }
        }

        string GetPreferredAIProvider()
        {
            if (preferGitHubCopilot && githubCopilotConnected)
                return "GitHub Copilot";
            else if (isConnected)
                return "Ollama";
            else if (githubCopilotConnected)
                return "GitHub Copilot";
            else
                return "Fallback Analysis";
        }

        string GetOverallConnectionStatus()
        {
            if (githubCopilotConnected && isConnected)
                return "🟢 Both Providers Ready";
            else if (githubCopilotConnected)
                return "🔐 GitHub Ready";
            else if (isConnected)
                return "🦙 Ollama Ready";
            else
                return "🔴 No Connections";
        }

        private async Task CheckAllProviderStatus()
        {
            statusMessage = "🔄 Checking all AI provider connections...";

            // Check GitHub Copilot
            if (!githubCopilotAuthenticating)
            {
                await CheckGitHubCopilotStatus();
            }

            // Check Ollama
            if (!isConnecting)
            {
                await CheckConnectionStatus();
            }

            UpdateProviderStatus();
        }

        private async Task RunFullSetup()
        {
            statusMessage = "🚀 Starting comprehensive Warbler setup...";

            bool setupConfirmed = EditorUtility.DisplayDialog(
                "🧙‍♂️ Warbler Full Setup",
                "This will set up both Ollama and GitHub Copilot integration.\n\n" +
                "The process may take several minutes and will:\n" +
                "• Download Ollama if needed (may be large)\n" +
                "• Start Ollama service\n" +
                "• Download a small AI model for testing\n" +
                "• Open browser for GitHub authentication\n\n" +
                "Continue with full setup?",
                "Yes, Set Up Everything",
                "Cancel"
            );

            if (!setupConfirmed)
            {
                statusMessage = "Setup cancelled by user";
                return;
            }

            try
            {
                string pythonPath = FindPythonPath();
                string bridgePath = Path.Combine(Application.dataPath, "..", "scripts", "warbler_terminus_bridge.py");

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{bridgePath}\" --full-setup",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = false, // Show terminal for progress
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                statusMessage = "🚀 Full setup running in terminal window...";
                UnityEngine.Debug.Log("🚀 Starting comprehensive Warbler setup. Check terminal for detailed progress.");

                var process = Process.Start(processInfo);

                if (process != null)
                {
                    // Run in background and periodically check connection status
                    var setupTask = Task.Run(async () =>
                    {
                        var output = await process.StandardOutput.ReadToEndAsync();
                        var errors = await process.StandardError.ReadToEndAsync();

                        process.WaitForExit();

                        // Log output to Unity console
                        if (!string.IsNullOrEmpty(output))
                        {
                            UnityEngine.Debug.Log($"Setup Output:\n{output}");
                        }

                        if (!string.IsNullOrEmpty(errors))
                        {
                            UnityEngine.Debug.LogWarning($"Setup Messages:\n{errors}");
                        }

                        return process.ExitCode;
                    });

                    // Update status while setup runs
                    while (!setupTask.IsCompleted)
                    {
                        statusMessage = "🔄 Setup in progress... (check terminal for details)";
                        await Task.Delay(2000);
                        Repaint();
                    }

                    int exitCode = await setupTask;

                    if (exitCode == 0)
                    {
                        statusMessage = "🎉 Full setup completed successfully!";
                        ShowNotification(new GUIContent("Setup complete ✅"));

                        // Refresh connection status
                        await CheckAllProviderStatus();

                        EditorUtility.DisplayDialog(
                            "🎉 Setup Complete!",
                            "Warbler AI is now fully configured!\n\n" +
                            "Both Ollama and GitHub Copilot are ready for use.\n" +
                            "You can now create AI-powered projects with confidence.",
                            "Awesome!"
                        );
                    }
                    else
                    {
                        statusMessage = "⚠️ Setup completed with some issues. Check terminal for details.";
                        ShowNotification(new GUIContent("Setup finished with warnings ⚠️"));

                        EditorUtility.DisplayDialog(
                            "⚠️ Setup Partially Complete",
                            "Some components may not have been set up correctly.\n\n" +
                            "Check the Unity console and terminal output for details.\n" +
                            "You can retry individual components using the connection buttons.",
                            "OK"
                        );
                    }
                }
            }
            catch (Exception e)
            {
                statusMessage = $"❌ Setup error: {e.Message}";
                UnityEngine.Debug.LogError($"Failed to run full setup: {e}");
                ShowNotification(new GUIContent("Setup failed ❌"));

                EditorUtility.DisplayDialog(
                    "❌ Setup Failed",
                    $"Setup encountered an error:\n\n{e.Message}\n\n" +
                    "Check the Unity console for more details and try using individual setup buttons.",
                    "OK"
                );
            }
        }

        private async Task RunDeepDiagnostic()
        {
            try
            {
                statusMessage = "🧪 Running deep diagnostics...";
                string pythonPath = FindPythonPath();
                string scriptPath = Path.Combine(Application.dataPath, "..", "scripts", "tlda_ai_setup.py");

                var psi = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{scriptPath}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = false,
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                var proc = Process.Start(psi);
                if (proc == null)
                {
                    statusMessage = "❌ Failed to start deep diagnostics";
                    return;
                }

                var monitorTask = Task.Run(async () =>
                {
                    var output = await proc.StandardOutput.ReadToEndAsync();
                    var error = await proc.StandardError.ReadToEndAsync();
                    proc.WaitForExit();

                    if (!string.IsNullOrWhiteSpace(output))
                        UnityEngine.Debug.Log($"Deep Diagnostic Output:\n{output}");
                    if (!string.IsNullOrWhiteSpace(error))
                        UnityEngine.Debug.LogWarning($"Deep Diagnostic Messages:\n{error}");
                    return proc.ExitCode;
                });

                while (!monitorTask.IsCompleted)
                {
                    statusMessage = "🧪 Deep diagnostics running... (see console/terminal)";
                    await Task.Delay(1500);
                    Repaint();
                }

                var code = await monitorTask;
                if (code == 0)
                {
                    statusMessage = "✅ Deep diagnostics completed";
                    ShowNotification(new GUIContent("Deep diagnostics complete ✅"));
                }
                else
                {
                    statusMessage = "⚠️ Deep diagnostics finished with issues";
                    ShowNotification(new GUIContent("Deep diagnostics issues ⚠️"));
                }
            }
            catch (Exception ex)
            {
                statusMessage = $"❌ Deep diagnostics error: {ex.Message}";
                UnityEngine.Debug.LogError($"Deep diagnostics failed: {ex}");
                ShowNotification(new GUIContent("Deep diagnostics failed ❌"));
            }
        }

        void ShowProgressGuide()
        {
            string guidePath = Path.Combine(Application.dataPath, "..", "docs", "WARBLER_PROGRESS_GUIDE.md");

            if (File.Exists(guidePath))
            {
                // Try to open with default application
                try
                {
                    Application.OpenURL("file://" + guidePath);
                    statusMessage = "📖 Progress guide opened in default application";
                }
                catch
                {
                    // Fallback: show in Unity console
                    var content = File.ReadAllText(guidePath);
                    UnityEngine.Debug.Log($"Warbler Progress Guide:\n{content}");
                    statusMessage = "📖 Progress guide content logged to Unity console";
                }
            }
            else
            {
                statusMessage = "📖 Progress guide not found - check docs/WARBLER_PROGRESS_GUIDE.md";
                UnityEngine.Debug.LogWarning("Progress guide file not found at: " + guidePath);
            }
        }

        private async Task CheckGitHubCopilotStatus()
        {
            try
            {
                string pythonPath = FindPythonPath();
                string authScript = Path.Combine(Application.dataPath, "..", "scripts", "github_copilot_auth.py");

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{authScript}\" validate",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                using (var process = Process.Start(processInfo))
                {
                    if (process != null)
                    {
                        var output = await process.StandardOutput.ReadToEndAsync();
                        process.WaitForExit();

                        if (process.ExitCode == 0)
                        {
                            githubCopilotConnected = true;
                            githubCopilotStatus = "🟢 Authenticated";
                        }
                        else
                        {
                            githubCopilotConnected = false;
                            githubCopilotStatus = "🔒 Not Authenticated";
                        }
                    }
                }
            }
            catch (Exception e)
            {
                githubCopilotConnected = false;
                githubCopilotStatus = "🔴 Error";
                UnityEngine.Debug.LogWarning($"GitHub status check failed: {e.Message}");
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
                };

                using (var process = Process.Start(processInfo))
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

        private async Task CheckConnectionStatus()
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
            statusMessage = "🚀 Starting/Installing Ollama (this may take 3–5 minutes)...";

            try
            {
                // 1) Ensure Ollama is installed
                if (!await EnsureOllamaInstalledAsync())
                {
                    connectionStatus = "🔴 Install Required";
                    statusMessage = "❌ Ollama not installed";
                    return;
                }

                // 2) Start Ollama server (serve)
                statusMessage = "🚀 Launching Ollama server...";
                UnityEngine.Debug.Log("Launching 'ollama serve' in background");
                try
                {
                    EnsureLogPath();
                    var serveInfo = new ProcessStartInfo
                    {
                        FileName = "ollama",
                        Arguments = "serve",
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true
                    };
                    ollamaServeProcess = Process.Start(serveInfo);
                    if (ollamaServeProcess != null)
                    {
                        // Pipe output to a rolling log file to avoid output buffer stalls
                        _ = Task.Run(async () => await PumpProcessLogsAsync(ollamaServeProcess, ollamaLogPath));
                    }
                }
                catch (Exception ex)
                {
                    UnityEngine.Debug.LogWarning($"Failed to start 'ollama serve' (may already be running): {ex.Message}");
                }

                // 3) Wait for Ollama API to become ready (long poll)
                var ready = await WaitForOllamaReadyAsync(TimeSpan.FromMinutes(8));
                if (!ready)
                {
                    connectionStatus = "🔴 No API Server";
                    statusMessage = "❌ Ollama did not become ready in time";
                    return;
                }

                // 4) Optionally ensure a small model exists
                statusMessage = "📥 Ensuring small model (llama3.2:1b) is available...";
                var pullOk = await PullModelAsync("llama3.2:1b", TimeSpan.FromMinutes(6));
                if (!pullOk)
                {
                    UnityEngine.Debug.LogWarning("Model pull may still be in progress or skipped.");
                }

                // 5) Mark connected
                isConnected = true;
                connectionStatus = "🟢 Connected";
                statusMessage = "✅ Ollama is ready";
            }
            catch (Exception e)
            {
                connectionStatus = "� Start Failed";
                statusMessage = $"❌ Failed to start Ollama: {e.Message}";
                UnityEngine.Debug.LogError($"Failed to start Ollama: {e}");
            }
            finally
            {
                isConnecting = false;
                Repaint();
            }
        }

        private void EnsureLogPath()
        {
            if (!string.IsNullOrEmpty(ollamaLogPath)) return;
            var logsDir = Path.Combine(Application.dataPath, "..", "Logs");
            try
            {
                if (!Directory.Exists(logsDir)) Directory.CreateDirectory(logsDir);
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogWarning($"Could not create Logs directory: {e.Message}");
            }
            ollamaLogPath = Path.Combine(logsDir, "ollama-serve.log");
        }

        private async Task PumpProcessLogsAsync(Process proc, string logPath)
        {
            try
            {
                using (var fs = new FileStream(logPath, FileMode.Append, FileAccess.Write, FileShare.Read))
                using (var writer = new StreamWriter(fs))
                {
                    writer.AutoFlush = true;
                    while (!proc.HasExited)
                    {
                        var std = await proc.StandardOutput.ReadLineAsync();
                        if (!string.IsNullOrEmpty(std))
                            await writer.WriteLineAsync("[OUT] " + std);
                        var err = await proc.StandardError.ReadLineAsync();
                        if (!string.IsNullOrEmpty(err))
                            await writer.WriteLineAsync("[ERR] " + err);
                        await Task.Delay(50);
                    }
                }
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogWarning($"Log pump ended: {e.Message}");
            }
        }

        private void OpenOllamaLogs()
        {
            EnsureLogPath();
            if (File.Exists(ollamaLogPath))
            {
                Application.OpenURL("file://" + ollamaLogPath);
                statusMessage = "📄 Opened Ollama logs";
            }
            else
            {
                statusMessage = "📄 No Ollama log file yet";
                UnityEngine.Debug.Log("Ollama log file not found. Start the service first.");
            }
        }

        private async Task StopOllamaServiceAsync()
        {
            try
            {
                statusMessage = "⏹ Stopping Ollama...";
                Repaint();

                // Try to kill process we started
                if (ollamaServeProcess != null && !ollamaServeProcess.HasExited)
                {
                    try
                    {
                        ollamaServeProcess.Kill();
                        ollamaServeProcess.WaitForExit(5000);
                    }
                    catch { /* ignore */ }
                }

                // Fallback by name
#if UNITY_EDITOR_WIN
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "taskkill",
                        Arguments = "/IM ollama.exe /F /T",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    using (var p = Process.Start(psi))
                    {
                        if (p != null)
                        {
                            await Task.Run(() => p.WaitForExit());
                        }
                    }
                }
                catch { /* ignore */ }
#else
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "pkill",
                        Arguments = "-f ollama",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    using (var p = Process.Start(psi))
                    {
                        if (p != null)
                        {
                            await p.WaitForExitAsync();
                        }
                    }
                }
                catch { /* ignore */ }
#endif

                // Give a moment then verify API is down
                await Task.Delay(1000);
                bool stillUp = await WaitForOllamaReadyAsync(TimeSpan.FromSeconds(1));
                if (!stillUp)
                {
                    isConnected = false;
                    connectionStatus = "🔴 Stopped";
                    statusMessage = "✅ Ollama stopped";
                }
                else
                {
                    statusMessage = "⚠️ Ollama may still be running (external instance).";
                }
            }
            catch (Exception ex)
            {
                statusMessage = $"❌ Stop error: {ex.Message}";
            }
            finally
            {
                Repaint();
            }
        }

        private async Task RunOllamaHealthCheckAsync()
        {
            try
            {
                statusMessage = "❤️ Running health check...";
                Repaint();

                bool installed = await IsCommandAvailableAsync("ollama", "--version", TimeSpan.FromSeconds(10));
                string version = "unknown";
                bool apiReady = false;
                int modelCount = 0;
                string quickTest = "skipped";
                var sw = System.Diagnostics.Stopwatch.StartNew();

                // Version via API preferred
                try
                {
                    using (var client = new System.Net.Http.HttpClient())
                    {
                        client.Timeout = TimeSpan.FromSeconds(5);
                        var resp = await client.GetAsync(aiServiceEndpoint + "/api/version");
                        if (resp.IsSuccessStatusCode)
                        {
                            apiReady = true;
                            var json = await resp.Content.ReadAsStringAsync();
                            version = json;
                        }
                    }
                }
                catch { apiReady = false; }

                // Model count via CLI
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "ollama",
                        Arguments = "list",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        CreateNoWindow = true
                    };
                    using (var p = Process.Start(psi))
                    {
                        if (p != null)
                        {
                            var output = await p.StandardOutput.ReadToEndAsync();
                            p.WaitForExit(5000);
                            modelCount = output.Split(new[] { '\'' }, StringSplitOptions.RemoveEmptyEntries)
                                               .Count(l => l.Trim().Length > 0 && !l.StartsWith("NAME"));
                        }
                    }
                }
                catch { /* ignore */ }

                // Quick API generate test
                if (apiReady)
                {
                    try
                    {
                        var payload = new
                        {
                            model = ollamaModelOptions[Mathf.Clamp(selectedModelIndex, 0, ollamaModelOptions.Length - 1)],
                            prompt = "Say hello",
                            stream = false
                        };
                        using (var client = new System.Net.Http.HttpClient())
                        {
                            client.Timeout = TimeSpan.FromSeconds(30);
                            var body = new StringContent(Newtonsoft.Json.JsonConvert.SerializeObject(payload), System.Text.Encoding.UTF8, "application/json");
                            sw.Restart();
                            var resp = await client.PostAsync(aiServiceEndpoint + "/api/generate", body);
                            sw.Stop();
                            quickTest = resp.IsSuccessStatusCode ? $"ok ({sw.ElapsedMilliseconds} ms)" : $"fail ({(int)resp.StatusCode})";
                        }
                    }
                    catch (Exception ex)
                    {
                        quickTest = "error: " + ex.Message;
                    }
                }

                EditorUtility.DisplayDialog(
                    "Ollama Health",
                    $"Installed: {(installed ? "yes" : "no")}\n" +
                    $"API Ready: {(apiReady ? "yes" : "no")}\n" +
                    $"Version: {version}\n" +
                    $"Models: {modelCount}\n" +
                    $"Quick Generate: {quickTest}",
                    "OK");

                statusMessage = "❤️ Health check complete";
            }
            catch (Exception ex)
            {
                statusMessage = $"❌ Health check error: {ex.Message}";
                UnityEngine.Debug.LogError(ex);
            }
        }

        private async Task<bool> EnsureOllamaInstalledAsync()
        {
            // Quick check
            if (await IsCommandAvailableAsync("ollama", "--version", TimeSpan.FromSeconds(10)))
                return true;

            // Windows winget path as primary option
#if UNITY_EDITOR_WIN
            bool proceed = EditorUtility.DisplayDialog(
                "Install Ollama",
                "Ollama is not installed. The installer will be downloaded and may take 3–5 minutes on fast networks.\n\nProceed to install via winget?",
                "Install with winget",
                "Open Download Page");

            if (proceed)
            {
                statusMessage = "� Installing Ollama via winget...";
                var winget = new ProcessStartInfo
                {
                    FileName = "winget",
                    Arguments = "install -e --id Ollama.Ollama",
                    UseShellExecute = true, // show native UI/progress if available
                    CreateNoWindow = false
                };
                try
                {
                    var p = Process.Start(winget);
                    // Long wait, user sees installer/winget progress
                    var startedAt = DateTime.UtcNow;
                    while (p != null && !p.HasExited)
                    {
                        statusMessage = $"📥 Installing Ollama (elapsed {(DateTime.UtcNow - startedAt).Minutes:D2}:{(DateTime.UtcNow - startedAt).Seconds:D2})...";
                        Repaint();
                        await Task.Delay(3000);
                    }
                }
                catch (Exception ex)
                {
                    UnityEngine.Debug.LogWarning($"winget installation failed: {ex.Message}");
                }

                // Re-check
                if (await IsCommandAvailableAsync("ollama", "--version", TimeSpan.FromSeconds(15)))
                    return true;
            }

            // Fallback: open download page
            Application.OpenURL("https://ollama.com/download/windows");
            EditorUtility.DisplayDialog(
                "Manual Install Required",
                "A browser window was opened. Please download and install Ollama, then return here and click 'Start Ollama' again.",
                "OK");
            return false;
#else
            // Non-Windows: open download page
            Application.OpenURL("https://ollama.com/download");
            return false;
#endif
        }

        private async Task<bool> IsCommandAvailableAsync(string fileName, string args, TimeSpan timeout)
        {
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = fileName,
                    Arguments = args,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };
                using (var p = Process.Start(psi))
                {
                    if (p == null) return false;
                    var exited = await Task.Run(() => p.WaitForExit((int)timeout.TotalMilliseconds));
                    return exited && p.ExitCode == 0;
                }
            }
            catch
            {
                return false;
            }
        }

        private async Task<bool> WaitForOllamaReadyAsync(TimeSpan maxWait)
        {
            var start = DateTime.UtcNow;
            var deadline = start + maxWait;
            while (DateTime.UtcNow < deadline)
            {
                try
                {
                    using (var client = new System.Net.Http.HttpClient())
                    {
                        client.Timeout = TimeSpan.FromSeconds(5);
                        var res = await client.GetAsync(aiServiceEndpoint + "/api/version");
                        if (res.IsSuccessStatusCode)
                        {
                            return true;
                        }
                    }
                }
                catch { /* keep waiting */ }

                var elapsed = DateTime.UtcNow - start;
                statusMessage = $"⏳ Waiting for Ollama to be ready ({elapsed.Minutes:D2}:{elapsed.Seconds:D2})...";
                connectionStatus = "⏳ Starting...";
                Repaint();
                await Task.Delay(3000);
            }
            return false;
        }

        private async Task<bool> PullModelAsync(string model, TimeSpan maxWait)
        {
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = "ollama",
                    Arguments = $"pull {model}",
                    UseShellExecute = true,
                    RedirectStandardOutput = false,
                    RedirectStandardError = false,
                    CreateNoWindow = false
                };
                var p = Process.Start(psi);
                if (p == null) return false;

                var startedAt = DateTime.UtcNow;
                while (!p.HasExited)
                {
                    statusMessage = $"📥 Downloading model {model} (elapsed {(DateTime.UtcNow - startedAt).Minutes:D2}:{(DateTime.UtcNow - startedAt).Seconds:D2})...";
                    Repaint();
                    await Task.Delay(2000);
                }

                return p.ExitCode == 0;
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.LogWarning($"Model pull failed: {ex.Message}");
                return false;
            }
        }

        async void RunConnectionDiagnostic()
        {
            statusMessage = "🛠️ Running comprehensive connection diagnostic...";

            try
            {
                string pythonPath = FindPythonPath();
                string bridgePath = Path.Combine(Application.dataPath, "..", "scripts", "warbler_terminus_bridge.py");

                // Add await to prevent compiler warning
                await Task.Delay(100);

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{bridgePath}\" --diagnostic",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = false, // Show window for diagnostic
                    WorkingDirectory = Path.Combine(Application.dataPath, "..")
                };

                // Start the diagnostic in a visible terminal for better user experience
                try
                {
                    var process = Process.Start(processInfo);
                    statusMessage = "🛠️ Diagnostic running in terminal window...";
                    UnityEngine.Debug.Log("🛠️ Connection diagnostic started. Check terminal for detailed results.");

                    // Also capture output for Unity console
                    if (process != null)
                    {
                        var output = await process.StandardOutput.ReadToEndAsync();
                        var errors = await process.StandardError.ReadToEndAsync();

                        process.WaitForExit();

                        if (!string.IsNullOrEmpty(output))
                        {
                            UnityEngine.Debug.Log($"Diagnostic Output:\n{output}");
                        }

                        if (!string.IsNullOrEmpty(errors))
                        {
                            UnityEngine.Debug.LogWarning($"Diagnostic Warnings:\n{errors}");
                        }

                        statusMessage = process.ExitCode == 0
                            ? "✅ Diagnostic completed successfully. Check terminal and console for results."
                            : "⚠️ Diagnostic completed with warnings. Check terminal for details.";
                    }
                }
                catch (Exception)
                {
                    // Fallback to hidden window if visible terminal fails
                    processInfo.CreateNoWindow = true;
                    var process = Process.Start(processInfo);
                    statusMessage = "🛠️ Running diagnostic (check Unity console for results)...";

                    if (process != null)
                    {
                        var output = await process.StandardOutput.ReadToEndAsync();
                        process.WaitForExit();
                        UnityEngine.Debug.Log($"Connection Diagnostic Results:\n{output}");
                        statusMessage = "✅ Diagnostic completed. Check Unity console for results.";
                    }
                }
            }
            catch (Exception e)
            {
                statusMessage = $"❌ Diagnostic error: {e.Message}";
                UnityEngine.Debug.LogError($"Failed to run diagnostic: {e}");
            }
        }

        async Task<ProjectAnalysis?> GetAIAnalysis(string request)
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

                // Build arguments based on provider preference
                string arguments = $"\"{scriptPath}\" \"{request}\" --generate-files";
                if (!preferGitHubCopilot)
                {
                    arguments += " --prefer-ollama";
                }

                var processInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = arguments,
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
                                    if (result?.success == true && result.analysis != null)
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
                                if (result?.success == true && result.analysis != null)
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
            // 👀TODO: Implement AI-recommended functionality
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
        public string game_type = "";
        public string complexity_level = "";
        public string[] required_systems = System.Array.Empty<string>();
        public string[] recommended_folders = System.Array.Empty<string>();
        public string[] unity_packages = System.Array.Empty<string>();
        public string estimated_dev_time = "";
        public string[] key_mechanics = System.Array.Empty<string>();
        public string[] technical_considerations = System.Array.Empty<string>();
        public string suggested_architecture = "";
        public string warbler_insights = "";
        public WarblerEnhancement warbler_enhancement = null;

        // New fields for multi-provider support
        public string ai_provider_used = "";
        public string[] providers_tried = System.Array.Empty<string>();
        public bool github_copilot_enhanced;
    }

    [System.Serializable]
    public class WarblerEnhancement
    {
        public string[] development_milestones = System.Array.Empty<string>();
        public string[] testing_strategy = System.Array.Empty<string>();
        public string[] suggested_tldl_tags = System.Array.Empty<string>();
    }

    [System.Serializable]
    public class AIAnalysisResult
    {
        public bool success;
        public ProjectAnalysis analysis = null;
        public string blueprint_path = "";
    }
}
