# 🧠 Warbler AI Project Orchestrator

An intelligent Unity project generator that integrates with Ollama AI for smart project structure creation and code generation.

## 🚀 Features

- **Progressive Timeout Handling**: Automatically escalates timeout values (30s → 60s → 120s) for reliable AI communication
- **Functional Fallbacks**: Generates working Unity scripts when AI is unavailable (not empty stubs!)
- **Streaming Support**: Real-time feedback for long-running AI operations
- **Unity Editor Integration**: Complete EditorWindow for seamless workflow
- **Comprehensive Testing**: Built-in connection validation and health checks

## 📦 Components

### 1. Connection Test (`scripts/connection_test.py`)
Validates Ollama connectivity and capability:
```bash
# Quick connectivity test
python3 scripts/connection_test.py --quick

# Comprehensive test with timeout escalation
python3 scripts/connection_test.py --model llama2

# JSON output for automation
python3 scripts/connection_test.py --json
```

### 2. AI Intelligence Engine (`scripts/warbler_project_intelligence.py`)
Main AI-powered project generation:
```bash
# Generate with AI (will fallback if Ollama unavailable)
python3 scripts/warbler_project_intelligence.py "Create a simple 2D platformer game"

# Force fallback mode (skip AI)
python3 scripts/warbler_project_intelligence.py "Create a simple 2D platformer game" --force-fallback

# Export to specific directory
python3 scripts/warbler_project_intelligence.py "Create a 3D adventure game" --output ./my_project

# Custom settings
python3 scripts/warbler_project_intelligence.py "Create a mobile puzzle game" \
    --type unity_2d_game \
    --platform mobile \
    --complexity medium \
    --requirements "Touch controls" "Level editor"
```

### 3. Unity Editor Integration (`Assets/TWG/Scripts/Editor/WarblerIntelligentOrchestrator.cs`)
Complete Unity EditorWindow accessible via:
**TWG → Warbler AI → Intelligent Project Orchestrator**

Features:
- Real-time connection status monitoring
- Project configuration interface
- AI generation with progress tracking
- Export functionality for generated projects
- Settings persistence

## 🛡️ Fallback System

When Ollama is unavailable, the system generates **functional Unity templates** including:

### 2D Platformer Template
- **PlayerController.cs**: Complete movement, jumping, and ground detection
- **GameManager.cs**: Pause/resume, scoring, lives, game over handling
- **PlatformController.cs**: Moving platform behavior with gizmos
- **Project Structure**: Organized folders for Scripts, Prefabs, Sprites, Audio

### Generated Code Example
```csharp
public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    public float moveSpeed = 5f;
    public float jumpForce = 10f;
    
    [Header("Ground Check")]
    public Transform groundCheck;
    public LayerMask groundLayerMask;
    
    private Rigidbody2D rb;
    private bool isGrounded;
    
    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        // Auto-create ground check if not assigned
        if (groundCheck == null)
        {
            groundCheck = new GameObject("GroundCheck").transform;
            groundCheck.parent = transform;
            groundCheck.localPosition = new Vector3(0, -0.5f, 0);
        }
    }
    
    void Update()
    {
        // Ground detection
        isGrounded = Physics2D.OverlapCircle(groundCheck.position, 0.1f, groundLayerMask);
        
        // Movement input
        float moveInput = Input.GetAxis("Horizontal");
        rb.velocity = new Vector2(moveInput * moveSpeed, rb.velocity.y);
        
        // Jump input
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.velocity = new Vector2(rb.velocity.x, jumpForce);
        }
    }
    
    void OnDrawGizmosSelected()
    {
        if (groundCheck != null)
        {
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawWireSphere(groundCheck.position, 0.1f);
        }
    }
}
```

## ⚙️ Setup Requirements

### For AI Features (Optional)
1. **Install Ollama**: [https://ollama.ai](https://ollama.ai)
2. **Pull a model**: `ollama pull llama2`
3. **Start Ollama**: `ollama serve`

### For Fallback Mode (Always Available)
- Python 3.6+ with `requests` library
- Unity 2020.3+ for Editor integration

## 🧪 Testing the System

Run the comprehensive test to verify everything works:
```bash
python3 scripts/test_timeout_behavior.py
```

This demonstrates:
- Original timeout issues vs our solution
- Connection validation
- Functional fallback generation
- Timeout escalation strategies

## 🔧 Configuration

### Ollama Settings
- **Default URL**: `http://localhost:11434`
- **Default Model**: `llama2`
- **Timeout Strategy**: 30s → 60s → 120s with automatic escalation

### Unity Settings
Settings are automatically saved in EditorPrefs:
- `WarblerAI.OllamaUrl`
- `WarblerAI.Model`
- `WarblerAI.LastDescription`
- `WarblerAI.ProjectType`
- `WarblerAI.Platform`
- `WarblerAI.Complexity`

## 🎯 Usage Workflow

1. **Open Unity Editor Window**: TWG → Warbler AI → Intelligent Project Orchestrator
2. **Check Connection**: Test button shows real-time Ollama status
3. **Configure Project**: Enter description, select type/platform/complexity
4. **Generate**: Choose AI generation or fallback template
5. **Export**: Save generated project structure to filesystem

## 🛠️ Troubleshooting

### "AI unavailable" in Unity
- Check if Ollama is running: `ollama serve`
- Test connection: `python3 scripts/connection_test.py --quick`
- Verify model is installed: `ollama list`

### Timeout Issues
- Use fallback mode for immediate results
- Check system resources (RAM/CPU for AI model)
- Try smaller/faster models for development

### Python Dependencies
```bash
pip install requests  # Usually pre-installed
```

## 📚 Advanced Usage

### Custom Templates
Extend the `FunctionalFallbackGenerator` class in `warbler_project_intelligence.py` to add new project templates.

### AI Prompt Customization
Modify the `_create_analysis_prompt()` method to adjust AI behavior for specific project types.

### Unity Integration Extensions
The `WarblerIntelligentOrchestrator` class can be extended with additional Unity-specific features.

## 🔍 Architecture

```
┌─ Unity Editor ─────────────────────┐
│  WarblerIntelligentOrchestrator    │
│  ├─ Connection Monitoring          │
│  ├─ Project Configuration          │
│  └─ Export Management              │
└────────────────┬───────────────────┘
                 │ Python Process
┌────────────────▼───────────────────┐
│  warbler_project_intelligence.py  │
│  ├─ OllamaAIClient                 │
│  │  ├─ Progressive Timeouts        │
│  │  ├─ Streaming Support           │
│  │  └─ Error Handling              │
│  └─ FunctionalFallbackGenerator    │
│     ├─ Unity Templates             │
│     ├─ Working Scripts             │
│     └─ Project Structure           │
└────────────────┬───────────────────┘
                 │ HTTP API
┌────────────────▼───────────────────┐
│  Ollama AI Service (Optional)      │
│  ├─ Local AI Model                 │
│  ├─ Text Generation                │
│  └─ Streaming Responses            │
└────────────────────────────────────┘
```

This system provides robust AI integration with graceful fallbacks, ensuring developers always get functional results regardless of AI availability.