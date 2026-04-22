# Phase 7C: Slash/Mention Commands — Quick Reference

**Time Estimate:** 10–12 hours  
**Todos:** T151–T165 (15 todos)  
**Dependencies:** Phase 7C components (T070–T075) + messaging integration  

---

## Feature Summary

| Trigger | Type | Use | Examples |
|---------|------|-----|----------|
| `/` | Command | Execute forensic tasks | `/analyze`, `/extract`, `/search` |
| `@` | Mention | Reference entities | `@case:INC-2024-001`, `@ioc:1.2.3.4` |

---

## Implementation Checklist

### Part A: Components (5.5 hours, T151–T155)

- [ ] **T151:** CommandMenu.tsx
  - File filtering, keyboard nav, hover effects
  - Render COMMANDS list, highlight selected index
  - Export: `CommandMenu` component

- [ ] **T152:** MentionMenu.tsx
  - Async search with 300ms debounce
  - Loading state indicator
  - Export: `MentionMenu` component

- [ ] **T153:** Menu positioning & animation
  - Calculate cursor X position (measure text width in canvas)
  - Viewport-aware placement (check if menu goes off-screen)
  - Fade-in animation (SCSS)

- [ ] **T154:** useCommandMenu hook
  - Track input changes, detect `/` or `@` at cursor
  - Keyboard handler (arrow keys, Enter, Escape)
  - State: `menuState`, `handleInput()`, `closeMenu()`

- [ ] **T155:** Type schemas
  - `src/frontend/src/types/commands.ts`
  - Command, Mention, MenuState, MentionResult, CommandContext

### Part B: Integration (5 hours, T156–T160)

- [ ] **T156:** SendMessagePrompt.tsx integration
  - Import hook + components
  - Trigger detection on input change
  - Menu open/close/render logic

- [ ] **T157:** Command execution
  - Template expansion (replace `{context}` with selection)
  - Special handling for `/open-panel` → `setActiveTab()`
  - Auto-send if template exists

- [ ] **T158:** Mention insertion
  - Find `@` position in text
  - Replace from `@` to cursor with formatted mention
  - Validate reference exists (e.g., case ID is valid)

- [ ] **T159:** Keyboard shortcuts
  - Ctrl+K = focus input + open menu
  - Alt+1..9 = quick-open frequent commands
  - Document shortcuts

- [ ] **T160:** State cleanup
  - Close menu on blur, Escape, outside click
  - Reset selectedIndex when query changes
  - Prevent memory leaks

### Part C: Testing & Docs (4.5 hours, T161–T165)

- [ ] **T161:** E2E tests (Playwright)
  - `/` triggers command menu
  - Keyboard navigation (arrow up/down/enter)
  - Escape closes, input preserved
  - Mention menu API search
  - Success: All tests pass

- [ ] **T162:** Unit tests
  - Command filtering (case-insensitive search)
  - Menu position calculation
  - Mention formatting
  - Success: >90% coverage

- [ ] **T163:** User docs
  - `docs/features/slash-commands-usage.md`
  - Command list + examples
  - Keyboard shortcuts
  - Tips & tricks

- [ ] **T164:** Developer docs
  - How to add new commands
  - How to add new mention types
  - API contract for mention search endpoint

- [ ] **T165:** Polish & accessibility
  - ARIA roles (listbox, option, aria-selected)
  - Focus trap while menu open
  - Screen reader support (results count)
  - High contrast colors (light/dark mode)
  - Mobile keyboard support

---

## Command List

### Slash Commands (/)

| Command | Template | Requires Selection | Use Case |
|---------|----------|-------------------|----------|
| `/analyze` | "Analyze the following IOC:\n" | Yes | Type detection + analysis |
| `/summarize` | "Please summarize:\n" | Yes | Long text reduction |
| `/extract` | "Extract all IOCs:\n" | Yes | Auto-extract CVEs, IPs, domains |
| `/search` | "Search for: " | No | Query forensic database |
| `/create-case` | "Create case: " | No | New investigation |
| `/open-panel` | "Open panel: " | No | Switch tab (chat, forensics, etc.) |
| `/help` | — | No | Show command list |

### Mention Types (@)

| Type | Prefix | Format | Search Endpoint | Example |
|------|--------|--------|-----------------|---------|
| Case | `@case` | `@case:INC-2024-001` | `/api/search/cases?q=` | @case:INC-2024-001 |
| Report | `@report` | `@report:APT-001` | `/api/search/reports?q=` | @report:APT-001 |
| IOC | `@ioc` | `@ioc:1.2.3.4` | `/api/search/iocs?q=` | @ioc:1.2.3.4 |
| File | `@file` | `@file:evidence-001.pcap` | `/api/search/files?q=` | @file:evidence.pcap |
| Workspace | `@workspace` | `@workspace:team-a` | `/api/search/workspaces?q=` | @workspace:team-a |

