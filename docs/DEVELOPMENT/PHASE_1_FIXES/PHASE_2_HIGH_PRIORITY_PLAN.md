# Phase 2: High-Priority Implementation Plan

**Status**: Ready to begin  
**Estimated Duration**: 2-3 weeks  
**Priority**: 🔴 MUST COMPLETE before production  
**Target**: Customer-facing product readiness  

---

## Overview

After fixing the critical Phase 1 issues, the following Phase 2 improvements are needed to reach production quality. These items improve reliability, security, and operational excellence.

---

## 1. INPUT VALIDATION & SANITIZATION

### Severity: 🔴 CRITICAL (Security Issue)

### Current State:
```csharp
var message = _messageInput.text.Trim();
if (string.IsNullOrEmpty(message)) return;
// No validation - message goes directly to UI!
```

### Security Risks:
- XSS (Cross-Site Scripting) if messages rendered in HTML
- Buffer overflow if messages too large
- No rate limiting (spam/DOS risk)

### Required Implementation:

**File**: `SeedEnhancedTLDAChat.cs`

```csharp
// Add at the top of the class
private const int MAX_MESSAGE_LENGTH = 2048;
private const int MIN_MESSAGE_LENGTH = 1;
private DateTime _lastMessageTime = DateTime.MinValue;
private const float MESSAGE_RATE_LIMIT_SECONDS = 0.5f;

// Add new validation method
private bool ValidateMessage(string message, out string validationError)
{
    validationError = string.Empty;
    
    if (string.IsNullOrWhiteSpace(message))
    {
        validationError = "Message cannot be empty";
        return false;
    }
    
    if (message.Length > MAX_MESSAGE_LENGTH)
    {
        validationError = $"Message too long (max {MAX_MESSAGE_LENGTH} characters)";
        return false;
    }
    
    if (message.Length < MIN_MESSAGE_LENGTH)
    {
        validationError = "Message too short";
        return false;
    }
    
    // Rate limiting
    var timeSinceLastMessage = (DateTime.Now - _lastMessageTime).TotalSeconds;
    if (timeSinceLastMessage < MESSAGE_RATE_LIMIT_SECONDS)
    {
        validationError = "Please wait before sending another message";
        return false;
    }
    
    // Check for malicious patterns
    if (ContainsMaliciousPatterns(message))
    {
        validationError = "Message contains invalid characters";
        return false;
    }
    
    _lastMessageTime = DateTime.Now;
    return true;
}

// Add sanitization method
private string SanitizeMessage(string message)
{
    // Remove potential XSS vectors
    var sanitized = System.Net.WebUtility.HtmlEncode(message);
    
    // Remove control characters except newline and tab
    sanitized = System.Text.RegularExpressions.Regex.Replace(
        sanitized,
        @"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        string.Empty
    );
    
    return sanitized.Trim();
}

// Add pattern checking
private bool ContainsMaliciousPatterns(string message)
{
    // Check for script tags, SQL injection patterns, etc.
    var dangerousPatterns = new[]
    {
        "<script",
        "javascript:",
        "onerror=",
        "onclick=",
        "onload=",
        "--",  // SQL comments
        "'; DROP",  // SQL injection
        "UNION SELECT"
    };
    
    var messageLower = message.ToLower();
    return dangerousPatterns.Any(pattern => messageLower.Contains(pattern));
}

// Update SendMessage() to use validation
async void SendMessage()
{
    var rawMessage = _messageInput.text.Trim();
    
    // Validate
    if (!ValidateMessage(rawMessage, out var error))
    {
        AddSystemMessage($"⚠️ {error}");
        return;
    }
    
    // Sanitize
    var message = SanitizeMessage(rawMessage);
    
    // ... rest of SendMessage logic
}
```

### Effort: Medium (4-6 hours)

---

## 2. COMPREHENSIVE LOGGING SYSTEM

### Severity: 🟡 HIGH (Operations Issue)

### Current State:
- Random Debug.Log calls scattered throughout
- No log levels (DEBUG, INFO, WARN, ERROR)
- No log file output
- Difficult to debug production issues

### Required Implementation:

**Create New File**: `SeedChatLogger.cs`

