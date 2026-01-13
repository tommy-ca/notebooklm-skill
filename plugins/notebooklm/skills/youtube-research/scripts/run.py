#!/usr/bin/env python3
"""
Universal runner for YouTube Research skill scripts
Ensures all scripts run with the correct virtual environment
"""

import sys
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from skill_runner import SkillRunner

# Security: Whitelist of allowed scripts to prevent command injection
ALLOWED_SCRIPTS = {
    'create_notebook.py',
    'auth_manager.py'
}


def main():
    """Main runner"""
    if len(sys.argv) < 2:
        print("Usage: python run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print("  create_notebook.py  - Create notebook from YouTube video")
        print("  auth_manager.py     - Handle authentication (shared)")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    runner = SkillRunner("youtube-research", ALLOWED_SCRIPTS)
    sys.exit(runner.run(script_name, script_args))


if __name__ == "__main__":
    main()
