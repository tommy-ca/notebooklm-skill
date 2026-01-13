---
status: pending
priority: p1
issue_id: "016"
tags: ["code-review", "architecture", "dependency-management", "youtube-research"]
dependencies: []
---

# Cross-Skill Dependency via Path Manipulation

## Problem Statement

The youtube-research skill directly imports browser utilities and authentication from the notebooklm skill using **filesystem path traversal**. This creates tight coupling between skills, violates architectural principles, and makes the youtube-research skill non-portable.

**Severity**: P1 - Violates Dependency Inversion Principle, creates fragile architecture, blocks independent skill deployment.

## Findings

**Violation location**: `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py:19-22`

```python
# ❌ VIOLATES ARCHITECTURE - Direct cross-skill dependency
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "notebooklm" / "scripts"))
from browser_utils import BrowserFactory, StealthUtils
from auth_manager import AuthManager
```

**Path traversal breakdown**:
```
create_notebook.py location:
  plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py

Path manipulation:
  .parent         → youtube-research/scripts/
  .parent.parent  → youtube-research/
  .parent³        → skills/
  / "notebooklm"  → skills/notebooklm/
  / "scripts"     → skills/notebooklm/scripts/
```

**Architecture violations**:

1. **Violates Dependency Inversion Principle**:
   - youtube-research depends on concrete notebooklm implementation
   - Should depend on shared abstractions instead

2. **Creates Hidden Dependencies**:
   - Not visible in requirements.txt
   - No explicit dependency declaration
   - Breaks skill portability

3. **Fragile Coupling**:
   - Breaks if notebooklm directory is renamed
   - Breaks if directory structure changes
   - Breaks if notebooklm skill is removed

4. **Violates Single Responsibility**:
   - Skills should be self-contained or use shared infrastructure
   - Not depend on other skills' internal implementation