```csharp
using System;
using UnityEngine;
using System.IO;
using System.Text;

namespace TWG.TLDA.Chat
{
    public class SeedChatLogger
    {
        private static SeedChatLogger _instance;
        public static SeedChatLogger Instance
        {
            get
            {
                if (_instance == null)
                    _instance = new SeedChatLogger();
                return _instance;
            }
        }

        public enum LogLevel
        {
            DEBUG = 0,
            INFO = 1,
            WARN = 2,
            ERROR = 3
        }

        private LogLevel _currentLevel = LogLevel.INFO;
        private string _logFilePath;
        private bool _logToFile = true;

        public SeedChatLogger()
        {
            _logFilePath = Path.Combine(
                Application.persistentDataPath,
                "Logs",
                $"seed-chat-{DateTime.Now:yyyy-MM-dd}.log"
            );
            
            var directory = Path.GetDirectoryName(_logFilePath);
            if (!Directory.Exists(directory))
                Directory.CreateDirectory(directory);
        }

        public void SetLogLevel(LogLevel level) => _currentLevel = level;

        public void Debug(string message) => Log(LogLevel.DEBUG, message);
        public void Info(string message) => Log(LogLevel.INFO, message);
        public void Warn(string message) => Log(LogLevel.WARN, message);
        public void Error(string message) => Log(LogLevel.ERROR, message);

        private void Log(LogLevel level, string message)
        {
            if (level < _currentLevel)
                return;

            var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
            var logEntry = $"[{timestamp}] [{level}] {message}";

            // Console output
            switch (level)
            {
                case LogLevel.DEBUG:
                case LogLevel.INFO:
                    Debug.Log(logEntry);
                    break;
                case LogLevel.WARN:
                    Debug.LogWarning(logEntry);
                    break;
                case LogLevel.ERROR:
                    Debug.LogError(logEntry);
                    break;
            }

            // File output
            if (_logToFile)
            {
                try
                {
                    File.AppendAllText(_logFilePath, logEntry + Environment.NewLine);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to write to log file: {ex.Message}");
                }
            }
        }
    }
}
```

**Update SeedEnhancedTLDAChat.cs**:
```csharp
private SeedChatLogger _logger = SeedChatLogger.Instance;

void InitializeChatUI()
{
    _logger.Info("Initializing chat UI...");
    // ... rest of init
}

async void SendMessage()
{
    _logger.Debug($"SendMessage called with: {_messageInput.text}");
    // ... rest of method
}
```

### Effort: Medium (6-8 hours)

---

## 3. ERROR HANDLING & RETRY LOGIC

### Severity: 🔴 CRITICAL (Reliability Issue)

### Current State:
```csharp
try
{
    await seedBridge.RegisterNewEntity(message, "narrative");
}
catch (Exception ex)
{
    Debug.LogError($"Failed: {ex.Message}");  // Just logs, no retry
}
```

### Required Implementation:

```csharp
// Add at top of class
private const int MAX_RETRY_ATTEMPTS = 3;
private const float INITIAL_RETRY_DELAY = 1.0f;

// Add retry method
private async Task<T> RetryWithExponentialBackoff<T>(
    Func<Task<T>> operation,
    string operationName,
    int maxAttempts = MAX_RETRY_ATTEMPTS)
{
    var retryDelay = INITIAL_RETRY_DELAY;
    
    for (int attempt = 1; attempt <= maxAttempts; attempt++)
    {
        try
        {
            _logger.Debug($"Attempting {operationName} (attempt {attempt}/{maxAttempts})");
            var result = await operation();
            
            if (attempt > 1)
                _logger.Info($"{operationName} succeeded after {attempt} attempts");
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.Warn($"{operationName} failed on attempt {attempt}: {ex.Message}");
            
            if (attempt < maxAttempts)
            {
                _logger.Debug($"Retrying in {retryDelay} seconds...");
                await Task.Delay((int)(retryDelay * 1000));
                retryDelay *= 2;  // Exponential backoff
            }
            else
            {
                _logger.Error($"{operationName} failed after {maxAttempts} attempts");
                throw;
            }
        }
    }
    
    throw new InvalidOperationException($"{operationName} exhausted all retries");
}

// Update SendMessage to use retry logic
if (autoRegisterNarratives && seedBridge != null)
{
    _ = Task.Run(async () =>
    {
        try
        {
            await RetryWithExponentialBackoff(
                async () => await seedBridge.RegisterNewEntity(message, "narrative"),
                "RegisterNewEntity"
            );
            AddSystemMessage("📝 Message registered as narrative entity");
        }
        catch (Exception ex)
        {
            AddSystemMessage($"❌ Failed to register narrative after retries: {ex.Message}");
        }
    });
}
```

### Effort: High (8-12 hours)

---

## 4. CONFIGURATION SYSTEM

### Severity: 🔴 CRITICAL (Production Issue)

### Current State:
```csharp
[SerializeField] private bool autoRegisterNarratives = true;  // Hardcoded in editor
this.websocket = new WebSocket('ws://localhost:8765');  // Hardcoded URL
```

