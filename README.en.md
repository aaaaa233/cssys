# CSSys - Computer System Architecture Experiment Framework

This project is a computer system architecture experiment framework based on gem5, used to conduct various architectural experiments ranging from caches to accelerators.

## Project Introduction

CSSys (Computer System Structure) is a modular computer system architecture simulation platform that implements modeling and analysis of processors, cache hierarchies, and custom hardware accelerators using the gem5 simulator. The project contains 7 progressive experiment modules, covering:

- CPU model comparison and fidelity analysis
- Cache hierarchy design (associativity, replacement policy, prefetching)
- Branch predictor design
- Hardware accelerator (Dotp8) design and optimization
- System integration and performance evaluation

## Directory Structure

```
.
├── _tools/          # Experiment scripts and tools
│   ├── run_*.sh     # Run scripts for each experiment
│   ├── lab*.sh      # Experiment-related scripts
│   ├── ppt/         # Experiment report PPT generation scripts
│   └── *.py         # Python helper tools
├── bench/           # Benchmark programs
│   ├── src/         # Source code
│   │   ├── pchase.c     # Pointer chase test
│   │   ├── stream.c     # Memory bandwidth test
│   │   ├── gemm.c       # Matrix multiplication
│   │   ├── qnn.c        # Quantized neural network inference
│   │   └── branchy.c    # Branch prediction test
│   └── include/     # Header files
├── framework/       # Simulation framework core modules
│   ├── cssys_se.py  # gem5 SE mode system configuration
│   ├── sweep.py     # Parameter sweeping and experiment management
│   ├── area.py      # Area and energy consumption model
│   ├── stats.py     # Statistical data parsing
│   └── report.py    # Experiment report generation
├── gem5src/         # gem5 extension source code
│   └── cssys/
│       ├── Dotp8Accel.py    # Accelerator Python interface
│       ├── dotp8_accel.cc   # Accelerator implementation
│       └── dotp8_accel.hh   # Header file
└── results/         # Experiment result data
    └── lab*.csv     # Measurement data for each experiment
```

## Core Components

### 1. Benchmark Programs

- **pchase**: Pointer chase test, evaluates cache access efficiency
- **stream**: STREAM memory bandwidth benchmark
- **gemm**: Matrix multiplication, evaluates computational performance
- **qnn**: 8-bit quantized neural network inference (MLP)
- **branchy**: Branch-intensive program

### 2. Dotp8 Accelerator

Custom 8-bit vector dot product hardware accelerator, supporting:

- Configurable number of Processing Elements (PE)
- Asynchronous FIFO request queue
- Adjustable launch latency and throughput

### 3. Parameter Sweep Framework

`framework/sweep.py` supports flexible parameter space sweeping, allowing simultaneous variation of hardware configurations and software (binaries), realizing Cartesian product experiments of hardware and software parameters.

## Quick Start

### Environment Requirements

- gem5 Simulator
- Python 3.x
- SCons Build System

### Compile gem5

```bash
cd _tools
./build_gem5.sh
```

### Run Experiments

```bash
# Run Lab 1 experiment
./run_lab1.sh

# Run specified benchmark
./run_lab5.sh qnn timing
```

## Experiment Overview

| Experiment | Topic | Key Metrics |
|------|------|----------|
| Lab 1 | CPU Model | CPI, IPC, Fidelity |
| Lab 2 | Cache Design | Hit Rate, Latency, Associativity |
| Lab 3 | Prefetching & Replacement | MRM, Coverage |
| Lab 4 | Branch Prediction | Prediction Accuracy, BTB Hit Rate |
| Lab 5 | Dot Product Optimization | Instruction Count, Loop Unrolling |
| Lab 6 | Accelerator Integration | Speedup, Batching |
| Lab 7 | Optimization & Robustness | Area-Performance Trade-off |

## Technical Details

### Cache Configuration

The framework supports flexible three-level cache configuration:

- L1 I/D Cache: Configurable associativity, capacity, replacement policy
- L2 Cache: Unified cache, supports prefetcher
- Optional L3 Cache

### CPU Model

- **TimingSimpleCPU**: Simple timing model
- **O3CPU**: Out-of-order execution processor, supports configurable pipeline width, ROB capacity, issue queue depth, etc.

## License

This project is a course experiment framework; please refer to relevant files for specific license details.