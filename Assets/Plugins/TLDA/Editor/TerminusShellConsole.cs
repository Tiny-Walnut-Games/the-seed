#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System;

namespace LivingDevAgent.Editor.Scribe
{
    /// <summary>
    /// 🔥 LEGENDARY - Terminus: In-Unity Shell Console
    /// The sacred command interface that brings bash/PowerShell directly into Unity!
    /// Complete with realtime feedback, command history, and quick action buttons.
    /// Sacred Vision: "No more switching to external terminals - the shell lives HERE!"
    /// </summary>
    public class TerminusShellConsole : EditorWindow
    {
        // Console state
        private readonly List<TerminalEntry> _history = new();
        private readonly List<string> _commandHistory = new();
        private string _currentCommand = "";
        private string _currentDirectory = "";
        private int _commandHistoryIndex = -1;
        private Vector2 _scrollPosition;
        private bool _focusCommandInput = false;
        
        // Shell process
        private Process _shellProcess;
        private bool _isExecuting = false;
        private readonly StringBuilder _outputBuffer = new();

        // UI Styles
        private GUIStyle _terminalStyle;
        private GUIStyle _commandStyle;
        private GUIStyle _outputStyle;
        private GUIStyle _errorStyle;
        private bool _stylesInitialized = false;
        
        // Quick commands - now organized by category
        private readonly Dictionary<string, string[]> _commandCategories = new()
        {
            ["System"] = new[] { "ls", "dir", "pwd", "cd ..", "ps", "top", "df -h", "free -h" },
            ["Git"] = new[] { "git status", "git log --oneline -5", "git branch", "git diff" },
            ["Package Mgr"] = new[] { "python --version", "pip --version", "npm --version", "node --version" },
            ["Network"] = new[] { "ping google.com", "curl --version", "wget --version", "ssh --version" }
        };
        
        [MenuItem("Tools/Living Dev Agent/🔥 Terminus Console")]
        public static void ShowWindow()
        {
            var window = GetWindow<TerminusShellConsole>("🔥 Terminus");
            window.minSize = new Vector2(600, 400);
            window.Show();
        }
        
        void OnEnable()
        {
            _currentDirectory = Path.GetDirectoryName(Application.dataPath);
            AddHistoryEntry("🔥 Terminus Shell Console Activated", TerminalEntryType.System);
            AddHistoryEntry($"📁 Working Directory: {_currentDirectory}", TerminalEntryType.System);
            AddHistoryEntry("Type 'help' for available commands, or use quick buttons below", TerminalEntryType.System);
        }
        
        void OnDisable()
        {
            CleanupShellProcess();
        }
        
        void OnGUI()
        {
            InitializeStyles();
            
            EditorGUILayout.BeginVertical();
            {
                DrawHeader();
                DrawTerminalOutput();
                DrawCommandInput();
                DrawQuickActions();
            }
            EditorGUILayout.EndVertical();
            
            HandleKeyboardShortcuts();
        }
        
        void InitializeStyles()
        {
            if (_stylesInitialized) return;
            
            _terminalStyle = new GUIStyle(EditorStyles.textArea)
            {
                font = Font.CreateDynamicFontFromOSFont(new[] { "Consolas", "Monaco", "Lucida Console" }, 11),
                richText = true,
                wordWrap = true,
                normal = { background = CreateColorTexture(new Color(0.1f, 0.1f, 0.1f, 0.8f)) }
            };
            
            _commandStyle = new GUIStyle(EditorStyles.textField)
            {
                font = Font.CreateDynamicFontFromOSFont(new[] { "Consolas", "Monaco", "Lucida Console" }, 12),
                normal = { textColor = Color.green }
            };
            
            _outputStyle = new GUIStyle(EditorStyles.label)
            {
                font = Font.CreateDynamicFontFromOSFont(new[] { "Consolas", "Monaco", "Lucida Console" }, 10),
                richText = true,
                wordWrap = true,
                normal = { textColor = Color.white }
            };
            
            _errorStyle = new GUIStyle(_outputStyle)
            {
                normal = { textColor = Color.red }
            };
            
            _stylesInitialized = true;
        }
        