### Required Implementation:

**Create New File**: `SeedChatConfiguration.cs`

```csharp
using UnityEngine;
using System.Collections.Generic;

namespace TWG.TLDA.Chat
{
    [System.Serializable]
    public class SeedChatConfiguration : ScriptableObject
    {
        [Header("Server Configuration")]
        public string websocketUrl = "ws://localhost:8765";
        public string seedEngineApiUrl = "http://localhost:5000";
        public bool useSecureWebSocket = false;

        [Header("Chat Settings")]
        public int maxMessageLength = 2048;
        public float messageRateLimitSeconds = 0.5f;
        public bool autoRegisterNarratives = true;
        public bool enableCrossPlatformSync = true;

        [Header("Features")]
        public bool enableSpatialSearch = true;
        public bool highlightStat7Addresses = true;
        public bool enableNarrativeVisualization = true;

        [Header("Logging")]
        public SeedChatLogger.LogLevel logLevel = SeedChatLogger.LogLevel.INFO;
        public bool logToFile = true;
        public int maxLogFileDays = 7;

        [Header("Retry Configuration")]
        public int maxRetryAttempts = 3;
        public float initialRetryDelaySeconds = 1.0f;

        private static SeedChatConfiguration _instance;
        public static SeedChatConfiguration Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = Resources.Load<SeedChatConfiguration>("SeedChatConfig");
                    if (_instance == null)
                    {
                        Debug.LogError("SeedChatConfiguration not found in Resources!");
                        _instance = CreateInstance<SeedChatConfiguration>();
                    }
                }
                return _instance;
            }
        }

        /// <summary>
        /// Load from environment variables (for Docker/cloud deployment)
        /// </summary>
        public static void LoadFromEnvironment()
        {
            var config = Instance;
            
            if (!string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("SEED_WEBSOCKET_URL")))
                config.websocketUrl = System.Environment.GetEnvironmentVariable("SEED_WEBSOCKET_URL");
            
            if (!string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("SEED_API_URL")))
                config.seedEngineApiUrl = System.Environment.GetEnvironmentVariable("SEED_API_URL");
            
            if (bool.TryParse(System.Environment.GetEnvironmentVariable("SEED_USE_SECURE_WS"), out var useSecure))
                config.useSecureWebSocket = useSecure;
        }
    }
}
```

**Setup Instructions for Your Team**:

1. Create folder: `Assets/Resources/`
2. Create asset: Right-click → Create → Seed Chat Configuration
3. Set values for Development environment
4. For production: Use environment variables

### Effort: Medium (4-6 hours)

---

## 5. UNIT & INTEGRATION TESTS

### Severity: 🟠 HIGH (Quality Issue)

### Current State:
- No tests for SeedEnhancedTLDAChat
- No test coverage for critical paths
- Manual testing only

### Required Implementation:

**Create New File**: `Tests/Editor/SeedChatTests.cs`

```csharp
using NUnit.Framework;
using UnityEngine;
using TWG.TLDA.Chat;
using System.Threading.Tasks;

public class SeedChatTests
{
    private SeedEnhancedTldaChat _chatSystem;

    [SetUp]
    public void Setup()
    {
        // Create mock objects
        var gameObject = new GameObject("TestChat");
        _chatSystem = gameObject.AddComponent<SeedEnhancedTldaChat>();
    }

    [TearDown]
    public void Teardown()
    {
        Object.DestroyImmediate(_chatSystem.gameObject);
    }

    [Test]
    public void MessageValidation_EmptyMessage_ReturnsFalse()
    {
        // Arrange & Act
        var result = _chatSystem.ValidateMessage("", out var error);

        // Assert
        Assert.IsFalse(result);
        Assert.IsNotEmpty(error);
    }

    [Test]
    public void MessageValidation_TooLongMessage_ReturnsFalse()
    {
        // Arrange
        var longMessage = new string('a', 3000);

        // Act
        var result = _chatSystem.ValidateMessage(longMessage, out var error);

        // Assert
        Assert.IsFalse(result);
    }

    [Test]
    public void AddMessage_CreatesValidChatMessage()
    {
        // Arrange
        var sender = "Test";
        var content = "Test message";

        // Act
        _chatSystem.AddMessage(sender, content, SeedEnhancedTldaChat.SeedChatMessageType.User);

        // Assert
        Assert.AreEqual(1, _chatSystem.MessageHistory.Count);
    }

    [Test]
    public async Task SendMessage_WithValidInput_IncrementsMessageHistory()
    {
        // Arrange
        var initialCount = _chatSystem.MessageHistory.Count;

        // Act
        _chatSystem.SendMessage("Test message");
        await Task.Delay(100);

        // Assert
        Assert.Greater(_chatSystem.MessageHistory.Count, initialCount);
    }
}
```

