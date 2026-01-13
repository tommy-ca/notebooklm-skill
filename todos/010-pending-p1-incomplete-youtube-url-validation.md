---
status: pending
priority: p1
issue_id: 010
tags: [security, ssrf, url-validation, code-review]
dependencies: [007]
---

# Incomplete YouTube URL Validation - SSRF Vulnerability

## Problem Statement

The YouTube URL validation has incomplete video ID format checking. While it validates the domain and scheme, the actual video ID validation is inconsistent between `youtu.be` and `youtube.com` URLs, allowing potential SSRF attacks through malformed URLs.

**Why it matters**: An attacker could bypass validation with specially crafted URLs containing path traversal, XSS payloads, or redirect attacks. The validation doesn't extract and validate the actual video ID in all cases.

**Severity**: P1 - High security risk (CWE-918: Server-Side Request Forgery)

## Findings

**File**: `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py`
**Lines**: 74-81

**Source**: Security review agent (security-sentinel) + Pattern recognition specialist

**Vulnerable Code**:
```python
if parsed.netloc == 'youtu.be':
    # Format: https://youtu.be/VIDEO_ID
    if not re.match(r'^/[A-Za-z0-9_-]{11}$', parsed.path):
        return False
else:
    # Format: https://youtube.com/watch?v=VIDEO_ID
    if 'watch' not in parsed.path and 'v=' not in parsed.query:
        return False  # ❌ Doesn't validate video ID format!
```

**Attack Vectors**:
```python
# These bypass current validation:
"https://youtube.com/watch?v=@attacker.com"  # @ in video ID
"https://youtube.com/watch?v=<script>"        # XSS attempt
"https://youtube.com/watch?v=../../../etc"    # Path traversal
```

**Problem**: The `else` branch only checks if the string `'watch'` or `'v='` exists, but doesn't validate the video ID is actually 11 alphanumeric characters.

## Proposed Solutions

### Solution 1: Extract and Validate Video ID (Recommended)
**Pros**:
- Defense in depth with actual video ID extraction
- Prevents all identified attack vectors
- More robust than string matching

**Cons**: Slightly more complex code

**Effort**: Medium (30 minutes)
**Risk**: Low

**Implementation**:
```python
def validate_youtube_url(url: str) -> bool:
    """Validate YouTube URL with strict video ID validation"""
    try:
        parsed = urlparse(url)

        # Must be HTTPS
        if parsed.scheme != 'https':
            return False

        # Whitelist domains
        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
        if parsed.netloc not in allowed_domains:
            return False

        # Extract and validate video ID
        video_id = None
        if parsed.netloc == 'youtu.be':
            # Format: https://youtu.be/VIDEO_ID
            match = re.match(r'^/([A-Za-z0-9_-]{11})/?$', parsed.path)
            if match:
                video_id = match.group(1)
        else:
            # Format: https://youtube.com/watch?v=VIDEO_ID
            from urllib.parse import parse_qs
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                potential_id = query_params['v'][0]
                if re.match(r'^[A-Za-z0-9_-]{11}$', potential_id):
                    video_id = potential_id

        return video_id is not None

    except (ValueError, AttributeError, KeyError):
        return False
```

### Solution 2: Regex on Full youtube.com URLs
**Pros**: Simpler than extraction
**Cons**: Less robust, regex can be bypassed

**Effort**: Small
**Risk**: Medium

## Recommended Action

Implement **Solution 1** (extract and validate video ID) for comprehensive protection against SSRF attacks. This ensures we're actually validating the video ID format, not just checking for presence of strings.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py` (lines 54-85)

**CWE Classification**: CWE-918 (Server-Side Request Forgery)

**Attack Surface**: All YouTube URL inputs in the youtube-research skill

## Acceptance Criteria

- [ ] Extract video ID from both youtu.be and youtube.com formats
- [ ] Validate video ID is exactly 11 characters: [A-Za-z0-9_-]
- [ ] Reject URLs with query parameters containing special characters
- [ ] Add unit tests for attack vectors
- [ ] Test with valid YouTube URLs to ensure no false negatives

## Work Log

_No work completed yet_

## Resources

- OWASP SSRF Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- YouTube URL formats: https://gist.github.com/rodrigoborgesdeoliveira/987683cfbfcc8d800192da1e73adc486
- CWE-918: https://cwe.mitre.org/data/definitions/918.html
