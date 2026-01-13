#!/usr/bin/env python3
"""
Shared Skill Runner
Eliminates code duplication across skill run.py files
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Set


class SkillRunner:
    """Universal runner for skill scripts with venv management and security validation"""

    def __init__(self, skill_name: str, allowed_scripts: Set[str]):
        """
        Initialize skill runner

        Args:
            skill_name: Name of the skill (e.g., 'notebooklm', 'youtube-research')
            allowed_scripts: Set of allowed script names (security whitelist)
        """
        self.skill_name = skill_name
        self.allowed_scripts = allowed_scripts
        self.skill_dir = Path(__file__).parent.parent / "skills" / skill_name

    def get_venv_python(self) -> Path:
        """Get the virtual environment Python executable"""
        venv_dir = self.skill_dir / ".venv"

        if os.name == 'nt':  # Windows
            venv_python = venv_dir / "Scripts" / "python.exe"
        else:  # Unix/Linux/Mac
            venv_python = venv_dir / "bin" / "python"

        return venv_python

    def ensure_venv(self) -> Path:
        """Ensure virtual environment exists"""
        venv_dir = self.skill_dir / ".venv"
        setup_script = self.skill_dir / "scripts" / "setup_environment.py"

        # Check if venv exists
        if not venv_dir.exists():
            print("🔧 First-time setup: Creating virtual environment...")
            print("   This may take a minute...")

            # Run setup with system Python
            result = subprocess.run([sys.executable, str(setup_script)])
            if result.returncode != 0:
                print("❌ Failed to set up environment")
                sys.exit(1)

            print("✅ Environment ready!")

        return self.get_venv_python()

    def validate_script(self, script_name: str) -> Path:
        """
        Validate and resolve script path

        Args:
            script_name: Script name to validate

        Returns:
            Resolved script path

        Raises:
            SystemExit: If validation fails
        """
        # Handle both "scripts/script.py" and "script.py" formats
        if script_name.startswith('scripts/'):
            # Remove the scripts/ prefix if provided
            script_name = script_name[8:]  # len('scripts/') = 8

        # Ensure .py extension
        if not script_name.endswith('.py'):
            script_name += '.py'

        # Security: Validate script name against whitelist
        if script_name not in self.allowed_scripts:
            print(f"❌ Invalid script: {script_name}")
            print(f"   Allowed: {', '.join(sorted(self.allowed_scripts))}")
            sys.exit(1)

        # Get script path
        script_path = (self.skill_dir / "scripts" / script_name).resolve()
        scripts_dir = (self.skill_dir / "scripts").resolve()

        # Security: Verify path is within scripts directory (prevent path traversal)
        if not str(script_path).startswith(str(scripts_dir)):
            print("❌ Security violation: Path traversal detected")
            sys.exit(1)

        if not script_path.exists():
            print(f"❌ Script not found: {script_name}")
            print(f"   Working directory: {Path.cwd()}")
            print(f"   Skill directory: {self.skill_dir}")
            print(f"   Looked for: {script_path}")
            sys.exit(1)

        return script_path

    def run(self, script_name: str, script_args: list) -> int:
        """
        Execute script in venv

        Args:
            script_name: Script to run
            script_args: Arguments to pass to script

        Returns:
            Exit code from script
        """
        # Validate script and get path
        script_path = self.validate_script(script_name)

        # Ensure venv exists and get Python executable
        venv_python = self.ensure_venv()

        # Build command
        cmd = [str(venv_python), str(script_path)] + script_args

        # Run the script
        try:
            result = subprocess.run(cmd)
            return result.returncode
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            return 130
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
