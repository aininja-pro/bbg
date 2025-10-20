# Frontend Guideline Document

This document describes the frontend setup for the BBG Rebate Processing Automation Tool. It explains the architecture, design principles, styles, components, state management, routing, performance optimizations, testing strategy, and how everything fits together.

## 1. Frontend Architecture

### 1.1 Overview
- **Framework:** React 18 (single-page application) 
- **Styling:** Tailwind CSS (utility-first)  
- **UI Library:** shadcn/ui components for common patterns (buttons, modals, forms)  
- **File Upload:** React Dropzone  
- **Data Preview:** TanStack Table or AG Grid for tabular data  
- **Build & Deploy:** Vercel (automatic builds from the main branch)  

### 1.2 Structure & Folder Layout
```
src/
├── components/       # Reusable presentational & layout components
├── pages/            # Route-level pages (Upload, Preview, Rules, Lookups)
├── hooks/            # Custom React hooks (useUpload, useRules, useLookups)
├── contexts/         # React Context providers (AppContext)
├── services/         # API calls (REST functions to FastAPI)
├── utils/            # Utility functions (date conversion, validation)
├── assets/           # Static assets (icons, images)
└── App.jsx           # Entry point with Router & Context
```

### 1.3 Scalability, Maintainability & Performance
- **Modular code:** small, focused components and hooks allow independent updates and easy testing.  
- **Code splitting:** lazy-load pages and heavy components (e.g., AG Grid) to reduce initial bundle size.  
- **Tailwind JIT:** removes unused styles at build time, keeping CSS minimal.  
- **Well-defined services:** encapsulate API calls so backend changes (endpoints, payloads) are isolated.

## 2. Design Principles

### 2.1 Key Principles
- **Usability:** Simple, clear workflows—upload, preview, export.  
- **Consistency:** Uniform components, spacing, and typography throughout.  
- **Accessibility:** Follow WCAG guidelines (semantic HTML, aria-labels, keyboard navigation).  
- **Responsiveness:** Layout adapts from small screens (table horizontal scroll) to desktops.  
- **Feedback:** Real-time progress bars, inline validation messages, clear error vs. warning states.

### 2.2 Applying Principles
- Forms and buttons use consistent focus and hover states (Tailwind focus:ring).  
- Tables show loading skeletons during data fetch.  
- Modal dialogs trap focus and return it when closed.  
- Color and contrast ratios meet accessibility standards (4.5:1 for text).

## 3. Styling and Theming

### 3.1 Styling Approach
- **Utility-First:** Tailwind CSS for margins, padding, typography, colors.  
- **Component Styles:** shadcn/ui styled with Tailwind classes.  
- **No preprocessors:** rely on Tailwind’s configuration file for custom theming.

### 3.2 Theming
- Single, neutral theme—no user-selectable themes in Phase 1.  
- All colors defined in `tailwind.config.js` under `theme.extend.colors`.

### 3.3 Visual Style
- **Design Style:** Flat, modern UI with subtle shadows (for cards/modals) and rounded corners (border-radius: 0.5rem).  
- **Glassmorphism Accents:** Light glass panels for modals with `backdrop-filter: blur(8px)` and semi-transparent backgrounds.

### 3.4 Color Palette
- Primary Blue: #3B82F6 (buttons, links)  
- Success Green: #10B981 (success messages)  
- Warning Amber: #F59E0B (warnings)  
- Danger Red: #EF4444 (errors)  
- Neutral Gray (light): #F9FAFB (background)  
- Neutral Gray (dark): #374151 (text)  
- White: #FFFFFF  

### 3.5 Typography
- **Font Family:** Inter, system-fallback (`font-sans`).  
- **Headings:** 600 weight, scalable sizes (h1–h4).  
- **Body Text:** 400 weight, base size 1rem, line-height 1.5.

## 4. Component Structure

- **Atomic Components:** Buttons, Inputs, Modals, Tables—located in `components/ui/`.  
- **Feature Components:** UploadForm, PreviewTable, RulesManager, LookupsManager—grouped by page.  
- **Containers vs. Presentational:** Containers handle data (fetching, state), then pass props to presentational UI components.  
- **Reusability:** Generic form fields and table cell renderers reduce duplication.

Benefits:
- Easier testing and isolation of UI pieces.  
- Clear separation of concerns—presentation vs. logic.  
- Faster onboarding for new developers.

## 5. State Management

### 5.1 Approach
- **Local State:** `useState` for ephemeral values (form inputs, modal open state).  
- **Global State:** React Context + `useReducer` for shared data—upload status, rules list, lookup tables.  
- **Data Fetching:** custom hooks in `services/` that use `fetch` or Axios + caching in Context.

### 5.2 Data Flow
1. **Upload Flow:** UploadForm → onDrop → service.uploadFile → update `uploadStatus` in Context.  
2. **Preview Flow:** service.fetchPreview → store preview rows in Context → PreviewTable reads from Context.  
3. **Rules & Lookups:** Context holds arrays; actions dispatched for add/edit/delete; UI re-renders automatically.

## 6. Routing and Navigation

- **Library:** React Router v6.  
- **Routes:**   
  • `/` → Upload & Preview page  
  • `/rules` → Rules Management page  
  • `/lookups` → Lookup Management page  
- **Navigation:** Header/Navbar component with links; active link highlighted.  
- **Nested Routes:** Modal routes for “Add Rule” or “Edit Lookup” open on top of parent route.

## 7. Performance Optimization

- **Lazy Loading:** `React.lazy` + `Suspense` for pages and heavy components (AG Grid).  
- **Tree Shaking:** only import needed functions from large libraries (e.g., Pandas-like helper libraries).  
- **Memoization:** `React.memo` and `useMemo` for large tables, computed rows.  
- **Virtualized Tables:** AG Grid or TanStack Table virtualization for 600+ rows.  
- **Asset Optimization:** SVG icons inlined, no large image bundles.  
- **Tailwind Purge:** drop unused CSS classes in production build.

## 8. Testing and Quality Assurance

### 8.1 Unit Tests
- **Framework:** Jest + React Testing Library.  
- **Scope:** components render correctly, validation functions, hooks behavior.

### 8.2 Integration Tests
- **Framework:** React Testing Library (combined with mocking of service calls).  
- **Scope:** full flows: upload & preview, adding a rule, editing a lookup.

### 8.3 End-to-End Tests
- **Framework:** Cypress.  
- **Scope:** simulate user, upload a sample .xlsm, preview data, add a rule, export CSV, verify ZIP contents.

### 8.4 Linting & Formatting
- **ESLint:** Airbnb config + React rules.  
- **Prettier:** consistent code formatting.  
- **CI Checks:** run lint, type checks (if TS used), and tests on each pull request.

## 9. Conclusion and Overall Frontend Summary

This frontend is built as a modern React SPA with clear separation of concerns, a utility-first styling approach, and well-defined patterns for components, state, and routing. It focuses on usability (simple flows, real-time feedback), accessibility (semantic markup, contrast), and performance (lazy loading, virtualization). Testing at multiple levels ensures reliability. This setup meets project goals: fast processing previews, self-service rule and lookup management, batch CSV exports, and zero friction for internal users.