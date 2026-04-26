# TypeScript Frontend Linting & Fixing Plan

**Date:** 2026-04-26  
**Status:** Diagnostic Complete — Ready to Execute  
**Priority:** CRITICAL BLOCKER (Phase 5E)  
**Estimated Effort:** 1-3 hours (depends on root cause)

---

## 🎯 Objective

Fix **110+ TypeScript compilation errors** blocking frontend build. This is the critical blocker preventing Phase 5E React dashboard validation.

**Success Criteria:** 
- ✅ `npm run type-check` passes with 0 errors
- ✅ `npm run build` succeeds
- ✅ All Phase 5E components compile correctly

---

## 📊 Error Analysis

### Total Errors: 110+

**Distribution by Category:**

| Category | Count | Severity | Quick Fix? |
|----------|-------|----------|-----------|
| React Query imports | 28+ | CRITICAL | Maybe (cache) |
| JSX in style tags (`jsx={true}`) | 15+ | MEDIUM | Yes (bulk replace) |
| Type-only imports missing | 12+ | MEDIUM | Yes (pattern) |
| Parameter types (implicit any) | 10+ | MEDIUM | Yes (annotate) |
| Vite/client types missing | 1 | HIGH | Maybe (reinstall) |
| Named export mismatch | 8+ | MEDIUM | Yes (import fix) |
| Type assignment conflicts | 15+ | MEDIUM | Partial |
| Unused imports | 3 | LOW | Yes (remove) |
| Missing @types dependencies | 2 | MEDIUM | Yes (install) |

---

## 🔍 Root Cause Analysis

### Root Cause 1: React Query v5 Export Issue [CRITICAL]

**Error:**
```
TS2305: Module '"@tanstack/react-query"' has no exported member 'useMutation'
TS2305: Module '"@tanstack/react-query"' has no exported member 'useQueryClient'
TS2305: Module '"@tanstack/react-query"' has no exported member 'useQuery'
```

**Current State:**
- ✅ Installed: `@tanstack/react-query@5.99.2`
- ✅ Installed in node_modules
- ❓ TypeScript can't find exports

**Likely Causes:**
1. **Module resolution cache issue** (most likely)
   - TypeScript cache has stale module info
   - Solution: Clean install + cache clear
   
2. **Missing @types definitions**
   - Unlikely with @tanstack v5+ (has built-in types)
   - But worth checking
   
3. **Circular dependency in tsconfig**
   - Less likely but possible

**Solution (Ordered by likelihood):**
1. **FIRST:** Clean install + cache clear (fastest, ~5 min)
   ```bash
   cd src/frontend
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

2. **If persists:** Verify types exist
   ```bash
   ls -la node_modules/@tanstack/react-query/dist/
   # Should have: index.d.ts, query/index.d.ts, etc.
   ```

3. **If still missing:** Force reinstall
   ```bash
   npm install @tanstack/react-query@5.99.2 --force
   npm run type-check
   ```

**Impact if fixed:** Resolves ~28 errors immediately ✨

---

### Root Cause 2: JSX as Style Tag Attribute [MEDIUM]

**Error:**
```
TS2322: Type '{ children: string; jsx: true; }' is not assignable to type 
'DetailedHTMLProps<StyleHTMLAttributes<HTMLStyleElement>, HTMLStyleElement>'.
Property 'jsx' does not exist on type 'DetailedHTMLProps<...>'
```

**Root Cause:**
- Code uses `<style jsx={true}>` syntax (from styled-jsx/Next.js)
- Project uses **Tailwind CSS**, not styled-jsx
- HTML `<style>` element doesn't have `jsx` attribute

**Affected Files:** 15 instances across src/components/orchestrator/

**Examples:**
```tsx
// ❌ WRONG (styled-jsx syntax)
<style jsx={true}>{`
  .container { color: red; }
`}</style>

// ✅ CORRECT (plain style tag)
<style>{`
  .container { color: red; }
`}</style>
```

**Solution:**
1. Remove `jsx={true}` attribute from all `<style>` tags
2. Keep the content as-is

**Files to Fix:**
- src/components/orchestrator/APIKeyManager.tsx (line 127)
- src/components/orchestrator/AlertPreferences.tsx (line 117)
- src/components/orchestrator/AnalyticsDashboard.tsx (line 201)
- src/components/orchestrator/BatchScheduler.tsx (line 197)
- src/components/orchestrator/ConfigForm.tsx (line 62)
- src/components/orchestrator/ConfigHistory.tsx (line 59)
- src/components/orchestrator/ConfigManager.tsx (line 158)
- src/components/orchestrator/HealthDashboard.tsx (line 186)
- src/components/orchestrator/JobList.tsx (line 59)
- src/components/orchestrator/LogsViewer.tsx (line 69)
- src/components/orchestrator/MetricsCharts.tsx (line 86)
- src/components/orchestrator/Navigation.tsx (line 93)
- src/components/orchestrator/NotificationCenter.tsx (line 141)
- src/components/orchestrator/ScheduleForm.tsx (line 165)
- src/components/orchestrator/StatusOverview.tsx (line 90)
- (and others)

**Bulk Fix (one-liner):**
```bash
cd src/frontend
find src/components/orchestrator -name "*.tsx" -type f -exec \
  sed -i 's/<style jsx={true}>/<style>/g; s/<style jsx>/<style>/g' {} \;
