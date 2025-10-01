#!/usr/bin/env python
"""Check for outdated dependencies and security vulnerabilities"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"{'=' * 60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("Dependency Security and Update Check")
    print("=" * 60)

    checks = [
        (
            "pip list --outdated",
            "Checking for outdated packages..."
        ),
        (
            "pip check",
            "Checking for package compatibility issues..."
        ),
    ]

    # Try to run safety check if available
    try:
        subprocess.run(["safety", "--version"], 
                      capture_output=True, check=True)
        checks.append((
            "safety check --file requirements.txt --json",
            "Running security vulnerability scan..."
        ))
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nNote: 'safety' not installed. Install with: pip install safety")
        print("      To scan for security vulnerabilities.")

    all_passed = True
    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ Dependency check completed")
    else:
        print("⚠ Some checks had issues - please review above")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
