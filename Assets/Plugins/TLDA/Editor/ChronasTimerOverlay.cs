#if UNITY_EDITOR
using System;
using System.Diagnostics;
using System.IO;
// 🔥 WARBLER COMPATIBILITY - Use facade types instead of real Unity types
using LivingDevAgent.Editor.Unity.Editor;
using LivingDevAgent.Editor.Unity.Editor.Overlays;
using LivingDevAgent.Editor.Unity;
using LivingDevAgent.Editor.Unity.UIElements;

// 🔥 WARBLER CORE COMPATIBILITY - Explicit namespace alias to avoid ML-Agents conflicts
using UnityDebug = LivingDevAgent.Editor.Unity.Debug;

namespace LivingDevAgent.Editor
{
    [Overlay(typeof(SceneView), "Chronas Timer", true)]
    public class ChronasTimerOverlay : Overlay
    {
        private VisualElement _root;
        private Label _statusLabel;
        private Label _timeLabel;
        private Button _startStopButton;
        private Button _pauseResumeButton;
        private TextField _taskNameField;
        private TextField _projectField;
        
        private bool _timerActive = false;
        private string _currentTask = "";
        private string _currentProject = "";
        private DateTime _lastUpdate = DateTime.MinValue;
        
        private const float UPDATE_INTERVAL = 1.0f; // Update every second
        
        public override VisualElement CreatePanelContent()
        {
            _root = new VisualElement();
            _root.style.minWidth = 250;
            _root.style.minHeight = 120;
            _root.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.9f);
            _root.style.borderTopColor = new Color(0.3f, 0.6f, 1.0f, 0.8f); // Reduced alpha for blue border
            _root.style.borderTopWidth = 2;
            _root.style.paddingTop = 5;
            _root.style.paddingBottom = 5;
            _root.style.paddingLeft = 5;
            _root.style.paddingRight = 5;
            _root.style.borderTopLeftRadius = 5;
            _root.style.borderTopRightRadius = 5;
            _root.style.borderBottomLeftRadius = 5;
            _root.style.borderBottomRightRadius = 5;
            
            // Header
            var header = new Label("🕰️ Chronas Timer");
            header.style.fontSize = 14;
            header.style.unityFontStyleAndWeight = FontStyle.Bold;
            header.style.color = Color.white;
            header.style.marginBottom = 5;
            _root.Add(header);
            
            // Status display
            _statusLabel = new Label("Timer: Stopped");
            _statusLabel.style.fontSize = 11;
            _statusLabel.style.color = new Color(0.8f, 0.8f, 0.8f);
            _root.Add(_statusLabel);
            
            _timeLabel = new Label("00:00:00");
            _timeLabel.style.fontSize = 12;
            _timeLabel.style.color = Color.white;
            _timeLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            _timeLabel.style.marginBottom = 5;
            _root.Add(_timeLabel);
            
            // Task input
            _taskNameField = new TextField("Task Name");
            _taskNameField.style.fontSize = 10;
            _taskNameField.style.marginBottom = 2;
            _taskNameField.value = "Scene work session";
            _root.Add(_taskNameField);
            
            _projectField = new TextField("Project");
            _projectField.style.fontSize = 10;
            _projectField.style.marginBottom = 5;
            _projectField.value = "Unity Development";
            _root.Add(_projectField);
            
            // Control buttons
            var buttonContainer = new VisualElement();
            buttonContainer.style.flexDirection = FlexDirection.Row;
            buttonContainer.style.justifyContent = Justify.SpaceBetween;

            _startStopButton = new Button(StartStopTimer)
            {
                text = "Start"
            };
            _startStopButton.style.fontSize = 10;
            _startStopButton.style.width = 60;
            _startStopButton.style.backgroundColor = new Color(0.2f, 0.7f, 0.2f, 0.8f);

            _pauseResumeButton = new Button(PauseResumeTimer)
            {
                text = "Pause"
            };
            _pauseResumeButton.style.fontSize = 10;
            _pauseResumeButton.style.width = 60;
            _pauseResumeButton.style.backgroundColor = new Color(0.7f, 0.5f, 0.2f, 0.8f);
            _pauseResumeButton.SetEnabled(false);

