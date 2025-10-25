╔════════════════════════════════════════════════════════════════════════════╗
║                 GPU ACCELERATION QUICK REFERENCE (PR#22)                    ║
║              For Cognitive Development Features (Bob & Alice)               ║
╚════════════════════════════════════════════════════════════════════════════╝

## SYSTEM INFO

**GPU:** NVIDIA GeForce RTX 2060 SUPER (8GB VRAM, 2176 CUDA cores)  
**CPU:** Intel i7-6700 (4 cores, 8 threads)  
**RAM:** 32GB  
**Current Issue:** Rider (60%) + Bob stress test (80-90%) = System overloaded

**Solution:** GPU acceleration → 3-5x faster ops, 40-50% CPU usage

---

## QUICK START (5 STEPS)

### 1. INSTALL CUDA TOOLKIT (if needed)
```powershell
# Download from: https://developer.nvidia.com/cuda-downloads
# Select: Windows 10 64-bit
# Verify installation:
nvidia-smi
```

### 2. INSTALL GPU LIBRARIES
```powershell
cd E:/Tiny_Walnut_Games/the-seed
pip install -r requirements-gpu.txt
# Takes ~5 min, installs: cupy-cuda12x, torch, pycuda
```

### 3. VERIFY INSTALLATION
```powershell
python scripts/verify_gpu_acceleration.py
# Should show: ✓ nvidia-smi, ✓ NumPy/CuPy/PyTorch, ✓ GPU module, ✓ Benchmarks
```

### 4. CHOOSE INTEGRATION APPROACH
- **Option A (Recommended):** Direct replacement
  ```powershell
  Copy-Item -Path "Packages/com.twg.the-seed/seed/engine/exp09_api_service_gpu_enabled.py" `
            -Destination "Packages/com.twg.the-seed/seed/engine/exp09_api_service.py"
  ```
- **Option B (Gradual):** Manual integration (see IMPLEMENTATION_CHECKLIST.md)

### 5. RUN STRESS TEST
```powershell
python Packages/com.twg.the-seed/seed/engine/optimized_bob_stress.py
```

---

## KEY FILES

| File | Location | Purpose |
|------|----------|---------|
| `gpu_acceleration.py` | `Packages/com.twg.the-seed/seed/engine/` | Core GPU module |
| `exp09_api_service_gpu_enabled.py` | `Packages/com.twg.the-seed/seed/engine/` | Integration example |
| `verify_gpu_acceleration.py` | `scripts/` | Verification tool |
| `requirements-gpu.txt` | Root | GPU dependencies |

---

## PERFORMANCE EXPECTATIONS

### Before GPU Acceleration
- CPU Usage: 85-95% (Rider frozen)
- Workers: 6 concurrent
- Stress test: 30 minutes

### After GPU Acceleration
- CPU Usage: 40-50% (Rider responsive)
- Workers: 12-15 concurrent
- Stress test: 10-15 minutes

### Speedups by Operation
- Coherence analysis: **3-5x faster**
- Batch processing: **2-3x faster**
- Similarity computation: **4-6x faster**

---

## TROUBLESHOOTING

### nvidia-smi not found
```powershell
# CUDA Toolkit not installed or not in PATH
# Download and install from: https://developer.nvidia.com/cuda-downloads
# Verify: nvidia-smi
```

### ImportError: No module named 'cupy'
```powershell
# CuPy not installed
pip install -r requirements-gpu.txt
# If fails, check CUDA 12.x installed:
nvidia-smi  # Should show CUDA Version: 12.x
```

### CUDA out of memory errors
```python
# Automatic: batch sizes reduce if VRAM < 1GB
# Manual: Adjust batch size in gpu_acceleration.py
# GPUAccelerationManager: 
#   - Monitors available VRAM
#   - Automatically adjusts
#   - Falls back to CPU if needed
```

### GPU operations slower than CPU
```python
# Normal for small arrays (< 1000 elements)
# GPU memory transfer overhead dominates
# Threshold automatically adjusts for optimal performance
```

### verify_gpu_acceleration.py fails
```powershell
# Check prerequisites:
python -c "import numpy; print('NumPy OK')"
python -c "import cupy; print('CuPy OK')"
python -c "import torch; print('PyTorch OK')"

# If any fails:
pip install -r requirements-gpu.txt
```

---

## MONITORING COMMANDS

### Check GPU Status
```powershell
nvidia-smi                           # Real-time GPU info
nvidia-smi -l 1                      # Update every 1 second
nvidia-smi dmon -s pucvmet          # Detailed monitoring
```

### Check Python GPU Access
```powershell
python -c "import cupy as cp; print(cp.cuda.Device())"
python -c "import torch; print(torch.cuda.is_available())"
```

### Check VRAM Usage
```powershell
nvidia-smi --query-gpu=memory.free,memory.total --format=csv
```

---

## PERFORMANCE TUNING

### Batch Size Configuration
```python
# In gpu_acceleration.py, GPUAccelerationManager:
self.batch_size = 1024  # Adjust based on your VRAM
# RTX 2060 SUPER: 512-2048 is safe range
```

### GPU Acceleration Threshold
```python
# Minimum array size for GPU (smaller = CPU faster)
self.gpu_threshold = 1000  # elements
# Decrease for more GPU usage (more overhead)
# Increase for less GPU usage (more CPU time)
```

### Memory Reserve
```python
# Safety margin for OS (don't use all VRAM)
self.memory_reserve_gb = 0.5  # 500MB
# For 8GB GPU: leaves 7.5GB for computation
```

---

## EXPECTED LOG OUTPUT

### Verification Script
```
✓ nvidia-smi found: CUDA Version: 12.4
✓ Checking Python imports...
  ✓ NumPy 1.24.0
  ✓ CuPy 12.0.0
  ✓ PyTorch 2.1.0
✓ GPU acceleration module loaded
✓ Benchmarks completed:
  - Coherence (1K): 2.3ms GPU vs 10.5ms CPU (4.6x faster)
  - Similarity (100x768): 4.1ms GPU vs 20.2ms CPU (4.9x faster)
  - Overlap ratio (1K): 6.3ms GPU vs 30.1ms CPU (4.8x faster)
✓ GPU acceleration ready!
```

### Service Integration
```
[INFO] GPUAccelerationManager initialized
[INFO] GPU detected: NVIDIA GeForce RTX 2060 SUPER
[INFO] Available VRAM: 7.8GB
[INFO] GPU coherence analysis: 3.2x speedup
[INFO] GPU stress test acceleration: 1.8x speedup
```

---

## DOCUMENTATION STRUCTURE

```
docs/SEED/GPU_ACCELERATION/
├── README.md                          [Overview of this folder]
├── OVERVIEW.md                        [Executive summary & architecture]
├── QUICK_REFERENCE.md                 [This file]
├── IMPLEMENTATION_CHECKLIST.md        [16-point integration guide]
└── INTEGRATION_GUIDE.md               [Detailed code examples]
```

---

## NEXT STEPS

1. **Install & Verify** (10 min)
   - Follow steps 1-3 above
   - Run `verify_gpu_acceleration.py`

2. **Choose Approach** (5 min)
   - Option A: Direct replacement (easiest)
   - Option B: Gradual integration (learn more)

3. **Integrate** (30-60 min)
   - Follow IMPLEMENTATION_CHECKLIST.md
   - Option A takes ~5 min
   - Option B takes ~60 min

4. **Test** (30 min)
   - Run stress test
   - Monitor GPU/CPU usage
   - Verify speedups

5. **Document** (20 min)
   - Note performance improvements
   - Update PR with metrics

**Total Time: ~1.5-2 hours for complete setup**

---

## SUPPORT

For detailed guidance, see:
- **Installation:** IMPLEMENTATION_CHECKLIST.md
- **Code Integration:** INTEGRATION_GUIDE.md
- **Architecture:** OVERVIEW.md

For issues, check:
- Troubleshooting section above
- Script logs in verify_gpu_acceleration.py
- Error messages from pip install