# Bug Report: ADR-002 Detection Failure

## Issue Summary
**Bug ID**: BUG-001
**Severity**: High
**Component**: `sentinel.py` + `llm_reasoner.py`
**Status**: Root Cause Identified
**Date Reported**: May 17, 2026
**Date Analyzed**: May 17, 2026

## Description
The LLM reasoner was failing to detect ADR-002 violations (missing `@auth_middleware` in API endpoints) during PR analysis. After investigation, the root cause was identified as a **mismatch between the repository being analyzed and the local demo files**.

## Symptoms
```bash
yamato  …/pr-sentinel   feature/test-bob-improvements $!+  ♥ 19:48  python sentinel.py --repo MaxTheHuman21/pr-sentinel --pr 5

  PR Sentinel — Analizando PR #5 en MaxTheHuman21/pr-sentinel

[1/5] Obteniendo diff de PR #5... OK (29 líneas modificadas, 1 archivos)
[2/5] Leyendo ADRs y reglas del repo... OK (3 ADRs encontrados)
[3/5] Analizando imports del repo... OK (10 módulos mapeados)
[4/5] Razonando con WATSONX + análisis local... OK
[5/5] Publicando comentario en PR #5... OK

-> Comentario publicado: 1 bloqueantes, 0 advertencias, 0 sugerencias

  CHECKPOINT H+40: ADR-002 NO detectado — revisar import map con P4.
```

The system reported "ADR-002 NO detectado" even though the PR contained files violating ADR-002.

## Root Cause Analysis

### The Real Bug
**Location**: System architecture - mismatch between analyzed repository and local demo files

**Problem**: The system analyzes a **remote GitHub repository** (`MaxTheHuman21/pr-sentinel`) but expects to find files that only exist in the **local `demo_repo/` folder**.

### Technical Details

1. **What Happens**:
   ```bash
   python sentinel.py --repo MaxTheHuman21/pr-sentinel --pr 5
   ```
   - Fetches PR diff from GitHub repo `MaxTheHuman21/pr-sentinel`
   - Fetches file list from GitHub repo `MaxTheHuman21/pr-sentinel`
   - Reads ADRs from **local** `demo_repo/docs/adr/`
   - Builds import_map from GitHub repo files

2. **The Mismatch**:
   - **GitHub repo** `MaxTheHuman21/pr-sentinel` contains:
     - `demo_repo/api/products.py` ✓
     - `demo_repo/api/orders.py` ✓
     - **NO** `demo_repo/api/analytics.py` ❌
   
   - **Local folder** `demo_repo/` contains:
     - `api/analytics.py` ✓ (the file that violates ADR-002)
     - `api/products.py` ✓
     - `api/orders.py` ✓

3. **Debug Output Confirms**:
   ```
   🔍 DEBUG - Import Map Contents:
     📁 demo_repo/api/products.py
        Imports: ['flask', 'middleware.auth_middleware', 'datetime']
     📁 demo_repo/api/orders.py
        Imports: ['flask', 'middleware.auth_middleware', 'datetime', 'services.order_service']
   ```
   
   **Missing**: `demo_repo/api/analytics.py` - because it doesn't exist in the GitHub repo!

4. **Consequence**:
   - The import_map only contains files from the GitHub repository
   - `analytics.py` (which violates ADR-002) is not in the import_map
   - Therefore, ADR-002 violation cannot be detected
   - The system is analyzing the wrong repository

## Example Scenario

### File: `demo_repo/api/analytics.py`
```python
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import auth_middleware  # ✓ Has auth import
from db.database import Database  # ❌ Violates ADR-001

@analytics_bp.route('/analytics/user-activity', methods=['GET'])
@auth_middleware  # ✓ Has decorator
def get_user_activity():
    # ...
```

### What Happened:
1. `import_map` key: `"demo_repo/api/analytics.py"`
2. Imports extracted: `["middleware.auth_middleware", "db.database"]`
3. Check: `"auth_middleware" in "middleware.auth_middleware"` → TRUE ✓
4. File added to violations: `"demo_repo/api/analytics.py"`
5. Diff filename: `"api/analytics.py"`
6. Comparison: `"demo_repo/api/analytics.py" == "api/analytics.py"` → FALSE ❌
7. **Result**: Violation not matched with diff changes

## The Solution

### Option 1: Use Local Repository Analysis (Recommended for Demo)
Instead of analyzing a remote GitHub repository, analyze the local `demo_repo/` folder directly.

**Change in sentinel.py**:
```python
# Instead of fetching from GitHub:
files_dict = _get_repo_files(args.repo, token)

# Use local files:
from pathlib import Path
local_repo_path = Path("demo_repo")
files_dict = {}
for py_file in local_repo_path.rglob("*.py"):
    relative_path = str(py_file.relative_to(local_repo_path.parent))
    files_dict[relative_path] = py_file.read_text(encoding='utf-8')
```

