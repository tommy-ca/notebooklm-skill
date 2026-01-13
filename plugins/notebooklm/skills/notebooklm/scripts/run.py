#!/usr/bin/env python3
"""
Universal runner for NotebookLM skill scripts
Ensures all scripts run with the correct virtual environment
"""

import sys
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from skill_runner import SkillRunner

# Security: Whitelist of allowed scripts to prevent command injection
ALLOWED_SCRIPTS = {
    'ask_question.py',
    'notebook_manager.py',
    'session_manager.py',
    'auth_manager.py',
    'cleanup_manager.py'
}


def main():
    """Main runner"""
    if len(sys.argv) < 2:
        print("Usage: python run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print("  ask_question.py    - Query NotebookLM")
        print("  notebook_manager.py - Manage notebook library")
        print("  session_manager.py  - Manage sessions")
        print("  auth_manager.py     - Handle authentication")
        print("  cleanup_manager.py  - Clean up skill data")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    runner = SkillRunner("notebooklm", ALLOWED_SCRIPTS)
    sys.exit(runner.run(script_name, script_args))


if __name__ == "__main__":
    main()
