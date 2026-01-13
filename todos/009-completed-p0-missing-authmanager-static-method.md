---
status: completed
priority: p0
issue_id: 009
tags: [agent-native, runtime-error, authentication, api-design]
dependencies: []
---

# Missing AuthManager.check_auth_status() Static Method

## Problem Statement

The youtube-research skill calls `AuthManager.check_auth_status()` as a static method, but this method does not exist in the AuthManager class. The code will crash with `AttributeError` when attempting to check authentication status.

**Why it matters**: This is a critical runtime bug that prevents the youtube-research skill from functioning at all. Every execution will fail immediately when checking authentication.

**Severity**: P0 - CRITICAL runtime error (blocks all usage)

## Findings

**File**: `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py`
**Line**: 230

**Source**: Agent-native reviewer

**Broken Code**:
```python
# Line 230 - CALLS undefined method
auth_check = AuthManager.check_auth_status()

if not auth_check["authenticated"]:
    print("\n❌ Not authenticated with Google!")
```

**Missing Implementation**:
The `AuthManager` class in `plugins/notebooklm/skills/notebooklm/scripts/auth_manager.py` has:
- `is_authenticated()` - instance method
- `get_auth_info()` - instance method
- `setup_auth()` - instance method

But does NOT have:
- `check_auth_status()` - static method ❌

## Proposed Solutions

### Solution 1: Add Static Method to AuthManager (Recommended)
**Pros**:
- Matches the calling code's expectations
- Provides clean static API for auth checks
- No changes needed in create_notebook.py

**Cons**: Slight duplication with get_auth_info()

**Effort**: Small (10 minutes)
**Risk**: Low

**Implementation**:
```python
# Add to auth_manager.py after line 285 (before main())
@staticmethod
def check_auth_status() -> Dict[str, Any]:
    """
    Static method to check authentication status without context.
    Used by other scripts to verify auth before operations.

    Returns:
        Dict with 'authenticated' bool and other auth info
    """
    auth = AuthManager()
    return auth.get_auth_info()
```

### Solution 2: Change create_notebook.py to Use Instance Method
**Pros**: Uses existing API
**Cons**: Requires creating AuthManager instance (less clean API)

**Effort**: Small
**Risk**: Low

**Implementation**:
```python
# Line 230 in create_notebook.py
auth = AuthManager()
auth_check = auth.get_auth_info()

if not auth_check["authenticated"]:
    print("\n❌ Not authenticated with Google!")
```

## Recommended Action

Implement **Solution 1** (add static method) because it provides a cleaner API and matches the design intent of the calling code.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/notebooklm/scripts/auth_manager.py` (needs new method after line 285)
- `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py` (line 230 calls the method)

**Error Message** (current code):
```
AttributeError: type object 'AuthManager' has no attribute 'check_auth_status'
```

**Agent-Native Impact**: Prevents agents from using youtube-research skill at all

## Acceptance Criteria

- [ ] Add `check_auth_status()` static method to AuthManager class
- [ ] Method returns dict with 'authenticated' key
- [ ] Test youtube-research skill can check auth status successfully
- [ ] Verify both authenticated and unauthenticated states work correctly

## Work Log

_No work completed yet_

## Resources

- Python @staticmethod decorator: https://docs.python.org/3/library/functions.html#staticmethod
- Type hints for Dict: https://docs.python.org/3/library/typing.html
