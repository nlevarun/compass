# Compass Design System

Quick reference for maintaining consistent UI design across all components.

## Color Palette

### Primary Colors
```css
Indigo 600: #4F46E5  /* Primary actions, brand */
Indigo 700: #4338CA  /* Hover states */
Indigo 50:  #EEF2FF  /* Light backgrounds */
Indigo 100: #E0E7FF  /* Badges, subtle highlights */
```

### Semantic Colors
```css
/* Success - Green */
Green 500: #10B981  /* Success states, connected */
Green 50:  #F0FDF4  /* Success backgrounds */

/* Warning - Amber */
Yellow 500: #F59E0B  /* Medium priority, warnings */
Yellow 50:  #FFFBEB  /* Warning backgrounds */

/* Danger - Red */
Red 500: #EF4444    /* High priority, errors */
Red 50:  #FEF2F2    /* Error backgrounds */

/* Info - Blue */
Blue 500: #3B82F6   /* Informational */
Blue 50:  #EFF6FF   /* Info backgrounds */
```

### Neutrals (Grays)
```css
Gray 50:  #F9FAFB  /* Page background */
Gray 100: #F3F4F6  /* Card hover, secondary backgrounds */
Gray 200: #E5E7EB  /* Borders, dividers */
Gray 600: #4B5563  /* Secondary text */
Gray 900: #111827  /* Primary text */
```

### Usage Examples
```jsx
// Primary button
className="bg-indigo-600 hover:bg-indigo-700 text-white"

// Secondary button
className="bg-white hover:bg-gray-50 border border-gray-300 text-gray-700"

// Success badge
className="bg-green-100 text-green-800 border border-green-200"

// High priority badge
className="bg-red-100 text-red-800 border border-red-200"
```

## Typography

### Font Family
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Font Sizes
```css
text-xs:   12px / 1rem      /* Small labels, timestamps */
text-sm:   14px / 1.25rem   /* Secondary text, descriptions */
text-base: 16px / 1.5rem    /* Body text (default) */
text-lg:   18px / 1.75rem   /* Section headers */
text-xl:   20px / 1.75rem   /* Card titles */
text-2xl:  24px / 2rem      /* Page titles */
text-3xl:  30px / 2.25rem   /* Hero titles */
```

### Font Weights
```css
font-normal:    400  /* Body text */
font-medium:    500  /* Buttons, labels */
font-semibold:  600  /* Headings, emphasis */
font-bold:      700  /* Strong emphasis */
```

### Usage Examples
```jsx
// Page title
<h1 className="text-2xl font-semibold text-gray-900">

// Card title
<h3 className="text-lg font-semibold text-gray-900">

// Body text
<p className="text-base text-gray-600">

// Small label
<span className="text-xs font-medium text-gray-600 uppercase">
```

## Spacing

### Base Unit: 4px (0.25rem)
```css
Gap sizes (multiples of 4):
space-2:  8px   /* Tight spacing (buttons, badges) */
space-3:  12px  /* Standard spacing (cards) */
space-4:  16px  /* Medium spacing (sections) */
space-6:  24px  /* Large spacing (major sections) */
space-8:  32px  /* XL spacing (page sections) */
```

### Usage Examples
```jsx
// Card padding
<div className="p-5">  {/* 20px = 5 × 4px */}

// Section gaps
<div className="space-y-8">  {/* 32px between items */}

// Button group
<div className="flex items-center space-x-3">  {/* 12px gap */}
```

## Border Radius

```css
rounded:    8px   /* Default (cards, buttons, inputs) */
rounded-lg: 12px  /* Large (hero sections, modals) */
rounded-xl: 16px  /* XL (app logo, special cards) */
rounded-full:     /* Circles (avatars, badges) */
```

### Usage Examples
```jsx
// Standard card
<div className="rounded-lg">

// Button
<button className="rounded-lg">

// Avatar
<div className="rounded-lg w-10 h-10">
```

## Shadows

```css
shadow-sm:  Subtle (cards at rest)
shadow:     Standard (cards on hover)
shadow-md:  Medium (dropdowns, popovers)
shadow-lg:  Large (modals, dialogs)
```

### Usage Examples
```jsx
// Card
<div className="shadow-sm hover:shadow-md">

// Modal
<div className="shadow-2xl">
```

## Components

### Buttons

#### Primary Button
```jsx
<button className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm">
  <svg className="w-4 h-4 mr-2">...</svg>
  Button Text
</button>
```

#### Secondary Button
```jsx
<button className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-gray-700 bg-white rounded-lg hover:bg-gray-50 border border-gray-300 transition-colors">
  Button Text
</button>
```

#### Icon Button
```jsx
<button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50 transition-colors">
  <svg className="w-5 h-5">...</svg>
</button>
```

### Cards

#### Standard Card
```jsx
<div className="bg-white rounded-lg border border-gray-200 p-5 hover:border-gray-300 transition-colors">
  {/* Content */}
</div>
```

#### Hero Card (gradient background)
```jsx
<div className="bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-100 p-8">
  {/* Content */}
</div>
```

