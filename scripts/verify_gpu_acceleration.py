#!/usr/bin/env python3
"""
GPU Acceleration Verification Script

Verifies NVIDIA GPU setup and tests GPU acceleration components for
Cognitive Development Features (Bob & Alice).

Usage:
    python verify_gpu_acceleration.py
    python verify_gpu_acceleration.py --full      # Run full test suite
    python verify_gpu_acceleration.py --benchmark # Run performance benchmarks
"""

import sys
import argparse
from pathlib import Path
import subprocess

# Add seed engine to path
seed_engine = Path(__file__).parent.parent / "Packages" / "com.twg.the-seed" / "seed" / "engine"
sys.path.insert(0, str(seed_engine))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_cuda_toolkit():
    """Test NVIDIA CUDA Toolkit installation"""
    logger.info("\n" + "=" * 80)
    logger.info("1. Testing NVIDIA CUDA Toolkit")
    logger.info("=" * 80)
    
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✓ nvidia-smi found")
            # Parse output for key info
            for line in result.stdout.split('\n'):
                if 'NVIDIA GeForce' in line or 'CUDA Version' in line:
                    logger.info(f"  {line.strip()}")
            return True
        else:
            logger.error("✗ nvidia-smi failed")
            return False
    except FileNotFoundError:
        logger.error("✗ nvidia-smi not found - CUDA Toolkit not installed")
        logger.error("  Download from: https://developer.nvidia.com/cuda-downloads")
        return False


