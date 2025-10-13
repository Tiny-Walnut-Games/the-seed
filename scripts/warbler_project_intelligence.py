#!/usr/bin/env python3
"""
🧠 Warbler AI Project Intelligence Engine
Sacred Mission: AI-powered Unity project analysis and generation using Ollama

Provides intelligent project structure analysis, code generation, and development guidance
through proper Ollama API integration with robust timeout handling and functional fallbacks.

Author: Bootstrap Sentinel & Living Dev Agent
Chronicle: Core component of the Warbler AI Project Orchestrator
"""

import os
import sys
import json
import time
import argparse
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ProjectAnalysisRequest:
    """Request for AI project analysis"""
    project_description: str
    project_type: str = "unity_2d_game"
    target_platform: str = "pc"
    complexity_level: str = "simple"
    additional_requirements: List[str] = None
    
    def __post_init__(self):
        if self.additional_requirements is None:
            self.additional_requirements = []


@dataclass
class ProjectStructureItem:
    """Individual project structure item"""
    path: str
    type: str  # 'file' or 'directory'
    content: str = ""
    description: str = ""
    is_generated: bool = True


@dataclass
class ProjectAnalysisResult:
    """Result of AI project analysis"""
    success: bool
    project_name: str
    description: str
    structure: List[ProjectStructureItem]
    scripts: List[Dict[str, str]]
    assets_needed: List[Dict[str, str]]
    setup_instructions: List[str]
    development_notes: List[str]
    generation_time: float
    ai_generated: bool = True
    fallback_used: bool = False
    error_message: str = ""


