---
status: completed
priority: p1
issue_id: "015"
tags: ["code-review", "python", "type-safety", "code-quality"]
dependencies: []
---

# Missing Type Hints Throughout Codebase

## Problem Statement

**Every Python file** in the NotebookLM skill lacks proper type annotations. Modern Python 3.10+ requires type hints for maintainability, IDE support, and catching bugs before runtime. The absence of type hints makes the codebase harder to maintain, prevents static analysis, and increases bug risk.

**Severity**: P1 - High priority for code quality and long-term maintainability, but not immediately blocking.

## Findings

**Scope of issue**: All 15+ Python modules lack type hints

**Examples from key files**:

1. **skill_runner.py:106** (most critical shared code):
```python
# ❌ CURRENT - No type hints
def run(self, script_name: str, script_args: list) -> int:
    pass

# ✅ SHOULD BE
def run(self, script_name: str, script_args: list[str]) -> int:
    pass
```

2. **browser_utils.py:68-89**:
```python
# ❌ CURRENT
@staticmethod
def human_type(page, selector, text, wpm_min=320, wpm_max=480):
    pass

# ✅ SHOULD BE
from patchright.sync_api import Page

@staticmethod
def human_type(
    page: Page,
    selector: str,
    text: str,
    wpm_min: int = 320,
    wpm_max: int = 480
) -> None:
    pass
```

3. **notebook_manager.py:63-72**:
```python
# ❌ CURRENT
def add_notebook(
    self,
    url: str,
    name: str,
    description: str,
    topics: List[str],
    content_types: Optional[List[str]] = None,
    use_cases: Optional[List[str]] = None,
    tags: Optional[List[str]] = None
):  # Missing return type annotation

# ✅ SHOULD BE
def add_notebook(
    self,
    url: str,
    name: str,
    description: str,
    topics: list[str],
    content_types: Optional[list[str]] = None,
    use_cases: Optional[list[str]] = None,
    tags: Optional[list[str]] = None
) -> dict[str, Any]:  # Added return type
    pass
```

**Impact**:
- IDEs cannot provide accurate autocomplete
- Type checkers (mypy, pyright) cannot catch bugs
- Harder to onboard new contributors
- Refactoring becomes error-prone
- No compile-time safety

**Evidence from Python reviewer**:
> "Modern Python 3.10+ requires type hints for maintainability. IDEs can't provide autocomplete, type checkers can't catch bugs."

## Proposed Solutions

### Solution 1: Phased Type Hint Addition (Recommended)

**Pros:**
- Incremental progress
- Low risk of breaking changes
- Can prioritize high-impact files first
- Easier to review

**Cons:**
- Takes longer to complete
- Codebase temporarily inconsistent

**Implementation Plan**:

**Phase 1 - Shared Infrastructure (Week 1)**:
1. `shared/skill_runner.py` - Most reused module
2. `shared/browser_utils.py` (when moved to shared)
3. `shared/auth_manager.py` (when moved to shared)
4. `shared/config.py` (when created)

**Phase 2 - Core Modules (Week 2)**:
5. `scripts/notebook_manager.py` - Public API
6. `scripts/ask_question.py` - Main functionality
7. `scripts/auth_manager.py` - Authentication

**Phase 3 - Supporting Modules (Week 3)**:
8. `scripts/browser_session.py`
9. `scripts/cleanup_manager.py`
10. `scripts/create_notebook.py` (youtube-research)

**Effort per file**: 30-60 minutes
**Total effort**: 10-15 hours across 3 weeks
**Risk**: Very low - type hints are backward compatible

---

### Solution 2: Add Stub Files (.pyi) First

**Pros:**
- Faster to implement
- Provides type safety without modifying source
- Can be auto-generated with tools

**Cons:**
- Maintains duplicate files
- Out-of-sync risk
- Less readable than inline hints

**Implementation**:
```bash
# Generate stub files
pip install mypy
stubgen plugins/notebooklm/skills/notebooklm/scripts/*.py -o stubs/
```

**Effort**: Small (2-3 hours)
**Risk**: Low

---

### Solution 3: Use Type Checking Tool to Auto-Generate

**Pros:**
- Automated approach
- Consistent style
- Fast initial pass

