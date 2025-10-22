using UnityEngine;
using UnityEditor;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using Debug = UnityEngine.Debug; // Resolve namespace conflict

namespace TWG.TLDA.TestSuite.Editor
{
    /// <summary>
    /// 🎯 LEGENDARY - One-Click Validation Runner
    /// Quick access to all Sacred Instructions validation tools
    /// Perfect for Unity developers who need instant validation feedback
    /// Sacred Vision: "All validation power in one click!"
    /// </summary>
    public static class OneClickValidationRunner
    {
        [MenuItem("Tools/Living Dev Agent/🚀 Run All Validations")]
        public static async void RunAllValidations()
        {
            Debug.Log("🚀 Starting One-Click Validation Suite...");
            
            var startTime = System.DateTime.Now;
            int passed = 0, failed = 0, warnings = 0;
            
            // 1. Symbolic Linter (~68ms)
            Debug.Log("🧙‍♂️ Running Symbolic Linter...");
            var symbolicResult = await RunValidationTool("src/SymbolicLinter/symbolic_linter.py", "--path src/");
            if (symbolicResult.Success) passed++; else failed++;
            warnings += CountWarnings(symbolicResult.Output);
            
            // 2. TLDL Validation (~60ms)
            Debug.Log("📜 Running TLDL Validation...");
            var tldlResult = await RunValidationTool("src/SymbolicLinter/validate_docs.py", "--tldl-path TLDL/entries/");
            if (tldlResult.Success) passed++; else failed++;
            warnings += CountWarnings(tldlResult.Output);
            
            // 3. Debug Overlay Validation (~56ms)
            Debug.Log("🐛 Running Debug Overlay Validation...");
            var debugResult = await RunValidationTool("src/DebugOverlayValidation/debug_overlay_validator.py", "--path src/DebugOverlayValidation/");
            if (debugResult.Success) passed++; else failed++;
            warnings += CountWarnings(debugResult.Output);
            
            var totalTime = (System.DateTime.Now - startTime).TotalSeconds;
            var overallSuccess = failed == 0;
            
            var status = overallSuccess ? "✅ ALL VALIDATIONS PASSED" : "❌ SOME VALIDATIONS FAILED";
            var message = $"{status}\n\nPassed: {passed}\nFailed: {failed}\nWarnings: {warnings}\nTime: {totalTime:F2}s";
            
            Debug.Log($"🎉 One-Click Validation Complete: {message}");
            EditorUtility.DisplayDialog("Validation Complete", message, "OK");
        }
        
        [MenuItem("Tools/Living Dev Agent/🧙‍♂️ Quick Symbolic Linter")]
        public static async void RunSymbolicLinter()
        {
            Debug.Log("🧙‍♂️ Running Quick Symbolic Linter...");
            var result = await RunValidationTool("src/SymbolicLinter/symbolic_linter.py", "--path src/");
            ShowQuickResult("Symbolic Linter", result);
        }
        
        [MenuItem("Tools/Living Dev Agent/📜 Quick TLDL Validation")]
        public static async void RunTLDLValidation()
        {
            Debug.Log("📜 Running Quick TLDL Validation...");
            var result = await RunValidationTool("src/SymbolicLinter/validate_docs.py", "--tldl-path TLDL/entries/");
            ShowQuickResult("TLDL Validation", result);
        }
        
        [MenuItem("Tools/Living Dev Agent/🐛 Quick Debug Overlay")]
        public static async void RunDebugOverlayValidation()
        {
            Debug.Log("🐛 Running Quick Debug Overlay Validation...");
            var result = await RunValidationTool("src/DebugOverlayValidation/debug_overlay_validator.py", "--path src/DebugOverlayValidation/");
            ShowQuickResult("Debug Overlay", result);
        }
        
