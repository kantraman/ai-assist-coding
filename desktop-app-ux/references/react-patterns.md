# React patterns for desktop-style UIs

Contents: platform helper, hotkeys, action registry, command palette, context menu, resizable panes, selection model, persistent state, app shell CSS.

All snippets are dependency-free and use only React. Adapt names to the project.

## Platform helper

```jsx
export const isMac =
  typeof navigator !== "undefined" &&
  /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);

export const modLabel = isMac ? "⌘" : "Ctrl";
```

## Hotkeys

Parse strings like `"Mod+Shift+K"`. Ignore plain-key shortcuts while typing in inputs.

```jsx
import { useEffect, useRef } from "react";

function matches(e, combo) {
  const parts = combo.toLowerCase().split("+");
  const key = parts.pop();
  const want = {
    mod: parts.includes("mod"),
    shift: parts.includes("shift"),
    alt: parts.includes("alt"),
  };
  const mod = isMac ? e.metaKey : e.ctrlKey;
  return (
    mod === want.mod &&
    e.shiftKey === want.shift &&
    e.altKey === want.alt &&
    e.key.toLowerCase() === key
  );
}

export function useHotkeys(bindings) {
  const ref = useRef(bindings);
  ref.current = bindings;
  useEffect(() => {
    const onKey = (e) => {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
      for (const b of ref.current) {
        if (!matches(e, b.combo)) continue;
        if (typing && !b.combo.toLowerCase().includes("mod")) continue;
        e.preventDefault();
        b.run(e);
        return;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
}
```

## Action registry

One source of truth for menus, palette, context menus, and hotkeys.

```jsx
export const actions = [
  { id: "file.new",   title: "New file",       combo: "Mod+N",     run: (ctx) => ctx.newFile() },
  { id: "file.save",  title: "Save",           combo: "Mod+S",     run: (ctx) => ctx.save() },
  { id: "view.sidebar", title: "Toggle sidebar", combo: "Mod+B",   run: (ctx) => ctx.toggleSidebar() },
  { id: "edit.delete", title: "Delete",        combo: "Backspace", run: (ctx) => ctx.deleteSelection(),
    enabled: (ctx) => ctx.selection.size > 0 },
];

// In the app:
// useHotkeys(actions.filter(a => a.combo).map(a => ({ combo: a.combo, run: () => a.run(ctx) })));
```

## Command palette

```jsx
import { useState, useMemo, useEffect, useRef } from "react";

export function CommandPalette({ open, onClose, actions, ctx }) {
  const [q, setQ] = useState("");
  const [i, setI] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => { if (open) { setQ(""); setI(0); setTimeout(() => inputRef.current?.focus(), 0); } }, [open]);

  const results = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return actions
      .filter((a) => !a.enabled || a.enabled(ctx))
      .filter((a) => !needle || a.title.toLowerCase().includes(needle));
  }, [q, actions, ctx]);

  if (!open) return null;

  const onKeyDown = (e) => {
    if (e.key === "Escape") onClose();
    else if (e.key === "ArrowDown") { e.preventDefault(); setI((x) => Math.min(x + 1, results.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setI((x) => Math.max(x - 1, 0)); }
    else if (e.key === "Enter" && results[i]) { onClose(); results[i].run(ctx); }
  };

  return (
    <div className="overlay" onMouseDown={onClose}>
      <div className="palette" role="dialog" aria-label="Command palette" onMouseDown={(e) => e.stopPropagation()}>
        <input ref={inputRef} value={q} onChange={(e) => { setQ(e.target.value); setI(0); }}
               onKeyDown={onKeyDown} placeholder="Type a command…" />
        <ul role="listbox">
          {results.map((a, n) => (
            <li key={a.id} role="option" aria-selected={n === i}
                className={n === i ? "active" : ""}
                onMouseEnter={() => setI(n)}
                onClick={() => { onClose(); a.run(ctx); }}>
              <span>{a.title}</span>
              {a.combo && <kbd>{a.combo.replace("Mod", modLabel)}</kbd>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

Replace the simple substring filter with a real fuzzy matcher if the list is long.

## Context menu

```jsx
import { useState, useEffect, useLayoutEffect, useRef } from "react";

export function useContextMenu() {
  const [menu, setMenu] = useState(null); // { x, y, items }
  const open = (e, items) => { e.preventDefault(); setMenu({ x: e.clientX, y: e.clientY, items }); };
  const close = () => setMenu(null);
  return { menu, open, close };
}

export function ContextMenu({ menu, onClose }) {
  const ref = useRef(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });

  useLayoutEffect(() => {
    if (!menu || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    setPos({
      x: Math.min(menu.x, window.innerWidth - r.width - 8),
      y: Math.min(menu.y, window.innerHeight - r.height - 8),
    });
  }, [menu]);

  useEffect(() => {
    if (!menu) return;
    const off = () => onClose();
    const esc = (e) => e.key === "Escape" && onClose();
    window.addEventListener("mousedown", off);
    window.addEventListener("keydown", esc);
    window.addEventListener("blur", off);
    return () => {
      window.removeEventListener("mousedown", off);
      window.removeEventListener("keydown", esc);
      window.removeEventListener("blur", off);
    };
  }, [menu, onClose]);

  if (!menu) return null;
  return (
    <div ref={ref} className="ctx" role="menu" style={{ left: pos.x, top: pos.y }}
         onMouseDown={(e) => e.stopPropagation()}>
      {menu.items.map((it, n) =>
        it === "-" ? <hr key={n} /> : (
          <button key={it.id} role="menuitem" disabled={it.disabled}
                  onClick={() => { onClose(); it.run(); }}>
            <span>{it.title}</span>
            {it.combo && <kbd>{it.combo.replace("Mod", modLabel)}</kbd>}
          </button>
        ))}
    </div>
  );
}
```

Usage: `onContextMenu={(e) => open(e, [{id:"rename", title:"Rename", combo:"F2", run: ...}, "-", {id:"del", title:"Delete", run: ...}])}`.

## Resizable panes

```jsx
import { useRef } from "react";

