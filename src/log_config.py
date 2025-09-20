import os
import logging
import absl.logging
import warnings

def initialize_logging():
    """Initialize logging to suppress gRPC warnings."""
    # Remove any existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    # Configure basic logging
    logging.basicConfig(level=logging.WARNING)
    
    # Suppress specific warnings
    warnings.filterwarnings('ignore', category=Warning)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    # Initialize absl logging
    absl.logging.set_verbosity(absl.logging.ERROR)
    # Prevent absl from writing to stderr
    absl.logging.get_absl_handler().setLevel(absl.logging.ERROR)
    absl.logging.use_absl_handler()
    
    # Set GRPC logging to ERROR only
    logging.getLogger('grpc').setLevel(logging.ERROR)