        Texture2D CreateColorTexture(Color color)
        {
            var texture = new Texture2D(1, 1);
            texture.SetPixel(0, 0, color);
            texture.Apply();
            return texture;
        }
        
        void DrawHeader()
        {
            EditorGUILayout.BeginHorizontal(EditorStyles.toolbar);
            {
                GUILayout.Label("🔥 Terminus Shell Console", EditorStyles.boldLabel);
                
                GUILayout.FlexibleSpace();
                
                if (GUILayout.Button("📁 CD", EditorStyles.toolbarButton, GUILayout.Width(60)))
                {
                    ChangeDirectory();
                }
                
                if (GUILayout.Button("🧹 Clear", EditorStyles.toolbarButton, GUILayout.Width(70)))
                {
                    ClearHistory();
                }
                
                if (GUILayout.Button("⚙️ Settings", EditorStyles.toolbarButton, GUILayout.Width(80)))
                {
                    ShowSettings();
                }
            }
            EditorGUILayout.EndHorizontal();
            
            // Current directory display
            EditorGUILayout.BeginHorizontal(EditorStyles.helpBox);
            {
                GUILayout.Label("📁", GUILayout.Width(20));
                EditorGUILayout.SelectableLabel(_currentDirectory, EditorStyles.miniLabel);
                
                if (GUILayout.Button("📋", GUILayout.Width(25)))
                {
                    GUIUtility.systemCopyBuffer = _currentDirectory;
                }
            }
            EditorGUILayout.EndHorizontal();
        }
        
        void DrawTerminalOutput()
        {
            _scrollPosition = EditorGUILayout.BeginScrollView(_scrollPosition, _terminalStyle, GUILayout.ExpandHeight(true));
            {
                foreach (var entry in _history)
                {
                    var style = entry.Type switch
                    {
                        TerminalEntryType.Command => _commandStyle,
                        TerminalEntryType.Error => _errorStyle,
                        TerminalEntryType.System => _outputStyle,
                        _ => _outputStyle
                    };
                    
                    var icon = entry.Type switch
                    {
                        TerminalEntryType.Command => "$ ",
                        TerminalEntryType.Error => "❌ ",
                        TerminalEntryType.System => "🔥 ",
                        _ => "   "
                    };
                    
                    EditorGUILayout.SelectableLabel($"{icon}{entry.Text}", style);
                }
                
                if (_isExecuting)
                {
                    EditorGUILayout.LabelField("⏳ Executing...", _outputStyle);
                }
            }
            EditorGUILayout.EndScrollView();
            
            // Auto-scroll to bottom
            if (Event.current.type == EventType.Repaint)
            {
                _scrollPosition.y = float.MaxValue;
            }
        }
        
        void DrawCommandInput()
        {
            EditorGUILayout.BeginHorizontal();
            {
                GUILayout.Label("$", GUILayout.Width(15));
                
                GUI.SetNextControlName("CommandInput");
                var newCommand = EditorGUILayout.TextField(_currentCommand, _commandStyle);
                
                if (_focusCommandInput)
                {
                    GUI.FocusControl("CommandInput");
                    _focusCommandInput = false;
                }
                
                // Handle command execution
                if (Event.current.type == EventType.KeyDown)
                {
                    if (Event.current.keyCode == KeyCode.Return)
                    {
                        ExecuteCommand(_currentCommand);
                        _currentCommand = "";
                        _focusCommandInput = true;
                        Event.current.Use();
                    }
                    else if (Event.current.keyCode == KeyCode.UpArrow)
                    {
                        NavigateCommandHistory(-1);
                        Event.current.Use();
                    }
                    else if (Event.current.keyCode == KeyCode.DownArrow)
                    {
                        NavigateCommandHistory(1);
                        Event.current.Use();
                    }
                    else if (Event.current.keyCode == KeyCode.Tab)
                    {
                        AutoCompleteCommand();
                        Event.current.Use();
                    }
                }
                
                _currentCommand = newCommand;
                
                GUI.enabled = !_isExecuting;
                if (GUILayout.Button("▶️", GUILayout.Width(30)))
                {
                    ExecuteCommand(_currentCommand);
                    _currentCommand = "";
                    _focusCommandInput = true;
                }
                GUI.enabled = true;
            }
            EditorGUILayout.EndHorizontal();
        }
        