**Cons:**
- Auto-generated hints may be imprecise
- Requires manual review and refinement
- Tools like MonkeyType need runtime execution

**Implementation**:
```bash
# Install MonkeyType
pip install MonkeyType

# Run tests to collect type information
monkeytype run -m pytest

# Apply collected types
monkeytype apply plugins.notebooklm.skills.notebooklm.scripts.ask_question
```

**Effort**: Medium (5-8 hours including review)
**Risk**: Medium - requires thorough review

## Recommended Action

**Recommendation**: Solution 1 (Phased Type Hint Addition)

**Rationale**:
1. Most sustainable long-term approach
2. High-quality, manually reviewed annotations
3. Incremental progress reduces risk
4. Aligns with refactoring work (moving to shared/)

**Immediate First Step** (2 hours):
Add type hints to `skill_runner.py` since it's shared infrastructure:

```python
from pathlib import Path
from typing import Optional
import sys
import subprocess

class SkillRunner:
    def __init__(self, skill_name: str, allowed_scripts: set[str]) -> None:
        self.skill_name: str = skill_name
        self.allowed_scripts: set[str] = allowed_scripts
        self.skill_dir: Path = Path(__file__).parent.parent / "skills" / skill_name
        self.venv_dir: Path = self.skill_dir / ".venv"
        self.requirements_file: Path = self.skill_dir / "requirements.txt"

    def run(self, script_name: str, script_args: list[str]) -> int:
        """
        Execute a whitelisted script in the skill's virtual environment

        Args:
            script_name: Name of script to execute (must be in ALLOWED_SCRIPTS)
            script_args: Command-line arguments to pass to script

        Returns:
            Exit code from subprocess (0 = success)
        """
        # Implementation...
        pass
```

## Technical Details

**Required imports** (add to files):
```python
from typing import Optional, Any, Union
from pathlib import Path
from patchright.sync_api import Page, BrowserContext, Playwright
```

**Modern Python 3.10+ syntax**:
```python
# Use built-in generics (no typing.List needed)
def foo(items: list[str]) -> dict[str, int]:
    pass

# Use Union with | operator
def bar(value: str | int) -> None:
    pass

# Use Optional or explicit None union
def baz(config: dict[str, Any] | None = None) -> bool:
    pass
```

**Components requiring most attention**:
- Browser automation (Page, BrowserContext types)
- Dict return types (add TypedDict for structured dicts)
- Optional parameters
- List/Dict generics

**Affected Files**: All 15 Python modules

**Database Changes**: None

**API Changes**: None (type hints are annotations only, no runtime effect)

## Acceptance Criteria

- [ ] All public functions have parameter and return type hints
- [ ] All class attributes have type annotations
- [ ] Import statements include necessary typing imports
- [ ] mypy passes with no errors: `mypy plugins/notebooklm/ --strict`
- [ ] pyright/pylance provide accurate autocomplete in VSCode
- [ ] CI/CD includes type checking step

## Work Log

### 2026-01-13 - Initial Discovery
- **Action**: Comprehensive Python code review
- **Agent**: kieran-python-reviewer
- **Findings**: Zero files have complete type coverage
- **Impact**: Reduces code quality and maintainability
- **Recommendation**: Phased implementation starting with shared modules

## Resources

**Documentation**:
- Python typing docs: https://docs.python.org/3/library/typing.html
- mypy documentation: https://mypy.readthedocs.io/
- Playwright Python types: https://playwright.dev/python/docs/api/class-page

**Tools**:
- mypy: Static type checker
- pyright: Microsoft's fast type checker
- MonkeyType: Runtime type collector
- stubgen: Stub file generator

**Style Guides**:
- PEP 484: Type Hints
- PEP 526: Syntax for Variable Annotations
- PEP 585: Type Hinting Generics In Standard Collections (Python 3.9+)

**Example Reference**:
Look at well-typed Python projects:
- FastAPI source code (excellent type coverage)
- Pydantic models (TypedDict patterns)

**Integration with CI/CD**:
```yaml
# .github/workflows/type-check.yml
name: Type Check
on: [push, pull_request]
jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install mypy
      - run: mypy plugins/notebooklm/ --strict
```
