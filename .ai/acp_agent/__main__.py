"""Entry point: run as `python /path/to/acp_agent/__main__.py`"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from acp_agent.server import main  # noqa: E402

main()
