#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/runner.py
Core test runner for xwentity
Auto-discovers and runs core tests with colored output and Markdown logging.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

import sys
from pathlib import Path
# Configure UTF-8 encoding for Windows console
from exonware.xwsystem.console.cli import ensure_utf8_console
ensure_utf8_console()
# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
from exonware.xwsystem.utils.test_runner import TestRunner
if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwentity",
        layer_name="0.core",
        description="Core Tests - Fast, High-Value Checks (20% tests for 80% value)",
        test_dir=Path(__file__).parent,
        markers=["xwentity_core"]
    )
    sys.exit(runner.run())
