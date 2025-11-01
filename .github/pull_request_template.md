## 🎭 Change Impact Classification

<!-- Please check one box to indicate the impact of your changes -->

- [ ] **TLDA (Unity) Changes** - Unity game engine components, editor tools, or mechanics
- [ ] **Seed (Python) Changes** - STAT7 backend, AI components, or Python infrastructure
- [ ] **Bridge Changes** - WebSocket protocols, Unity↔Python communication, or data bridges
- [ ] **Documentation** - README, comments, or guides updates only
- [ ] **CI/CD Changes** - Workflow, automation, or build configuration
- [ ] **Other** - Please describe: _______________

## 📋 Validation Checklist

<!-- Check all items that apply to ensure quality and consistency -->

### For TLDA (Unity) Changes
- [ ] Unity Test Runner passes all relevant tests
- [ ] New components include appropriate unit tests
- [ ] API changes maintain backward compatibility (or are marked as breaking)
- [ ] Unity console shows no errors or warnings
- [ ] Build process completes successfully for target platforms

### For Seed (Python) Changes
- [ ] All existing pytest tests pass
- [ ] New functionality includes appropriate tests
- [ ] Code follows Python PEP 8 style guidelines
- [ ] Dependencies are properly declared in requirements files
- [ ] STAT7 experiments validate successfully

### For Bridge Changes
- [ ] WebSocket communication protocols work correctly
- [ ] Unity↔Python data bridges pass integration tests
- [ ] JSON schema contracts are maintained
- [ ] Real-time event streaming functions properly
- [ ] Cross-system compatibility verified

### For All Changes
- [ ] Build process completes without errors
- [ ] No compilation errors in any affected system
- [ ] Changes follow existing code style and conventions
- [ ] Documentation is updated where necessary

## 🔄 Dependency Impact

<!-- Check if this PR affects dependency management -->

- [ ] Changes affect Unity package dependencies
- [ ] Changes affect Python pip/conda dependencies
- [ ] Updates require CI/CD configuration changes
- [ ] Changes may affect cross-system compatibility
- [ ] None of the above

## 📝 Description

<!-- Provide a clear description of your changes -->

### What Changed
<!-- Describe what you modified, added, or removed -->

### Why
<!-- Explain the motivation for this change -->

### How to Test
<!-- Describe how to verify these changes work correctly -->

### Breaking Changes
<!-- List any breaking changes and migration steps -->

## 🎯 Related Issues

<!-- Link any related issues or discussions -->

Closes #
Related to #

## 🧪 Testing Done

<!-- Describe the testing you performed -->

- [ ] Unity Test Runner validation
- [ ] Python pytest test coverage
- [ ] Integration testing across systems
- [ ] Manual testing of workflows
- [ ] Performance/memory impact testing
- [ ] Cross-system compatibility testing

## 📸 Screenshots/Examples

<!-- For UI changes, new features, or system integrations, include examples -->

```
Example output:
[Add relevant examples for your changes here]
```

## 🌟 Additional Notes

<!-- Any additional context, concerns, or considerations -->

---

<!--
This template helps maintain consistency in The Seed development and ensures
quality across all three systems (TLDA, Seed, and Bridges). Thank you for contributing!
-->

**Reviewer Notes:**
- TLDA changes should focus on Unity-specific functionality
- Seed changes should focus on Python backend and STAT7 functionality
- Bridge changes require careful review for cross-system compatibility
- All changes should pass appropriate validation workflows before merge