class OllamaAIClient:
    """🤖 Ollama API client with intelligent timeout handling"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        
        # Progressive timeout strategy: start conservative, escalate as needed
        self.timeouts = [30, 60, 120]  # 30s, 1min, 2min
        self.current_timeout_index = 0
        
    def _get_current_timeout(self) -> int:
        """Get current timeout value"""
        return self.timeouts[min(self.current_timeout_index, len(self.timeouts) - 1)]
    
    def _escalate_timeout(self) -> bool:
        """Escalate to next timeout level if available"""
        if self.current_timeout_index < len(self.timeouts) - 1:
            self.current_timeout_index += 1
            return True
        return False
    
    def test_connectivity(self) -> Tuple[bool, str]:
        """Test if Ollama is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=(5, 10))
            if response.status_code == 200:
                return True, "Connected"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=(5, 15))
            if response.status_code == 200:
                data = response.json()
                return [model.get('name', '') for model in data.get('models', [])]
        except:
            pass
        return []
    
    def generate_text(self, prompt: str, max_retries: int = 3) -> Tuple[bool, str, Dict]:
        """Generate text with progressive timeout handling"""
        
        for attempt in range(max_retries):
            timeout = self._get_current_timeout()
            
            print(f"🤖 AI Generation attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)")
            
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Slightly creative but focused
                        "top_p": 0.9,
                        "max_tokens": 2000  # Reasonable limit for project analysis
                    }
                }
                
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=(10, timeout)
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    generated_text = data.get('response', '').strip()
                    
                    return True, generated_text, {
                        'elapsed_time': elapsed,
                        'timeout_used': timeout,
                        'attempt': attempt + 1,
                        'model': self.model
                    }
                else:
                    print(f"❌ HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.Timeout:
                elapsed = time.time() - start_time
                print(f"⏰ Timeout after {elapsed:.1f}s on attempt {attempt + 1}")
                
                # Try escalating timeout for next attempt
                if attempt < max_retries - 1 and self._escalate_timeout():
                    print(f"🔄 Escalating timeout to {self._get_current_timeout()}s")
                    continue
                    
            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
        
        return False, "", {'error': 'All attempts failed'}
    
    def generate_streaming(self, prompt: str, timeout: int = 60) -> Tuple[bool, str, Dict]:
        """Generate text with streaming for real-time feedback"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=(10, timeout)
            )
            
            if response.status_code == 200:
                full_text = ""
                chunk_count = 0
                
                print("🔄 Streaming response...")
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line)
                            chunk_text = chunk_data.get('response', '')
                            full_text += chunk_text
                            chunk_count += 1
                            
                            # Show progress every 10 chunks
                            if chunk_count % 10 == 0:
                                print(f"📝 Received {chunk_count} chunks...")
                                
                            # Check if done
                            if chunk_data.get('done', False):
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                elapsed = time.time() - start_time
                
                return True, full_text.strip(), {
                    'elapsed_time': elapsed,
                    'chunk_count': chunk_count,
                    'streaming': True,
                    'model': self.model
                }
            else:
                return False, "", {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            elapsed = time.time() - start_time
            return False, "", {'error': str(e), 'elapsed_time': elapsed}


class FunctionalFallbackGenerator:
    """🛡️ Generate functional project templates when AI is unavailable"""
    
    def __init__(self):
        self.templates = {
            'unity_2d_platformer': self._unity_2d_platformer_template,
            'unity_2d_game': self._unity_2d_game_template,
            'unity_3d_game': self._unity_3d_game_template,
            'generic': self._generic_unity_template
        }
    
    def generate_fallback_project(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Generate functional fallback project structure"""
        print("🛡️ Generating functional fallback project structure...")
        
        # Determine appropriate template
        template_key = self._determine_template(request.project_description, request.project_type)
        template_func = self.templates.get(template_key, self.templates['generic'])
        
        start_time = time.time()
        result = template_func(request)
        generation_time = time.time() - start_time
        
        result.generation_time = generation_time
        result.ai_generated = False
        result.fallback_used = True
        
        print(f"✅ Generated functional fallback in {generation_time:.2f}s")
        return result
    
    def _determine_template(self, description: str, project_type: str) -> str:
        """Determine best template based on description"""
        description_lower = description.lower()
        
        if 'platformer' in description_lower:
            return 'unity_2d_platformer'
        elif '2d' in description_lower or project_type == 'unity_2d_game':
            return 'unity_2d_game'
        elif '3d' in description_lower or project_type == 'unity_3d_game':
            return 'unity_3d_game'
        else:
            return 'generic'
    
    def _unity_2d_platformer_template(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Generate a functional 2D platformer template"""
        project_name = "Simple2DPlatformer"
        
        structure = [
            ProjectStructureItem("Assets/Scripts", "directory", "", "Main scripts directory"),
            ProjectStructureItem("Assets/Scripts/Player", "directory", "", "Player-related scripts"),
            ProjectStructureItem("Assets/Scripts/Enemies", "directory", "", "Enemy scripts"),
            ProjectStructureItem("Assets/Scripts/Environment", "directory", "", "Environment interaction scripts"),
            ProjectStructureItem("Assets/Scripts/Managers", "directory", "", "Game management scripts"),
            ProjectStructureItem("Assets/Prefabs", "directory", "", "Prefab assets"),
            ProjectStructureItem("Assets/Sprites", "directory", "", "2D sprite assets"),
            ProjectStructureItem("Assets/Audio", "directory", "", "Audio files"),
            ProjectStructureItem("Assets/Scenes", "directory", "", "Unity scenes"),
            ProjectStructureItem("Assets/Materials", "directory", "", "2D materials"),
        ]
        
        scripts = [
            {
                "name": "PlayerController.cs",
                "path": "Assets/Scripts/Player/PlayerController.cs",
                "description": "Main player movement and input handling",
                "content": self._get_player_controller_script()
            },
            {
                "name": "GameManager.cs", 
                "path": "Assets/Scripts/Managers/GameManager.cs",
                "description": "Core game state management",
                "content": self._get_game_manager_script()
            },
            {
                "name": "PlatformController.cs",
                "path": "Assets/Scripts/Environment/PlatformController.cs", 
                "description": "Moving platform behavior",
                "content": self._get_platform_controller_script()
            }
        ]
        
        assets_needed = [
            {"type": "sprite", "name": "Player Character", "description": "Simple character sprite"},
            {"type": "sprite", "name": "Ground Tiles", "description": "Tileable ground sprites"},
            {"type": "sprite", "name": "Platform", "description": "Moving platform sprite"},
            {"type": "audio", "name": "Jump Sound", "description": "Player jump sound effect"},
            {"type": "audio", "name": "Background Music", "description": "Simple background loop"}
        ]
        
        setup_instructions = [
            "1. Create a new Unity 2D project",
            "2. Import the provided scripts into the Scripts folder structure",
            "3. Create basic sprites or use Unity's built-in sprites for prototyping",
            "4. Set up a simple scene with ground platforms",
            "5. Create player GameObject and attach PlayerController script",
            "6. Set up Physics2D layers for player and platforms",
            "7. Test player movement and jumping mechanics"
        ]
        
        development_notes = [
            "This is a functional starter template for a 2D platformer",
            "Scripts include basic movement, jumping, and collision detection",
            "Uses Unity's Physics2D system for realistic movement",
            "Easy to extend with enemies, collectibles, and more levels",
            "Includes proper separation of concerns with manager classes"
        ]
        
        return ProjectAnalysisResult(
            success=True,
            project_name=project_name,
            description=f"Functional 2D platformer template based on: {request.project_description}",
            structure=structure,
            scripts=scripts,
            assets_needed=assets_needed,
            setup_instructions=setup_instructions,
            development_notes=development_notes,
            generation_time=0,  # Will be set by caller
            ai_generated=False,
            fallback_used=True
        )
    
    def _unity_2d_game_template(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Generate a general 2D game template"""
        project_name = "Simple2DGame"
        
        structure = [
            ProjectStructureItem("Assets/Scripts", "directory", "", "Main scripts directory"),
            ProjectStructureItem("Assets/Scripts/Core", "directory", "", "Core game systems"),
            ProjectStructureItem("Assets/Scripts/UI", "directory", "", "User interface scripts"),
            ProjectStructureItem("Assets/Prefabs", "directory", "", "Prefab assets"),
            ProjectStructureItem("Assets/Sprites", "directory", "", "2D sprite assets"),
            ProjectStructureItem("Assets/Audio", "directory", "", "Audio files"),
            ProjectStructureItem("Assets/Scenes", "directory", "", "Unity scenes"),
        ]
        
        scripts = [
            {
                "name": "GameManager.cs",
                "path": "Assets/Scripts/Core/GameManager.cs",
                "description": "Core game management",
                "content": self._get_simple_game_manager_script()
            },
            {
                "name": "UIManager.cs",
                "path": "Assets/Scripts/UI/UIManager.cs", 
                "description": "UI state management",
                "content": self._get_ui_manager_script()
            }
        ]
        
        return ProjectAnalysisResult(
            success=True,
            project_name=project_name,
            description=f"General 2D game template for: {request.project_description}",
            structure=structure,
            scripts=scripts,
            assets_needed=[],
            setup_instructions=["Create Unity 2D project", "Import scripts", "Set up basic scene"],
            development_notes=["Expandable template for various 2D game types"],
            generation_time=0,
            ai_generated=False,
            fallback_used=True
        )
    
    def _unity_3d_game_template(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Generate a general 3D game template"""
        project_name = "Simple3DGame"
        
        structure = [
            ProjectStructureItem("Assets/Scripts", "directory", "", "Main scripts directory"),
            ProjectStructureItem("Assets/Models", "directory", "", "3D model assets"),
            ProjectStructureItem("Assets/Materials", "directory", "", "3D materials"),
            ProjectStructureItem("Assets/Textures", "directory", "", "Texture assets"),
            ProjectStructureItem("Assets/Prefabs", "directory", "", "Prefab assets"),
            ProjectStructureItem("Assets/Scenes", "directory", "", "Unity scenes"),
        ]
        
        return ProjectAnalysisResult(
            success=True,
            project_name=project_name,
            description=f"3D game template for: {request.project_description}",
            structure=structure,
            scripts=[],
            assets_needed=[],
            setup_instructions=["Create Unity 3D project", "Set up basic 3D scene"],
            development_notes=["Basic 3D game structure"],
            generation_time=0,
            ai_generated=False,
            fallback_used=True
        )
    
    def _generic_unity_template(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Generate a generic Unity project template"""
        project_name = "UnityProjectTemplate"
        
        structure = [
            ProjectStructureItem("Assets/Scripts", "directory", "", "Scripts directory"),
            ProjectStructureItem("Assets/Prefabs", "directory", "", "Prefabs directory"), 
            ProjectStructureItem("Assets/Scenes", "directory", "", "Scenes directory"),
        ]
        
        return ProjectAnalysisResult(
            success=True,
            project_name=project_name,
            description=f"Generic Unity template for: {request.project_description}",
            structure=structure,
            scripts=[],
            assets_needed=[],
            setup_instructions=["Create Unity project", "Set up basic structure"],
            development_notes=["Basic Unity project structure"],
            generation_time=0,
            ai_generated=False,
            fallback_used=True
        )
    
    def _get_player_controller_script(self) -> str:
        """Generate functional PlayerController script"""
        return '''using UnityEngine;

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
    private float groundCheckRadius = 0.1f;
    
    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        
        // Create ground check if not assigned
        if (groundCheck == null)
        {
            groundCheck = new GameObject("GroundCheck").transform;
            groundCheck.parent = transform;
            groundCheck.localPosition = new Vector3(0, -0.5f, 0);
        }
    }
    
    void Update()
    {
        // Ground check
        isGrounded = Physics2D.OverlapCircle(groundCheck.position, groundCheckRadius, groundLayerMask);
        
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
            Gizmos.DrawWireSphere(groundCheck.position, groundCheckRadius);
        }
    }
}'''
    
    def _get_game_manager_script(self) -> str:
        """Generate functional GameManager script"""
        return '''using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    [Header("Game Settings")]
    public int lives = 3;
    public int score = 0;
    
    [Header("UI References")]
    public GameObject gameOverUI;
    public GameObject pauseUI;
    
    private bool isPaused = false;
    private bool isGameOver = false;
    
    void Awake()
    {
        // Singleton pattern
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Update()
    {
        // Pause input
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            if (isPaused)
                ResumeGame();
            else
                PauseGame();
        }
    }
    
    public void AddScore(int points)
    {
        score += points;
        Debug.Log($"Score: {score}");
    }
    
    public void LoseLife()
    {
        lives--;
        Debug.Log($"Lives remaining: {lives}");
        
        if (lives <= 0)
        {
            GameOver();
        }
    }
    
    public void PauseGame()
    {
        isPaused = true;
        Time.timeScale = 0f;
        if (pauseUI != null) pauseUI.SetActive(true);
    }
    
    public void ResumeGame()
    {
        isPaused = false;
        Time.timeScale = 1f;
        if (pauseUI != null) pauseUI.SetActive(false);
    }
    
    public void GameOver()
    {
        isGameOver = true;
        Time.timeScale = 0f;
        if (gameOverUI != null) gameOverUI.SetActive(true);
        Debug.Log("Game Over!");
    }
    
    public void RestartGame()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
}'''
    
    def _get_platform_controller_script(self) -> str:
        """Generate functional platform controller script"""
        return '''using UnityEngine;

public class PlatformController : MonoBehaviour
{
    [Header("Movement")]
    public Vector3 pointA;
    public Vector3 pointB;
    public float moveSpeed = 2f;
    
    [Header("Settings")]
    public bool startAtPointA = true;
    public bool useLocalSpace = true;
    
    private Vector3 targetPosition;
    private Vector3 startPosition;
    
    void Start()
    {
        startPosition = transform.position;
        
        if (useLocalSpace)
        {
            pointA = startPosition + pointA;
            pointB = startPosition + pointB;
        }
        
        targetPosition = startAtPointA ? pointB : pointA;
    }
    
    void Update()
    {
        // Move towards target
        transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);
        
        // Switch target when reached
        if (Vector3.Distance(transform.position, targetPosition) < 0.1f)
        {
            targetPosition = (targetPosition == pointA) ? pointB : pointA;
        }
    }
    
    void OnDrawGizmos()
    {
        Vector3 posA = useLocalSpace ? transform.position + pointA : pointA;
        Vector3 posB = useLocalSpace ? transform.position + pointB : pointB;
        
        Gizmos.color = Color.blue;
        Gizmos.DrawWireSphere(posA, 0.3f);
        Gizmos.DrawWireSphere(posB, 0.3f);
        Gizmos.DrawLine(posA, posB);
    }
}'''
    
    def _get_simple_game_manager_script(self) -> str:
        """Simple game manager for general templates"""
        return '''using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Start()
    {
        Debug.Log("Game Started!");
    }
}'''
    
    def _get_ui_manager_script(self) -> str:
        """Simple UI manager script"""
        return '''using UnityEngine;

public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public void ShowMessage(string message)
    {
        Debug.Log($"UI Message: {message}");
    }
}'''


class WarblerProjectIntelligence:
    """🧠 Main AI project intelligence orchestrator"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        self.ai_client = OllamaAIClient(ollama_url, model)
        self.fallback_generator = FunctionalFallbackGenerator()
        
    def analyze_project_request(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Main entry point for project analysis"""
        print(f"🎯 Analyzing project request: {request.project_description}")
        
        # Check AI availability first
        connected, status = self.ai_client.test_connectivity()
        if not connected:
            print(f"⚠️ AI unavailable ({status}), using functional fallback")
            return self.fallback_generator.generate_fallback_project(request)
        
        # Try AI generation first
        print("🤖 Attempting AI-powered analysis...")
        try:
            ai_result = self._generate_ai_analysis(request)
            if ai_result.success:
                return ai_result
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
        
        # Fall back to functional templates
        print("🛡️ Falling back to functional templates...")
        return self.fallback_generator.generate_fallback_project(request)
    
    def _generate_ai_analysis(self, request: ProjectAnalysisRequest) -> ProjectAnalysisResult:
        """Generate project analysis using AI"""
        prompt = self._create_analysis_prompt(request)
        
        # Try streaming first for better UX
        success, response_text, metadata = self.ai_client.generate_streaming(prompt, timeout=90)
        
        if not success:
            # Fall back to non-streaming
            print("🔄 Streaming failed, trying standard generation...")
            success, response_text, metadata = self.ai_client.generate_text(prompt)
        
        if not success:
            return ProjectAnalysisResult(
                success=False,
                project_name="",
                description="",
                structure=[],
                scripts=[],
                assets_needed=[],
                setup_instructions=[],
                development_notes=[],
                generation_time=metadata.get('elapsed_time', 0),
                error_message="AI generation failed after all attempts"
            )
        
        # Parse AI response into structured result
        try:
            return self._parse_ai_response(response_text, request, metadata)
        except Exception as e:
            print(f"❌ Failed to parse AI response: {e}")
            return ProjectAnalysisResult(
                success=False,
                project_name="",
                description="",
                structure=[],
                scripts=[],
                assets_needed=[], 
                setup_instructions=[],
                development_notes=[],
                generation_time=metadata.get('elapsed_time', 0),
                error_message=f"AI response parsing failed: {e}"
            )
    
    def _create_analysis_prompt(self, request: ProjectAnalysisRequest) -> str:
        """Create AI prompt for project analysis"""
        return f"""You are an expert Unity game developer creating a project structure for: "{request.project_description}"

Project Type: {request.project_type}
Target Platform: {request.target_platform}
Complexity: {request.complexity_level}
Additional Requirements: {', '.join(request.additional_requirements) if request.additional_requirements else 'None'}

Create a detailed Unity project structure with the following format:

PROJECT_NAME: [Clear, descriptive name]

DESCRIPTION: [Brief project overview]

DIRECTORY_STRUCTURE:
- Assets/Scripts/ (Main scripts directory)
- Assets/Scripts/Player/ (Player-related scripts)
- [Continue with logical directory structure]

KEY_SCRIPTS:
1. Script Name: [ScriptName.cs]
   Path: Assets/Scripts/[ScriptName.cs]
   Purpose: [Clear description of script purpose]

ASSETS_NEEDED:
- Sprite: [Asset description]
- Audio: [Asset description]
- [Continue with needed assets]

SETUP_STEPS:
1. [Clear setup instruction]
2. [Continue with setup steps]

DEVELOPMENT_NOTES:
- [Important development guidance]
- [Technical considerations]

Keep the response practical and implementable. Focus on core functionality."""
    
    def _parse_ai_response(self, response_text: str, request: ProjectAnalysisRequest, metadata: Dict) -> ProjectAnalysisResult:
        """Parse AI response into structured result"""
        lines = response_text.split('\n')
        
        # Initialize result data
        project_name = "AIGeneratedProject"
        description = ""
        structure = []
        scripts = []
        assets_needed = []
        setup_instructions = []
        development_notes = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if line.startswith('PROJECT_NAME:'):
                project_name = line.replace('PROJECT_NAME:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                description = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('DIRECTORY_STRUCTURE:'):
                current_section = 'structure'
            elif line.startswith('KEY_SCRIPTS:'):
                current_section = 'scripts'
            elif line.startswith('ASSETS_NEEDED:'):
                current_section = 'assets'
            elif line.startswith('SETUP_STEPS:'):
                current_section = 'setup'
            elif line.startswith('DEVELOPMENT_NOTES:'):
                current_section = 'notes'
            else:
                # Process content based on current section
                if current_section == 'structure' and line.startswith('-'):
                    # Parse directory structure
                    path = line.replace('-', '').strip()
                    if '(' in path:
                        path_part = path.split('(')[0].strip()
                        desc_part = path.split('(')[1].replace(')', '').strip()
                    else:
                        path_part = path
                        desc_part = ""
                    
                    structure.append(ProjectStructureItem(
                        path=path_part,
                        type="directory" if path_part.endswith('/') else "file",
                        description=desc_part
                    ))
                
                elif current_section == 'scripts' and any(x in line.lower() for x in ['script name:', 'path:', 'purpose:']):
                    # Basic script parsing (simplified)
                    if 'script name:' in line.lower():
                        script_name = line.split(':')[1].strip()
                        scripts.append({
                            'name': script_name,
                            'path': f"Assets/Scripts/{script_name}",
                            'description': "AI-generated script",
                            'content': "// AI-generated script placeholder"
                        })
                
                elif current_section == 'assets' and line.startswith('-'):
                    asset_desc = line.replace('-', '').strip()
                    if ':' in asset_desc:
                        asset_type = asset_desc.split(':')[0].strip()
                        asset_name = asset_desc.split(':')[1].strip()
                    else:
                        asset_type = "unknown"
                        asset_name = asset_desc
                    
                    assets_needed.append({
                        'type': asset_type.lower(),
                        'name': asset_name,
                        'description': asset_desc
                    })
                
                elif current_section == 'setup' and (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-'))):
                    instruction = line.lstrip('0123456789.- ').strip()
                    setup_instructions.append(instruction)
                
                elif current_section == 'notes' and line.startswith('-'):
                    note = line.replace('-', '').strip()
                    development_notes.append(note)
        
        return ProjectAnalysisResult(
            success=True,
            project_name=project_name,
            description=description or f"AI-generated project for: {request.project_description}",
            structure=structure,
            scripts=scripts,
            assets_needed=assets_needed,
            setup_instructions=setup_instructions,
            development_notes=development_notes,
            generation_time=metadata.get('elapsed_time', 0),
            ai_generated=True,
            fallback_used=False
        )


def export_project_analysis(result: ProjectAnalysisResult, output_dir: str) -> str:
    """Export project analysis to files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Export main analysis as JSON
    analysis_file = output_path / "project_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    # Export README with setup instructions
    readme_file = output_path / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f"# {result.project_name}\n\n")
        f.write(f"{result.description}\n\n")
        
        if result.ai_generated:
            f.write("*Generated using AI-powered Warbler Project Intelligence*\n\n")
        else:
            f.write("*Generated using functional fallback templates*\n\n")
        
        f.write("## Project Structure\n\n")
        for item in result.structure:
            f.write(f"- `{item.path}` - {item.description}\n")
        
        f.write("\n## Setup Instructions\n\n")
        for i, instruction in enumerate(result.setup_instructions, 1):
            f.write(f"{i}. {instruction}\n")
        
        f.write("\n## Development Notes\n\n")
        for note in result.development_notes:
            f.write(f"- {note}\n")
    
    # Export individual scripts
    if result.scripts:
        scripts_dir = output_path / "Scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script in result.scripts:
            script_file = scripts_dir / script['name']
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script.get('content', f"// {script['description']}"))
    
    return str(output_path)


def main():
    """CLI interface for Warbler Project Intelligence"""
    parser = argparse.ArgumentParser(description="🧠 Warbler AI Project Intelligence Engine")
    parser.add_argument('description', help='Project description (e.g., "Create a simple 2D platformer game")')
    parser.add_argument('--type', default='unity_2d_game', 
                        choices=['unity_2d_game', 'unity_3d_game', 'unity_2d_platformer'],
                        help='Project type (default: unity_2d_game)')
    parser.add_argument('--platform', default='pc',
                        choices=['pc', 'mobile', 'web', 'console'],
                        help='Target platform (default: pc)')
    parser.add_argument('--complexity', default='simple',
                        choices=['simple', 'medium', 'complex'],
                        help='Complexity level (default: simple)')
    parser.add_argument('--requirements', nargs='*', default=[],
                        help='Additional requirements')
    parser.add_argument('--output', '-o', 
                        help='Output directory for generated files (default: temp directory)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                        help='Ollama API URL (default: http://localhost:11434)')
    parser.add_argument('--model', default='llama2',
                        help='Ollama model to use (default: llama2)')
    parser.add_argument('--force-fallback', action='store_true',
                        help='Force use of fallback templates (skip AI)')
    parser.add_argument('--json', action='store_true',
                        help='Output result as JSON only')
    
    args = parser.parse_args()
    
    # Create request
    request = ProjectAnalysisRequest(
        project_description=args.description,
        project_type=args.type,
        target_platform=args.platform,
        complexity_level=args.complexity,
        additional_requirements=args.requirements
    )
    
    # Initialize intelligence engine
    intelligence = WarblerProjectIntelligence(args.ollama_url, args.model)
    
    if args.force_fallback:
        print("🛡️ Forcing fallback mode (skipping AI)")
        result = intelligence.fallback_generator.generate_fallback_project(request)
    else:
        # Normal analysis
        result = intelligence.analyze_project_request(request)
    
    if args.json:
        # JSON output only
        print(json.dumps(asdict(result), indent=2))
        return
    
    # Display results
    print("\n" + "=" * 60)
    print("🎯 PROJECT ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"📝 Project: {result.project_name}")
    print(f"📖 Description: {result.description}")
    print(f"⏱️ Generation time: {result.generation_time:.2f}s")
    print(f"🤖 AI generated: {'Yes' if result.ai_generated else 'No (Fallback)'}")
    
    if result.success:
        print(f"📁 Structure items: {len(result.structure)}")
        print(f"📜 Scripts: {len(result.scripts)}")
        print(f"🎨 Assets needed: {len(result.assets_needed)}")
        print(f"⚙️ Setup steps: {len(result.setup_instructions)}")
        
        # Export files if requested
        if args.output:
            output_dir = export_project_analysis(result, args.output)
            print(f"💾 Files exported to: {output_dir}")
        else:
            # Create temp directory and export
            with tempfile.TemporaryDirectory(prefix="warbler_project_") as temp_dir:
                output_dir = export_project_analysis(result, temp_dir)
                print(f"💾 Files created in: {output_dir}")
                print("📋 Summary files:")
                for file_path in Path(output_dir).rglob("*"):
                    if file_path.is_file():
                        print(f"   - {file_path.name}")
        
        print("\n✅ Project analysis completed successfully!")
    else:
        print(f"\n❌ Analysis failed: {result.error_message}")
        sys.exit(1)


if __name__ == '__main__':
    main()