        [MenuItem("Tools/Living Dev Agent/🔧 Validate Environment")]
        public static void ValidateEnvironment()
        {
            Debug.Log("🔧 Validating development environment...");
            
            var pythonAvailable = CheckPythonAvailability();
            var projectStructure = CheckProjectStructure();
            var dependencies = CheckDependencies();
            
            var message = $"🔧 Environment Validation\n\n" +
                         $"Python Available: {(pythonAvailable ? "✅" : "❌")}\n" +
                         $"Project Structure: {(projectStructure ? "✅" : "❌")}\n" +
                         $"Dependencies: {(dependencies ? "✅" : "❌")}";
            
            Debug.Log(message);
            EditorUtility.DisplayDialog("Environment Validation", message, "OK");
        }
        
        private static async Task<ValidationResult> RunValidationTool(string scriptPath, string arguments)
        {
            try
            {
                var pythonCmd = GetPythonExecutable();
                var projectRoot = GetProjectRoot();
                
                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonCmd,
                    Arguments = $"{scriptPath} {arguments}",
                    WorkingDirectory = projectRoot,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };
                
                using var process = Process.Start(startInfo);
                await Task.Run(() => process.WaitForExit(30000)); // 30 second timeout
                
                var output = await process.StandardOutput.ReadToEndAsync();
                var error = await process.StandardError.ReadToEndAsync();
                
                return new ValidationResult
                {
                    Success = process.ExitCode == 0,
                    Output = output,
                    Error = error,
                    ExitCode = process.ExitCode
                };
            }
            catch (System.Exception ex)
            {
                return new ValidationResult
                {
                    Success = false,
                    Error = ex.Message,
                    ExitCode = -1
                };
            }
        }
        
        private static string GetPythonExecutable()
        {
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
            
            return "python3";
        }
        
        private static string GetProjectRoot()
        {
            var currentDir = Directory.GetCurrentDirectory();
            var assetsDir = Path.Combine(currentDir, "Assets");
            
            if (Directory.Exists(assetsDir))
            {
                return currentDir;
            }
            
            return Application.dataPath + "/..";
        }
        
        private static bool CheckPythonAvailability()
        {
            try
            {
                var pythonCmd = GetPythonExecutable();
                var testInfo = new ProcessStartInfo
                {
                    FileName = pythonCmd,
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };
                
                using var testProcess = Process.Start(testInfo);
                testProcess.WaitForExit(2000);
                
                return testProcess.ExitCode == 0;
            }
            catch
            {
                return false;
            }
        }
        
        private static bool CheckProjectStructure()
        {
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
                if (!Directory.Exists(path))
                {
                    Debug.LogWarning($"Missing required directory: {path}");
                    return false;
                }
            }
            
            return true;
        }
        
        private static bool CheckDependencies()
        {
            var projectRoot = GetProjectRoot();
            var requirementsPath = Path.Combine(projectRoot, "scripts", "requirements.txt");
            
            if (!File.Exists(requirementsPath))
            {
                Debug.LogWarning("requirements.txt not found");
                return false;
            }
            
            // Could add more sophisticated dependency checking here
            return true;
        }
        
        private static int CountWarnings(string output)
        {
            if (string.IsNullOrEmpty(output)) return 0;
            return output.Split("WARNING", System.StringSplitOptions.None).Length - 1;
        }
        
        private static void ShowQuickResult(string toolName, ValidationResult result)
        {
            var status = result.Success ? "✅ PASSED" : "❌ FAILED";
            var warnings = CountWarnings(result.Output);
            var warningText = warnings > 0 ? $"\nWarnings: {warnings}" : "";
            
            var message = $"{toolName}: {status}{warningText}";
            
            Debug.Log($"{toolName} Result: {message}");
            
            if (!result.Success)
            {
                Debug.LogError($"{toolName} Error: {result.Error}");
            }
        }
        
        private class ValidationResult
        {
            public bool Success;
            public string Output = "";
            public string Error = "";
            public int ExitCode;
        }
    }
}
