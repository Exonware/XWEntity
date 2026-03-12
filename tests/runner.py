#!/usr/bin/env python3
"""
#exonware/xwentity/tests/runner.py
Main test runner for xwentity
Orchestrates all test layers with hierarchical execution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
Usage:
  python tests/runner.py                # Run all tests
  python tests/runner.py --core         # Run only core tests
  python tests/runner.py --unit         # Run only unit tests
  python tests/runner.py --integration  # Run only integration tests
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
# Configure UTF-8 encoding for Windows console
from exonware.xwsystem.console.cli import ensure_utf8_console
ensure_utf8_console()
# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def run_sub_runner(runner_path: Path, description: str) -> int:
    """Run a sub-runner and return exit code."""
    print(f"\n{'='*80}")
    print(f"🚀 {description}")
    print(f"{'='*80}\n")
    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=runner_path.parent,
        capture_output=False,
        text=True
    )
    status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
    print(f"\n{status}\n")
    return result.returncode


def main():
    """Main test runner function."""
    test_dir = Path(__file__).parent
    reports_dir = test_dir.parent / "docs" / "tests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Parse arguments
    args = sys.argv[1:]
    # Define sub-runners
    core_runner = test_dir / "0.core" / "runner.py"
    unit_runner = test_dir / "1.unit" / "runner.py"
    integration_runner = test_dir / "2.integration" / "runner.py"
    exit_codes = []
    # Determine which tests to run
    if "--core" in args:
        if core_runner.exists():
            exit_codes.append(run_sub_runner(core_runner, "Layer 0: Core Tests"))
    elif "--unit" in args:
        if unit_runner.exists():
            exit_codes.append(run_sub_runner(unit_runner, "Layer 1: Unit Tests"))
    elif "--integration" in args:
        if integration_runner.exists():
            exit_codes.append(run_sub_runner(integration_runner, "Layer 2: Integration Tests"))
    else:
        # Run all tests in sequence
        print("\n🚀 Running: ALL Tests")
        print(" Layers: 0.core ✅ 1.unit ✅ 2.integration\n")
        # Core tests
        if core_runner.exists():
            exit_codes.append(run_sub_runner(core_runner, "Layer 0: Core Tests"))
        # Unit tests
        if unit_runner.exists():
            exit_codes.append(run_sub_runner(unit_runner, "Layer 1: Unit Tests"))
        # Integration tests
        if integration_runner.exists():
            exit_codes.append(run_sub_runner(integration_runner, "Layer 2: Integration Tests"))
    # Print summary
    print(f"\n{'='*80}")
    print("📈 TEST EXECUTION SUMMARY")
    print(f"{'='*80}")
    total_runs = len(exit_codes)
    passed = sum(1 for code in exit_codes if code == 0)
    failed = total_runs - passed
    print(f"Total Layers: {total_runs}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    # Final status
    if all(code == 0 for code in exit_codes):
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)
if __name__ == "__main__":
    main()
