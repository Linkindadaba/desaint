# DESAINT STATIONERIES — Project Rules & Guidelines

## 1. Version Control & Git Safety
- **DO NOT COMMIT TO GIT**: Never run `git commit` or create commits unless explicitly instructed by the user. Keep all modifications in the working tree / unstaged files.

## 2. Offline-First Frontend Assets
- Always maintain and link local offline copies of CSS and JS libraries (e.g., `static/css/bootstrap.min.css`, `static/js/bootstrap.bundle.min.js`, and `static/js/chart.umd.min.js`) alongside or as the primary source before CDN fallbacks. The application must render fully and correctly on localhost without internet access.

## 3. Customer Stock Display Policy
- **Never expose exact stock counts** (e.g. "5 in stock") to customers on public storefront or product detail pages. Low stock counts discourage bulk and institutional school buyers.
- Use status indicators ("In Stock", "Available on Order", "Backorder Allowed") and allow backorders with procurement notifications for staff.

## 4. Theme Contrast & Font Visibility Standards
- **Font Stack Hierarchy**: Always use `Inter` for general typography and UI text, paired with `JetBrains Mono` for tabular prices, currency amounts (`GH₵`), order references, and tax breakdowns.
- **No White-on-Yellow**: Never apply indiscriminate `.text-dark { color: white !important; }` in dark theme. Amber/warning elements (`.btn-warning`, `.badge.bg-warning`, `.alert-warning`) must strictly preserve dark slate text (`#0f172a !important`).
- **Dark Mode Overrides for `.bg-light`**: Whenever `.bg-light` is used in markup, dark mode must style it with a dark container background (`#1a2333 !important; border-color: #2b384e !important;`) to prevent white-on-white text inversion.
- **High-Contrast Secondary Text**: Maintain WCAG AAA contrast for muted text: `#475569` (Slate 600) in light theme and `#94a3b8` (Slate 400) in dark theme.

## 5. Mobile-First E-Commerce UI Standards (Jumia Style)
- **2-Column Mobile Catalog**: On mobile screens (`< 576px`), storefront product grids must render as a responsive 2-column layout (`col-6 col-md-4 col-lg-3` with `g-2 g-sm-3 g-lg-4`), never a single-column stack.
- **1:1 Square Product Frames**: Product images must sit inside square `aspect-ratio: 1 / 1` thumbnail frames with `object-fit: contain` so stationery reams, boxes, and tapes are fully visible without being cropped.
- **Uniform Card Alignment**: Enforce a strict 2-line title clamp (`-webkit-line-clamp: 2; height: 2.15rem;`) so cards across any row maintain uniform height.
- **Executive Navy Footers**: Storefront footers must utilize an executive deep navy grounding (`#090e1a` / `#060913`) with uppercase tracked section headers and mobile-stacked contact items.

## 6. Point-of-Sale (POS) & Thermal Receipt Printing Architecture
- **Dedicated Standalone Receipt View**: Never rely solely on printing Bootstrap modals with `window.print()`. Browser print engines often clip or render blank pages when modals are nested inside layout wrappers (`.wrapper` / `#main-content`).
- **Always Provide Direct URL**: Every POS sale must have a dedicated standalone view (e.g. `/admin/pos/receipt/<pk>/` with `orders:pos_receipt`) formatted for 80mm roll printers and standard A4 with clean `@media print` CSS.
- **Modal Placement In Templates**: In Django base templates, modals must strictly be placed in `{% block modals %}` mounted directly on `<body>`, never inside `#main-content` or transformed containers, to prevent backdrop freezing and scroll locks.
- **Reprint Actions on Till Logs**: Every sales history table (`pos_history.html`) must provide a "Print Receipt" action button on every row. Active POS terminals should feature a quick-reprint strip for earlier transactions.
- **Cash Tender & Change Audit**: Always record `amount_tendered` and `change_given` in POS models, and support quick-tender increment buttons (`Exact`, `+10`, `+50`, `+100`) on the cashier interface.

## 7. Dual Customer / Staff Access Pattern for Production Tools
- When a customer-facing tool (e.g., School Book Configurator, Quote Generator) also serves as an internal staff production interface, do NOT restrict the endpoint with staff-only decorators (`@staff_required`, `@graphics_required`).
- Dynamically adapt the layout template:
  ```python
  is_staff_user = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
  base_template = 'base_admin.html' if is_staff_user else 'base_storefront.html'
  ```
- This ensures public school proprietors access the tool via the public storefront navbar, while authenticated staff manage the same views within the administrative portal.

## 8. Business Graph Analytics Standards
- **Offline Chart Engine**: Use local `static/js/chart.umd.min.js` (205 KB) for all interactive graphs (line trajectories, channel doughnut mix, cash liquidity bars).
- **Tabular Monospace Styling**: Ensure chart tooltips and axis labels use `JetBrains Mono` for all currency amounts (`GH₵`) and numerical values.
- **Accessible Color Palette**: Use high-contrast brand hues: Navy (`#0B2545`), Crimson (`#D90429`), Emerald (`#10B981`), Amber (`#F59E0B`), and Sky Blue (`#0284C7`).
