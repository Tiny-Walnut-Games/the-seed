#!/usr/bin/env python3
"""
Direct Ollama Binary Manager - No Docker Required
Simplified integration for Warbler AI without Docker dependency
"""

import os
import sys
import platform
import subprocess
import urllib.request
import json
import time
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Dict, List
import threading
import signal


class OllamaManager:
    """Direct Ollama binary management without Docker dependency"""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.platform = self._detect_platform()
        self.data_dir = Path(data_dir or self._get_default_data_dir())
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.ollama_path = self._find_or_download_ollama()
        self.process = None
        self.port = 11434
        self.host = "127.0.0.1"
        self.models_dir = self.data_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Process management
        self._shutdown_handlers_registered = False
        self._register_shutdown_handlers()
    
    def _detect_platform(self) -> str:
        """Detect current platform for binary selection"""
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "darwin"  # macOS
        elif system == "linux":
            if arch in ["x86_64", "amd64"]:
                return "linux"
            elif arch in ["aarch64", "arm64"]:
                return "linux-arm64"
            else:
                return "linux"
        else:
            return "linux"  # Default fallback
    
    def _get_default_data_dir(self) -> str:
        """Get default directory for Ollama data"""
        if self.platform == "windows":
            return os.path.expandvars(r"%APPDATA%\TWG-TLDA\ollama")
        else:
            return os.path.expanduser("~/.twg-tlda/ollama")
    
    def _get_ollama_download_info(self) -> Dict[str, str]:
        """Get download URLs and filenames for current platform"""
        # Use the correct Ollama release URLs
        base_url = "https://github.com/ollama/ollama/releases/latest/download"
        
        downloads = {
            "windows": {
                "url": f"{base_url}/ollama-windows-amd64.zip",
                "filename": "ollama-windows-amd64.zip",
                "executable": "ollama.exe"
            },
            "darwin": {
                "url": f"{base_url}/ollama-darwin",
                "filename": "ollama",
                "executable": "ollama"
            },
            "linux": {
                "url": f"{base_url}/ollama-linux-amd64",
                "filename": "ollama",
                "executable": "ollama"
            },
            "linux-arm64": {
                "url": f"{base_url}/ollama-linux-arm64",
                "filename": "ollama",
                "executable": "ollama"
            }
        }
        
        return downloads.get(self.platform, downloads["linux"])
    
    def _find_or_download_ollama(self) -> Optional[Path]:
        """Find existing Ollama binary or download it"""
        # First, check if Ollama is already installed system-wide
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Found system-wide Ollama installation")
                return Path("ollama")  # Use system installation
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Check for local binary
        download_info = self._get_ollama_download_info()
        local_binary = self.data_dir / download_info["executable"]
        
        if local_binary.exists() and os.access(local_binary, os.X_OK):
            print(f"✅ Found local Ollama binary: {local_binary}")
            return local_binary
        
        # Attempt to download binary
        print(f"📥 Downloading Ollama for {self.platform}...")
        try:
            return self._download_ollama()
        except Exception as e:
            print(f"⚠️ Failed to download Ollama: {e}")
            print("💡 Ollama will be unavailable, but enhanced stubs will provide fallback functionality")
            return None
    
    def _download_ollama(self) -> Path:
        """Download and extract Ollama binary"""
        download_info = self._get_ollama_download_info()
        url = download_info["url"]
        filename = download_info["filename"]
        executable = download_info["executable"]
        
        download_path = self.data_dir / filename
        binary_path = self.data_dir / executable
        
        try:
            print(f"🌐 Downloading from {url}")
            urllib.request.urlretrieve(url, download_path)
            print(f"✅ Downloaded to {download_path}")
            
            # Extract if needed
            if filename.endswith('.zip'):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                download_path.unlink()  # Remove zip file
            elif filename.endswith('.tar.gz'):
                with tarfile.open(download_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.data_dir)
                download_path.unlink()  # Remove tar file
            else:
                # Direct binary download
                if download_path != binary_path:
                    download_path.rename(binary_path)
            
            # Make executable
            binary_path.chmod(0o755)
            print(f"✅ Ollama binary ready: {binary_path}")
            return binary_path
            
        except Exception as e:
            print(f"❌ Failed to download Ollama: {e}")
            raise
    
    def _register_shutdown_handlers(self):
        """Register handlers to clean up Ollama process on shutdown"""
        if self._shutdown_handlers_registered:
            return
            
        def cleanup_handler(signum, frame):
            self.stop()
            
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
        
        # Register atexit for Python shutdown
        import atexit
        atexit.register(self.stop)
        
        self._shutdown_handlers_registered = True
    
    def start(self, model: Optional[str] = None) -> bool:
        """Start Ollama server process"""
        if not self.ollama_path:
            print("❌ Ollama binary not available - cannot start server")
            return False
            
        if self.is_running():
            print("✅ Ollama is already running")
            return True
        
        try:
            print(f"🚀 Starting Ollama server on {self.host}:{self.port}")
            
            # Set environment variables
            env = os.environ.copy()
            env['OLLAMA_HOST'] = f"{self.host}:{self.port}"
            env['OLLAMA_MODELS'] = str(self.models_dir)
            
            # Start Ollama server
            self.process = subprocess.Popen(
                [str(self.ollama_path), "serve"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            max_retries = 30  # 30 seconds
            for i in range(max_retries):
                if self.is_running():
                    print(f"✅ Ollama server started (took {i+1}s)")
                    
                    # Auto-download model if specified
                    if model:
                        self.ensure_model(model)
                    
                    return True
                time.sleep(1)
            
            print("❌ Ollama server failed to start within 30 seconds")
            self.stop()
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False
    
    def stop(self):
        """Stop Ollama server process"""
        if self.process:
            try:
                print("🛑 Stopping Ollama server...")
                self.process.terminate()
                
                # Give it 5 seconds to shut down gracefully
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("⚡ Force stopping Ollama...")
                    self.process.kill()
                    self.process.wait()
                
                print("✅ Ollama stopped")
            except Exception as e:
                print(f"⚠️ Error stopping Ollama: {e}")
            finally:
                self.process = None
    
    def is_running(self) -> bool:
        """Check if Ollama server is running and responding"""
        try:
            import urllib.request
            import urllib.error
            
            url = f"http://{self.host}:{self.port}/api/tags"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
                
        except (urllib.error.URLError, ConnectionError, OSError):
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        if not self.is_running():
            return []
        
        try:
            import urllib.request
            import json
            
            url = f"http://{self.host}:{self.port}/api/tags"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            return []
    
    def ensure_model(self, model_name: str, timeout: int = 300) -> bool:
        """Download model if not available"""
        if not self.is_running():
            print("❌ Ollama server not running")
            return False
        
        # Check if model already exists
        models = self.list_models()
        if model_name in models:
            print(f"✅ Model {model_name} already available")
            return True
        
        print(f"📥 Downloading model {model_name}...")
        try:
            # Use ollama pull command
            result = subprocess.run(
                [str(self.ollama_path), "pull", model_name],
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Model {model_name} downloaded successfully")
                return True
            else:
                print(f"❌ Failed to download model: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Model download timed out after {timeout} seconds")
            return False
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
    
    def generate(self, model: str, prompt: str, stream: bool = False, **kwargs) -> Dict:
        """Generate response using Ollama API"""
        if not self.is_running():
            return {"error": "Ollama server not running"}
        
        try:
            import urllib.request
            import json
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                **kwargs
            }
            
            url = f"http://{self.host}:{self.port}/api/generate"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode())
                
        except Exception as e:
            return {"error": f"Generation failed: {e}"}
    
    def chat(self, model: str, messages: List[Dict], stream: bool = False, **kwargs) -> Dict:
        """Chat using OpenAI-compatible API"""
        if not self.is_running():
            return {"error": "Ollama server not running"}
        
        try:
            import urllib.request
            import json
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            url = f"http://{self.host}:{self.port}/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode())
                
        except Exception as e:
            return {"error": f"Chat failed: {e}"}
    
    def get_status(self) -> Dict:
        """Get comprehensive status information"""
        return {
            "platform": self.platform,
            "ollama_path": str(self.ollama_path),
            "data_dir": str(self.data_dir),
            "server_running": self.is_running(),
            "process_active": self.process is not None,
            "endpoint": f"http://{self.host}:{self.port}",
            "available_models": self.list_models()
        }


def test_ollama_manager():
    """Test the OllamaManager functionality"""
    print("🧪 Testing OllamaManager...")
    
    # Initialize manager
    manager = OllamaManager()
    status = manager.get_status()
    
    print(f"📊 Status: {json.dumps(status, indent=2)}")
    
    # Start Ollama
    if manager.start():
        print("✅ Ollama started successfully")
        
        # List models
        models = manager.list_models()
        print(f"📋 Available models: {models}")
        
        # Download a small model for testing
        if not models or "llama3.2:1b" not in models:
            print("📥 Downloading test model (llama3.2:1b)...")
            if manager.ensure_model("llama3.2:1b"):
                print("✅ Test model ready")
        
        # Test generation
        if models or manager.ensure_model("llama3.2:1b"):
            test_model = "llama3.2:1b" if "llama3.2:1b" in manager.list_models() else models[0]
            print(f"🧠 Testing generation with {test_model}...")
            
            response = manager.generate(
                model=test_model,
                prompt="Generate a one-sentence description of a 2D platformer game."
            )
            
            if "error" not in response:
                print(f"✅ Generation successful: {response.get('response', '')[:100]}...")
            else:
                print(f"❌ Generation failed: {response['error']}")
        
        # Stop Ollama
        manager.stop()
        print("✅ Test completed")
    else:
        print("❌ Failed to start Ollama")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_ollama_manager()
    else:
        print("OllamaManager - Direct binary management without Docker")
        print("Usage: python ollama_manager.py --test")