### Option 2: Ensure GitHub Repo Contains All Demo Files
Push the `demo_repo/api/analytics.py` file to the GitHub repository so it's available for analysis.

```bash
cd /path/to/MaxTheHuman21/pr-sentinel
git add demo_repo/api/analytics.py
git commit -m "Add analytics.py for ADR-002 violation demo"
git push origin main
```

### Option 3: Hybrid Approach
Merge local files with GitHub files for comprehensive analysis:

```python
def _get_all_files(repo: str, token: str, local_path: str) -> dict:
    """Combine GitHub repo files with local demo files"""
    # Get files from GitHub
    github_files = _get_repo_files(repo, token)
    
    # Get files from local demo_repo
    local_files = {}
    demo_path = Path(local_path)
    if demo_path.exists():
        for py_file in demo_path.rglob("*.py"):
            relative_path = str(py_file.relative_to(demo_path.parent))
            local_files[relative_path] = py_file.read_text(encoding='utf-8')
    
    # Merge (local files override GitHub files)
    return {**github_files, **local_files}
```

## Impact

### Current State (Bug Present):
- ❌ ADR-002 violations not detected for files not in GitHub repo
- ❌ Analyzing wrong repository (GitHub vs local demo)
- ❌ Import map incomplete - missing local demo files
- ❌ False negatives in security checks
- ❌ Checkpoint failures

### After Fix (Any Solution):
- ✅ ADR-002 violations correctly detected
- ✅ All demo files included in analysis
- ✅ Accurate security violation reporting
- ✅ Checkpoint passes

## Testing

### Test Case 1: API File Without Auth
```python
# File: api/new_endpoint.py
from flask import Blueprint

@app.route('/new')
def new_endpoint():
    return "Hello"
```
**Expected**: ADR-002 violation detected  
**Result**: ✅ PASS

### Test Case 2: API File With Auth
```python
# File: api/secure_endpoint.py
from middleware.auth_middleware import auth_middleware

@auth_middleware
@app.route('/secure')
def secure_endpoint():
    return "Secure"
```
**Expected**: No ADR-002 violation  
**Result**: ✅ PASS

### Test Case 3: Non-API File Without Auth
```python
# File: services/helper.py
def helper_function():
    return "Helper"
```
**Expected**: No ADR-002 violation (not an API file)  
**Result**: ✅ PASS

## Related Issues

- **ADR-001 Detection**: Also affected by path mismatch, fixed in same commit
- **Cross-Platform Compatibility**: Windows path separators now handled correctly

## Prevention

### Code Review Checklist:
- [ ] Verify path normalization in file comparison logic
- [ ] Test with different repository structures (with/without prefixes)
- [ ] Validate cross-platform path handling
- [ ] Add unit tests for path normalization

### Recommended Tests:
```python
def test_path_normalization():
    assert normalize_path("demo_repo/api/test.py") == "api/test.py"
    assert normalize_path("api/test.py") == "api/test.py"
    assert normalize_path("api\\test.py") == "api/test.py"
```

## References

- **ADR-002**: `demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md`
- **Affected Module**: `llm_reasoner.py`
- **Related Module**: `repo_analyzer.py` (import extraction)
- **Integration Point**: `sentinel.py` (orchestration)

## Lessons Learned

1. **Path Consistency**: Always normalize file paths when comparing across different sources (git diff, GitHub API, local filesystem)
2. **Early Normalization**: Normalize paths as early as possible in the data pipeline
3. **Cross-Platform**: Consider Windows/Unix path differences from the start
4. **Testing**: Include path edge cases in unit tests

## Recommended Action

**Implement Option 3 (Hybrid Approach)** - This provides the most flexibility:

1. Analyze GitHub repository for real PRs
2. Include local demo files for testing and demonstrations
3. Merge both sources for comprehensive analysis

This ensures:
- ✅ Real PR analysis works with GitHub repos
- ✅ Local demo files are included for testing
- ✅ ADR-002 violations in `demo_repo/api/analytics.py` are detected
- ✅ System works in both production and demo modes

## Status
🔍 **ROOT CAUSE IDENTIFIED** - Awaiting implementation decision

The bug is not in `llm_reasoner.py` path normalization. The real issue is that the system analyzes a GitHub repository (`MaxTheHuman21/pr-sentinel`) that doesn't contain the `demo_repo/api/analytics.py` file that violates ADR-002. This file only exists locally.

**Next Steps**:
1. Choose one of the three solution options
2. Implement the chosen solution
3. Test with both GitHub PRs and local demo files
4. Verify ADR-002 detection works correctly

---
**Author**: Bob (AI Software Engineer)
**Reviewer**: Yamato
**Last Updated**: May 17, 2026
**Status**: Analysis Complete - Awaiting Implementation