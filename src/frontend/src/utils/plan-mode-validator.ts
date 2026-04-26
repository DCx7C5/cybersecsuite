/**
 * Plan-mode validator utility for CyberSecSuite
 * Validates plan mode operations and ensures compliance with rules
 */

export interface PlanMode {
  enabled: boolean
  strict: boolean
  readonly: boolean
  preview: boolean
}

export interface ValidatedPlan {
  isValid: boolean
  errors: string[]
  warnings: string[]
  plan: PlanMode
}

/**
 * Default plan mode configuration
 */
export const DEFAULT_PLAN_MODE: PlanMode = {
  enabled: false,
  strict: false,
  readonly: false,
  preview: false,
}

/**
 * Validate plan mode configuration
 */
export function validatePlanMode(config: Partial<PlanMode>): ValidatedPlan {
  const errors: string[] = []
  const warnings: string[] = []
  const plan: PlanMode = { ...DEFAULT_PLAN_MODE, ...config }

  // Validation rules
  if (plan.strict && !plan.enabled) {
    warnings.push('Strict mode is enabled but plan mode is disabled')
  }

  if (plan.readonly && plan.preview) {
    errors.push('Cannot enable both readonly and preview modes simultaneously')
  }

  if (plan.enabled && !plan.readonly && !plan.preview) {
    warnings.push('Plan mode is enabled but neither readonly nor preview mode is set')
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    plan: errors.length === 0 ? plan : DEFAULT_PLAN_MODE,
  }
}

/**
 * Check if operation is allowed in current plan mode
 */
export function canExecuteOperation(
  operation: 'read' | 'write' | 'delete' | 'create',
  mode: PlanMode
): { allowed: boolean; reason?: string } {
  if (!mode.enabled) {
    return { allowed: true }
  }

  if (mode.readonly && (operation === 'write' || operation === 'delete' || operation === 'create')) {
    return {
      allowed: false,
      reason: `${operation} operation not allowed in readonly mode`,
    }
  }

  if (mode.preview && operation === 'write') {
    return {
      allowed: false,
      reason: 'write operations not allowed in preview mode',
    }
  }

  return { allowed: true }
}

/**
 * Merge plan mode configurations with precedence
 */
export function mergePlanModes(...configs: Partial<PlanMode>[]): PlanMode {
  return configs.reduce((acc, config) => ({ ...acc, ...config }), DEFAULT_PLAN_MODE)
}

/**
 * Get plan mode string representation
 */
export function getPlanModeString(mode: PlanMode): string {
  if (!mode.enabled) {
    return 'OFF'
  }

  const parts: string[] = []
  if (mode.strict) parts.push('STRICT')
  if (mode.readonly) parts.push('READONLY')
  if (mode.preview) parts.push('PREVIEW')

  return parts.length > 0 ? parts.join('+') : 'ON'
}

/**
 * Parse plan mode from string
 */
export function parsePlanMode(str: string): Partial<PlanMode> {
  const mode: Partial<PlanMode> = { enabled: true }

  if (str.includes('STRICT')) mode.strict = true
  if (str.includes('READONLY')) mode.readonly = true
  if (str.includes('PREVIEW')) mode.preview = true
  if (str === 'OFF') mode.enabled = false

  return mode
}

/**
 * Create a readonly plan mode (for preview/inspection)
 */
export function createReadonlyMode(): PlanMode {
  return {
    enabled: true,
    strict: true,
    readonly: true,
    preview: false,
  }
}

/**
 * Create a preview mode (for simulation/dry-run)
 */
export function createPreviewMode(): PlanMode {
  return {
    enabled: true,
    strict: false,
    readonly: false,
    preview: true,
  }
}

/**
 * Create a strict mode (strict validation rules)
 */
export function createStrictMode(): PlanMode {
  return {
    enabled: true,
    strict: true,
    readonly: false,
    preview: false,
  }
}
