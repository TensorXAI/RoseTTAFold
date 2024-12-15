import torch

def fallback_to_cpu_if_mps(device: torch.device) -> torch.device:
    """
    Ensures compatibility by falling back to CPU if the device is MPS.
    This is used in cases where PyTorch's automatic fallback cannot manage the fallback, or
    certain layers (e.g., DGL or Torch Geometric layers) may not fully support MPS. This ensures compatibility. 

    Args:
        device (torch.device): The original device.

    Returns:
        torch.device: The resolved device (CPU if MPS, otherwise the original device).
    """
    if device.type == 'mps':
        return torch.device('cpu')
    return device
