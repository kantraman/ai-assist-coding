# Making it feel human-made

Most generated interfaces converge on the same look because they optimize for "acceptable to
everyone." A human designer works from a specific person, place, and feeling. The gap shows up in
small choices: the words, the spacing, what's emphasized, what's left out. This file is about
closing that gap without sacrificing usability. It supports the rest of the skill: distinctiveness
never overrides accessibility, clarity, or conventions that help people.

## Contents
1. The autopilot look (and why to avoid it)
2. A procedure for finding a point of view
3. Voice and microcopy
4. Details that signal care
5. Real content, real edge cases
6. Interaction feel
7. Where to be conventional (don't be different for its own sake)
8. Human-ness tests
9. Anti-patterns, with replacements

---

## 1. The autopilot look

Signals that a UI was produced on defaults. Each is fine *when chosen*; the problem is when they appear regardless of subject.

**Visual**
- Purple/indigo→blue gradient, or a glowing gradient blob behind the hero
- Inter/Roboto/system-ui everywhere with weights 400/500/600 and nothing else
- Cream page + high-contrast serif + terracotta accent (currently the *other* default)
- Near-black background + a single neon accent
- Every element a rounded-2xl card with the same soft shadow and 1px border
- Glassmorphism/backdrop-blur on things that sit on a flat color
- The same 3-column "icon in a tinted circle → bold title → gray blurb" feature grid
- A row of four identical stat cards with a delta pill
- Centered hero: giant headline, one word gradient-colored, subhead, two buttons, screenshot in a browser frame
- Lucide/Heroicons at 20px inside pastel squares as the only visual idea
- Uniform 24px gap and identical section padding from top to bottom

**Motion**
- Fade-up on every section as it scrolls in; hover lift on every card; shimmering everything

**Copy**
- "Welcome back 👋", "Oops! Something went wrong", "Seamless", "Supercharge", "Unlock the power of", "Elevate your…", "All-in-one platform"
- Lorem ipsum, or "John Doe / Acme Inc / user@example.com" in every screenshot
- Title Case On Every Button, "Submit", "Click here", trailing arrows `→` on every link
- Emoji as bullets or icons
- Meta lines joined with middle dots (A · B · C), tracked-out ALL-CAPS eyebrow above every heading

**Structural**
- Section order dictated by a template (hero → logos → features → testimonials → pricing → FAQ → CTA) irrespective of what this product needs to prove
- Dashboard = sidebar + top search + four KPI cards + line chart + table; no decision about what *this* person checks first

## 2. A procedure for finding a point of view

Do this before writing UI code; it takes minutes.

1. **Write the autopilot version in one paragraph** (palette, type, layout, hero, copy tone) exactly as you'd produce it for any product of this kind. Name it honestly.
2. **Interrogate the subject.** Answer in one line each: Who is the person, and what state are they in? What objects/materials/paperwork live in this world? What do the best hand-made things in this domain look like (signage, forms, packaging, maps, ledgers, instruments)? What should the person *feel* after 10 seconds?
3. **Generate three directions** that differ in *structure*, not just skin (e.g. dense-and-tabular vs. spacious-and-guided vs. conversational-and-linear). Sketch each in ASCII or a two-sentence description.
4. **Choose the direction least like step 1** that still serves the task. If none differ, you haven't left autopilot.
5. **Pick one signature moment**: a single place where the product is allowed to be memorable (a distinctive header treatment, a great empty state, a tactile control, a data visualization with a point of view). Everything else stays quiet and disciplined. Spend boldness in one place.
6. **Write it into `DESIGN.md`** so later screens inherit the same decisions.

If the brief or existing product dictates the look, follow it exactly; the procedure applies to the choices still open. When redesigning a live project, also read `redesign-existing.md`: existing brand equity and user habits are constraints on how far to diverge.

## 3. Voice and microcopy

Words are interface. Write the way a considerate, competent person at this organization would speak aloud.

- **Plain and specific.** "We couldn't reach the server. Your changes are saved on this device; try again in a minute." beats "Something went wrong."
- **Say what will happen.** "Send invoice to Priya" not "Submit". The confirmation says the same verb: "Invoice sent."
- **Sentence case.** Verbs first. Cut "please", "successfully", "just", "simply".
- **No blame, no cute apologies.** "That password doesn't match" not "Oops! You entered the wrong password 😅". Errors explain and offer a route.
- **Name things the way the person does**, not the database: "Patients" not "Entities", "Team" not "Tenant".
- **Empty states teach**: what this space is for, and the first action. "No clients yet. Add your first client to start scheduling."
- **Celebrate rarely.** Warm acknowledgement for milestones people care about; everything else stays understated.
- **Numbers are human:** "3 days ago", "Tomorrow, 9:30", "2 of 5 steps"; with exact values available on hover/focus.
- **Tone follows stakes.** Playful in a café loyalty app; calm and exact in a medical or financial tool.
- **Consistency = trust:** the button, dialog title, toast, and menu item for one action use the same verb.

| Autopilot | Human |
|---|---|
| "Oops! Something went wrong." | "Couldn't save your changes. You're offline. We'll retry when you're back." |
| "Welcome back, John! 👋" | (Often nothing. Or) "Tuesday's schedule" |
| "Unlock powerful insights" | "See which routes ran late this week" |
| "Are you sure you want to delete this?" | "Delete “Q3 invoices”? Its 42 invoices will be removed." → [Keep] [Delete invoices] |
| "Submit" | "Book appointment" |
| "No data available" | "Nothing here yet. Import a CSV or add a supplier by hand." |
| "Error 422: Unprocessable entity" | "Enter a date that's in the future." |

## 4. Details that signal care

- **Typography with character:** pick type for the subject; pair only when the two are clearly distinct; use `font-variant-numeric: tabular-nums` in numeric columns; `text-wrap: balance` on headings; optical size axes if available; proper quotes/dashes; hanging punctuation where supported; a real italic. Set a scale and *use its extremes*: big things big, small things small.
- **Asymmetry with intent:** offset a heading against the grid; let a figure bleed; align to an axis. Symmetric-everything looks machine-made.
- **Density suited to the person:** dispatchers want dense; first-time patients want spacious. Vary within a product on purpose.
- **A designed focus ring, selection color, scrollbars/thumbs where supported, `accent-color`, caret color, favicon, theme-color, and a real 404.** They cost minutes and are noticed subconsciously.
- **Optical alignment:** nudge icons to the text's cap height; align by baseline; equalize visual weight rather than mathematical boxes.
- **One illustration/photography strategy**, real photography or simple, consistent drawings. Avoid generic 3D blobs and stock-people-at-laptops. If you can't do art direction well, use typography, data, and layout as the visual identity.
- **Borders vs shadows vs surface steps: pick one language** and hold it.
- **Sound and haptics:** none by default; never auto-play.
- **Print and share:** `@media print` for things people print (invoices, itineraries); meaningful `<title>` and OG metadata for shareable pages.

## 5. Real content, real edge cases

Placeholder content hides layout and voice problems. Use realistic data drawn from the domain:
- Names from many cultures and lengths (`Aoife Ní Bhriain`, `José Luis Rodríguez de la Cruz`, `Wei`, `Nguyễn Thị Minh Khai`, `Ólafur Þórðarson`). Avoid the John/Jane/Acme monoculture.
- Realistic quantities, dates, currencies, time zones, and units for the person's locale.
- The ugly cases: 0 items, 1 item, 10,000 items, missing avatar/name, long unbroken strings, all-caps input, RTL text, emoji in names.
- Write the actual headline, error messages, and empty-state copy: don't ship lorem ipsum or "Feature one/two/three."

## 6. Interaction feel

- **Immediate feedback:** press states in <100ms, optimistic updates with graceful rollback, inline "Saved" in place.
- **Continuity:** animate *what changed* (an item moving to Done; a panel expanding from its trigger), not decoration. 120-250ms, ease-out; exits quicker than entrances.
- **Forgiveness:** undo > confirm; autosave drafts; preserve input on error; don't lose scroll/selection on refresh; "Restore last session."
- **No surprises:** don't move things after they've loaded (reserve space); don't steal focus; don't auto-advance; don't change layout on hover.
- **Keyboard as a first-class citizen** for expert tools: visible shortcuts in menus, a command palette when there are many actions, `/` to search. Never at the expense of standard behavior.
- **Progressive disclosure:** the common path is short and obvious; advanced options live one step away, not gone.
- **Respect attention:** notifications only for things that need action; batch the rest.

## 7. Where to be conventional (don't be different for its own sake)

Novelty is a cost the person pays every time they use it. Keep these standard:
- Logo top-left links home; primary nav in the expected place; account menu top-right
- Underlined links in body text; buttons look like buttons; form fields look like fields
- Magnifier = search, × = close, ⚙ = settings, kebab/`…` = more actions (with labels where unfamiliar)
- Standard keyboard behaviors (Enter submits, Esc closes, Space toggles, arrows in lists)
- Form patterns (label above, error below, primary action after the fields)
- Standard status colors (see color reference)

**Be distinctive in the layer people don't have to *learn*:** palette, type, illustration, micro-copy, rhythm, motion character, the signature moment. **Be conventional in the layer they *operate*:** controls, navigation, interaction patterns.

## 8. Human-ness tests

Run these on your own output before delivering.

1. **The swap test:** replace the logo and copy with a competitor's. If nothing else has to change, it's generic.
2. **The squint test:** blur the screenshot. Is there a clear first, second, third thing? Or is it uniform mush of cards?
3. **The name test:** cover the product name. Can you tell what world this is from (clinic? freight? bookshop?) from color, type, and content alone?
4. **The screenshot-in-a-crowd test:** would a screenshot of this be mistaken for the top result of "modern SaaS dashboard"?
5. **The read-aloud test:** read every string aloud. Would a person at this organization say it? Cut anything that sounds like marketing.
6. **The rhythm test:** are all sections the same height/padding/structure? Break the pattern deliberately where content warrants.
7. **The constraint test:** does distinctiveness cost accessibility? If yes, keep the accessibility and find another way to be distinct.

## 9. Anti-patterns, with replacements

| Instead of… | Try… |
|---|---|
| Gradient hero blob | The product itself, shown at real scale with real data; or a typographic hero; or a photograph with a point of view |
| Feature grid of 3 identical cards | One feature shown in depth (annotated screenshot / short demo), the others as a plain list; or vary card size by importance |
| Four KPI cards in a row | One dominant figure with context (target, trend, "what changed"), the rest as a compact list |
| Testimonial carousel | A single, specific quote with name, role, and outcome; or omit |
| Pricing table with a highlighted "Most popular" | Plain comparison in the product's voice; lead with who each plan is *for* |
| Generic empty-state illustration | A sentence that teaches + an action + (optionally) a real sample of what it will look like |
| Toast for everything | Inline confirmation where the action happened; toast only when the trigger has left the screen |
| Modal for everything | Inline expansion, popover, or a dedicated page |
| Hamburger on desktop | Visible navigation with labels |
| Skeleton shimmer on 200ms loads | Nothing, or a stable placeholder that doesn't animate |
| Rounded pill on every control | Radius by role; pills only for genuinely pill-like things |
| "Learn more →" everywhere | Descriptive link text; the arrow only when direction matters |
