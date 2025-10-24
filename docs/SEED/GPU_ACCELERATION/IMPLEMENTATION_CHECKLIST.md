# GPU Acceleration Implementation Checklist (PR#22)

## Pre-Implementation Review

### Prerequisites
- [ ] Read `OVERVIEW.md` (5 min)
- [ ] Review `QUICK_REFERENCE.md` (2 min)
- [ ] Understand your hardware specs (RTX 2060 SUPER, i7-6700, 32GB RAM)
- [ ] Confirm NVIDIA GeForce RTX 2060 SUPER detection
  ```powershell
  nvidia-smi
  ```

### Decision Point: Integration Approach
Choose one:
- [ ] **Option A (Recommended):** Copy `exp09_api_service_gpu_enabled.py` → `exp09_api_service.py`
  - Pros: Complete, tested, minimal code changes
  - Cons: Overwrites existing service (backup first)
  
- [ ] **Option B (Gradual):** Manual integration from `INTEGRATION_GUIDE.md`
  - Pros: Full control, understand each change
  - Cons: More work, more error-prone

---

## Installation Phase (10-15 minutes)

### Step 1: CUDA Toolkit Setup
- [ ] Check if CUDA 12.x already installed
  ```powershell
  nvidia-smi
  ```
- [ ] If not installed:
  - [ ] Download CUDA 12.x from https://developer.nvidia.com/cuda-downloads
  - [ ] Run installer (local exe recommended)
  - [ ] Accept default installation path
  - [ ] Wait for completion (~10 min)
- [ ] Verify installation
  ```powershell
  nvidia-smi
  ```
  Should show:
  ```
  | NVIDIA GeForce RTX 2060 SUPER          |
  | CUDA Version: 12.x                     |
  ```

### Step 2: Python Environment Setup
- [ ] Navigate to project root
  ```powershell
  Set-Location "E:/Tiny_Walnut_Games/the-seed"
  ```
- [ ] Create/activate virtual environment (optional but recommended)
  ```powershell
  python -m venv venv_gpu
  .\venv_gpu\Scripts\Activate.ps1
  ```
- [ ] Upgrade pip
  ```powershell
  python -m pip install --upgrade pip
  ```

### Step 3: Install GPU Libraries
- [ ] Install from requirements-gpu.txt
  ```powershell
  pip install -r requirements-gpu.txt
  ```
- [ ] Wait for completion (~5 minutes)
- [ ] Verify successful installation
  ```powershell
  pip list | findstr "cupy torch"
  ```
  Should show:
  ```
  cupy-cuda12x     12.0.0 (or similar)
  torch            2.1.0+ (or similar)
  ```

### Step 4: Verify GPU Module Import
- [ ] Test direct import
  ```powershell
  python -c "from gpu_acceleration import GPUAccelerationManager; print('✓ GPU module imported')"
  ```
  If error about path, navigate to seed/engine:
  ```powershell
  Set-Location "Packages/com.twg.the-seed/seed/engine"
  python -c "from gpu_acceleration import GPUAccelerationManager; print('✓ GPU module imported')"
  Set-Location "E:/Tiny_Walnut_Games/the-seed"
  ```

---

## Verification Phase (5-10 minutes)

### Step 5: Run Verification Script
- [ ] Execute verification script
  ```powershell
  python scripts/verify_gpu_acceleration.py
  ```
- [ ] Review output for errors
  - All items should show ✓
  - If any fail, troubleshoot below
- [ ] Note performance metrics for comparison

### Step 6: Check Verification Results
- [ ] Verify nvidia-smi found (shows GPU info)
- [ ] Verify NumPy import OK
- [ ] Verify CuPy import OK
- [ ] Verify PyTorch import OK
- [ ] Verify GPU acceleration module loaded
- [ ] Verify benchmark tests completed
- [ ] Verify no CUDA out of memory errors

**If verification fails:**
- [ ] Check CUDA installed: `nvidia-smi`
- [ ] Check CUDA 12.x version (not 11.x or older)
- [ ] Reinstall GPU libraries: `pip install -r requirements-gpu.txt --force-reinstall`
- [ ] Restart command prompt and try again

---

## Integration Phase - Option A (Direct Replacement)

