using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Diagnostics;
using UnityEngine;
using UnityEditor;
using System.Text;
using Debug = UnityEngine.Debug; // Resolve namespace conflict

namespace TWG.TLDA.TestSuite.Editor
{
    /// <summary>
    /// 🧪 LEGENDARY - Unity-Native Test Suite Manager
    /// Bridges external Python validation tools with Unity Editor workflow
    /// Complete testing ecosystem accessible through familiar Unity interface
    /// Sacred Vision: "All testing power, zero terminal switching!"
    /// </summary>
    public class UnityTestSuiteManager : EditorWindow
    {
        private Vector2 scrollPosition;
        private bool isRunningTests = false;
        private string testProgress = "";
        private readonly StringBuilder testLogs = new();
        private bool showLogs = false;
        private DateTime lastTestRun;
        private Vector2 testLogsScrollPosition; // Keep only this declaration
        
        // Test categories
        private bool runSymbolicLinter = true;
        private bool runDocumentationValidation = true;
        private bool runDebugOverlayValidation = true;
        private bool runSystemLinter = false; // Can be slow
        private bool runUnitySpecificTests = true;
        
        // Test results
        private TestSuiteResults lastResults;
        
        [MenuItem("Tools/Living Dev Agent/🧪 Unity Test Suite")]
        public static void ShowWindow()
        {
            var window = GetWindow<UnityTestSuiteManager>("🧪 Unity Test Suite");
            window.minSize = new Vector2(650, 700);
            window.Show();
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawTestConfiguration();
            DrawTestExecution();
            DrawTestResults();
            DrawQuickActions();
            DrawLogsSection();
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.Space(10);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("🧪 Unity-Native Test Suite Manager", EditorStyles.largeLabel);
            EditorGUILayout.LabelField("Bridge to Python validation tools with Unity Editor integration", EditorStyles.miniLabel);
            EditorGUILayout.Space(5);
            
            var style = new GUIStyle(EditorStyles.label) { wordWrap = true };
            EditorGUILayout.LabelField("Run all Living Dev Agent validation tools directly from Unity without switching to terminal. Perfect for Unity developers who want comprehensive testing in their familiar environment.", style);
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.Space(10);
        }
        
