---
name: desktop-app-ux
description: Build React frontends that feel like native desktop applications (VS Code, Linear, Figma, Notion, Finder) instead of scrolling web pages. Use this skill whenever the user asks for a React app, dashboard, admin panel, editor, file manager, inbox, IDE-like tool, or internal tool, or says things like "desktop-like", "native feel", "app-like", "Electron/Tauri UI", "Mac/Windows app feel", "keyboard-driven", "command palette", "resizable panels", or "make the UI feel more professional/less like a website". Also use it when restyling an existing React UI that feels like a web page, even if the user never says "desktop".
---

# Desktop-app UX for React

Web pages are documents: they scroll, flow, and are decorated. Desktop apps are tools: they fill the window, keep chrome fixed, respond instantly to keyboard and mouse, and remember where you left off. The goal of this skill is to make React UIs behave like tools. Most of the "native feel" comes from behavior (keyboard, selection, context menus, persistence), not from visual styling, so do not stop at a sidebar and a dark theme.

Read `references/react-patterns.md` when you need code for hotkeys, the command palette, context menus, resizable panes, or the selection model. Prefer small hand-rolled implementations of these when the app is self-contained; suggest well-known libraries (e.g. `react-resizable-panels`, `cmdk`, Radix UI primitives) when the user has a real project with a package manager.

## 1. App shell

The window is the app. The page body never scrolls.

- `html, body, #root { height: 100%; overflow: hidden; }` and the root is a flex or grid shell.
- Structure: title/toolbar row (top), optional sidebar (left), main content (center), optional inspector (right), status bar (bottom). Use `display: grid` with `grid-template-columns` driven by pane sizes.
- Every pane that has overflowing content scrolls on its own (`overflow: auto; min-height: 0; min-width: 0`). Forgetting `min-height: 0` on flex children is the usual reason inner scrolling breaks.
- Sidebars and inspectors are collapsible (button plus shortcut), and splitters are draggable with a double-click to reset.
- Put a status bar at the bottom for ambient information: selection count, sync/save state, cursor position, connection status. Desktop users expect state to be visible without opening anything.

## 2. Keyboard is a first-class input

A desktop app that can only be used by mouse feels like a website.

- Register a central shortcut map rather than scattering `onKeyDown` handlers. Support `Mod` = Cmd on macOS and Ctrl elsewhere (detect via `navigator.platform` or `userAgentData`).
- Include the baseline set where it makes sense: `Mod+K` command palette, `Mod+S` save, `Mod+Z` / `Mod+Shift+Z` undo and redo, `Mod+F` find, `Mod+N` new, `Delete`/`Backspace` remove selection, `Esc` closes the top-most overlay or clears selection, `Mod+,` settings, `Mod+B` toggle sidebar.
- Lists, trees, and tables support arrow-key navigation, `Home`/`End`, `Enter` to open, `Space` to toggle, `Shift+Arrow` to extend selection, type-ahead where cheap.
- Show shortcut hints in menus, tooltips, and the command palette. Discoverability is what makes shortcuts get used.
- Call `preventDefault()` only for shortcuts you actually handle, and never hijack keys while the user is typing in an input unless the shortcut uses `Mod`.

## 3. Command palette and menus

- A command palette (`Mod+K`) lists every action in the app, fuzzy-searchable, with shortcut hints. Build actions as a single registry (`id`, `title`, `shortcut`, `run`) and drive the palette, menu bar, context menus, and hotkeys from it so they never drift apart.
- Provide a menu bar or toolbar menus (File / Edit / View) for apps with more than a handful of actions. Menus open on click, then switch on hover while one is open, and close on `Esc` or outside click.
- Right-click opens a context menu appropriate to the clicked object. Suppress the browser's native menu only on app surfaces (not on text inputs or links where the native menu is useful). Position the menu within the viewport.
- Disable (grey out) unavailable actions instead of hiding them, so menus keep a stable shape.

## 4. Selection, focus, and direct manipulation

- Model selection explicitly (a `Set` of ids plus an anchor) so click, `Ctrl/Cmd+Click` (toggle), and `Shift+Click` (range) behave as in Finder or Explorer. Double-click opens or renames; `F2` renames inline.
- Drag and drop for reordering, moving between panes, and dropping files in. Show a drop indicator, and make the drop target obvious.
- Focus is visible and sensible: a clear `:focus-visible` ring, focus moves into a dialog on open and returns on close, and `Tab` order follows layout. A desktop-style UI has one active pane at a time; dim or mark inactive panes subtly.
- Undo/redo for destructive and structural edits. Prefer undo over "Are you sure?" confirmations; reserve confirmation dialogs for irreversible actions.

## 5. Look and feel

Visual choices should signal "tool", not "marketing site".