def test_python_imports():
    """Test required Python libraries"""
    logger.info("\n" + "=" * 80)
    logger.info("2. Testing Python Imports")
    logger.info("=" * 80)
    
    results = {}
    
    # NumPy
    try:
        import numpy as np
        logger.info(f"✓ NumPy {np.__version__}")
        results['numpy'] = True
    except ImportError:
        logger.error("✗ NumPy not found")
        results['numpy'] = False
    
    # CuPy
    try:
        import cupy as cp
        logger.info(f"✓ CuPy {cp.__version__}")
        try:
            device = cp.cuda.Device()
            logger.info(f"  - CUDA Device: {device.name.decode() if isinstance(device.name, bytes) else device.name}")
        except:
            logger.warning("  - Could not get device name")
        results['cupy'] = True
    except ImportError:
        logger.error("✗ CuPy not found - GPU acceleration unavailable")
        logger.error("  Install with: pip install cupy-cuda12x")
        results['cupy'] = False
    
    # PyTorch
    try:
        import torch
        logger.info(f"✓ PyTorch {torch.__version__}")
        logger.info(f"  - CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"  - CUDA Device: {torch.cuda.get_device_name(0)}")
        results['torch'] = True
    except ImportError:
        logger.warning("⚠ PyTorch not found (optional)")
        results['torch'] = False
    
    # PyCUDA
    try:
        import pycuda.driver
        logger.info(f"✓ PyCUDA available")
        results['pycuda'] = True
    except ImportError:
        logger.warning("⚠ PyCUDA not found (optional)")
        results['pycuda'] = False
    
    return results


def test_gpu_acceleration_module():
    """Test GPU acceleration module"""
    logger.info("\n" + "=" * 80)
    logger.info("3. Testing GPU Acceleration Module")
    logger.info("=" * 80)
    
    try:
        from gpu_acceleration import (
            get_gpu_manager,
            gpu_acceleration_status,
            GPUCoherenceAnalyzer,
            GPUSemanticSimilarity,
            GPUAccelerationConfig
        )
        logger.info("✓ GPU acceleration module imported")
        
        # Get status
        status = gpu_acceleration_status()
        logger.info(f"  - GPU Available: {status['gpu_available']}")
        logger.info(f"  - GPU Type: {status['gpu_type']}")
        
        if status['gpu_available']:
            logger.info(f"  - CUDA Capability: {status.get('cuda_capability', 'Unknown')}")
        
        # Initialize manager
        manager = get_gpu_manager()
        logger.info("✓ GPU manager initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ GPU acceleration module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_performance_benchmark():
    """Run performance benchmarks"""
    logger.info("\n" + "=" * 80)
    logger.info("4. Running Performance Benchmarks")
    logger.info("=" * 80)
    
    try:
        import numpy as np
        import time
        from gpu_acceleration import get_gpu_manager
        
        manager = get_gpu_manager()
        
        # Benchmark 1: Variance computation
        logger.info("\nBenchmark 1: Semantic Variance (10,000 elements)")
        scores = np.random.rand(10000).astype(np.float32)
        
        # CPU
        start = time.time()
        cpu_var = np.var(scores)
        cpu_time = (time.time() - start) * 1000
        logger.info(f"  CPU: {cpu_var:.6f} in {cpu_time:.2f}ms")
        
        # GPU
        if manager.gpu_available:
            start = time.time()
            gpu_var = manager.coherence_analyzer.compute_semantic_variance_gpu(scores)
            gpu_time = (time.time() - start) * 1000
            logger.info(f"  GPU: {gpu_var:.6f} in {gpu_time:.2f}ms")
            logger.info(f"  Speedup: {cpu_time/gpu_time:.1f}x")
        
        # Benchmark 2: Similarity computation
        logger.info("\nBenchmark 2: Cosine Similarity (100 docs × 768 dims)")
        query = np.random.rand(768).astype(np.float32)
        docs = np.random.rand(100, 768).astype(np.float32)
        
        # CPU
        start = time.time()
        cpu_sim = manager.semantic_similarity._compute_similarity_cpu(query, docs)
        cpu_time = (time.time() - start) * 1000
        logger.info(f"  CPU: {cpu_time:.2f}ms")
        
        # GPU
        if manager.gpu_available:
            start = time.time()
            gpu_sim = manager.semantic_similarity.compute_similarity_matrix_gpu(query, docs)
            gpu_time = (time.time() - start) * 1000
            logger.info(f"  GPU: {gpu_time:.2f}ms")
            logger.info(f"  Speedup: {cpu_time/gpu_time:.1f}x")
        
        logger.info("\n✓ Benchmarks completed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main verification routine"""
    parser = argparse.ArgumentParser(description="Verify GPU acceleration setup")
    parser.add_argument("--full", action="store_true", help="Run full test suite")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmarks")
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("GPU Acceleration Verification")
    logger.info("=" * 80)
    
    results = {}
    
    # Test 1: CUDA Toolkit
    results['cuda'] = test_cuda_toolkit()
    
    # Test 2: Python imports
    results['imports'] = test_python_imports()
    
    # Test 3: GPU acceleration module
    results['module'] = test_gpu_acceleration_module()
    
    # Test 4: Benchmarks
    if args.benchmark:
        results['benchmark'] = run_performance_benchmark()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    
    cuda_ok = results.get('cuda', False)
    imports_ok = results.get('imports', {}).get('cupy', False)
    module_ok = results.get('module', False)
    
    if cuda_ok and imports_ok and module_ok:
        logger.info("✓ GPU Acceleration Fully Functional!")
        logger.info("\nYou can now use GPU acceleration in:")
        logger.info("  - Bob's coherence analysis")
        logger.info("  - Stress testing operations")
        logger.info("  - Semantic similarity calculations")
        logger.info("\nNext steps:")
        logger.info("  1. Use exp09_api_service_gpu_enabled.py instead of exp09_api_service.py")
        logger.info("  2. Or integrate gpu_acceleration module into existing services")
        logger.info("  3. Run stress tests with: python optimized_bob_stress.py --gpu-accelerated")
        return 0
    else:
        logger.error("\n✗ GPU Acceleration Setup Incomplete")
        
        if not cuda_ok:
            logger.error("\nAction Required:")
            logger.error("  1. Install NVIDIA CUDA Toolkit 12.x")
            logger.error("     Download: https://developer.nvidia.com/cuda-downloads")
            logger.error("  2. Verify installation: nvidia-smi")
        
        if not imports_ok:
            logger.error("\nAction Required:")
            logger.error("  1. Install CuPy:")
            logger.error("     pip install cupy-cuda12x")
            logger.error("  2. Or use CPU-only mode by setting FORCE_CPU=True")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())