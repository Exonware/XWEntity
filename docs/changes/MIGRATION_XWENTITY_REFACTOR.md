# XWEntity Refactoring Migration Guide

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.0.1.0  
**Last Updated:** 07-Feb-2026

*(Value captured from repo-root docs; original archived in `docs/_archive/`.)*

---

## Overview

This document tracks the migration from the current architecture to the new unified architecture:

- **Merge XWObject and XWEntity** into one unified XWEntity class
- **Rename current xwentity** to xwmodels (collections/groups with providers)
- **Update xwbase** to use xwmodels

## Architecture Changes

### Before
- `xwobject`: XWObject class (schema + actions + data)
- `xwentity`: XWEntity class (schema + actions + data + entity features) + Collections + Groups + BaaS features

### After
- `xwentity`: Unified XWEntity class (merged XWObject + XWEntity features)
- `xwmodels`: Collections and Groups with provider support
- `xwbase`: Uses xwmodels

## Migration Steps

### Phase 1: Preparation ✅
- [x] Create backup branch: `backup/pre-xwentity-refactor`
- [x] Create migration tracking document
- [ ] Identify all files to merge

### Phase 2: Merge Classes
- [ ] Rename xwentity → xwmodels_temp
- [ ] Analyze XWObject and XWEntity classes
- [ ] Merge into unified XWEntity
- [ ] Rename xwobject → xwentity

### Phase 3: Rename to XWModels
- [ ] Rename xwmodels_temp → xwmodels
- [ ] Remove merged entity files
- [ ] Update imports

### Phase 4: Update XWBase
- [ ] Update xwbase to use xwmodels

### Phase 5: Update Imports
- [ ] Update all library imports

### Phase 6: Create Server Packages
- [ ] Create server package structures

### Phase 7: Testing
- [ ] Update tests
- [ ] Run integration tests

### Phase 8: Documentation
- [ ] Update READMEs
- [ ] Update migration guide

### Phase 9: Cleanup
- [ ] Remove temporary directories
- [ ] Final validation

## Breaking Changes

1. **XWObject class removed** - merged into XWEntity
2. **Import changes**:
   - `from exonware.xwobject import XWObject` → `from exonware.xwentity import XWEntity`
   - `from exonware.xwentity import XWCollection` → `from exonware.xwmodels import XWCollection`
3. **Package name changes**:
   - `exonware-xwobject` → `exonware-xwentity`
   - `exonware-xwentity` → `exonware-xwmodels` (for collections/groups)

## Migration Examples

### Before
```python
from exonware.xwobject import XWObject
from exonware.xwentity import XWEntity, XWCollection

obj = XWObject(schema={...}, data={...})
entity = XWEntity(schema={...}, data={...})
collection = XWCollection(...)
```

### After
```python
from exonware.xwentity import XWEntity
from exonware.xwmodels import XWCollection

# Unified class - use XWEntity for everything
obj = XWEntity(schema={...}, data={...})
entity = XWEntity(schema={...}, data={...})
collection = XWCollection(...)
```

## Notes

- All features from both XWObject and XWEntity are preserved in unified XWEntity
- No functionality is removed - only merged
- Follows GUIDE_31_DEV, GUIDE_51_TEST, GUIDE_41_DOCS standards
