---
status: pending
priority: p0
issue_id: "014"
tags: ["code-review", "security", "authentication", "youtube-research", "bug"]
dependencies: []
---

# Incorrect Authentication File Path in check_auth_status()

## Problem Statement

The `AuthManager.check_auth_status()` static method looks for `auth_state.json` but the actual authentication state file is `state.json` (in a subdirectory). This causes the youtube-research skill to **always report authentication as failed**, even when properly authenticated.

**Severity**: P0 - Blocks youtube-research skill from detecting valid authentication, causing unnecessary re-authentication prompts and workflow disruption.

## Findings

**Incorrect implementation**: `plugins/notebooklm/skills/notebooklm/scripts/auth_manager.py:299`

```python
@staticmethod
def check_auth_status():
    """Static method to check authentication status without context."""
    from pathlib import Path
    import json

    # ❌ WRONG FILE PATH
    state_file = Path(__file__).parent.parent / "data" / "auth_state.json"

    if not state_file.exists():
        return {"authenticated": False}
```

**Actual state file location** (from `config.py:14`):
```python
STATE_FILE = BROWSER_STATE_DIR / "state.json"
# Expands to: ~/.claude/skills/notebooklm/data/browser_state/state.json
```

**Path discrepancies**:
1. ❌ Wrong directory: `data/auth_state.json` vs. `data/browser_state/state.json`
2. ❌ Wrong filename: `auth_state.json` vs. `state.json`
3. ❌ Hardcoded path instead of using config constant

**Impact on youtube-research skill**: `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py:210`

```python
auth_check = AuthManager.check_auth_status()
if not auth_check["authenticated"]:
    print("⚠️ Not authenticated. Please authenticate first using:")
    print("  python -m notebooklm.scripts.auth_manager setup")
    sys.exit(1)
```

**Result**: Users who ARE authenticated get told they're NOT, leading to:
- Confusion and workflow interruption
- Unnecessary re-authentication attempts
- Trust issues with the skill

## Proposed Solutions

### Solution 1: Fix Path to Use Config Constants (Recommended)

**Pros:**
- Uses centralized configuration (DRY principle)
- Aligns with rest of codebase
- Single source of truth for file paths
- Easy to maintain

**Cons:**
- Requires importing config module
- Static method becomes less self-contained

**Implementation**:
```python
@staticmethod
def check_auth_status():
    """
    Static method to check authentication status without context.
    Used by other scripts to verify auth before operations.

    Returns:
        Dict with 'authenticated' bool and other auth info
    """
    from config import STATE_FILE  # Import from centralized config
    import json

    if not STATE_FILE.exists():
        return {"authenticated": False}

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return {
                "authenticated": True,
                "cookies_count": len(state.get('cookies', [])),
                "has_storage": bool(state.get('origins', []))
            }
    except Exception:
        return {"authenticated": False}
```

**Effort**: Small (15 minutes)
**Risk**: Very low - aligns with existing patterns

---

### Solution 2: Remove Static Method, Use Instance Method Everywhere

**Pros:**
- Eliminates code duplication (`is_authenticated()` already exists)
- Cleaner architecture (single way to check auth)
- No import issues

**Cons:**
- Requires updating youtube-research skill
- Breaks current API contract
- More refactoring needed

**Implementation**:
```python
# Remove check_auth_status() entirely

# Update youtube-research/scripts/create_notebook.py:210
from auth_manager import AuthManager

auth = AuthManager()
if not auth.is_authenticated():
    print("Not authenticated...")
    sys.exit(1)
```

**Effort**: Medium (30 minutes + testing)
**Risk**: Low - well-defined change

---

### Solution 3: Quick Hardcoded Fix (Not Recommended)

**Pros:**
- Immediate fix without imports
- Minimal code change

**Cons:**
- Still hardcoded (violates DRY)
- Duplicates path logic from config.py
- Fragile if paths change in future

**Implementation**:
```python
@staticmethod
def check_auth_status():
    from pathlib import Path
    import json

    # Hardcoded correct path
    data_dir = Path.home() / ".claude" / "skills" / "notebooklm" / "data"
    state_file = data_dir / "browser_state" / "state.json"

    # ... rest of logic ...
```

**Effort**: Trivial (5 minutes)
**Risk**: Medium - creates technical debt

## Recommended Action

**Recommendation**: Solution 1 (Fix Path Using Config)

**Rationale**:
1. Aligns with codebase architecture (centralized config)
2. Low effort, low risk
3. Fixes the bug completely
4. Maintainable and clear

**Alternative**: If static method is rarely used, consider Solution 2 for cleaner architecture.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/notebooklm/scripts/auth_manager.py` (bug location)
- `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py` (caller)
- `plugins/notebooklm/skills/notebooklm/scripts/config.py` (correct path definition)

**Components**:
- Authentication management
- YouTube research skill integration
- Shared authentication between skills

**File Structure**:
```
~/.claude/skills/notebooklm/data/
├── library.json
├── auth_info.json
└── browser_state/
    ├── state.json           # ← ACTUAL FILE
    └── browser_profile/
```

**Database Changes**: None

**API Changes**: None (internal method fix)

## Acceptance Criteria

- [ ] `check_auth_status()` looks for correct file: `data/browser_state/state.json`
- [ ] youtube-research skill correctly detects authentication status
- [ ] Manual test: Authenticate once, verify both skills see auth status
- [ ] No hardcoded paths (uses config constants)
- [ ] Existing tests pass (if any)

## Work Log

### 2026-01-13 - Initial Discovery
- **Action**: Security audit identified incorrect file path
- **Agent**: security-sentinel, architecture-strategist
- **Root cause**: Static method added without referencing config.py
- **Impact**: youtube-research authentication checks always fail
- **Decision**: Created P0 todo for immediate fix

### Evidence from Security Review
```
FINDING H-1 Excerpt:
The static method check_auth_status() at line 287-313 has a hardcoded
path that differs from config.STATE_FILE. File is named `auth_state.json`
but config uses `state.json` (naming inconsistency).
```

## Resources

**Related Issues**:
- Part of larger authentication sharing architecture between skills
- Related to cross-skill dependency patterns

**Documentation**:
- `AUTHENTICATION.md` in notebooklm skill
- v2.1.0 changelog: "Shares authentication with main notebooklm skill"

**Similar Patterns**:
- Instance method `is_authenticated()` does this correctly
- Uses config.STATE_FILE properly
- Should consolidate to single pattern

**Historical Context**:
- Static method added for youtube-research skill convenience
- Allows checking auth without instantiating AuthManager
- But implemented with incorrect path assumptions