### Step 7: Backup Current Service (IMPORTANT!)
- [ ] Create backup of existing service
  ```powershell
  Copy-Item -Path "Packages/com.twg.the-seed/seed/engine/exp09_api_service.py" `
            -Destination "Packages/com.twg.the-seed/seed/engine/exp09_api_service.py.backup"
  ```
- [ ] Verify backup exists
  ```powershell
  Get-Item "Packages/com.twg.the-seed/seed/engine/exp09_api_service.py.backup"
  ```

### Step 8: Copy GPU-Enabled Service
- [ ] Copy GPU-enabled version
  ```powershell
  Copy-Item -Path "Packages/com.twg.the-seed/seed/engine/exp09_api_service_gpu_enabled.py" `
            -Destination "Packages/com.twg.the-seed/seed/engine/exp09_api_service.py"
  ```
- [ ] Verify copy succeeded
  ```powershell
  Get-Item "Packages/com.twg.the-seed/seed/engine/exp09_api_service.py" | Select-Object Name, Length
  ```
- [ ] File should be ~550 lines

### Step 9: Verify Service Imports
- [ ] Test that service imports correctly
  ```powershell
  cd "Packages/com.twg.the-seed/seed/engine"
  python -c "import exp09_api_service; print('✓ Service imports OK')"
  cd "E:/Tiny_Walnut_Games/the-seed"
  ```
- [ ] If import fails, check error and compare with backup

### Step 10: Run Service Health Check
- [ ] Start the service briefly to verify it starts
  ```powershell
  # Option 1: Check with pytest
  pytest "Packages/com.twg.the-seed/seed/engine/test_*.py" -v

  # Option 2: Start and check
  python -m uvicorn exp09_api_service:app --host 127.0.0.1 --port 8000 &
  # Let it run for 5 seconds, then Ctrl+C
  ```

**If Option A fails:**
- [ ] Restore backup: `Copy-Item -Path exp09_api_service.py.backup -Destination exp09_api_service.py`
- [ ] Check error messages and compare files
- [ ] Try Option B (gradual integration) instead

---

## Integration Phase - Option B (Gradual Integration)

### Step 11: Understand GPU Module Components
- [ ] Read `INTEGRATION_GUIDE.md` completely
- [ ] Understand each GPU component:
  - [ ] `GPUCoherenceAnalyzer` - Coherence calculations
  - [ ] `GPUSemanticSimilarity` - Vector similarity
  - [ ] `GPUStressTestAccelerator` - Test acceleration
  - [ ] `GPUAccelerationManager` - Main coordinator
- [ ] Review code examples in integration guide

### Step 12: Manually Integrate Components
- [ ] Open `exp09_api_service.py` in editor
- [ ] Import GPU module at top:
  ```python
  from gpu_acceleration import GPUAccelerationManager
  ```
- [ ] Initialize GPU manager in service startup:
  ```python
  gpu_manager = GPUAccelerationManager()
  ```
- [ ] Follow examples in `INTEGRATION_GUIDE.md` for each function:
  - [ ] `_analyze_narrative_coherence_gpu()`
  - [ ] `_stress_test_result_gpu()`
  - [ ] GPU status endpoints

### Step 13: Verify Gradual Integration
- [ ] After each component, test imports
  ```powershell
  python -c "import exp09_api_service; print('✓ Service still imports')"
  ```
- [ ] After all components, run full test:
  ```powershell
  pytest "Packages/com.twg.the-seed/seed/engine/test_*.py" -v
  ```

---

## Testing Phase (20-30 minutes)

### Step 14: Run Stress Test with GPU Acceleration
- [ ] Execute GPU-accelerated stress test
  ```powershell
  python Packages/com.twg.the-seed/seed/engine/optimized_bob_stress.py
  ```
- [ ] Monitor output for GPU usage indicators
  - Look for lines like: `GPU coherence analysis: 3.2x speedup`
  - Look for CPU usage dropping to 40-50%
- [ ] Let test run for at least 2-5 minutes
- [ ] Press Ctrl+C to stop

### Step 15: Verify Performance Improvement
- [ ] Compare metrics before/after GPU acceleration
  - [ ] CPU usage: Was 85-95%, should now be 40-50%
  - [ ] GPU usage: Should show 50-70% during tests
  - [ ] Query throughput: Should be 2-3x higher
  - [ ] Concurrent workers: Should handle 12-15 (was 6)