export function Splitter({ onDrag, onReset, orientation = "vertical" }) {
  const dragging = useRef(false);
  const down = (e) => {
    dragging.current = true;
    e.currentTarget.setPointerCapture(e.pointerId);
    document.body.style.userSelect = "none";
    document.body.style.cursor = orientation === "vertical" ? "col-resize" : "row-resize";
  };
  const move = (e) => dragging.current && onDrag(orientation === "vertical" ? e.clientX : e.clientY);
  const up = (e) => {
    dragging.current = false;
    e.currentTarget.releasePointerCapture(e.pointerId);
    document.body.style.userSelect = "";
    document.body.style.cursor = "";
  };
  return (
    <div role="separator" aria-orientation={orientation}
         className={`splitter ${orientation}`}
         onPointerDown={down} onPointerMove={move} onPointerUp={up}
         onDoubleClick={onReset} />
  );
}

// const [sidebarW, setSidebarW] = usePersistentState("sidebarW", 240);
// <aside style={{ width: sidebarW }} />
// <Splitter onDrag={(x) => setSidebarW(Math.max(160, Math.min(480, x)))} onReset={() => setSidebarW(240)} />
```

Clamp sizes to min/max and keep the splitter hit area wider (6-8px) than its visible line (1px).

## Selection model

```jsx
import { useState, useCallback } from "react";

export function useSelection(ids) {
  const [selected, setSelected] = useState(new Set());
  const [anchor, setAnchor] = useState(null);

  const select = useCallback((id, e) => {
    if (e.shiftKey && anchor != null) {
      const a = ids.indexOf(anchor), b = ids.indexOf(id);
      const [lo, hi] = a < b ? [a, b] : [b, a];
      setSelected(new Set(ids.slice(lo, hi + 1)));
    } else if (e.metaKey || e.ctrlKey) {
      setSelected((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
      setAnchor(id);
    } else {
      setSelected(new Set([id]));
      setAnchor(id);
    }
  }, [ids, anchor]);

  const clear = () => setSelected(new Set());
  return { selected, select, clear, setSelected };
}
```

For a right-click on an unselected row, select it first; on a selected row, keep the current selection.

## Persistent state

```jsx
import { useState, useEffect } from "react";

export function usePersistentState(key, initial) {
  const [value, setValue] = useState(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw != null ? JSON.parse(raw) : initial;
    } catch { return initial; }
  });
  useEffect(() => {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
  }, [key, value]);
  return [value, setValue];
}
```

In Claude.ai artifacts, `localStorage` is not available: fall back to plain `useState` (the try/catch above already degrades to `initial`, but state will not persist).

## Undo / redo

```jsx
import { useReducer } from "react";

function reducer(state, action) {
  switch (action.type) {
    case "set": return { past: [...state.past, state.present], present: action.value, future: [] };
    case "undo": if (!state.past.length) return state;
      return { past: state.past.slice(0, -1), present: state.past.at(-1), future: [state.present, ...state.future] };
    case "redo": if (!state.future.length) return state;
      return { past: [...state.past, state.present], present: state.future[0], future: state.future.slice(1) };
    default: return state;
  }
}

export const useHistory = (initial) =>
  useReducer(reducer, { past: [], present: initial, future: [] });
```

## App shell CSS tokens

```css
:root {
  --bg: #ffffff;  --bg-pane: #f6f6f7;  --bg-hover: #ececee;
  --fg: #1d1d1f;  --fg-muted: #6e6e73;
  --border: #dcdce0;  --accent: #0a64ff;  --accent-fg: #fff;
  --row-h: 28px;  --radius: 5px;
  font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}
:root:not([data-theme="light"]) { color-scheme: light dark; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1e1e20; --bg-pane: #252527; --bg-hover: #303033;
    --fg: #e8e8ea; --fg-muted: #9a9aa0; --border: #38383c;
  }
}
:root[data-theme="dark"] {
  --bg: #1e1e20; --bg-pane: #252527; --bg-hover: #303033;
  --fg: #e8e8ea; --fg-muted: #9a9aa0; --border: #38383c;
}

html, body, #root { height: 100%; margin: 0; overflow: hidden; overscroll-behavior: none; }
body { background: var(--bg); color: var(--fg); }

.app { display: grid; height: 100%;
  grid-template-rows: auto 1fr auto;            /* toolbar / body / status bar */
}
.body { display: flex; min-height: 0; }
.pane { overflow: auto; min-height: 0; min-width: 0; }
.chrome { user-select: none; cursor: default; }
button { cursor: default; font: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }

.splitter.vertical { width: 1px; background: var(--border); position: relative; cursor: col-resize; }
.splitter.vertical::after { content: ""; position: absolute; inset: 0 -3px; }  /* wider hit area */

.row { height: var(--row-h); display: flex; align-items: center; padding: 0 8px; }
.row:hover { background: var(--bg-hover); }
.row[aria-selected="true"] { background: var(--accent); color: var(--accent-fg); }

kbd { font: 11px ui-monospace, Menlo, Consolas, monospace; color: var(--fg-muted); }

@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
```