- **Density:** compact. Row heights 24-32px, body text 12-14px, tight padding (4-8px). Use `font-size` and spacing tokens so a density toggle is easy.
- **Fonts:** the system stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`) so the app matches the OS. Monospace for code, IDs, and numbers that should align (`font-variant-numeric: tabular-nums`).
- **Chrome is not selectable and not a link:** `user-select: none` on toolbars, tabs, sidebars, and buttons; `cursor: default` on controls (pointer cursors are a web convention). Keep `user-select: text` on content people may want to copy.
- **Surfaces:** flat, with 1px hairline borders and subtle background steps between panes instead of heavy shadows and large radii. Radii 4-6px. Reserve shadows for floating layers (menus, popovers, dialogs).
- **Motion:** near-instant. 80-150ms on hover/press and overlays, no page-style entrance animations, no scroll-jacking. Respect `prefers-reduced-motion`.
- **Theme:** define colors as CSS variables; follow `prefers-color-scheme`; offer a manual override; pick one accent color and use it sparingly for selection and primary actions. Selection color should read as the OS selection (a solid accent row with light text, a lighter tint when the pane is inactive).
- **Scrollbars:** thin, themed (`scrollbar-width: thin`, `::-webkit-scrollbar`), shown inside panes, never on the body.
- **Icons:** one consistent set (e.g. lucide-react) at 14-16px, paired with labels or tooltips.
- Disable pull-to-refresh and overscroll bounce on the shell (`overscroll-behavior: none`) and avoid text-selection flicker on double-click of chrome.

## 6. Windows, tabs, and overlays

- Multi-document apps use tabs: closable, reorderable by drag, middle-click closes, `Mod+W` closes, `Mod+Tab` or `Ctrl+Tab` cycles, dirty indicator dot for unsaved changes.
- Dialogs are modal with a focus trap, `Esc` to dismiss, `Enter` for the primary button, and the destructive/cancel button not default-focused for dangerous actions. Use sheets or inspectors rather than dialogs for anything the user will tweak repeatedly.
- Tooltips appear after ~500ms, include the shortcut, and never block interaction. Toasts are small, bottom-corner, auto-dismiss, and include Undo when relevant.
- Empty states are quiet and instructive (one line plus the relevant shortcut), not illustrated landing sections.

## 7. State that survives

Desktop apps remember. Persist the following so reopening feels continuous:

- Pane sizes, collapsed state, active tab, open tabs, last selection, sort/filter, theme, density.
- Unsaved drafts (autosave) with a visible "Saved / Saving… / Unsaved" indicator in the status bar.
- Where storage is available, use `localStorage` through a small `usePersistentState` hook, with try/catch and sensible defaults. In Claude.ai artifacts, `localStorage` is unavailable, so keep this in React state (and `window.storage` only if that API is offered); say so to the user in one line. In a real project or published page, localStorage or IndexedDB are fine.
- Make loading feel instant: render the shell immediately and fill panes progressively; use skeletons only for content, never for the chrome.

## 8. Electron / Tauri specifics (only if the user mentions them)

- Use a custom title bar only with proper drag regions (`-webkit-app-region: drag`, interactive children set to `no-drag`) and keep native window controls on the correct side per platform.
- Expose native capabilities (file dialogs, menus, notifications, global shortcuts) through the preload/IPC bridge rather than imitating them in the DOM. Native menus and shortcuts beat DOM imitations when running inside the shell; keep the DOM versions as the browser fallback.
- Detect the platform to swap `Cmd`/`Ctrl` labels and traffic-light spacing.

## 9. Accessibility is part of "native"

Native apps are accessible by default, so the imitation must be too: use real `<button>`, `role="menu"/"menuitem"`, `role="tree"`/`"treeitem"`, `role="tablist"`, `aria-selected`, `aria-activedescendant` for roving focus, labelled icon buttons, sufficient contrast, and keyboard access to every pointer feature. Prefer Radix/React Aria primitives when available because they get these details right.

## Workflow

1. Identify the app's main objects and actions (what is selected, opened, renamed, deleted, searched). Everything else in the UI is driven from that.
2. Build the shell first (layout, panes, scroll containment), then the action registry, then keyboard/palette/context menus, then selection, then persistence, then polish.
3. Use realistic sample data so density and selection behavior can be judged.
4. Before finishing, check this list: body never scrolls; every action reachable by keyboard; `Esc` closes things in the right order; right-click works on items; pane sizes persist; light and dark both look right; focus ring visible; shortcut hints shown.
5. If the output is a `.jsx` file or published page, follow the environment's own rules for React imports, available libraries, and storage, and use the `frontend-design` skill alongside this one for typography and palette decisions. This skill governs behavior and structure; that one governs aesthetics.

## What to avoid

- Hero sections, large marketing typography, big rounded cards with drop shadows, and generous whitespace: these read as a website.
- Page-level scrolling, sticky headers that fake an app shell, and layouts that reflow into a single column on desktop widths.
- Confirmation dialogs for everything, instead of undo.
- Hover-only affordances with no keyboard equivalent.
- Custom components that break text input behavior (selection, IME, spellcheck, native context menu in inputs).