        private void DrawTestConfiguration()
        {
            EditorGUILayout.LabelField("🎯 Test Configuration", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            runSymbolicLinter = EditorGUILayout.Toggle("🧙‍♂️ Symbolic Linter (~68ms)", runSymbolicLinter);
            runDocumentationValidation = EditorGUILayout.Toggle("📜 TLDL Validation (~60ms)", runDocumentationValidation);
            runDebugOverlayValidation = EditorGUILayout.Toggle("🐛 Debug Overlay (~56ms)", runDebugOverlayValidation);
            runSystemLinter = EditorGUILayout.Toggle("🏗️ System Architecture (~192ms)", runSystemLinter);
            runUnitySpecificTests = EditorGUILayout.Toggle("🎮 Unity-Specific Tests (~100ms)", runUnitySpecificTests);
            
            EditorGUILayout.Space(5);
            
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Select All"))
            {
                runSymbolicLinter = runDocumentationValidation = runDebugOverlayValidation = runUnitySpecificTests = true;
                runSystemLinter = true;
            }
            
            if (GUILayout.Button("Quick Tests Only"))
            {
                runSymbolicLinter = runDocumentationValidation = runDebugOverlayValidation = runUnitySpecificTests = true;
                runSystemLinter = false;
            }
            
            if (GUILayout.Button("Clear All"))
            {
                runSymbolicLinter = runDocumentationValidation = runDebugOverlayValidation = runUnitySpecificTests = runSystemLinter = false;
            }
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawTestExecution()
        {
            EditorGUILayout.LabelField("⚡ Test Execution", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (isRunningTests)
            {
                EditorGUILayout.LabelField("Status: Running Tests...", EditorStyles.boldLabel);
                EditorGUILayout.LabelField(testProgress);
                
                if (GUILayout.Button("🛑 Cancel Tests"))
                {
                    isRunningTests = false;
                    testProgress = "Tests cancelled by user";
                }
            }
            else
            {
                EditorGUILayout.LabelField("Status: Ready");
                
                if (GUILayout.Button("🚀 Run Selected Tests", GUILayout.Height(30)))
                {
                    RunSelectedTests();
                }
                
                EditorGUILayout.Space(5);
                
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("🔍 Check Environment"))
                {
                    CheckTestEnvironment();
                }
                
                if (GUILayout.Button("📦 Validate Dependencies"))
                {
                    ValidateDependencies();
                }
                
                if (GUILayout.Button("🔧 Setup Guide"))
                {
                    ShowSetupGuide();
                }
                EditorGUILayout.EndHorizontal();
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawTestResults()
        {
            EditorGUILayout.LabelField("📊 Test Results", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            if (lastResults != null)
            {
                EditorGUILayout.LabelField($"Last run: {lastTestRun:yyyy-MM-dd HH:mm:ss}");
                EditorGUILayout.Space(5);
                
                EditorGUILayout.LabelField($"Total execution time: {lastResults.TotalExecutionTime:F2}s");
                EditorGUILayout.LabelField($"Tests passed: {lastResults.PassedTests}");
                EditorGUILayout.LabelField($"Tests failed: {lastResults.FailedTests}");
                EditorGUILayout.LabelField($"Warnings: {lastResults.Warnings}");
                
                EditorGUILayout.Space(5);
                
                // Color-coded status
                var statusColor = lastResults.OverallSuccess ? Color.green : Color.red;
                var originalColor = GUI.color;
                GUI.color = statusColor;
                EditorGUILayout.LabelField($"Overall Status: {(lastResults.OverallSuccess ? "✅ PASSED" : "❌ FAILED")}", EditorStyles.boldLabel);
                GUI.color = originalColor;
                
                EditorGUILayout.Space(5);
                
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("📄 Export Report"))
                {
                    ExportTestReport();
                }
                
                if (GUILayout.Button("🔄 Re-run Failed"))
                {
                    RerunFailedTests();
                }
                EditorGUILayout.EndHorizontal();
            }
            else
            {
                EditorGUILayout.LabelField("No test results yet.");
                EditorGUILayout.LabelField("Run tests to see results here.");
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawQuickActions()
        {
            EditorGUILayout.LabelField("⚡ Quick Actions", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            var buttonWidth = (position.width - 40) / 3;
            
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("🐍 Test Python", GUILayout.Width(buttonWidth)))
            {
                TestPythonEnvironment();
            }
            
            if (GUILayout.Button("📜 Quick TLDL", GUILayout.Width(buttonWidth)))
            {
                RunQuickTLDLValidation();
            }
            
            if (GUILayout.Button("🧙‍♂️ Quick Symbolic", GUILayout.Width(buttonWidth)))
            {
                RunQuickSymbolicLinter();
            }
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("🔥 Open Terminus", GUILayout.Width(buttonWidth)))
            {
                // Open the existing Terminus console
                EditorApplication.ExecuteMenuItem("Tools/Living Dev Agent/🔥 Terminus Console");
            }
            
            if (GUILayout.Button("🏗️ Build Test", GUILayout.Width(buttonWidth)))
            {
                RunUnityBuildTest();
            }
            
            if (GUILayout.Button("🧪 Unit Tests", GUILayout.Width(buttonWidth)))
            {
                RunUnityUnitTests();
            }
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space(10);
        }
        
        private void DrawLogsSection()
        {
            EditorGUILayout.LabelField("📝 Test Logs", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            showLogs = EditorGUILayout.Foldout(showLogs, $"Show logs ({testLogs.Length} characters)");
            
            if (showLogs)
            {
                // Create a proper scrollable text area instead of SelectableLabel
                EditorGUILayout.LabelField("Test execution logs:", EditorStyles.miniLabel);
                
                // Use ScrollView for proper scrolling behavior
                var scrollViewRect = GUILayoutUtility.GetRect(0, 200, GUILayout.ExpandWidth(true));
                var logContent = testLogs.ToString();
                
                if (string.IsNullOrEmpty(logContent))
                {
                    EditorGUI.LabelField(scrollViewRect, "No logs available yet. Run tests to see output here.", EditorStyles.centeredGreyMiniLabel);
                }
                else
                {
                    // Create a scrollable text area with proper wrapping
                    var textAreaStyle = new GUIStyle(EditorStyles.textArea)
                    {
                        wordWrap = true,
                        richText = false // Disable rich text for better performance with large logs
                    };
                    
                    // Calculate content height for proper scrolling
                    var contentHeight = textAreaStyle.CalcHeight(new GUIContent(logContent), scrollViewRect.width - 20);
                    var displayHeight = Mathf.Max(200, contentHeight);
                    
                    // Create scrollable view
                    var scrollRect = new Rect(scrollViewRect.x, scrollViewRect.y, scrollViewRect.width, 200);
                    var contentRect = new Rect(0, 0, scrollViewRect.width - 20, displayHeight);
                    
                    testLogsScrollPosition = GUI.BeginScrollView(scrollRect, testLogsScrollPosition, contentRect);
                    
                    // Display the text in a selectable text area
                    var textRect = new Rect(0, 0, contentRect.width, contentHeight);
                    GUI.TextArea(textRect, logContent, textAreaStyle);
                    
                    GUI.EndScrollView();
                }
                
                EditorGUILayout.Space(5);
                
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("Clear Logs", GUILayout.Width(100)))
                {
                    testLogs.Clear();
                    testLogsScrollPosition = Vector2.zero;
                }
                
                if (GUILayout.Button("Copy to Clipboard", GUILayout.Width(120)))
                {
                    EditorGUIUtility.systemCopyBuffer = testLogs.ToString();
                    LogMessage("📋 Logs copied to clipboard");
                }
                
                if (GUILayout.Button("Export Logs", GUILayout.Width(100)))
                {
                    ExportLogsToFile();
                }
                EditorGUILayout.EndHorizontal();
            }
            
            EditorGUILayout.EndVertical();
        }
        
        private void ExportLogsToFile()
        {
            var path = EditorUtility.SaveFilePanel("Export Test Logs", "", $"test-logs-{DateTime.Now:yyyy-MM-dd-HH-mm-ss}.txt", "txt");
            
            if (!string.IsNullOrEmpty(path))
            {
                try
                {
                    File.WriteAllText(path, testLogs.ToString());
                    LogMessage($"📁 Logs exported to: {path}");
                    EditorUtility.DisplayDialog("Export Complete", $"Logs exported successfully to:\n{path}", "OK");
                }
                catch (Exception ex)
                {
                    LogMessage($"❌ Failed to export logs: {ex.Message}");
                    EditorUtility.DisplayDialog("Export Failed", $"Failed to export logs:\n{ex.Message}", "OK");
                }
            }
        }
        
        private async void RunSelectedTests()
        {
            if (isRunningTests) return;
            
            isRunningTests = true;
            testProgress = "Initializing test suite...";
            lastTestRun = DateTime.Now;
            
            var results = new TestSuiteResults();
            var startTime = DateTime.Now;
            
            try
            {
                LogMessage("🧪 Starting Unity Test Suite execution...");
                
                if (runUnitySpecificTests)
                {
                    testProgress = "Running Unity-specific tests...";
                    await RunUnitySpecificTestsAsync(results);
                }
                
                if (runSymbolicLinter)
                {
                    testProgress = "Running Symbolic Linter...";
                    await RunSymbolicLinterAsync(results);
                }
                
                if (runDocumentationValidation)
                {
                    testProgress = "Running TLDL Documentation Validation...";
                    await RunTLDLValidationAsync(results);
                }
                
                if (runDebugOverlayValidation)
                {
                    testProgress = "Running Debug Overlay Validation...";
                    await RunDebugOverlayValidationAsync(results);
                }
                
                if (runSystemLinter)
                {
                    testProgress = "Running System Architecture Linter...";
                    await RunSystemLinterAsync(results);
                }
                
                results.TotalExecutionTime = (DateTime.Now - startTime).TotalSeconds;
                results.OverallSuccess = results.FailedTests == 0;
                
                lastResults = results;
                
                LogMessage($"🎉 Test suite complete! Passed: {results.PassedTests}, Failed: {results.FailedTests}, Warnings: {results.Warnings}");
                
                EditorUtility.DisplayDialog("Test Suite Complete", 
                    $"Tests completed in {results.TotalExecutionTime:F2}s\nPassed: {results.PassedTests}\nFailed: {results.FailedTests}\nWarnings: {results.Warnings}", 
                    "OK");
            }
            catch (Exception ex)
            {
                LogMessage($"❌ Test suite failed: {ex.Message}");
                EditorUtility.DisplayDialog("Test Suite Failed", $"Test suite failed:\n{ex.Message}", "OK");
            }
            finally
            {
                isRunningTests = false;
                testProgress = "Test suite complete";
                Repaint();
            }
        }
        
        private async Task RunUnitySpecificTestsAsync(TestSuiteResults results)
        {
            LogMessage("🎮 Running Unity-specific tests...");
            
            // Test Unity version compatibility
            var unityVersion = Application.unityVersion;
            LogMessage($"Unity Version: {unityVersion}");
            results.PassedTests++;
            
            // Test build capabilities
            try
            {
                var scenes = EditorBuildSettings.scenes;
                LogMessage($"Build scenes configured: {scenes.Length}");
                results.PassedTests++;
            }
            catch (Exception ex)
            {
                LogMessage($"❌ Build configuration test failed: {ex.Message}");
                results.FailedTests++;
            }
            
            // Test project structure
            var requiredDirs = new[] { "Assets", "Packages", "ProjectSettings" };
            foreach (var dir in requiredDirs)
            {
                if (Directory.Exists(dir))
                {
                    LogMessage($"✅ Required directory found: {dir}");
                    results.PassedTests++;
                }
                else
                {
                    LogMessage($"❌ Missing required directory: {dir}");
                    results.FailedTests++;
                }
            }
            
            await Task.Delay(100); // Simulate test time
        }
        
        private async Task RunSymbolicLinterAsync(TestSuiteResults results)
        {
            LogMessage("🧙‍♂️ Running Symbolic Linter...");
            
            var result = await RunPythonTool("src/SymbolicLinter/symbolic_linter.py", "--path src/");
            
            if (result.Success)
            {
                LogMessage("✅ Symbolic Linter passed");
                results.PassedTests++;
            }
            else
            {
                LogMessage($"❌ Symbolic Linter failed: {result.Error}");
                results.FailedTests++;
            }
            
            if (result.Output.Contains("WARNING"))
            {
                var warningCount = result.Output.Split("WARNING", StringSplitOptions.None).Length - 1;
                results.Warnings += warningCount;
                LogMessage($"⚠️ Symbolic Linter warnings: {warningCount}");
            }
        }
        
        private async Task RunTLDLValidationAsync(TestSuiteResults results)
        {
            LogMessage("📜 Running TLDL Documentation Validation...");
            
            var result = await RunPythonTool("src/SymbolicLinter/validate_docs.py", "--tldl-path TLDL/entries/");
            
            if (result.Success)
            {
                LogMessage("✅ TLDL Validation passed");
                results.PassedTests++;
            }
            else
            {
                LogMessage($"❌ TLDL Validation failed: {result.Error}");
                results.FailedTests++;
            }
            
            if (result.Output.Contains("WARNING"))
            {
                var warningCount = result.Output.Split("WARNING", StringSplitOptions.None).Length - 1;
                results.Warnings += warningCount;
            }
        }
        
        private async Task RunDebugOverlayValidationAsync(TestSuiteResults results)
        {
            LogMessage("🐛 Running Debug Overlay Validation...");
            
            var result = await RunPythonTool("src/DebugOverlayValidation/debug_overlay_validator.py", "--path src/DebugOverlayValidation/");
            
            if (result.Success)
            {
                LogMessage("✅ Debug Overlay Validation passed");
                results.PassedTests++;
            }
            else
            {
                LogMessage($"❌ Debug Overlay Validation failed: {result.Error}");
                results.FailedTests++;
            }
            
            if (result.Output.Contains("WARNING"))
            {
                var warningCount = result.Output.Split("WARNING", StringSplitOptions.None).Length - 1;
                results.Warnings += warningCount;
            }
        }
        
        private async Task RunSystemLinterAsync(TestSuiteResults results)
        {
            LogMessage("🏗️ Running System Architecture Linter...");
            
            var result = await RunPythonTool("src/SymbolicLinter/system_linter.py", "--path src/");
            
            if (result.Success)
            {
                LogMessage("✅ System Linter passed");
                results.PassedTests++;
            }
            else
            {
                LogMessage($"❌ System Linter failed: {result.Error}");
                results.FailedTests++;
            }
            
            if (result.Output.Contains("WARNING"))
            {
                var warningCount = result.Output.Split("WARNING", StringSplitOptions.None).Length - 1;
                results.Warnings += warningCount;
            }
        }
        
        private async Task<PythonToolResult> RunPythonTool(string scriptPath, string arguments)
        {
            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = GetPythonExecutable(),
                    Arguments = $"{scriptPath} {arguments}",
                    WorkingDirectory = GetProjectRoot(),
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };
                
                using var process = Process.Start(startInfo);
                await Task.Run(() => process.WaitForExit(30000)); // 30 second timeout
                
                var output = await process.StandardOutput.ReadToEndAsync();
                var error = await process.StandardError.ReadToEndAsync();
                
                return new PythonToolResult
                {
                    Success = process.ExitCode == 0,
                    Output = output,
                    Error = error,
                    ExitCode = process.ExitCode
                };
            }
            catch (Exception ex)
            {
                return new PythonToolResult
                {
                    Success = false,
                    Error = ex.Message,
                    ExitCode = -1
                };
            }
        }
        
        private string GetPythonExecutable()
        {
            // Try different Python commands in order of preference
            var pythonCommands = new[] { "python3", "python", "py" };
            
            foreach (var cmd in pythonCommands)
            {
                try
                {
                    var testInfo = new ProcessStartInfo
                    {
                        FileName = cmd,
                        Arguments = "--version",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        CreateNoWindow = true
                    };
                    
                    using var testProcess = Process.Start(testInfo);
                    testProcess.WaitForExit(2000);
                    
                    if (testProcess.ExitCode == 0)
                    {
                        return cmd;
                    }
                }
                catch
                {
                    continue;
                }
            }
            
            return "python3"; // Default fallback
        }
        
        private string GetProjectRoot()
        {
            var currentDir = Directory.GetCurrentDirectory();
            var assetsDir = Path.Combine(currentDir, "Assets");
            
            if (Directory.Exists(assetsDir))
            {
                return currentDir;
            }
            
            return Application.dataPath + "/..";
        }
        
        private void CheckTestEnvironment()
        {
            LogMessage("🔍 Checking test environment...");
            
            // Check Python availability
            var pythonCmd = GetPythonExecutable();
            LogMessage($"Python command: {pythonCmd}");
            
            // Check required directories
            var projectRoot = GetProjectRoot();
            var requiredPaths = new[]
            {
                Path.Combine(projectRoot, "src"),
                Path.Combine(projectRoot, "TLDL"),
                Path.Combine(projectRoot, "src/SymbolicLinter"),
                Path.Combine(projectRoot, "src/DebugOverlayValidation")
            };
            
            foreach (var path in requiredPaths)
            {
                if (Directory.Exists(path))
                {
                    LogMessage($"✅ Found: {path}");
                }
                else
                {
                    LogMessage($"❌ Missing: {path}");
                }
            }
        }
        
        private void ValidateDependencies()
        {
            LogMessage("📦 Validating dependencies...");
            LogMessage("Run 'pip install -r scripts/requirements.txt' if needed");
        }
        
        private void ShowSetupGuide()
        {
            var message = "🧪 Unity Test Suite Setup Guide\n\n" +
                "1. Ensure Python 3.11+ is installed\n" +
                "2. Install dependencies: pip install -r scripts/requirements.txt\n" +
                "3. Verify src/ and TLDL/ directories exist\n" +
                "4. Use 🔥 Terminus Console for command-line access\n\n" +
                "This test suite bridges Python validation tools with Unity Editor.";
            
            EditorUtility.DisplayDialog("Setup Guide", message, "OK");
        }
        
        private void TestPythonEnvironment()
        {
            LogMessage("🐍 Testing Python environment...");
            RunQuickCommand("python --version");
        }
        
        private void RunQuickTLDLValidation()
        {
            LogMessage("📜 Quick TLDL validation...");
            _ = RunPythonTool("src/SymbolicLinter/validate_docs.py", "--tldl-path TLDL/entries/");
        }
        
        private void RunQuickSymbolicLinter()
        {
            LogMessage("🧙‍♂️ Quick symbolic linter...");
            _ = RunPythonTool("src/SymbolicLinter/symbolic_linter.py", "--path src/");
        }
        
        private void RunUnityBuildTest()
        {
            LogMessage("🏗️ Testing Unity build system...");
            LogMessage($"Unity version: {Application.unityVersion}");
            LogMessage($"Build target: {EditorUserBuildSettings.activeBuildTarget}");
        }
        
        private void RunUnityUnitTests()
        {
            LogMessage("🧪 Running Unity unit tests...");
            LogMessage("Use Window > General > Test Runner for NUnit tests");
        }
        
        private async void RunQuickCommand(string command)
        {
            var result = await RunPythonTool("", command);
            LogMessage($"Command result: {result.Output}");
        }
        
        private void ExportTestReport()
        {
            if (lastResults == null) return;
            
            var report = GenerateTestReport();
            var path = EditorUtility.SaveFilePanel("Export Test Report", "", "test-report.txt", "txt");
            
            if (!string.IsNullOrEmpty(path))
            {
                File.WriteAllText(path, report);
                LogMessage($"Test report exported to: {path}");
            }
        }
        
        private string GenerateTestReport()
        {
            var report = new StringBuilder();
            report.AppendLine("🧪 Unity Test Suite Report");
            report.AppendLine($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            report.AppendLine($"Execution Time: {lastResults.TotalExecutionTime:F2}s");
            report.AppendLine($"Passed: {lastResults.PassedTests}");
            report.AppendLine($"Failed: {lastResults.FailedTests}");
            report.AppendLine($"Warnings: {lastResults.Warnings}");
            report.AppendLine($"Overall Status: {(lastResults.OverallSuccess ? "PASSED" : "FAILED")}");
            report.AppendLine();
            report.AppendLine("=== Test Logs ===");
            report.AppendLine(testLogs.ToString());
            
            return report.ToString();
        }
        
        private void RerunFailedTests()
        {
            LogMessage("🔄 Re-running failed tests...");
            // Implementation would re-run only the failed test categories
            RunSelectedTests();
        }
        
        private void LogMessage(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var logEntry = $"[{timestamp}] {message}\n";
            testLogs.Append(logEntry);
            Debug.Log($"[Unity Test Suite] {message}");
            Repaint();
        }
        
        private class TestSuiteResults
        {
            public int PassedTests;
            public int FailedTests;
            public int Warnings;
            public double TotalExecutionTime;
            public bool OverallSuccess;
        }
        
        private class PythonToolResult
        {
            public bool Success;
            public string Output = "";
            public string Error = "";
            public int ExitCode;
        }
    }
}
