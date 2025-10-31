#!/usr/bin/env python3
"""
STAT7 Visualization System Diagnostic Tool
Checks for common issues and provides solutions
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Python Version Check")
    print("-" * 30)

    version = sys.version_info
    print(f"Current version: {version.major}.{version.minor}.{version.micro}")

    if version >= (3, 8):
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        print("   Please upgrade Python")
        return False

def check_packages():
    """Check required packages."""
    print("\n📦 Package Check")
    print("-" * 30)

    required_packages = {
        'websockets': 'WebSocket server support',
        'asyncio': 'Async programming support',
        'json': 'JSON handling',
        'threading': 'Multi-threading support',
        'pathlib': 'Path handling'
    }

    missing_packages = []

    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📥 Install missing packages:")
        if 'websockets' in missing_packages:
            print("   pip install websockets")
        return False

    return True

def check_files():
    """Check for required files."""
    print("\n📁 File Check")
    print("-" * 30)

    required_files = {
        'stat7wsserve.py': 'WebSocket server',
        'stat7threejs.html': 'Main visualization HTML',
        'stat7-core.js': 'Three.js core engine',
        'stat7-websocket.js': 'WebSocket client',
        'stat7-ui.js': 'User interface controller',
        'stat7-main.js': 'Main visualization class',
        'simple_web_server.py': 'Web server launcher'
    }

    missing_files = []

    for file, description in required_files.items():
        if os.path.exists(file):
            file_size = os.path.getsize(file)
            print(f"✅ {file} ({file_size} bytes) - {description}")
        else:
            print(f"❌ {file} - {description}")
            missing_files.append(file)

    if missing_files:
        print(f"\n📂 Missing files: {missing_files}")
        return False

    return True

def check_javascript_syntax():
    """Basic check for JavaScript syntax issues."""
    print("\n🔧 JavaScript Syntax Check")
    print("-" * 30)

    js_files = [
        'stat7-core.js',
        'stat7-websocket.js',
        'stat7-ui.js',
        'stat7-main.js'
    ]

    syntax_errors = []

    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Basic syntax checks
                brace_count = content.count('{') - content.count('}')
                paren_count = content.count('(') - content.count(')')
                bracket_count = content.count('[') - content.count(']')

                if brace_count == 0 and paren_count == 0 and bracket_count == 0:
                    print(f"✅ {js_file} - Balanced brackets")
                else:
                    error_msg = f"{js_file} - Unbalanced: "
                    if brace_count != 0:
                        error_msg += f"braces({brace_count:+d}) "
                    if paren_count != 0:
                        error_msg += f"parens({paren_count:+d}) "
                    if bracket_count != 0:
                        error_msg += f"brackets({bracket_count:+d}) "

                    print(f"❌ {error_msg}")
                    syntax_errors.append(js_file)
        else:
            print(f"⚠️ {js_file} - File not found")

    return len(syntax_errors) == 0

def check_ports():
    """Check if required ports are available."""
    print("\n🔌 Port Check")
    print("-" * 30)

    import socket

    ports_to_check = [
        (8000, "Web server (default)"),
        (8765, "WebSocket server"),
        (8080, "Web server (fallback)")
    ]

    available_ports = []

    for port, description in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print(f"✅ Port {port} available - {description}")
                available_ports.append(port)
        except OSError:
            print(f"❌ Port {port} in use - {description}")

    return len(available_ports) >= 2  # Need at least 2 ports

def test_websocket_import():
    """Test if the WebSocket server can be imported."""
    print("\n🧪 WebSocket Server Import Test")
    print("-" * 30)

    try:
        # Test basic imports first
        web_dir = os.path.dirname(os.path.abspath(__file__))
        server_dir = os.path.join(web_dir, 'server')
        sys.path.insert(0, server_dir)

        # Test individual components
        from stat7wsserve import STAT7EventStreamer
        print("✅ STAT7EventStreamer import successful")

        from stat7wsserve import ExperimentVisualizer
        print("✅ ExperimentVisualizer import successful")

        from stat7wsserve import generate_random_bitchain
        print("✅ generate_random_bitchain import successful")

        # Test basic functionality
        streamer = STAT7EventStreamer()
        print("✅ STAT7EventStreamer instantiation successful")

        bitchain = generate_random_bitchain()
        print("✅ Random bitchain generation successful")

        event = streamer.create_bitchain_event(bitchain)
        print("✅ Event creation successful")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        return False

def run_quick_test():
    """Run a quick functional test."""
    print("\n⚡ Quick Functional Test")
    print("-" * 30)

    try:
        import asyncio
        # Ensure server directory is in path
        web_dir = os.path.dirname(os.path.abspath(__file__))
        server_dir = os.path.join(web_dir, 'server')
        if server_dir not in sys.path:
            sys.path.insert(0, server_dir)
        from stat7wsserve import generate_random_bitchain, STAT7EventStreamer

        # Generate a test bitchain
        bitchain = generate_random_bitchain()
        print(f"✅ Generated bitchain: {bitchain.entity_type} in {bitchain.realm}")

        # Create streamer
        streamer = STAT7EventStreamer()
        event = streamer.create_bitchain_event(bitchain, "DIAGNOSTIC_TEST")
        print(f"✅ Created event: {event.event_type}")

        # Test JSON serialization
        event_dict = event.to_dict()
        import json
        json_str = json.dumps(event_dict)
        print(f"✅ JSON serialization successful ({len(json_str)} chars)")

        return True

    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def generate_report():
    """Generate a diagnostic report."""
    print("\n📋 Generating Diagnostic Report")
    print("=" * 60)

    results = {
        'python_version': check_python_version(),
        'packages': check_packages(),
        'files': check_files(),
        'javascript_syntax': check_javascript_syntax(),
        'ports': check_ports(),
        'websocket_import': test_websocket_import(),
        'quick_test': run_quick_test()
    }

    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 Your STAT7 visualization system is ready to run!")
        print("\n📋 To start the system:")
        print("   Option 1: python launch_stat7_complete.py")
        print("   Option 2: start_visualization.bat (Windows)")
        print("   Option 3: python start_stat7_visualization.py")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("\n🔧 Recommended fixes:")

        if not results['python_version']:
            print("   • Upgrade to Python 3.8+")
        if not results['packages']:
            print("   • Run: pip install -r requirements-visualization.txt")
        if not results['files']:
            print("   • Ensure all JavaScript and Python files are present")
        if not results['javascript_syntax']:
            print("   • Check JavaScript files for syntax errors (unbalanced braces)")
        if not results['ports']:
            print("   • Close applications using ports 8000, 8765, or 8080")
        if not results['websocket_import']:
            print("   • Check stat7wsserve.py for syntax errors")
        if not results['quick_test']:
            print("   • Run basic functionality test")

    return all_passed

def main():
    """Main diagnostic function."""
    print("🔍 STAT7 Visualization System Diagnostics")
    print("=" * 60)
    print("This tool will check your system for common issues")
    print()

    try:
        success = generate_report()

        if not success:
            print("\n❓ Need help?")
            print("   • Check the error messages above")
            print("   • Ensure all files are present and not corrupted")
            print("   • Try running: pip install -r requirements-visualization.txt")
            print("   • Restart your terminal/IDE after installing packages")

    except Exception as e:
        print(f"\n💥 Diagnostic tool crashed: {e}")
        print("This suggests a serious configuration issue.")

    print(f"\n📁 Working directory: {os.getcwd()}")
    print("👋 Diagnostic complete")

if __name__ == "__main__":
    main()