---

## Key Code Paths

### 1. Trigger Detection

**File:** `useCommandMenu.ts`
```typescript
if (text[pos - 1] === '/') {
  // Show command menu
  setMenuState({ open: true, type: 'command', query: text.slice(pos) })
}
```

### 2. Keyboard Navigation

**File:** `useCommandMenu.ts`
```typescript
case 'ArrowDown':
  setMenuState(prev => ({
    selectedIndex: Math.min(prev.items.length - 1, prev.selectedIndex + 1)
  }))
case 'Enter':
  handleSelectItem(menuState.items[menuState.selectedIndex])
```

### 3. Command Execution

**File:** `SendMessagePrompt.tsx`
```typescript
const executeCommand = (command: Command) => {
  let msg = command.template || ''
  if (command.requiresSelection && selectedText) {
    msg = msg.replace('{context}', selectedText)
  }
  setMessage(msg)
}
```

### 4. Mention Insertion

**File:** `SendMessagePrompt.tsx`
```typescript
const lastAt = message.lastIndexOf('@', cursorPos)
const newMsg = message.slice(0, lastAt) + mention + message.slice(cursorPos)
setMessage(newMsg)
```

---

## File Structure

```
src/frontend/src/
├── components/
│   ├── ui/
│   │   ├── CommandMenu.tsx
│   │   ├── CommandMenu.scss
│   │   ├── MentionMenu.tsx
│   │   ├── MentionMenu.scss
│   ├── layout/
│   │   └── SendMessagePrompt.tsx (modified)
├── types/
│   └── commands.ts
├── hooks/
│   └── useCommandMenu.ts
├── config/
│   └── commands.ts
├── utils/
│   └── commandHelpers.ts (optional)
│
tests/
├── unit/
│   └── commands.test.ts
├── e2e/
│   └── slash-mentions.spec.ts
```

---

## Dependencies

```
T151 → T156 (components needed before integration)
T152 → T156
T154 → T156
T156 → T157 (need integration before execution)
T156 → T158 (need integration before insertion)
T157 → T162 (need executor for unit tests)
T158 → T161 (need insertion for e2e tests)
```

---

## Testing Checklist

### E2E (Playwright)
- [ ] Command menu appears on `/`
- [ ] Mention menu appears on `@`
- [ ] Arrow keys navigate both menus
- [ ] Enter/Tab selects highlighted item
- [ ] Escape closes and preserves input
- [ ] Click on menu item selects it
- [ ] Hover highlights correctly
- [ ] Menu positions correctly (not off-screen)
- [ ] Mention API search works (200ms debounce)
- [ ] Loading indicator appears during search

### Unit Tests
- [ ] Command filtering (case-insensitive)
- [ ] Menu position calculation
- [ ] Mention formatting
- [ ] Query parsing (extract trigger + query)
- [ ] Selected index bounds (0 ≤ index < items.length)
- [ ] Empty query behavior
- [ ] Special chars in query (escaped)

### Manual Verification
- [ ] Tab through all commands, verify descriptions accurate
- [ ] Type partial command (e.g., `/ana`), confirm filter works
- [ ] Test with long input (menu still visible, positioned correctly)
- [ ] Test on mobile device (no touch-only issues)
- [ ] Test in light/dark modes (high contrast)
- [ ] Test with screen reader (ARIA labels read correctly)
- [ ] Test keyboard-only navigation (no mouse needed)

---

## Success Criteria

✅ All 15 todos marked `done`  
✅ E2E tests passing (Playwright)  
✅ No console errors in browser  
✅ Menu animations smooth (<100ms)  
✅ Keyboard nav instant (no lag)  
✅ ARIA labels correct  
✅ Mention API returns results  
✅ Commands execute correctly  
✅ User docs complete  
✅ Code reviewed & approved  

---

## Notes

- **Performance:** Keep COMMANDS list < 50 items (if more, pagination needed)
- **Accessibility:** Use `role="listbox"`, `aria-selected`, proper focus management
- **Mobile:** Test with on-screen keyboard (iOS/Android)
- **Search debounce:** 300ms optimal for UX (fast response, minimal API calls)
- **Future:** Ctrl+K can open global command palette (Discord/Slack pattern)

---

**Status:** Ready for implementation  
**Next:** Start T151 after Phase 7C components (T070–T075) approved
