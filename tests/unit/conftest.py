import sys
from unittest.mock import MagicMock

# Mock magic to avoid ImportError: failed to find libmagic
sys.modules["magic"] = MagicMock()