        void DrawQuickActions()
        {
            EditorGUILayout.LabelField("🚀 Quick Commands:", EditorStyles.boldLabel);
            
            var buttonWidth = (position.width - 40) / 4;
            
            // 🔧 Package Manager Installation Shortcuts
            EditorGUILayout.LabelField("📦 Package Manager Shortcuts:", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("🐍 Install Python", GUILayout.Width(buttonWidth)))
                {
                    ShowPythonInstallGuide();
                }
                
                if (GUILayout.Button("📦 Install pip", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("python -m ensurepip --upgrade");
                }
                
                if (GUILayout.Button("📱 Install npm", GUILayout.Width(buttonWidth)))
                {
                    ShowNpmInstallGuide();
                }
                
                if (GUILayout.Button("🎮 UPM Registry", GUILayout.Width(buttonWidth)))
                {
                    ShowUnityPackageManager();
                }
            }
            EditorGUILayout.EndHorizontal();
            
            // Git workflow commands
            EditorGUILayout.LabelField("🐙 Git Workflow:", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("🔐 Config", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git config --list");
                }
                
                if (GUILayout.Button("💾 Status", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git status");
                }
                
                if (GUILayout.Button("📡 Fetch", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git fetch");
                }
                
                if (GUILayout.Button("⬆️ Push", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git push");
                }
            }
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("⬇️ Pull", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git pull");
                }
                
                if (GUILayout.Button("🌿 Branch", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git branch -a");
                }
                
                if (GUILayout.Button("📜 Log", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git log --oneline -10");
                }
                
                if (GUILayout.Button("🔀 Diff", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("git diff");
                }
            }
            EditorGUILayout.EndHorizontal();
            
            // 🌐 Network & System Tools
            EditorGUILayout.LabelField("🌐 Network & System:", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("🏓 Ping Test", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("ping -c 4 google.com");
                }
                
                if (GUILayout.Button("📊 System Info", GUILayout.Width(buttonWidth)))
                {
                    var sysCommand = Application.platform == RuntimePlatform.WindowsEditor ? "systeminfo" : "uname -a";
                    ExecuteCommand(sysCommand);
                }
                
                if (GUILayout.Button("💾 Disk Usage", GUILayout.Width(buttonWidth)))
                {
                    var diskCommand = Application.platform == RuntimePlatform.WindowsEditor ? "dir /-c" : "df -h";
                    ExecuteCommand(diskCommand);
                }
                
                if (GUILayout.Button("🔄 Processes", GUILayout.Width(buttonWidth)))
                {
                    var procCommand = Application.platform == RuntimePlatform.WindowsEditor ? "tasklist" : "ps aux";
                    ExecuteCommand(procCommand);
                }
            }
            EditorGUILayout.EndHorizontal();
            
            // 🎭 LDA-Specific Commands
            EditorGUILayout.LabelField("🎭 Living Dev Agent:", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("🔧 Scripts", GUILayout.Width(buttonWidth)))
                {
                    var scriptsPath = Path.Combine(Path.GetDirectoryName(Application.dataPath), "scripts");
                    if (Directory.Exists(scriptsPath))
                    {
                        ExecuteCommand($"cd \"{scriptsPath}\" && ls -la");
                    }
                    else
                    {
                        AddHistoryEntry("Scripts directory not found", TerminalEntryType.Error);
                    }
                }
                
                if (GUILayout.Button("📚 Docs", GUILayout.Width(buttonWidth)))
                {
                    var docsPath = Path.Combine(Path.GetDirectoryName(Application.dataPath), "docs");
                    if (Directory.Exists(docsPath))
                    {
                        ExecuteCommand($"cd \"{docsPath}\" && ls -la");
                    }
                    else
                    {
                        AddHistoryEntry("Docs directory not found", TerminalEntryType.Error);
                    }
                }
                
                if (GUILayout.Button("🎭 Quote Oracle", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("python src/ScrollQuoteEngine/warbler_quote_engine.py --warbler");
                }
                
                if (GUILayout.Button("🧪 Validate", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("python scripts/validate_setup.py");
                }
            }
            EditorGUILayout.EndHorizontal();
            
            // 🛠️ Development Environment Tools
            EditorGUILayout.LabelField("🛠️ Dev Environment:", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            {
                if (GUILayout.Button("🔍 Which Python", GUILayout.Width(buttonWidth)))
                {
                    var whichCommand = Application.platform == RuntimePlatform.WindowsEditor ? "where python" : "which python3";
                    ExecuteCommand(whichCommand);
                }
                
                if (GUILayout.Button("📦 Pip List", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("pip list");
                }
                
                if (GUILayout.Button("🎯 Node Info", GUILayout.Width(buttonWidth)))
                {
                    ExecuteCommand("node --version && npm --version");
                }
                
                if (GUILayout.Button("⚙️ Environment", GUILayout.Width(buttonWidth)))
                {
                    var envCommand = Application.platform == RuntimePlatform.WindowsEditor ? "set" : "env";
                    ExecuteCommand(envCommand);
                }
            }
            EditorGUILayout.EndHorizontal();
        }
        
        void ExecuteCommand(string command)
        {
            if (string.IsNullOrWhiteSpace(command)) return;
            
            AddHistoryEntry(command, TerminalEntryType.Command);
            
            if (!_commandHistory.Contains(command))
            {
                _commandHistory.Add(command);
            }
            _commandHistoryIndex = -1;
            
            // Handle built-in commands
            if (HandleBuiltInCommand(command)) return;
            
            // Execute external command
            ExecuteExternalCommand(command);
        }
        
        bool HandleBuiltInCommand(string command)
        {
            var parts = command.Split(' ', System.StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length == 0) return false;
            
            switch (parts[0].ToLower())
            {
                case "help":
                    ShowHelp();
                    return true;
                    
                case "clear":
                    ClearHistory();
                    return true;
                    
                case "cd":
                    if (parts.Length > 1)
                    {
                        ChangeDirectoryTo(string.Join(" ", parts, 1, parts.Length - 1));
                    }
                    else
                    {
                        ChangeDirectory();
                    }
                    return true;
                    
                case "pwd":
                    AddHistoryEntry(_currentDirectory, TerminalEntryType.Output);
                    return true;
                    
                case "history":
                    ShowCommandHistory();
                    return true;
                    
                default:
                    return false;
            }
        }
        
        async void ExecuteExternalCommand(string command)
        {
            _isExecuting = true;
            Repaint();
            
            try
            {
                await Task.Run(() =>
                {
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = GetShellExecutable(),
                        Arguments = GetShellArguments(command),
                        WorkingDirectory = _currentDirectory,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };
                    
                    using var process = Process.Start(startInfo);
                    process.WaitForExit(30000); // 30 second timeout
                    
                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    
                    if (!string.IsNullOrEmpty(output))
                    {
                        EditorApplication.delayCall += () => AddHistoryEntry(output.TrimEnd(), TerminalEntryType.Output);
                    }
                    
                    if (!string.IsNullOrEmpty(error))
                    {
                        EditorApplication.delayCall += () => AddHistoryEntry(error.TrimEnd(), TerminalEntryType.Error);
                    }
                    
                    if (process.ExitCode != 0 && string.IsNullOrEmpty(error))
                    {
                        EditorApplication.delayCall += () => AddHistoryEntry($"Process exited with code {process.ExitCode}", TerminalEntryType.Error);
                    }
                });
            }
            catch (System.Exception e)
            {
                AddHistoryEntry($"Command failed: {e.Message}", TerminalEntryType.Error);
            }
            finally
            {
                _isExecuting = false;
                EditorApplication.delayCall += () => Repaint();
            }
        }
        
        string GetShellExecutable()
        {
            return Application.platform == RuntimePlatform.WindowsEditor ? "cmd" : "/bin/bash";
        }
        
        string GetShellArguments(string command)
        {
            return Application.platform == RuntimePlatform.WindowsEditor ? $"/c {command}" : $"-c \"{command}\"";
        }
        
        void NavigateCommandHistory(int direction)
        {
            if (_commandHistory.Count == 0) return;
            
            _commandHistoryIndex += direction;
            _commandHistoryIndex = Mathf.Clamp(_commandHistoryIndex, -1, _commandHistory.Count - 1);
            
            if (_commandHistoryIndex >= 0)
            {
                _currentCommand = _commandHistory[_commandHistoryIndex];
            }
            else
            {
                _currentCommand = "";
            }
        }
        
        void AutoCompleteCommand()
        {
            // Basic autocomplete for quick commands
            foreach (var category in _commandCategories.Values)
            {
                foreach (var quickCmd in category)
                {
                    if (quickCmd.StartsWith(_currentCommand, System.StringComparison.OrdinalIgnoreCase))
                    {
                        _currentCommand = quickCmd;
                        return;
                    }
                }
            }
        }
        
        void ChangeDirectory()
        {
            var newPath = EditorUtility.OpenFolderPanel("Change Directory", _currentDirectory, "");
            if (!string.IsNullOrEmpty(newPath))
            {
                _currentDirectory = newPath;
                AddHistoryEntry($"Changed directory to: {_currentDirectory}", TerminalEntryType.System);
            }
        }
        
        void ChangeDirectoryTo(string path)
        {
            try
            {
                // Sanitize the path to avoid illegal characters
                if (string.IsNullOrWhiteSpace(path))
                {
                    AddHistoryEntry("Path cannot be empty", TerminalEntryType.Error);
                    return;
                }
                
                // Remove quotes if present
                path = path.Trim('"', '\'');

                var targetPath = Path.IsPathRooted(path) ? path : Path.Combine(_currentDirectory, path);
                
                if (Directory.Exists(targetPath))
                {
                    _currentDirectory = Path.GetFullPath(targetPath);
                    AddHistoryEntry($"Changed directory to: {_currentDirectory}", TerminalEntryType.System);
                }
                else
                {
                    AddHistoryEntry($"Directory not found: {targetPath}", TerminalEntryType.Error);
                }
            }
            catch (ArgumentException ex)
            {
                AddHistoryEntry($"Invalid path: {ex.Message}", TerminalEntryType.Error);
            }
            catch (Exception ex)
            {
                AddHistoryEntry($"Failed to change directory: {ex.Message}", TerminalEntryType.Error);
            }
        }
        
        void ShowHelp()
        {
            AddHistoryEntry("🔥 Terminus Commands & Interfaces:", TerminalEntryType.System);
            AddHistoryEntry("", TerminalEntryType.Output);
            
            AddHistoryEntry("🖥️ Built-in Commands:", TerminalEntryType.System);
            AddHistoryEntry("  help - Show this comprehensive help", TerminalEntryType.Output);
            AddHistoryEntry("  clear - Clear terminal history", TerminalEntryType.Output);
            AddHistoryEntry("  cd [path] - Change directory", TerminalEntryType.Output);
            AddHistoryEntry("  pwd - Show current directory", TerminalEntryType.Output);
            AddHistoryEntry("  history - Show command history", TerminalEntryType.Output);
            AddHistoryEntry("", TerminalEntryType.Output);
            
            AddHistoryEntry("📦 Package Managers:", TerminalEntryType.System);
            AddHistoryEntry("  🐍 Python: python, pip, pip3", TerminalEntryType.Output);
            AddHistoryEntry("  📱 Node.js: node, npm, npx, yarn", TerminalEntryType.Output);
            AddHistoryEntry("  🎮 Unity: UPM (Window > Package Manager)", TerminalEntryType.Output);
            AddHistoryEntry("  🪟 Windows: winget, choco", TerminalEntryType.Output);
            AddHistoryEntry("  🍺 macOS: brew, port", TerminalEntryType.Output);
            AddHistoryEntry("  🐧 Linux: apt, yum, dnf, pacman", TerminalEntryType.Output);
            AddHistoryEntry("", TerminalEntryType.Output);
            
            AddHistoryEntry("🛠️ System Tools Available:", TerminalEntryType.System);
            AddHistoryEntry("  📂 Navigation: ls, dir, find, tree", TerminalEntryType.Output);
            AddHistoryEntry("  ⚙️ Processes: ps, top, htop, tasklist", TerminalEntryType.Output);
            AddHistoryEntry("  🌐 Network: ping, curl, wget, ssh", TerminalEntryType.Output);
            AddHistoryEntry("  💾 System: df, du, free, systeminfo", TerminalEntryType.Output);
            AddHistoryEntry("  🐙 Git: status, log, branch, diff, push, pull", TerminalEntryType.Output);
            AddHistoryEntry("", TerminalEntryType.Output);
            
            AddHistoryEntry("🎮 Keyboard Shortcuts:", TerminalEntryType.System);
            AddHistoryEntry("  Enter - Execute command", TerminalEntryType.Output);
            AddHistoryEntry("  Up/Down - Navigate command history", TerminalEntryType.Output);
            AddHistoryEntry("  Tab - Autocomplete command", TerminalEntryType.Output);
            AddHistoryEntry("  Ctrl+L - Clear terminal", TerminalEntryType.Output);
            AddHistoryEntry("", TerminalEntryType.Output);
            
            AddHistoryEntry("🎭 LDA-Specific Features:", TerminalEntryType.System);
            AddHistoryEntry("  🎭 Quote Oracle - Warbler wisdom generation", TerminalEntryType.Output);
            AddHistoryEntry("  🧪 Validation - Project health checks", TerminalEntryType.Output);
            AddHistoryEntry("  📚 Docs/Scripts - Quick navigation helpers", TerminalEntryType.Output);
            AddHistoryEntry("", TerminalEntryType.Output);
            
            AddHistoryEntry("💡 Pro Tips:", TerminalEntryType.System);
            AddHistoryEntry("  • Use quick buttons for common operations", TerminalEntryType.Output);
            AddHistoryEntry("  • Commands execute in current working directory", TerminalEntryType.Output);
            AddHistoryEntry("  • Platform-specific commands auto-detected", TerminalEntryType.Output);
            AddHistoryEntry("  • 30-second timeout on external commands", TerminalEntryType.Output);
        }
        
        void ShowCommandHistory()
        {
            AddHistoryEntry("📜 Command History:", TerminalEntryType.System);
            for (int i = 0; i < _commandHistory.Count; i++)
            {
                AddHistoryEntry($"  {i + 1}: {_commandHistory[i]}", TerminalEntryType.Output);
            }
        }
        
        void ClearHistory()
        {
            _history.Clear();
            AddHistoryEntry("🔥 Terminal cleared", TerminalEntryType.System);
        }
        
        void ShowSettings()
        {
            AddHistoryEntry("⚙️ Settings panel not yet implemented", TerminalEntryType.System);
        }
        
        void HandleKeyboardShortcuts()
        {
            var e = Event.current;
            if (e.type == EventType.KeyDown)
            {
                if (e.control && e.keyCode == KeyCode.L)
                {
                    ClearHistory();
                    e.Use();
                }
            }
        }
        
        void AddHistoryEntry(string text, TerminalEntryType type)
        {
            _history.Add(new TerminalEntry { Text = text, Type = type, Timestamp = System.DateTime.Now });
            
            // Limit history size
            while (_history.Count > 1000)
            {
                _history.RemoveAt(0);
            }
            
            Repaint();
        }
        
        void CleanupShellProcess()
        {
            if (_shellProcess != null && !_shellProcess.HasExited)
            {
                _shellProcess.Kill();
                _shellProcess.Dispose();
                _shellProcess = null;
            }
        }
        
        struct TerminalEntry
        {
            public string Text;
            public TerminalEntryType Type;
            public System.DateTime Timestamp;
        }
        
        enum TerminalEntryType
        {
            Command,
            Output,
            Error,
            System
        }

        /// <summary>
        /// 🐍 Python Installation Guide for different platforms
        /// </summary>
        void ShowPythonInstallGuide()
        {
            var message = Application.platform == RuntimePlatform.WindowsEditor ?
                "🐍 Python Installation (Windows):\n\n" +
                "1. Download from python.org\n" +
                "2. Run: winget install Python.Python.3.12\n" +
                "3. Or use Microsoft Store\n" +
                "4. Restart terminal after install" :
                "🐍 Python Installation (macOS/Linux):\n\n" +
                "macOS: brew install python3\n" +
                "Ubuntu: sudo apt install python3 python3-pip\n" +
                "CentOS: sudo yum install python3 python3-pip";
            
            AddHistoryEntry(message, TerminalEntryType.System);
            
            if (Application.platform == RuntimePlatform.WindowsEditor)
            {
                AddHistoryEntry("Checking if Python is already installed...", TerminalEntryType.System);
                ExecuteCommand("python --version");
            }
        }
        
        /// <summary>
        /// 📱 NPM Installation Guide
        /// </summary>
        void ShowNpmInstallGuide()
        {
            var message = Application.platform == RuntimePlatform.WindowsEditor ?
                "📱 Node.js & NPM Installation (Windows):\n\n" +
                "1. Download from nodejs.org\n" +
                "2. Run: winget install OpenJS.NodeJS\n" +
                "3. Or download installer from nodejs.org\n" +
                "4. NPM comes bundled with Node.js" :
                "📱 Node.js & NPM Installation:\n\n" +
                "macOS: brew install node\n" +
                "Ubuntu: sudo apt install nodejs npm\n" +
                "Or use Node Version Manager (nvm)";
            
            AddHistoryEntry(message, TerminalEntryType.System);
            ExecuteCommand("node --version && npm --version");
        }
        
        /// <summary>
        /// 🎮 Unity Package Manager integration
        /// </summary>
        void ShowUnityPackageManager()
        {
            AddHistoryEntry("🎮 Unity Package Manager (UPM) Quick Actions:", TerminalEntryType.System);
            AddHistoryEntry("• Window > Package Manager (in Unity)", TerminalEntryType.Output);
            AddHistoryEntry("• Add package from git URL", TerminalEntryType.Output);
            AddHistoryEntry("• Add package by name", TerminalEntryType.Output);
            AddHistoryEntry("• Local package development", TerminalEntryType.Output);
            
            // Try to open Unity Package Manager if Unity is running
            try
            {
                var packageManagerCommand = "echo 'Use Unity Editor: Window > Package Manager'";
                ExecuteCommand(packageManagerCommand);
            }
            catch
            {
                AddHistoryEntry("Open Unity Editor and use Window > Package Manager", TerminalEntryType.System);
            }
        }
    }
}
#endif
