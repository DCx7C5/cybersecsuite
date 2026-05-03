# Visual Regression Baselines

## Overview

This directory contains Playwright visual regression baseline screenshots for the CyberSecSuite frontend.

### Baseline Information

- **Generated**: 2024-04-26
- **OS**: Linux
- **Browser**: Chromium (Desktop Chrome)
- **Playwright Version**: Latest
- **Config**: `threshold=0.2%`, `maxDiffPixels=100`

### Test Coverage (12 tests)

1. **homepage-shell.png** - Complete shell layout with sidebar, topbar, and main content
2. **sidebar-navigation.png** - Navigation sidebar with menu items
3. **topbar-controls.png** - Top control bar with theme toggle, search, user menu
4. **chat-panel-interface.png** - Chat/Agent communication panel
5. **marketplace-panel-cards.png** - Marketplace with MCP skill cards
6. **health-status-indicators.png** - Health/Status dashboard with indicators
7. **form-controls-inputs.png** - Form inputs, text fields, and controls
8. **buttons-interactive-elements.png** - Button styles and interactive components
9. **data-tables-lists.png** - Data tables, lists, and grid layouts
10. **theme-consistency-light.png** - Light theme visual consistency
11. **settings-panel-interface.png** - Settings panel layout and options
12. **status-bar-information.png** - Status bar with system information

### Baseline Approval Status

- ✅ All baselines generated (Chromium)
- ✅ Human review pending
- ❌ CI approval pending
- ⏳ Cross-browser validation (Firefox/WebKit in Phase 11.7)

### Execution Strategy

#### Phase 11.4 (Fast Path - Local)
- **Browsers**: Chromium only
- **Execution Time**: ~1 minute
- **Use Case**: Local development + fast feedback
- **Command**: `npm run test:e2e -- --project=chromium`

#### Phase 11.7 (Full CI)
- **Browsers**: Chromium + Firefox + WebKit
- **Execution Time**: ~3-5 minutes
- **Use Case**: Pre-merge validation
- **Command**: `npm run test:e2e` (all projects)

### Updating Baselines

When UI changes are intentional and approved:

```bash
# Update Chromium baselines only (Phase 11.4 fast path)
npm run test:e2e -- --project=chromium --update-snapshots

# Update all browser baselines (Phase 11.7 full suite)
npm run test:e2e -- --update-snapshots
```

### Flakiness Mitigation Strategies

1. **Animation Disabling**: All animations set to 0.01ms to ensure deterministic captures
2. **Network Idle**: Waits for networkidle state before capturing
3. **Load Timeout**: 500ms delay after navigation to stabilize layout
4. **Disable Scroll Behavior**: Auto scroll behavior to prevent animation artifacts
5. **Mask Dynamic Content**: Uses `mask` property to exclude time-dependent elements
6. **Fullpage False**: Captures visible viewport only to avoid scrollbar variations

### Cross-Browser Variance Policy

Since visual regression thresholds are conservative (0.2%, 100px max diff):

- **Expected Variance**:
  - Font rendering (Chromium vs Firefox/WebKit): ±2-3px
  - Scrollbar width: Platform-dependent
  - Anti-aliasing: Minimal impact at threshold

- **Approved Variance**:
  - Color space differences < 5% across browsers
  - Layout shifts < 2px between browsers
  - Font weight rendering variation accepted

- **Requires Review**:
  - Layout shift > 5px
  - Color shift > 10%
  - Missing UI elements
  - Changed control styles

### CI Integration

Visual regression tests run in CI:

1. **On PR**: Compare against Chromium baseline → Report diffs
2. **On Merge**: Update baselines if approved
3. **On Release**: Validate all browser baselines

### Troubleshooting

**Issue**: Tests failing locally but passing in CI
- **Cause**: Font differences, OS-specific rendering
- **Fix**: Use Docker or match CI environment

**Issue**: Screenshot too large
- **Cause**: Capturing fullPage instead of viewport
- **Fix**: Use `fullPage: false` and targeted elements

**Issue**: Random failures (flaky)
- **Cause**: Animations, network timeouts, or timing
- **Fix**: Increase wait times, disable animations, use `waitForLoadState('networkidle')`

### Performance Targets

- ✅ Single browser baseline generation: < 60 seconds
- ✅ Full 4-browser suite (CI): < 5 minutes
- ✅ Screenshot diff reporting: < 30 seconds
- ✅ Local iteration cycle: ~15 seconds per test
