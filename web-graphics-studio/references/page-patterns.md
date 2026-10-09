# Page Patterns and Style Directions

Contents: section blueprints · copy tips · three style directions · polish pass

## Section blueprints

**Hero**: a short, specific headline (6–10 words) stating the outcome or the point of view, one supporting sentence, one primary call to action and an optional quiet secondary link. Put the signature visual (animated canvas, 3D object, SVG illustration, big type) here. Keep it to one screen height with the next section peeking in.

**Social proof strip**: logos in a muted monochrome row or a marquee, or three crisp numbers with labels. Never fake logos or metrics; use clearly labeled placeholders if real ones are unknown.

**Features**: 3–6 items. Prefer a bento grid or alternating image/text rows over a uniform card row. Each item: a small graphic, a 3–5 word title, one sentence. Give one feature a larger tile as the hero feature.

**How it works**: numbered steps with a connecting line that draws as you scroll (SVG `pathLength` + scroll-driven animation).

**Showcase / portfolio**: large images or generated SVG/canvas thumbnails, hover reveals title and tags, consistent aspect ratio, a tilt or spotlight effect on hover.

**Testimonials**: one large quote at a time or a staggered two-column layout; include name and role. Avoid carousels that auto-advance quickly.

**Pricing**: 2–3 tiers, highlight the recommended one with an accent border and a small label, list differences clearly, and keep the same row order across tiers.

**Final call to action**: restate the promise, one button, optional reassurance line (no credit card, cancel anytime), generous padding and a distinct background.

**Footer**: compact; navigation groups, legal links, small brand mark.

**Navigation**: sticky, translucent with `backdrop-filter`, collapses to a menu button under ~720px, clearly shows the current section.

## Copywriting tips

- Lead with the benefit, not the feature. "Ship a site in an afternoon" beats "A powerful website builder".
- Use concrete nouns and numbers; avoid filler like "revolutionary", "seamless", "next-generation".
- Button labels are verbs about the outcome: "Start building", "See the demo".
- Keep paragraphs under three lines in marketing sections.
- When the user gives no content, write plausible, tasteful placeholder copy that fits the subject and mention it is placeholder.

## Three style directions

**1. Editorial minimal**
Off-white background, near-black text, one vivid accent (tomato, cobalt or acid green). Oversized serif or grotesk headlines with tight tracking, thin rules, lots of whitespace, small caps labels, subtle underline-sweep links. Motion: gentle masked text reveals, slow parallax on one image. Suits portfolios, studios, writers.

**2. Dark neon tech**
Deep navy or near-black, gradient mesh glows in violet/cyan, glass cards with hairline borders, monospace accents for labels and stats, grain overlay. Hero: shader or particle network background, glowing gradient border on the primary card. Motion: spotlight following pointer, number counters, scrubbed scroll sections. Suits developer tools, AI, crypto, music tech.

**3. Playful tactile**
Warm pastel palette, chunky rounded shapes, thick outlines or hard offset shadows (`box-shadow: 6px 6px 0 #000`), sticker-like rotated elements, bouncy `back.out` easing, hand-drawn SVG squiggles. Motion: wobble on hover, elements that settle with overshoot, draggable stickers. Suits education, consumer apps, kids, food, events.

Mix the direction with the subject. A bakery should not look like a developer tool, and a security product should not look like a sticker book.

## Polish pass (do before delivering)

1. Squint test: is there a clear focal point and visual hierarchy?
2. Align to the grid; check that spacing between sections is consistent (use a few spacing tokens).
3. Reduce: remove one effect, one color or one font weight from what you first wrote.
4. Add the details: custom `::selection` color, styled scrollbar (subtle), `color-scheme` meta, favicon (emoji data URI or inline SVG), meaningful `<title>` and meta description.
5. Test states: hover, focus-visible, active, disabled, empty, loading.
6. Check long words and narrow widths for overflow; set `overflow-wrap: anywhere` on text containers where needed.