npm run type-check
```

**Impact if fixed:** Resolves ~15 errors ✨

---

### Root Cause 3: Type-Only Imports Required [MEDIUM]

**Error:**
```
TS1484: 'ReactNode' is a type and must be imported using a type-only import 
when 'verbatimModuleSyntax' is enabled.
```

**Root Cause:**
- tsconfig.json sets `"verbatimModuleSyntax": true`
- This enforces strict separation of type vs value imports
- React types must use `import type { ... }`

**Current (Wrong):**
```tsx
import { ReactNode, Dispatch, SetStateAction } from 'react'
```

**Required (Correct):**
```tsx
import type { ReactNode, Dispatch, SetStateAction } from 'react'
```

**Affected Types:**
- ReactNode (in many files)
- Dispatch (state callbacks)
- SetStateAction (state updaters)
- RefObject (useRef)

**Solution:**
1. Identify all type imports from React
2. Change `import { Type }` → `import type { Type }`
3. Keep value imports unchanged (React, useState, etc.)

**Bulk Fix (find & replace pattern):**
```bash
# Find files with type imports
rg 'import \{ ([^}]*ReactNode[^}]*) \}' --type tsx src/
rg 'import \{ ([^}]*Dispatch[^}]*) \}' --type tsx src/

# Fix using sed or eslint --fix
```

**Impact if fixed:** Resolves ~12 errors ✨

---

### Root Cause 4: Missing Parameter Type Annotations [MEDIUM]

**Error:**
```
TS7006: Parameter 't' implicitly has an 'any' type.
TS7006: Parameter 'data' implicitly has an 'any' type.
```

**Root Cause:**
- tsconfig.json sets `"noUnusedParameters": true`
- All function parameters need explicit types
- Current code has bare parameters without types

**Examples:**
```tsx
// ❌ WRONG (implicit any)
const map = (t) => t.id
const handler = (data) => setWorker(data)

// ✅ CORRECT (explicit types)
const map = (t: Template) => t.id
const handler = (data: WorkerResponse) => setWorker(data)
```

**Solution:**
1. Add type annotations to all arrow function parameters
2. Use context clues or explicit types
3. For generic data, use `unknown` as fallback

**Affected Parameters:**
- `(t)` - likely Template
- `(data)` - likely WorkerMetrics or API response
- `(col)` - likely column type
- `(template)` - Template type
- etc.

**Impact if fixed:** Resolves ~10 errors ✨

---

### Root Cause 5: Vite/client Types Not Found [HIGH]

**Error:**
```
TS2688: Cannot find type definition file for 'vite/client'.
The file is in the program because:
    Entry point of type library 'vite/client' specified in compilerOptions
```

**Root Cause:**
- tsconfig.json specifies: `"types": ["vite/client"]`
- Vite is installed, but types might not be
- OR: types are in different location

**Current Setup:**
- ✅ vite@8.0.9 installed
- ✅ @vitejs/plugin-react@6.0.1 installed
- ✅ Should include vite/client types

**Solution (ordered):**
1. Verify types exist:
   ```bash
   ls node_modules/vite/client.d.ts
   ```

2. If missing, types should be included with vite. Reinstall:
   ```bash
   npm install vite@latest --save-dev
   ```

3. If @types/vite doesn't exist, may not be needed (vite has built-in)

4. Verify tsconfig.json has correct entry:
   ```json
   "types": ["vite/client"]
   ```

**Impact if fixed:** Resolves 1 error

---

### Root Cause 6: Named vs Default Export Mismatch [MEDIUM]

**Error:**
```
TS2614: Module '"./Card"' has no exported member 'Card'. 
Did you mean to use 'import Card from "./Card"' instead?
```

**Root Cause:**
- Component files export as **default**: `export default Card`
- But imported as **named**: `import { Card } from "./Card"`
- Mismatch causes TypeScript error

**Examples:**
```tsx
// In Card.tsx
export default Card  // default export

