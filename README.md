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
