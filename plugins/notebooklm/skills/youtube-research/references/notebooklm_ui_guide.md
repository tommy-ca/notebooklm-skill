# NotebookLM UI Quick Reference

Reference guide for NotebookLM UI elements and selectors for automation.

## Interface Layout

### Home Page
- **New Notebook Button**: Creates a new notebook
- **Notebook Cards**: Displays existing notebooks

### Notebook View
- **Sources Panel**: Left sidebar showing all sources
- **Chat Interface**: Center area for queries
- **Studio Panel**: Right panel with Audio Overview

## Selector Cheatsheet

### Textareas (CRITICAL - Multiple exist!)

**Problem**: NotebookLM has multiple textareas. Generic selectors grab the wrong one!

**Solutions:**

```python
# URL input (for YouTube, websites, etc.)
YOUTUBE_URL_INPUT = "textarea[placeholder='Paste any links']"

# Text input (for pasting research, documents)
TEXT_SOURCE_INPUT = "textarea[placeholder='Paste text here']"

# Query input (for asking questions)
QUERY_INPUT = "textarea.query-box-input"
```

### Buttons

```python
# Home page
NEW_NOTEBOOK_BUTTON = "button:has-text('New notebook')"

# Source management
ADD_SOURCE_BUTTON = "button:has-text('Add source')"
INSERT_BUTTON = "button:has-text('Insert')"

# Audio Overview
AUDIO_OVERVIEW_BUTTON = "button:has-text('Audio Overview')"
GENERATE_BUTTON = "button:has-text('Generate')"
```

## Modal Detection

**Add Source Modal:**
- Opens when clicking "Add source"
- Contains multiple input options (URL, Text, Upload)
- Wait 2 seconds after clicking for modal to appear

**Audio Overview Modal:**
- Opens from Studio panel
- Contains "Generate" button
- Audio generation takes 5-10 minutes

## Common Mistakes

### ❌ Wrong Textarea Targeting

```python
# DON'T use generic selector
textarea = page.query_selector('textarea')  # Gets random textarea!

# DO use specific placeholder
textarea = page.query_selector("textarea[placeholder='Paste any links']")
```

### ❌ Not Waiting for Processing

```python
# DON'T click immediately
await page.fill(url_input, youtube_url)
await page.click(insert_button)  # Source may not be processed!

# DO wait for processing
await page.fill(url_input, youtube_url)
await page.click(insert_button)
await page.wait_for_timeout(10000)  # YouTube needs ~10s
```

### ❌ Assuming Button State

```python
# DON'T assume button is enabled
await page.click(insert_button)  # May be disabled!

# DO check button state
button = await page.query_selector(insert_button)
is_disabled = await button.get_attribute('disabled')
if not is_disabled:
    await button.click()
```

## Wait Times

| Action | Wait Time | Why |
|--------|-----------|-----|
| Page navigation | 3s | Full page load |
| Modal open | 2s | Animation + content load |
| YouTube processing | 8-10s | Video analysis |
| Text processing | 5s | Text indexing |
| Audio generation | 5-10min | AI generation |

## State Verification

### After Each Action

```python
# After adding YouTube source
# Verify: Source appears in sources list
sources = await page.query_selector_all('.source-item')
assert len(sources) == 1

# After adding text source
# Verify: 2 sources in list
sources = await page.query_selector_all('.source-item')
assert len(sources) == 2

# After clicking Audio Overview
# Verify: Generation started
generating = await page.query_selector('.audio-generating')
assert generating is not None
```

## Angular Event Pattern

NotebookLM uses Angular. To set textarea values:

```javascript
// Get property descriptor
const setter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype,
    'value'
).set;

// Set value and dispatch event
setter.call(textarea, 'your content here');
textarea.dispatchEvent(new Event('input', {bubbles: true}));
```

In Patchright/Playwright, use built-in methods which handle this automatically:

```python
await page.fill(selector, text)  # Handles Angular events
```

## Tips

1. **Screenshot First**: Take screenshot before each action to verify UI state
2. **Specific Selectors**: Always use placeholder-based selectors for textareas
3. **Wait Generously**: NotebookLM has async processing - wait longer than you think
4. **Verify State**: Check that actions succeeded before moving on
5. **Button States**: Always check if buttons are enabled before clicking