### Effort: High (12-16 hours)

---

## 6. WEBSOCKET SECURITY (WSS)

### Severity: 🟠 HIGH (Security Issue)

### Current State:
```javascript
this.websocket = new WebSocket('ws://localhost:8765');  // Unencrypted!
```

### Required Implementation:

**Update websocket/stat7-websocket.js**:
```javascript
class Stat7WebSocket {
    constructor(config = {}) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = config.host || window.location.host;
        const port = config.port || (window.location.protocol === 'https:' ? 443 : 8765);
        
        this.url = `${protocol}//${host}:${port}`;
        this.websocket = new WebSocket(this.url);
        
        // Add SSL certificate pinning for production
        if (config.certificatePin) {
            this.certificatePin = config.certificatePin;
        }
    }
}
```

### Effort: Medium (4-6 hours)

---

## 7. RACE CONDITION PREVENTION

### Severity: 🟠 HIGH (Stability Issue)

### Current State:
```csharp
_ = Task.Run(async () =>  // Fire and forget - no tracking!
{
    await seedBridge.RegisterNewEntity(message, "narrative");
});
```

### Required Implementation:

```csharp
private List<Task> _pendingOperations = new List<Task>();

private void TrackOperation(Task operation)
{
    lock (_pendingOperations)
    {
        _pendingOperations.Add(operation);
        operation.ContinueWith(t =>
        {
            lock (_pendingOperations)
            {
                _pendingOperations.Remove(t);
            }
        });
    }
}

// In OnDestroy():
void OnDestroy()
{
    lock (_pendingOperations)
    {
        Task.WaitAll(_pendingOperations.ToArray(), 5000);
    }
}

// Updated SendMessage:
if (autoRegisterNarratives && seedBridge != null)
{
    var task = Task.Run(async () =>
    {
        try
        {
            await seedBridge.RegisterNewEntity(message, "narrative");
        }
        catch (Exception ex) { /* handle */ }
    });
    TrackOperation(task);
}
```

### Effort: Low-Medium (2-4 hours)

---

## 8. PLATFORM BRIDGE VERIFICATION

### Severity: 🟠 HIGH (Integration Issue)

### Required Implementation:

Create test harness to verify:

```csharp
public class PlatformBridgeVerification
{
    [Test]
    public async Task IPlatformBridge_AuthenticateUser_ReturnsValidIdentity()
    {
        // Test each platform bridge implementation
        var bridges = new IPlatformBridge[]
        {
            new SteamBridge(),
            // Add other implementations as they're created
        };

        foreach (var bridge in bridges)
        {
            var identity = await bridge.AuthenticateUser();
            Assert.IsNotNull(identity);
            Assert.IsNotEmpty(identity.DisplayName);
        }
    }
}
```

### Effort: Medium (6-8 hours)

---

## 📅 IMPLEMENTATION TIMELINE

### Week 1:
- [ ] Input Validation (Priority #1)
- [ ] Logging System (Priority #2)

### Week 2:
- [ ] Error Handling & Retry Logic (Priority #3)
- [ ] Configuration System (Priority #4)

### Week 3:
- [ ] Unit Tests (Priority #5)
- [ ] WebSocket Security (Priority #6)
- [ ] Race Condition Prevention (Priority #7)

### Buffer:
- [ ] Platform Bridge Verification (Priority #8)
- [ ] Code review and fixes

---

## 🎯 DEFINITION OF DONE FOR PHASE 2

- [ ] All 8 items implemented
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Code review approved by team
- [ ] Security audit passed
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Zero critical bugs identified

---

## 📝 CHECKLIST FOR YOUR TEAM

### Before Starting Phase 2:
- [ ] All Phase 1 fixes reviewed and approved
- [ ] Repository compiled successfully
- [ ] Manual testing of Phase 1 features passed
- [ ] Team trained on new code structure

### During Phase 2:
- [ ] Daily standup on blockers
- [ ] Weekly code review meetings
- [ ] Continuous integration tests passing
- [ ] Security review at end of week 2

### After Phase 2:
- [ ] Full regression testing
- [ ] Load testing for concurrent users
- [ ] Security penetration testing
- [ ] Production readiness sign-off

---

**Ready to begin Phase 2? Contact your team lead with this plan and assign ownership for each priority item.**