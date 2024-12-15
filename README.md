## Hardware Configuration

### Rationale for Hardware Selection
The following hardware was chosen to optimize performance for bioinformatics workloads:

- **Unified Memory:** Eliminates data transfer bottlenecks between CPU and GPU, ensuring efficient memory usage.
- **PyTorch Support:** Acceleration via Metal Performance Shaders (MPS) for faster model inference.
- **Accelerate Framework:** Enhances CPU-bound linear algebra and vectorized computations.

### Configuration
- **Apple M3 Pro Chip:**
  - macOS 14.7
  - 12-core CPU
  - 18-core GPU
  - 18 GB Unified Memory
- **Storage:**
  - SanDisk Pro-G40 SSD
  - 4TB capacity
  - Up to 3 GB/s read speed

### Performance Considerations
- **Database Storage:** Sequence and structure template databases (~1.2 TB) were stored on the SanDisk SSD to enable fast I/O and rapid querying.
- **Unified Memory & SSD:** The combination ensured seamless handling of large datasets, significantly reducing computational latency during:
  - Model inference
  - Multiple Sequence Alignment (MSA) generation

## Software Contributions

This work developed a customized RoseTTAFold pipeline optimized for low-cost, ARM64-based infrastructure, enabling offloading of inference and prediction tasks from traditional HPC or cloud setups. The following contributions highlight key innovations:

### 1. Conda Environment Customization
- Implemented a custom Conda YAML configuration to select ARM64-compatible packages.
- For dependencies without native ARM64 support, dynamic libraries (C, C++) and associated Python APIs were rebuilt from source and linked with upgraded foundation libraries such as Numpy and PyTorch.
- Changes were applied to build configurations (e.g., `CMakeLists.txt`, compiler/linker flags) and occasionally the codebase to ensure ARM64 hardware acceleration while maintaining compatibility with the ecosystem.
- Rebuilding was performed on two core libraries critical to RoseTTAFold:
  - **Deep Graph Library (DGL)**
  - **Lie Learn Library**

### 2. GPU-to-CPU Fallback Mechanism
- Implemented a fallback mechanism to switch from GPU to CPU execution for third-party dependencies incompatible with Apple’s GPU acceleration.
- Ensured the pipeline could run efficiently with a mixed CPU-GPU approach across diverse hardware configurations.

### 3. Dockerization of Legacy Tools
- Created a custom Docker image (based on `ubuntu:22.04`) for ARM64 compatibility to containerize:
  - **NCBI BLAST** binaries distributed for x86-64.
  - **PSIPRED**, a secondary structure prediction tool leveraging PSSMs generated by PSI-BLAST.
- The Docker image enabled seamless execution by translating x86-64 instructions to ARM64 using the `--platform linux/amd64` flag.
- Maintained tool configurations close to the original RoseTTAFold pipeline, minimizing modifications to critical data preparation steps.
- Docker Engine version `27.1.1` was used, with no issues encountered during emulation.

### 4. Protein Sequence Testing
- Validated the modified pipeline on protein sequences of varying lengths, from hundreds to several hundred residues, demonstrating efficiency and reliability across diverse use cases.
- Structural accuracy of predicted models was assessed using the **Local Distance Difference Test (lDDT)**:
  - Quantifies local structural accuracy relative to a reference structure.
  - Scores range from 0 to 1, where higher scores indicate closer matches.
  - Highlights local features such as loops and side chains, offering insights beyond global metrics like RMSD.
- Since lDDT (part of the OpenStructure toolkit) lacked native ARM64 support, it was rebuilt from source:
  - Build configurations (e.g., `CMakeLists.txt`) were modified with ARM64-specific compiler and linker flags.
  - This ensured compatibility with the ARM64 pipeline without sacrificing functionality or performance.

