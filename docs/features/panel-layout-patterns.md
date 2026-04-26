# Panel Layout Documentation

## Overview

Panel layouts are used throughout the CyberSecSuite dashboard to organize and display content in flexible, reusable containers. This document describes the patterns, best practices, and implementation guidelines for panel layouts.

## Panel Layout Patterns

### Basic Panel Structure

```html
<div class="panel">
  <div class="panel-header">
    <h2 class="panel-title">Panel Title</h2>
    <div class="panel-actions">
      <!-- Action buttons -->
    </div>
  </div>
  <div class="panel-content">
    <!-- Panel content goes here -->
  </div>
  <div class="panel-footer">
    <!-- Footer content (optional) -->
  </div>
</div>
```

### CSS Classes

#### Core Classes
- `.panel` - Main container
- `.panel-header` - Header section
- `.panel-title` - Title element
- `.panel-content` - Main content area
- `.panel-footer` - Footer section
- `.panel-actions` - Action buttons container

#### Modifier Classes
- `.panel-compact` - Reduced padding/spacing
- `.panel-full-height` - Stretch to full height
- `.panel-bordered` - Add border
- `.panel-card` - Card-style appearance
- `.panel-elevated` - Shadow/elevation
- `.panel-collapsible` - Allow collapse/expand

#### State Classes
- `.panel-loading` - Show loading state
- `.panel-error` - Show error state
- `.panel-empty` - Show empty state
- `.panel-disabled` - Disabled state

## Component Patterns

### Collapsible Panel

```html
<div class="panel panel-collapsible">
  <div class="panel-header" role="button" aria-expanded="true">
    <h2 class="panel-title">Collapsible Panel</h2>
    <span class="collapse-icon">▼</span>
  </div>
  <div class="panel-content panel-content-collapsed">
    <!-- Content hidden when collapsed -->
  </div>
</div>
```

### Tabbed Panel

```html
<div class="panel">
  <div class="panel-header">
    <div class="panel-tabs">
      <button class="panel-tab active" data-tab="tab1">Tab 1</button>
      <button class="panel-tab" data-tab="tab2">Tab 2</button>
    </div>
  </div>
  <div class="panel-content">
    <div class="panel-tab-content" id="tab1">Tab 1 Content</div>
    <div class="panel-tab-content" id="tab2" style="display:none">Tab 2 Content</div>
  </div>
</div>
```

### Split Panel

```html
<div class="panel panel-split">
  <div class="panel-split-left">
    <div class="panel-header">Left Panel</div>
    <div class="panel-content">Left Content</div>
  </div>
  <div class="panel-split-right">
    <div class="panel-header">Right Panel</div>
    <div class="panel-content">Right Content</div>
  </div>
</div>
```

## Best Practices

### 1. Semantic HTML
- Use appropriate heading levels (`<h2>`, `<h3>`, etc.)
- Include `role` attributes for interactive elements
- Ensure keyboard navigation support

### 2. Responsive Design
- Use CSS Grid or Flexbox for layout
- Stack panels vertically on mobile devices
- Ensure content remains readable at all screen sizes

### 3. Accessibility
- Provide alt text for images
- Ensure sufficient color contrast
- Test with screen readers
- Support keyboard-only navigation

### 4. Performance
- Lazy load content when appropriate
- Minimize DOM complexity
- Use CSS containment for performance
- Debounce resize/scroll events

### 5. State Management
- Persist panel state to localStorage when needed
- Provide visual feedback for state changes
- Handle loading/error states gracefully
- Show empty states for no data

## Loading States

```html
<div class="panel panel-loading">
  <div class="panel-content">
    <div class="loading-spinner"></div>
    <p>Loading...</p>
  </div>
</div>
```

## Error States

```html
<div class="panel panel-error">
  <div class="panel-content">
    <div class="error-icon">⚠️</div>
    <p>An error occurred while loading content</p>
    <button class="btn-retry">Retry</button>
  </div>
</div>
```

## Empty States

```html
<div class="panel panel-empty">
  <div class="panel-content">
    <div class="empty-icon">📭</div>
    <p>No data available</p>
  </div>
</div>
```

## React Component Example

```tsx
interface PanelProps {
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  footer?: React.ReactNode;
  collapsible?: boolean;
  loading?: boolean;
  error?: string;
  empty?: boolean;
}

export const Panel: React.FC<PanelProps> = ({
  title,
  children,
  actions,
  footer,
  collapsible = false,
  loading = false,
  error,
  empty = false,
}) => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  return (
    <div className={`panel ${collapsible ? 'panel-collapsible' : ''}`}>
      {title && (
        <div className="panel-header">
          {collapsible && (
            <button
              className="collapse-btn"
              onClick={() => setIsCollapsed(!isCollapsed)}
            >
              {isCollapsed ? '▶' : '▼'}
            </button>
          )}
          <h2 className="panel-title">{title}</h2>
          {actions && <div className="panel-actions">{actions}</div>}
        </div>
      )}
      {!isCollapsed && (
        <div className="panel-content">
          {loading && <div className="loading-spinner" />}
          {error && <div className="error-message">{error}</div>}
          {empty && <div className="empty-state">No data</div>}
          {!loading && !error && !empty && children}
        </div>
      )}
      {footer && <div className="panel-footer">{footer}</div>}
    </div>
  );
};
```

## Sizing Guidelines

### Standard Sizes
- **Small**: `max-width: 300px`
- **Medium**: `max-width: 500px`
- **Large**: `max-width: 800px`
- **Full**: `width: 100%`

### Padding Guidelines
- **Compact**: `8px` padding
- **Normal**: `16px` padding
- **Spacious**: `24px` padding

## Color and Styling

### Background Colors
- Default: `var(--surface-1)`
- Secondary: `var(--surface-2)`
- Accent: `var(--mode-color)`

### Border Styling
- Default border: `1px solid var(--border)`
- Focus border: `2px solid var(--mode-color)`

### Shadow
- Default: `0 2px 8px rgba(0,0,0,0.1)`
- Elevated: `0 4px 16px rgba(0,0,0,0.15)`

## Examples

### Agent Panel
Used for displaying agent configuration and status

### Settings Panel
Used for application settings and preferences

### Analysis Panel
Used for displaying analysis results and insights

### Chat Panel
Used for multi-turn conversations

## Migration Guide

### From Old System
Old panels should be migrated to the new panel layout system:

1. Identify existing panel HTML structure
2. Apply appropriate CSS classes
3. Update JavaScript event handlers
4. Test responsive behavior
5. Verify accessibility
6. Update documentation

## Troubleshooting

### Panel Not Displaying
- Check CSS classes are applied
- Verify width/height constraints
- Check z-index values
- Ensure parent container has proper layout

### Content Overflow
- Use `overflow-y: auto` for scrollable content
- Apply `word-break: break-word` for long text
- Use `text-overflow: ellipsis` for truncation

### Responsive Issues
- Check media queries
- Test on various screen sizes
- Ensure touch targets are at least 44x44px

## Resources

- [CyberSecSuite Dashboard Guide](../README.md)
- [CSS Containment](https://developer.mozilla.org/en-US/docs/Web/CSS/contain)
- [ARIA Patterns](https://www.w3.org/WAI/ARIA/apg/)
- [Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