#### Stats Card
```jsx
<div className="bg-white rounded-lg border border-gray-200 p-5">
  <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">
    Label
  </p>
  <p className="text-2xl font-semibold text-gray-900">
    Value
  </p>
  <p className="text-xs text-gray-500 mt-0.5">
    Subtext
  </p>
</div>
```

### Badges

#### Status Badge
```jsx
<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
  <svg className="w-3 h-3 mr-1">...</svg>
  Connected
</span>
```

#### Priority Badge
```jsx
<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
  🔴 HIGH
</span>
```

#### Count Badge
```jsx
<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-200">
  45 mentions
</span>
```

### Icons

#### Size Guidelines
```css
w-4 h-4:  16px  /* Inline with text, button icons */
w-5 h-5:  20px  /* Navigation, toolbar */
w-6 h-6:  24px  /* Section icons */
w-8 h-8:  32px  /* Hero sections */
w-10 h-10: 40px /* Large feature icons */
```

#### Icon Colors
```jsx
// Default (inactive)
<svg className="w-5 h-5 text-gray-400">

// Active
<svg className="w-5 h-5 text-indigo-600">

// Hover
<svg className="w-5 h-5 text-gray-400 group-hover:text-gray-600">
```

### Empty States

```jsx
<div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12">
  <div className="text-center">
    <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-200 rounded-full mb-4">
      <svg className="w-8 h-8 text-gray-400">...</svg>
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">
      No data yet
    </h3>
    <p className="text-gray-600 mb-6 max-w-md mx-auto">
      Description of what to do next.
    </p>
    <button className="...">
      Action Button
    </button>
  </div>
</div>
```

### Loading States

#### Spinner
```jsx
<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
```

#### Button Loading
```jsx
<button disabled className="...">
  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
  Loading...
</button>
```

## Layout

### Container
```jsx
<div className="max-w-7xl mx-auto px-6">
  {/* Content */}
</div>
```

### Grid Layouts
```jsx
// 3 column grid
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">

// 4 column grid
<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
```

### Flex Layouts
```jsx
// Space between
<div className="flex items-center justify-between">

// Centered
<div className="flex items-center justify-center">

// Horizontal list with gaps
<div className="flex items-center space-x-3">

// Vertical list with gaps
<div className="flex flex-col space-y-4">
```

## Animations

### Transitions
```css
transition-colors  /* Color changes (hover, active) */
transition-all     /* Everything (use sparingly) */
```

### Usage
```jsx
<button className="hover:bg-indigo-700 transition-colors">

<div className="hover:shadow-md transition-all">
```

## Responsive Design

### Breakpoints
```css
sm:  640px   /* Small tablets */
md:  768px   /* Tablets */
lg:  1024px  /* Desktops */
xl:  1280px  /* Large desktops */
```

### Usage
```jsx
// Stack on mobile, row on desktop
<div className="flex flex-col md:flex-row">

// 1 column mobile, 3 columns desktop
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
```

## Best Practices

### DO ✅
- Use consistent spacing (multiples of 4px)
- Keep text readable (min 16px base)
- Use semantic colors (green = success, red = error)
- Add hover states to interactive elements
- Use loading states for async actions
- Show helpful empty states
- Maintain visual hierarchy (size, weight, color)

### DON'T ❌
- Mix different spacing systems
- Use tiny text (< 12px)
- Use colors randomly
- Forget hover/focus states
- Show blank screens during loading
- Use technical jargon in UI
- Make everything the same size

## Accessibility

### Color Contrast
- Text on white: Use gray-900, gray-700, or gray-600
- White text: Only on dark backgrounds (indigo-600+)
- Badges: Always include border for definition

### Interactive Elements
- Minimum touch target: 44×44px
- Clear focus states (add `focus:ring-2 focus:ring-indigo-500`)
- Descriptive labels (use `aria-label` for icon buttons)

### Example
```jsx
<button
  aria-label="Close dialog"
  className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg"
>
  <svg>...</svg>
</button>
```

## Quick Reference

### Common Patterns

#### Section Header
```jsx
<div className="flex items-center justify-between mb-4">
  <h3 className="text-lg font-semibold text-gray-900">Section Title</h3>
  <span className="text-sm text-gray-500">Metadata</span>
</div>
```

#### Card with Icon
```jsx
<div className="bg-white rounded-lg border border-gray-200 p-5">
  <div className="flex items-start space-x-4">
    <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
      <svg className="w-6 h-6">...</svg>
    </div>
    <div className="flex-1">
      <h4 className="text-base font-semibold text-gray-900 mb-1">Title</h4>
      <p className="text-sm text-gray-600">Description</p>
    </div>
  </div>
</div>
```

#### Metric Display
```jsx
<div className="flex items-center space-x-2">
  <svg className="w-4 h-4 text-gray-400">...</svg>
  <span className="text-sm text-gray-700">
    <span className="font-medium">150</span> requests
  </span>
</div>
```

---

**Remember:** Consistency is more important than novelty. When in doubt, follow existing patterns.
