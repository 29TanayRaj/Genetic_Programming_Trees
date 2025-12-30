import numpy as np

def mse(predicted: np.ndarray, actual: np.ndarray) -> float:
    """Mean Squared Error"""
    return np.mean((predicted - actual) ** 2)

def mae(predicted: np.ndarray, actual: np.ndarray) -> float:
    """Mean Absolute Error"""
    return np.mean(np.abs(predicted - actual))

def rmse(predicted: np.ndarray, actual: np.ndarray) -> float:
    """Root Mean Squared Error"""
    return np.sqrt(np.mean((predicted - actual) ** 2))

def log_cosh(predicted: np.ndarray, actual: np.ndarray) -> float:
    """Log Cosh Loss: log(cosh(predicted - actual))
    Smoother than L1, less sensitive to outliers than L2.
    """
    error = predicted - actual
    # Use numpy's vectorized operations
    # For large errors, log(cosh(x)) approx |x| - log(2)
    # We can use a safe implementation to avoid overflow
    
    # Define a threshold for large values where cosh might overflow
    # cosh(710) is close to max float
    threshold = 700
    
    abs_error = np.abs(error)
    
    # Create a mask for values where direct cosh is safe
    safe_mask = abs_error <= threshold
    large_mask = ~safe_mask
    
    loss = np.zeros_like(error, dtype=float)
    
    # Calculate for safe values
    loss[safe_mask] = np.log(np.cosh(error[safe_mask]))
    
    # Calculate for large values using approximation
    loss[large_mask] = abs_error[large_mask] - np.log(2)
    
    return np.mean(loss)
