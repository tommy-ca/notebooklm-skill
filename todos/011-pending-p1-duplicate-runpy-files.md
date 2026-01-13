---
status: pending
priority: p1
issue_id: 011
tags: [architecture, code-duplication, maintainability]
dependencies: []
---

# Massive Code Duplication - Two Identical run.py Files

## Problem Statement

The `run.py` files in both `notebooklm` and `youtube-research` skills are 95% identical (111 of 123 lines), with only the `ALLOWED_SCRIPTS` whitelist differing. This violates the DRY principle and creates significant maintenance burden.

**Why it matters**: Any bug fix or improvement to the runner logic must be manually replicated across both files. This has already led to inconsistencies (missing trailing newline in youtube-research/run.py). As more skills are added, this duplication will multiply.

**Severity**: P1 - Critical technical debt that will worsen with scale

## Findings

**Files**:
- `plugins/notebooklm/skills/notebooklm/scripts/run.py` (123 lines)
- `plugins/notebooklm/skills/youtube-research/scripts/run.py` (117 lines)

**Source**: Pattern recognition specialist + Code simplicity reviewer + Architecture strategist

**Duplication**: ~95% identical code (111/123 lines)

**Only Differences**:
```python
# notebooklm/run.py
ALLOWED_SCRIPTS = {
    'ask_question.py',
    'notebook_manager.py',
    'session_manager.py',
    'auth_manager.py',
    'cleanup_manager.py'
}

# youtube-research/run.py
ALLOWED_SCRIPTS = {
    'create_notebook.py',
    'auth_manager.py'
}
```

**Evidence of Drift**:
- youtube-research/run.py missing trailing newline (fixed in notebooklm/run.py)
- Identical venv management logic duplicated
- Identical path validation logic duplicated
- Identical error messages duplicated

## Proposed Solutions

### Solution 1: Create Shared Runner Module (Recommended)
**Pros**:
- Eliminates all duplication
- Single point of maintenance
- Consistent behavior across skills
- Easy to add new skills

**Cons**: Requires creating shared module structure

**Effort**: Medium (2-3 hours)
**Risk**: Low

**Implementation**:
```python
# plugins/notebooklm/shared_lib/skill_runner.py
from pathlib import Path
from typing import Set
import subprocess
import sys

class SkillRunner:
    def __init__(self, skill_name: str, allowed_scripts: Set[str]):
        self.skill_name = skill_name
        self.allowed_scripts = allowed_scripts
        self.skill_dir = Path(__file__).parent.parent / "skills" / skill_name

    def get_venv_python(self) -> Path:
        """Get virtual environment Python executable"""
        # ... common logic ...

    def ensure_venv(self) -> Path:
        """Ensure virtual environment exists"""
        # ... common logic ...

    def validate_script(self, script_name: str) -> Path:
        """Validate and resolve script path"""
        # ... whitelist + path traversal checks ...

    def run(self, script_name: str, args: list) -> int:
        """Execute script in venv"""
        venv_python = self.ensure_venv()
        script_path = self.validate_script(script_name)

        cmd = [str(venv_python), str(script_path)] + args
        result = subprocess.run(cmd)
        return result.returncode

# notebooklm/scripts/run.py (simplified to 10 lines)
from shared_lib.skill_runner import SkillRunner

ALLOWED_SCRIPTS = {'ask_question.py', 'notebook_manager.py', ...}
runner = SkillRunner("notebooklm", ALLOWED_SCRIPTS)
sys.exit(runner.run(sys.argv[1], sys.argv[2:]))

# youtube-research/scripts/run.py (simplified to 10 lines)
from shared_lib.skill_runner import SkillRunner

ALLOWED_SCRIPTS = {'create_notebook.py', 'auth_manager.py'}
runner = SkillRunner("youtube-research", ALLOWED_SCRIPTS)
sys.exit(runner.run(sys.argv[1], sys.argv[2:]))
```

### Solution 2: Use Configuration File
**Pros**: Keep run.py, externalize allowed scripts
**Cons**: Still duplicates all runner logic

**Effort**: Small
**Risk**: Low

### Solution 3: Symlink run.py
**Pros**: Zero duplication
**Cons**: Can't specify different ALLOWED_SCRIPTS per skill

**Effort**: Small
**Risk**: Medium (same symlink issues as other files)

## Recommended Action

Implement **Solution 1** (shared runner module) as part of larger architectural cleanup. This sets foundation for future skills to be added in 10 lines instead of 120.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/notebooklm/scripts/run.py` (123 lines)
- `plugins/notebooklm/skills/youtube-research/scripts/run.py` (117 lines)

**LOC Reduction**: ~220 lines → ~20 lines + ~100 line shared module = net -100 lines

**Future Impact**: Every new skill adds 120 lines of duplication (current) vs 10 lines (with shared runner)

## Acceptance Criteria

- [ ] Create `plugins/notebooklm/shared_lib/skill_runner.py`
- [ ] Migrate common venv logic to SkillRunner class
- [ ] Migrate validation logic to SkillRunner class
- [ ] Update both run.py files to use SkillRunner
- [ ] Verify both skills work identically after refactoring
- [ ] Add unit tests for SkillRunner class

## Work Log

_No work completed yet_

## Resources

- DRY Principle: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
- Pattern recognition specialist findings (code duplication section)
- Architecture strategist findings (recommendation #3: "Unify Runner Scripts")
