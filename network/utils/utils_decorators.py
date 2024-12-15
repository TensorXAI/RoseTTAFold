import torch

def cuda_amp_autocast(enabled=True):
    """
    A reusable decorator for applying torch.cuda.amp.autocast conditionally.
    
    Args:
        enabled (bool): Whether autocast should be enabled or not.
    
    Returns:
        Callable: The decorated function or method.
    """
    def decorator(func):
        if torch.cuda.is_available():
            return torch.cuda.amp.autocast(enabled=enabled)(func)
        else:
            return func
    return decorator