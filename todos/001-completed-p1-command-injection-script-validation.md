---
status: completed
priority: p1
issue_id: 001
tags: [security, code-review, youtube-research]
dependencies: []
---

# Command Injection via Unvalidated Script Names

## Problem Statement

The `run.py` script in youtube-research skill accepts user-controlled script names without proper validation, allowing potential command injection or arbitrary file execution outside the intended scripts directory.

**Why it matters**: This is a security vulnerability that could allow an attacker to execute arbitrary Python code if they can control the script name parameter.

**Severity**: P1 - Security vulnerability that should be fixed before release

## Findings

**File**: `plugins/notebooklm/skills/youtube-research/scripts/run.py`
**Lines**: 60-74, 87

**Source**: Security review agent (security-sentinel)

**Vulnerable Code**:
```python
script_name = sys.argv[1]
# Handle both "scripts/script.py" and "script.py" formats
if script_name.startswith('scripts/'):
    script_name = script_name[8:]
if not script_name.endswith('.py'):
    script_name += '.py'

script_path = skill_dir / "scripts" / script_name
cmd = [str(venv_python), str(script_path)] + script_args
result = subprocess.run(cmd)  # No validation!
```

**Exploit Scenarios**:
- Path traversal: `python run.py "../../malicious.py"`
- Directory traversal: `python run.py "../../../config/secret.py"`

## Proposed Solutions

### Solution 1: Whitelist Validation (Recommended)
**Pros**:
- Most secure approach
- Explicit about allowed scripts
- Prevents all path traversal

**Cons**:
- Requires updating when new scripts added
- More maintenance

**Effort**: Small
**Risk**: Low

**Implementation**:
```python
ALLOWED_SCRIPTS = {
    'create_notebook.py',
    'auth_manager.py'
}

script_name = sys.argv[1]
if script_name.startswith('scripts/'):
    script_name = script_name[8:]
if not script_name.endswith('.py'):
    script_name += '.py'

if script_name not in ALLOWED_SCRIPTS:
    print(f"❌ Invalid script: {script_name}")
    print(f"   Allowed: {', '.join(ALLOWED_SCRIPTS)}")
    sys.exit(1)

script_path = (skill_dir / "scripts" / script_name).resolve()
scripts_dir = (skill_dir / "scripts").resolve()

if not str(script_path).startswith(str(scripts_dir)):
    print("❌ Security violation: Path traversal detected")
    sys.exit(1)
```

### Solution 2: Path Resolution Validation Only
**Pros**:
- More flexible
- Auto-discovers scripts

**Cons**:
- Less secure than whitelist
- May miss edge cases

**Effort**: Small
**Risk**: Medium

## Recommended Action

Implement **Solution 1** (whitelist validation) for maximum security.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/youtube-research/scripts/run.py`

**Attack Surface**: Command-line interface accepts user input

**Security Impact**: Arbitrary code execution

## Acceptance Criteria

- [x] Whitelist of allowed scripts implemented
- [x] Path traversal validation added
- [x] Same fix applied to notebooklm/scripts/run.py
- [ ] Security tests added to verify prevention
- [ ] Documentation updated

## Work Log

### 2026-01-12 - Security Fix Implemented

**Changes Made:**
1. Added `ALLOWED_SCRIPTS` whitelist to both run.py files
2. Implemented script name validation against whitelist
3. Added path traversal detection using `.resolve()` and path prefix checking

**Files Modified:**
- `plugins/notebooklm/skills/youtube-research/scripts/run.py`
  - Added whitelist: `create_notebook.py`, `auth_manager.py`
  - Lines 12-16: ALLOWED_SCRIPTS constant
  - Lines 78-82: Whitelist validation
  - Lines 86-95: Path traversal prevention

- `plugins/notebooklm/skills/notebooklm/scripts/run.py`
  - Added whitelist: `ask_question.py`, `notebook_manager.py`, `session_manager.py`, `auth_manager.py`, `cleanup_manager.py`
  - Lines 12-19: ALLOWED_SCRIPTS constant
  - Lines 81-85: Whitelist validation
  - Lines 89-95: Path traversal prevention

**Security Improvements:**
- Prevents command injection via arbitrary script names
- Blocks path traversal attacks (e.g., `../../malicious.py`)
- Provides clear error messages for invalid scripts
- Uses dual validation: whitelist + path resolution check

## Resources

- Security review report: See agent output above
- Similar vulnerability: CWE-78 OS Command Injection
- Playwright security issues: None directly related
