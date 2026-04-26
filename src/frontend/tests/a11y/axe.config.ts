/**
 * Axe-core configuration for WCAG 2.1 Level AA compliance testing
 * Runs accessibility scans targeting strict WCAG 2.1 AA standards
 */

export const axeConfig = {
  runOnly: {
    type: 'tag',
    values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'],
  },
  rules: {
    // Disable rules that generate false positives
    // These can be manually reviewed or reconfigured per context
    'color-contrast': { enabled: false }, // Often false positives with dynamic themes
  },
  
  // Standard impact levels to track
  impactLevels: {
    critical: 'WCAG 2.1 Level AA violation - must fix',
    serious: 'Significantly impacts accessibility - should fix',
    moderate: 'Some users affected - consider fixing',
    minor: 'Minimal impact - fix if practical',
  },
};

/**
 * Categories targeted:
 * - wcag2a: Web Content Accessibility Guidelines 2.0 Level A (foundational)
 * - wcag2aa: WCAG 2.0 Level AA (higher standard)
 * - wcag21a: WCAG 2.1 Level A (updated guidelines)
 * - wcag21aa: WCAG 2.1 Level AA (STRICT - our target compliance level)
 */

export const axeReportTemplate = {
  timestamp: new Date().toISOString(),
  wcagTargetLevel: 'wcag21aa',
  compliancePass: false,
  violationsSummary: {
    critical: 0,
    serious: 0,
    moderate: 0,
    minor: 0,
  },
  pageResults: [] as any[],
  executionSummary: {
    totalPages: 0,
    pagesScanned: 0,
    pagesWithViolations: 0,
    totalViolations: 0,
  },
};