// In using component
import { Card } from '@/components/ui/Card'  // ❌ named import
// Should be:
import Card from '@/components/ui/Card'  // ✅ default import
```

**Affected Components:**
- Card
- Badge
- Spinner
- Button
- Select
- Input
- Modal

**Affected Files (importing wrong syntax):**
- src/components/workers/WorkerList.tsx
- src/components/workers/WorkerDetail.tsx
- src/components/workers/MetricsCard.tsx
- src/components/orchestrator/*.tsx

**Solution:**
Change all named imports to default imports

**Before:**
```tsx
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
```

**After:**
```tsx
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Spinner from '@/components/ui/Spinner'
```

**Bulk Fix:**
```bash
cd src/frontend
# Replace pattern in all tsx files
find src -name "*.tsx" -type f -exec \
  sed -i "s/import { Card } from/import Card from/g" {} \;
find src -name "*.tsx" -type f -exec \
  sed -i "s/import { Badge } from/import Badge from/g" {} \;
find src -name "*.tsx" -type f -exec \
  sed -i "s/import { Spinner } from/import Spinner from/g" {} \;
```

**Impact if fixed:** Resolves ~8 errors ✨

---

### Root Cause 7: Type Assignment Conflicts [MEDIUM]

**Error Examples:**
```
TS2322: Type 'Dispatch<SetStateAction<ScheduledJob | null>>' is not assignable 
to type '(job: ScheduledJob) => void'
```

**Root Cause:**
- setState callback type doesn't match hook return type
- Union type mismatch (includes null but callback doesn't)

**Example:**
```tsx
const [job, setJob] = useState<ScheduledJob | null>(null)

// ❌ WRONG - callback doesn't handle null
const handleJob = (job: ScheduledJob) => {
  setJob(job)  // Error: type mismatch
}

// ✅ CORRECT - callback uses same type
const handleJob = (job: ScheduledJob | null) => {
  setJob(job)
}
```

**Solution:**
1. Align callback parameter types with state type
2. Include union types (null, undefined, etc.) if state allows
3. Use `useCallback` with proper typing if needed

**Impact if fixed:** Resolves ~15 errors ✨

---

### Root Cause 8: Missing @types Dependencies [MEDIUM]

**Errors:**
```
TS2503: Cannot find namespace 'NodeJS'
TS2591: Cannot find name 'process'
TS2552: Cannot find name 'HTMLAsideElement'
```

**Root Cause:**
- Missing type definitions
- Need: `@types/node`

**Solution:**
```bash
npm install --save-dev @types/node
```

**Impact if fixed:** Resolves ~3 errors ✨

---

## 🚀 Execution Plan

### Phase 1: Quick Fixes (Highest ROI) [~30 min]

**1.1 Clean Install & Cache Clear [5 min]**
```bash
cd /home/daen/Projects/cybersecsuite/src/frontend
rm -rf node_modules package-lock.json .npm
npm cache clean --force
npm install
```

**Expected:** React Query export errors may auto-resolve

**1.2 Remove JSX Style Attributes [10 min]**
```bash
# Bulk fix all <style jsx=> patterns
find src/components/orchestrator -name "*.tsx" -type f -print0 | \
  xargs -0 sed -i 's/<style jsx={true}>/<style>/g; s/<style jsx>/<style>/g'

# Verify
rg '<style jsx' src/
```

**Expected:** 15 jsx errors gone

**1.3 Fix Import Mismatches [10 min]**
```bash
# Fix named imports → default imports for UI components
find src -name "*.tsx" -type f -print0 | \
  xargs -0 sed -i \
    -e 's/import { Card } from/import Card from/g' \
    -e 's/import { Badge } from/import Badge from/g' \
    -e 's/import { Spinner } from/import Spinner from/g' \
    -e 's/import { Button } from/import Button from/g' \
    -e 's/import { Modal } from/import Modal from/g'

# Verify
npm run type-check 2>&1 | head -20
```

**Expected:** 8 export errors gone

**1.4 Test [5 min]**
```bash
npm run type-check
```

**If clean:** Skip to Phase 3 ✨  
**If errors remain:** Continue to Phase 2

---

### Phase 2: Medium Fixes (If Needed) [~1-1.5 hours]

**2.1 Fix Type-Only Imports [20 min]**

Create a script to find and fix:
```bash
# Find all type imports
rg 'import \{[^}]*(ReactNode|Dispatch|SetStateAction|RefObject)[^}]*\}' \
  --type tsx --type ts src/ > /tmp/type-imports.txt

# Manual review + fix
cat /tmp/type-imports.txt
```

Then fix each file:
```tsx
// Before
import { ReactNode, useState } from 'react'

// After  
import { useState } from 'react'
import type { ReactNode } from 'react'
```

**2.2 Add Parameter Type Annotations [30 min]**

Find implicit any parameters:
```bash
rg 'const \w+ = \([a-z][\w]*\) =>' --type tsx src/ | head -20
```

For each, add types using context:
```tsx
// Before
const map = (t) => t.id