**Historical context** (from recent commits):
- Previously used **symlinks** for sharing code
- Removed for security reasons (symlink path traversal vulnerability - P2 issue #005)
- Replaced with direct imports, but didn't move code to proper shared location

**Evidence from architecture review**:
> "Tight coupling between skills via filesystem path traversal. Violates Dependency Inversion Principle (depends on concrete skill location). Creates hidden dependencies not visible in requirements.txt."

## Proposed Solutions

### Solution 1: Move Shared Code to shared/ Module (Recommended)

**Pros:**
- Aligns with existing architecture (`skill_runner.py` already in shared/)
- Single source of truth for common utilities
- Clear architectural boundary
- Both skills import from same location
- Eliminates cross-skill dependencies

**Cons:**
- Requires moving 3 files
- Need to update imports in both skills

**Implementation**:

**Step 1: Move files to shared/**
```bash
# Create shared module structure
mkdir -p plugins/notebooklm/shared/

# Move shared utilities
mv plugins/notebooklm/skills/notebooklm/scripts/browser_utils.py \
   plugins/notebooklm/shared/browser_utils.py

mv plugins/notebooklm/skills/notebooklm/scripts/auth_manager.py \
   plugins/notebooklm/shared/auth_manager.py

mv plugins/notebooklm/skills/notebooklm/scripts/setup_environment.py \
   plugins/notebooklm/shared/setup_environment.py

# Update shared/__init__.py
cat > plugins/notebooklm/shared/__init__.py << 'EOF'
"""Shared utilities for NotebookLM plugin skills"""

from .browser_utils import BrowserFactory, StealthUtils
from .auth_manager import AuthManager
from .setup_environment import SetupEnvironment

__all__ = [
    'BrowserFactory',
    'StealthUtils',
    'AuthManager',
    'SetupEnvironment',
]
EOF
```

**Step 2: Update imports in notebooklm skill**
```python
# All scripts in notebooklm/scripts/*.py
import sys
from pathlib import Path

# Import from shared module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
from browser_utils import BrowserFactory, StealthUtils
from auth_manager import AuthManager
```

**Step 3: Update imports in youtube-research skill**
```python
# youtube-research/scripts/create_notebook.py
import sys
from pathlib import Path

# Import from shared module (same pattern as notebooklm)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
from browser_utils import BrowserFactory, StealthUtils
from auth_manager import AuthManager
```

**Step 4: Update config.py imports**
Both skills' config.py files should import shared paths:
```python
# Both config files can import from shared if needed
# Or keep DATA_DIR definitions local (skill-specific)
```

**Effort**: Medium (2-3 hours including testing)
**Risk**: Low - well-defined refactoring with clear rollback path

---

### Solution 2: Create Shared Configuration Module

**Combines with Solution 1** to also extract duplicate configuration:

```python
# shared/config.py - Common configuration
from pathlib import Path

# Shared data directory (backward compatible)
DATA_DIR = Path.home() / ".claude" / "skills" / "notebooklm" / "data"
BROWSER_STATE_DIR = DATA_DIR / "browser_state"
BROWSER_PROFILE_DIR = BROWSER_STATE_DIR / "browser_profile"
STATE_FILE = BROWSER_STATE_DIR / "state.json"
AUTH_INFO_FILE = DATA_DIR / "auth_info.json"
LIBRARY_FILE = DATA_DIR / "library.json"

# Browser configuration
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--no-first-run',
    '--no-default-browser-check'
]
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
PAGE_LOAD_TIMEOUT = 30000

# Authentication
LOGIN_TIMEOUT_MINUTES = 10
```

**Then skill-specific configs import and extend**:
```python
# notebooklm/scripts/config.py
from shared.config import *  # Import all shared config

# NotebookLM-specific
QUERY_INPUT_SELECTORS = [...]
RESPONSE_SELECTORS = [...]
QUERY_TIMEOUT_SECONDS = 120

# youtube-research/scripts/config.py
from shared.config import *  # Import all shared config

# YouTube-specific
NEW_NOTEBOOK_BUTTON = "button:has-text('New notebook')"
YOUTUBE_URL_INPUT = "textarea[placeholder='Paste any links']"
```

**Effort**: Additional 1 hour
**Risk**: Very low - pure configuration refactoring

---

### Solution 3: Package as Installable Module (Future-Proof)

**Pros:**
- Most professional approach
- Enables `pip install` workflow
- Proper dependency management
- Works with any skill location

**Cons:**
- Significant refactoring
- Overkill for current 2-skill plugin
- Requires packaging expertise

**Implementation**:
```python
# setup.py or pyproject.toml
[project]
name = "notebooklm-shared"
version = "2.1.0"

# Then skills can:
# pip install -e plugins/notebooklm/shared/
# from notebooklm_shared import BrowserFactory
```

**Effort**: Large (8+ hours)
**Risk**: Medium - significant architectural change

## Recommended Action

**Recommendation**: Solution 1 + Solution 2 (Move to shared/ + Extract Config)

**Rationale**:
1. Aligns with existing `skill_runner.py` pattern
2. Eliminates cross-skill dependencies
3. Creates single source of truth
4. Low risk, clear migration path
5. Fixes configuration duplication at same time
6. Total effort: 3-4 hours for complete solution

**Implementation Order**:
1. Create `shared/config.py` with common constants (30 min)
2. Move `browser_utils.py` to `shared/` (30 min)
3. Move `auth_manager.py` to `shared/` (30 min)
4. Move `setup_environment.py` to `shared/` (30 min)
5. Update imports in notebooklm skill (45 min)
6. Update imports in youtube-research skill (30 min)
7. Test both skills thoroughly (30 min)
8. Update documentation (15 min)

## Technical Details

**Current Directory Structure**:
```
plugins/notebooklm/
├── shared/
│   ├── skill_runner.py       # ✅ Already shared
│   └── __init__.py
└── skills/
    ├── notebooklm/
    │   └── scripts/
    │       ├── browser_utils.py    # ← Should be shared
    │       ├── auth_manager.py     # ← Should be shared
    │       └── setup_environment.py # ← Should be shared
    └── youtube-research/
        └── scripts/
            └── create_notebook.py  # ❌ Imports from notebooklm
```

**Target Directory Structure**:
```
plugins/notebooklm/
├── shared/
│   ├── __init__.py
│   ├── skill_runner.py       # ✅ Already here
│   ├── browser_utils.py      # ← Move here
│   ├── auth_manager.py       # ← Move here
│   ├── setup_environment.py  # ← Move here
│   └── config.py             # ← Create here
└── skills/
    ├── notebooklm/
    │   └── scripts/
    │       ├── config.py     # Skill-specific config only
    │       └── ...
    └── youtube-research/
        └── scripts/
            ├── config.py     # Skill-specific config only
            └── ...
```

**Files to modify**:
- `shared/` - Add 4 files
- `notebooklm/scripts/` - Update imports in 8 files
- `youtube-research/scripts/` - Update imports in 3 files
- Total: 15 files touched

**Affected Components**:
- Browser automation layer
- Authentication system
- Environment setup
- Configuration management
- Both skills' import statements

**Database Changes**: None

**API Changes**: None (internal refactoring)

## Acceptance Criteria

- [ ] `browser_utils.py`, `auth_manager.py`, `setup_environment.py` in `shared/`
- [ ] Both skills import from `shared/` module
- [ ] No cross-skill imports (youtube-research → notebooklm)
- [ ] Shared configuration in `shared/config.py`
- [ ] Skill-specific config files only contain skill-specific constants
- [ ] Both skills function correctly after refactoring
- [ ] All tests pass
- [ ] Documentation updated to reflect new structure

## Work Log

### 2026-01-13 - Initial Discovery
- **Action**: Comprehensive architecture review
- **Agent**: architecture-strategist, pattern-recognition-specialist
- **Finding**: Cross-skill dependency via path manipulation
- **Root cause**: Symlink removal without proper code organization
- **Impact**: Violates architectural principles, fragile coupling
- **Decision**: Move shared code to proper location

### Historical Context
- **v2.0.0**: Removed symlinks for security (path traversal risk)
- **Current**: Replaced with direct imports instead of proper shared module
- **Next**: Complete the refactoring by moving to shared/

## Resources

**Related Issues**:
- Todo #015: Configuration duplication (solved by shared/config.py)
- Original P2 issue #005: Symlink path traversal security risk
- Architecture principle: Dependency Inversion

**Documentation**:
- SOLID Principles: https://en.wikipedia.org/wiki/SOLID
- Python packaging guide: https://packaging.python.org/
- Plugin architecture best practices

**Similar Patterns**:
- `skill_runner.py` already demonstrates the shared module pattern
- Just needs to be extended to include utilities

**Testing Strategy**:
1. Unit test each shared module independently
2. Integration test: notebooklm authentication flow
3. Integration test: youtube-research notebook creation
4. Verify both skills work after refactoring
5. Check import statements resolve correctly