            var refreshButton = new Button(RefreshStatus)
            {
                text = "Refresh"
            };
            refreshButton.style.fontSize = 10;
            refreshButton.style.width = 60;
            refreshButton.style.backgroundColor = new Color(0.2f, 0.5f, 0.7f, 0.8f);
            
            buttonContainer.Add(_startStopButton);
            buttonContainer.Add(_pauseResumeButton);
            buttonContainer.Add(refreshButton);
            _root.Add(buttonContainer);
            
            // Register for updates
            EditorApplication.update += UpdateTimerDisplay;
            
            // Initial status check
            RefreshStatus();
            
            return _root;
        }
        
        public override void OnWillBeDestroyed()
        {
            EditorApplication.update -= UpdateTimerDisplay;
            base.OnWillBeDestroyed();
        }
        
        private void UpdateTimerDisplay()
        {
            // Only update every second to avoid performance issues
            if ((DateTime.Now - _lastUpdate).TotalSeconds < UPDATE_INTERVAL)
                return;
                
            _lastUpdate = DateTime.Now;
            
            // Auto-refresh status periodically when timer is active
            if (_timerActive)
            {
                RefreshStatus();
            }
        }
        
        private void StartStopTimer()
        {
            try
            {
                if (_timerActive)
                {
                    // Stop timer
                    var notes = $"Scene work completed via Unity overlay";
                    RunChronasCommand($"--stop --notes \"{notes}\"");
                }
                else
                {
                    // Start timer
                    var taskName = string.IsNullOrWhiteSpace(_taskNameField.value) ? "Unity scene work" : _taskNameField.value;
                    var project = string.IsNullOrWhiteSpace(_projectField.value) ? "" : _projectField.value;
                    
                    var projectArg = string.IsNullOrEmpty(project) ? "" : $"--project \"{project}\"";
                    RunChronasCommand($"--start \"{taskName}\" {projectArg} --category \"unity-development\"");
                }
                
                // Refresh status after a short delay
                EditorApplication.delayCall += () => {
                    System.Threading.Thread.Sleep(100);
                    RefreshStatus();
                };
            }
            catch (Exception ex)
            {
                UnityDebug.LogError($"[Chronas Overlay] Error in start/stop: {ex.Message}");
                _statusLabel.text = $"Error: {ex.Message}";
            }
        }
        
        private void PauseResumeTimer()
        {
            try
            {
                // For now, we'll use shared timer service pause/resume
                var timerServicePath = GetTimerServicePath();
                if (File.Exists(timerServicePath))
                {
                    if (_statusLabel.text.Contains("running"))
                    {
                        RunPythonCommand(timerServicePath, "--pause");
                    }
                    else if (_statusLabel.text.Contains("paused"))
                    {
                        RunPythonCommand(timerServicePath, "--resume");
                    }
                    
                    EditorApplication.delayCall += () => {
                        System.Threading.Thread.Sleep(100);
                        RefreshStatus();
                    };
                }
            }
            catch (Exception ex)
            {
                UnityDebug.LogError($"[Chronas Overlay] Error in pause/resume: {ex.Message}");
            }
        }
        
        private void RefreshStatus()
        {
            try
            {
                var statusOutput = RunChronasCommand("--status");
                ParseStatusOutput(statusOutput);
            }
            catch (Exception ex)
            {
                UnityDebug.LogError($"[Chronas Overlay] Error refreshing status: {ex.Message}");
                _statusLabel.text = "Error: Could not get status";
                _timeLabel.text = "00:00:00";
                _timerActive = false;
                UpdateButtonStates();
            }
        }
        