// After (infer from usage)
const map = (t: Template) => t.id
```

**2.3 Fix Type Assignment Conflicts [20 min]**

Review setState callbacks, ensure types match:
```tsx
// Find mismatches
rg 'useState<' --type tsx src/ | grep -i job | head -10
```

Align callback types to state types.

**2.4 Add Missing Dependencies [5 min]**
```bash
npm install --save-dev @types/node
npm run type-check
```

---

### Phase 3: Validation [~15 min]

**3.1 Full Type Check**
```bash
npm run type-check
```

**Expected Output:**
```
✓ No errors detected
```

**3.2 Full Build**
```bash
npm run build
```

**Expected Output:**
```
✓ 1234 modules transformed
✓ Build complete!
```

**3.3 Verify Phase 5E Components**
```bash
# Check specific files compile
npx tsc --noEmit src/components/workers/WorkerList.tsx
npx tsc --noEmit src/components/workers/WorkerDetail.tsx
npx tsc --noEmit src/components/workers/ExecutionTimeline.tsx
```

**Expected:** All pass with no errors

---

## ✅ Success Checklist

- [ ] `npm run type-check` outputs: "No errors detected"
- [ ] `npm run build` completes successfully
- [ ] No TypeScript errors in VSCode
- [ ] All Phase 5E components (t374-t379) import correctly
- [ ] useWorkers hook compiles
- [ ] useWorkerDetail compiles
- [ ] useWorkerMetrics compiles
- [ ] All worker components have no red squiggles
- [ ] Build time < 15 seconds
- [ ] No warnings in console

---

## 📋 Detailed Files to Fix

### Group 1: Remove JSX Attributes (15 files)
```
src/components/orchestrator/
├── APIKeyManager.tsx (line 127)
├── AlertPreferences.tsx (line 117)
├── AnalyticsDashboard.tsx (line 201)
├── BatchScheduler.tsx (line 197)
├── ConfigForm.tsx (line 62)
├── ConfigHistory.tsx (line 59)
├── ConfigManager.tsx (line 158)
├── HealthDashboard.tsx (line 186)
├── JobList.tsx (line 59)
├── LogsViewer.tsx (line 69)
├── MetricsCharts.tsx (line 86)
├── Navigation.tsx (line 93)
├── NotificationCenter.tsx (line 141)
├── ScheduleForm.tsx (line 165)
├── StatusOverview.tsx (line 90)
├── TemplateBuilder.tsx (line 208)
└── (and others)
```

### Group 2: Fix Import Statements (Multiple files)
```
src/components/workers/
├── WorkerList.tsx
├── WorkerDetail.tsx
├── ExecutionTimeline.tsx
├── MetricsCard.tsx
└── BatchOperations.tsx

src/components/orchestrator/*.tsx
src/components/ui/*.tsx
```

### Group 3: Add Type Annotations (Various)
```
Arrow functions with implicit any parameters
- SearchPanel.tsx
- RoutingPanel.tsx
- QolPanel.tsx (referenced in resources)
- etc.
```

---

## 🎯 Expected Timeline

| Phase | Task | Duration | Impact |
|-------|------|----------|--------|
| 1.1 | Clean install + cache clear | 5 min | ~28 errors (maybe) |
| 1.2 | Remove JSX attributes | 10 min | 15 errors |
| 1.3 | Fix import mismatches | 10 min | 8 errors |
| 1.4 | Test build | 5 min | Validate |
| **SUBTOTAL** | | **30 min** | **~50 errors** |
| 2.1 | Type-only imports | 20 min | 12 errors |
| 2.2 | Parameter types | 30 min | 10 errors |
| 2.3 | Type conflicts | 20 min | 15 errors |
| 2.4 | Missing deps | 5 min | 3 errors |
| **SUBTOTAL** | | **75 min** | **~40 errors** |
| 3 | Validation | 15 min | Confirm clean |
| **TOTAL** | | **~120 min** | **110+ errors → 0** |

**If clean install fixes React Query:** ~30 minutes total ✨

---

## 🔗 Phase 5E Blocker Resolution

Once TypeScript is fixed:
1. ✅ Frontend build succeeds
2. ✅ Can validate Phase 5E components
3. ✅ Can proceed with component completion (t374-t379)
4. ✅ Can write frontend tests
5. ✅ Can deploy Phase 5E

**This fix unblocks:** 18-28 hours of Phase 5E work

---

## 📌 Notes

- **Priority:** This is the CRITICAL blocker preventing Phase 5E progress
- **Recommendation:** Start with clean install (Phase 1.1) — often fixes everything
- **If issues:** Follow Phase 2 sequentially, test after each fix
- **Success:** When `npm run build` produces zero errors
- **Next:** After TypeScript fix, begin Phase 5E component completion work

---

**Status:** Ready to execute. Recommend starting immediately with Phase 1.1 (clean install).
