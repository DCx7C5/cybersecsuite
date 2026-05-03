import { test, expect } from '@playwright/test'

test.describe('Plan mode validator', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('validatePlanMode returns valid config', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { validatePlanMode } = validator
      return validatePlanMode({ enabled: true })
    })

    expect(result.isValid).toBe(true)
    expect(result.errors).toHaveLength(0)
    expect(result.plan).toBeDefined()
  })

  test('validatePlanMode detects conflicting modes', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { validatePlanMode } = validator
      return validatePlanMode({ readonly: true, preview: true })
    })

    expect(result.isValid).toBe(false)
    expect(result.errors.length).toBeGreaterThan(0)
  })

  test('validatePlanMode generates warnings', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { validatePlanMode } = validator
      return validatePlanMode({ strict: true, enabled: false })
    })

    expect(result.warnings.length).toBeGreaterThan(0)
  })

  test('canExecuteOperation respects readonly mode', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { canExecuteOperation, createReadonlyMode } = validator
      const mode = createReadonlyMode()

      return {
        readAllowed: canExecuteOperation('read', mode).allowed,
        writeAllowed: canExecuteOperation('write', mode).allowed,
        deleteAllowed: canExecuteOperation('delete', mode).allowed,
      }
    })

    expect(result.readAllowed).toBe(true)
    expect(result.writeAllowed).toBe(false)
    expect(result.deleteAllowed).toBe(false)
  })

  test('canExecuteOperation respects preview mode', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { canExecuteOperation, createPreviewMode } = validator
      const mode = createPreviewMode()

      return {
        readAllowed: canExecuteOperation('read', mode).allowed,
        writeAllowed: canExecuteOperation('write', mode).allowed,
      }
    })

    expect(result.readAllowed).toBe(true)
    expect(result.writeAllowed).toBe(false)
  })

  test('getPlanModeString represents mode correctly', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const {
        getPlanModeString,
        createReadonlyMode,
        createPreviewMode,
        createStrictMode,
      } = validator
      const DEFAULT_PLAN_MODE = validator.DEFAULT_PLAN_MODE || { enabled: false }

      return {
        default: getPlanModeString(DEFAULT_PLAN_MODE),
        readonly: getPlanModeString(createReadonlyMode()),
        preview: getPlanModeString(createPreviewMode()),
        strict: getPlanModeString(createStrictMode()),
      }
    })

    expect(result.default).toBe('OFF')
    expect(result.readonly).toContain('READONLY')
    expect(result.preview).toContain('PREVIEW')
    expect(result.strict).toContain('STRICT')
  })

  test('parsePlanMode parses string correctly', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { parsePlanMode, validatePlanMode } = validator

      const mode1 = parsePlanMode('STRICT+READONLY')
      const validated1 = validatePlanMode(mode1)

      const mode2 = parsePlanMode('OFF')
      const validated2 = validatePlanMode(mode2)

      return {
        parsed1Strict: mode1.strict,
        parsed1Readonly: mode1.readonly,
        parsed2Enabled: mode2.enabled,
        valid1: validated1.isValid,
        valid2: validated2.isValid,
      }
    })

    expect(result.parsed1Strict).toBe(true)
    expect(result.parsed1Readonly).toBe(true)
    expect(result.parsed2Enabled).toBe(false)
    expect(result.valid1).toBe(true)
    expect(result.valid2).toBe(true)
  })

  test('mergePlanModes combines configurations', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const { mergePlanModes } = validator

      const merged = mergePlanModes(
        { enabled: true },
        { strict: true },
        { readonly: true }
      )

      return {
        enabled: merged.enabled,
        strict: merged.strict,
        readonly: merged.readonly,
      }
    })

    expect(result.enabled).toBe(true)
    expect(result.strict).toBe(true)
    expect(result.readonly).toBe(true)
  })

  test('Preset modes are properly configured', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const validator = await import('../src/utils/plan-mode-validator')
      const {
        createReadonlyMode,
        createPreviewMode,
        createStrictMode,
      } = validator

      const readonly = createReadonlyMode()
      const preview = createPreviewMode()
      const strict = createStrictMode()

      return {
        readonlyEnabled: readonly.enabled,
        previewEnabled: preview.enabled,
        strictEnabled: strict.enabled,
        readonlyReadonly: readonly.readonly,
        previewPreview: preview.preview,
        strictStrict: strict.strict,
      }
    })

    expect(result.readonlyEnabled).toBe(true)
    expect(result.previewEnabled).toBe(true)
    expect(result.strictEnabled).toBe(true)
    expect(result.readonlyReadonly).toBe(true)
    expect(result.previewPreview).toBe(true)
    expect(result.strictStrict).toBe(true)
  })
})