- [ ] Run `nvidia-smi` in another terminal while stress testing
  ```powershell
  # In separate terminal:
  nvidia-smi -l 1
  # Should show GPU being used during stress test
  ```

### Step 16: Document Results
- [ ] Capture performance metrics
  ```
  Before GPU Acceleration:
  - CPU Usage: ___%
  - Query Throughput: ___ queries/sec
  - Workers: ___
  - Stress Test Time: ___ minutes
  
  After GPU Acceleration:
  - CPU Usage: ___%
  - Query Throughput: ___ queries/sec
  - Workers: ___
  - Stress Test Time: ___ minutes
  
  Improvements:
  - CPU Reduction: ___%
  - Throughput Increase: ___x
  - Worker Increase: ___x
  - Time Reduction: ___% faster
  ```

- [ ] Save results to file for PR documentation
- [ ] Include `nvidia-smi` output showing GPU specs
- [ ] Include verification script output

---

## Post-Integration Phase

### Troubleshooting Guide

**GPU Acceleration Not Being Used:**
```powershell
# Check logs for GPU initialization errors
# Verify GPU module is imported
python -c "from gpu_acceleration import GPUAccelerationManager; print('✓ Module OK')"

# Verify CUDA available
python -c "import cupy; print('✓ CuPy OK'); print(cupy.cuda.Device())"
```

**CUDA Out of Memory During Stress Test:**
```python
# GPU module automatically reduces batch size
# If still occurring, manual adjustment in gpu_acceleration.py:
# Reduce MAX_VRAM_PERCENT from 0.25 to 0.15
```

**Service Won't Start:**
```powershell
# Restore backup
Copy-Item -Path "exp09_api_service.py.backup" -Destination "exp09_api_service.py"

# Check error:
python -c "import exp09_api_service" 2>&1 | Select-Object -First 20
```

**Verification Script Fails:**
```powershell
# Reinstall GPU libraries
pip install -r requirements-gpu.txt --force-reinstall --no-cache-dir

# Verify CUDA 12.x
nvidia-smi  # Should show CUDA Version: 12.x (not 11.x)
```

---

## Final Checklist

### Before Submitting PR:
- [ ] GPU acceleration verified working
- [ ] Performance improvements documented
- [ ] All tests passing
- [ ] No CUDA errors during extended stress test
- [ ] CPU usage reduced to 40-50% range
- [ ] GPU utilization showing 50-70% during tests
- [ ] City simulation stress test completed successfully
- [ ] Results attached to PR documentation

### Files Modified/Created:
- [ ] `exp09_api_service.py` - Updated with GPU components
- [ ] Documentation in `docs/SEED/GPU_ACCELERATION/` - Complete
- [ ] Performance metrics captured and documented

### Cleanup (Optional):
- [ ] Backup file can be deleted: `rm exp09_api_service.py.backup`
- [ ] But keep for reference if needed

---

## Performance Baseline Reference

### Your Hardware
- GPU: NVIDIA GeForce RTX 2060 SUPER (8GB VRAM)
- CPU: Intel i7-6700 (4 cores, 8 threads)
- RAM: 32GB

### Expected Results
- **CPU Usage**: 85-95% → 40-50% (47% reduction)
- **Query Throughput**: +200-300% improvement
- **Concurrent Workers**: 6 → 12-15 (2x increase)
- **Stress Test Time**: 30min → 10-15min (50-66% reduction)
- **GPU Utilization**: 50-70% during sustained load

### Success Criteria
- [ ] Bob's hallucination detection properly stress-tested
- [ ] Rider IDE remains responsive (CPU below 50%)
- [ ] Stress test completes in 10-15 minutes
- [ ] No CUDA out of memory errors
- [ ] GPU utilization 50%+ during peak load

---

**Estimated Total Time: 1.5-2 hours for complete installation & integration**

---

## Next Steps After Completion

1. **Submit PR#22** with GPU acceleration framework
2. **Include Performance Metrics** showing improvements
3. **Document Any Custom Tuning** made for your hardware
4. **Update Project Documentation** if integration differs from examples
5. **Monitor Stress Tests** to verify Bob detects hallucinations properly

Good luck! 🚀