        private void ParseStatusOutput(string output)
        {
            if (string.IsNullOrEmpty(output))
            {
                _statusLabel.text = "Timer: Stopped";
                _timeLabel.text = "00:00:00";
                _timerActive = false;
                UpdateButtonStates();
                return;
            }
            
            _timerActive = output.Contains("Active Session") || output.Contains("Active Timer");
            
            if (_timerActive)
            {
                // Extract task name
                var lines = output.Split("\n");
                foreach (var line in lines)
                {
                    if (line.Contains("Task:"))
                    {
                        _currentTask = line[ (line.IndexOf("Task:") + 5).. ].Trim();
                        break;
                    }
                    else if (line.Contains("Active Timer:"))
                    {
                        _currentTask = line[ (line.IndexOf("Active Timer:") + 13).. ].Trim();
                        break;
                    }
                }
                
                // Extract project
                foreach (var line in lines)
                {
                    if (line.Contains("Project:"))
                    {
                        _currentProject = line[ (line.IndexOf("Project:") + 8).. ].Trim();
                        break;
                    }
                }
                
                // Extract elapsed time
                string elapsedTime = "00:00:00";
                foreach (var line in lines)
                {
                    if (line.Contains("Elapsed:"))
                    {
                        var elapsedPart = line[ (line.IndexOf("Elapsed:") + 8).. ].Trim();
                        // Extract time portion (HH:MM:SS format)
                        var timeMatch = System.Text.RegularExpressions.Regex.Match(elapsedPart, @"(\d{2}:\d{2}:\d{2})");
                        if (timeMatch.Success)
                        {
                            elapsedTime = timeMatch.Groups[1].Value;
                        }
                        break;
                    }
                }
                
                _statusLabel.text = $"Timer: Running - {_currentTask}";
                _timeLabel.text = elapsedTime;
                
                if (!string.IsNullOrEmpty(_currentProject))
                {
                    _statusLabel.text += $" ({_currentProject})";
                }
            }
            else
            {
                _statusLabel.text = "Timer: Stopped";
                _timeLabel.text = "00:00:00";
                _currentTask = "";
                _currentProject = "";
            }
            
            UpdateButtonStates();
        }
        
        private void UpdateButtonStates()
        {
            if (_timerActive)
            {
                _startStopButton.text = "Stop";
                _startStopButton.style.backgroundColor = new Color(0.7f, 0.2f, 0.2f, 0.8f);
                _pauseResumeButton.SetEnabled(true);
                _taskNameField.SetEnabled(false);
                _projectField.SetEnabled(false);
            }
            else
            {
                _startStopButton.text = "Start";
                _startStopButton.style.backgroundColor = new Color(0.2f, 0.7f, 0.2f, 0.8f);
                _pauseResumeButton.SetEnabled(false);
                _taskNameField.SetEnabled(true);
                _projectField.SetEnabled(true);
            }
        }
        
        private string RunChronasCommand(string args)
        {
            try
            {
                var chronasPath = GetChronasPath();
                if (!File.Exists(chronasPath))
                {
                    throw new FileNotFoundException($"Chronas script not found at: {chronasPath}");
                }
                
                return RunPythonCommand(chronasPath, args);
            }
            catch (Exception ex)
            {
                UnityDebug.LogError($"[Chronas Overlay] Failed to run Chronas command: {ex.Message}");
                throw;
            }
        }
        
        private string RunPythonCommand(string scriptPath, string args)
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = "python3",
                Arguments = $"\"{scriptPath}\" {args}",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                WorkingDirectory = GetProjectRoot()
            };
            
            using (var process = Process.Start(startInfo))
            {
                process.WaitForExit(5000); // 5 second timeout
                
                if (!process.HasExited)
                {
                    process.Kill();
                    throw new TimeoutException("Python command timed out");
                }
                
                var output = process.StandardOutput.ReadToEnd();
                var error = process.StandardError.ReadToEnd();
                
                if (process.ExitCode != 0 && !string.IsNullOrEmpty(error))
                {
                    throw new Exception($"Python command failed: {error}");
                }
                
                return output;
            }
        }
        
        private string GetChronasPath()
        {
            var projectRoot = GetProjectRoot();
            return Path.Combine(projectRoot, "src", "TimeTracking", "chronas.py");
        }
        
        private string GetTimerServicePath()
        {
            var projectRoot = GetProjectRoot();
            return Path.Combine(projectRoot, "src", "SharedServices", "timer_service.py");
        }
        
        private string GetProjectRoot()
        {
            // Find project root by looking for Assets directory
            var currentDir = Directory.GetCurrentDirectory();
            var assetsDir = Path.Combine(currentDir, "Assets");
            
            if (Directory.Exists(assetsDir))
            {
                return currentDir;
            }
            
            // Fallback: look for parent directories
            var parent = Directory.GetParent(currentDir);
            while (parent != null)
            {
                var testAssetsDir = Path.Combine(parent.FullName, "Assets");
                if (Directory.Exists(testAssetsDir))
                {
                    return parent.FullName;
                }
                parent = parent.Parent;
            }
            
            // Ultimate fallback
            return currentDir;
        }
    }
}
#endif
