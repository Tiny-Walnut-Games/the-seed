# GPU Acceleration Framework - PR#22

GPU acceleration for Cognitive Development Features (Bob & Alice) enabling proper stress testing on RTX 2060 SUPER hardware.

## Documentation Files

- **[OVERVIEW.md](./OVERVIEW.md)** - Executive summary and architecture
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - One-page quick start guide
- **[IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)** - Step-by-step 16-point integration guide
- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Detailed code integration examples

## Quick Start

```powershell
# 1. Verify CUDA installed
nvidia-smi

# 2. Install GPU libraries
pip install -r requirements-gpu.txt

# 3. Verify setup
python scripts/verify_gpu_acceleration.py

# 4. Integrate GPU acceleration
# See IMPLEMENTATION_CHECKLIST.md for options

# 5. Run stress test
python Packages/com.twg.the-seed/seed/engine/optimized_bob_stress.py
```

## Core Modules

Located in `Packages/com.twg.the-seed/seed/engine/`:

- **gpu_acceleration.py** - Core GPU module with accelerators
- **exp09_api_service_gpu_enabled.py** - Integration example service
- **verify_gpu_acceleration.py** - Verification script (in scripts/)

## System Requirements

- NVIDIA GPU with CUDA support (RTX 2060 SUPER tested)
- CUDA 12.x toolkit installed
- CuPy 12.x and PyTorch libraries
- 8GB+ VRAM recommended

## Expected Performance

- **CPU Usage**: 85-95% → 40-50% (47% reduction)
- **Query Throughput**: 2-3x improvement
- **Concurrent Workers**: 6 → 12-15
- **Stress Test Duration**: 30min → 10-15min