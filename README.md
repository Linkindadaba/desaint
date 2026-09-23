# Desaint Stationeries — Educational Printworks & Management Platform

> **Naito De Saint Enterprise**  
> *"Write. Create. Inspire."* &bull; *"Quality You See and Trust"*  
> Commercial Educational Printing, Custom School Books (5k–10k MOQ) & Wholesale Stationery Hub  
> **Head Office:** Sunyani Municipal, Bono Region, Ghana

---

## 1. Overview & Architecture

**Desaint Stationeries** is an enterprise management and e-commerce platform built for high-volume school supplies, custom student exercise books, and regional wholesale stationery distribution across Bono, Ahafo, Ashanti, and Northern Ghana.

The platform architecture cleanly separates:
1. **Public Storefront Layer** (`/`):
   - Executive-branded mobile-first storefront (`base_storefront.html`) featuring an announcement banner, multi-tier trust citations, and Jumia-style 2-column mobile catalog.
   - Dual Piece (Retail) and Carton/Box (Wholesale) browsing with customer stock display concealment (status badges only).
   - Flagship **5k–10k MOQ School Book Configurator** allowing prospective headmasters and proprietors to design custom rulings, upload school crests, and calculate volume pricing.
   - Self-service institutional quotation generator with statutory GRA Act 896 (3% WHT) deduction proformas.
   - Session-based customer shopping cart and multi-channel order checkout.

2. **Unified Administrative & Operational Layer** (`/admin/`):
   - Gated management portal under strict Role-Based Access Control (RBAC) with dedicated sign-in (`/admin/login/`).
   - Dynamic sidebar navigation (`base_admin.html`) rendering only role-authorized operational modules.
   - Four distinct operational roles:
     - **Founder & CEO** (`CEO`): Full executive operations, business graph analytics, school credit recovery ledger, proforma generator, database backup hub, and staff management.
     - **Counter POS Cashier** (`Cashier`): Walk-in POS terminal, cash tender & change calculator, 80mm thermal receipt printing, and daily till history.
     - **Graphics Manager** (`Graphics`): Institutional book customizer order queue and zero-misprint digital artwork proof sign-off suite.
     - **Logistics & Dispatch Officer** (`Logistics`): Regional bus parcel waybill tracking (VIP Jeoun, OA Travel, Imperial Express) and terminal delivery dispatch.

---

## 2. Core Features & Operational Engines

### School Book Configurator & Pricing Engine
* **MOQ Enforcement**: Strict 5,000 to 10,000 copy volume thresholds with tiered unit discounts and free plate setup for large runs.
* **Ruling Types**: Standard 80-page, Note 1 (single rule), Note 3 (mathematics grid), and hardcover ledger formats.
* **Zero-Misprint Digital Proof Sign-off**: School proprietors approve high-resolution vector proof layouts online prior to plate manufacturing.
* **Dual Customer / Staff Access**: Shared engine accessible to the public on the storefront and managed internally within the staff portal.

### Point-of-Sale (POS) & Standalone Thermal Receipts
* **Optimized Walk-in Terminal** (`/admin/pos/`): Instant product search (`#posSearchInput`), category filter pills, and one-tap piece vs carton quantity additions.
* **Cash Tender & Change Audit**: Automatic change calculator with quick-increment buttons (`Exact`, `+10`, `+50`, `+100`).
* **Standalone Printable Receipts** (`/admin/pos/receipt/<pk>/`): Dedicated route formatted for standard 80mm roll printers and A4, bypassing modal clipping issues with pure `@media print` CSS.
* **Till History & Quick Reprint**: Every sales transaction in the till log features instant reprint actions and a quick-reprint strip on the active counter terminal.

### Business Graph Analytics Suite (`/admin/analytics/`)
* **100% Offline Engine**: Local `static/js/chart.umd.min.js` (205 KB) with zero external CDN dependency.
* **Executive KPIs**: Real-time gross revenue, net margin trajectories, commercial channel mix (Retail POS, B2B Wholesale, School Custom, Institutional Tenders), and payment rails mix (Cash, MoMo Till, Bank).
* **Institutional Debt & Credit Recovery Gauge**: Real-time monitoring of school fee term credit recovery health.

### Distinctive Aura Gradient Theme System
* **Light Theme ("Desaint Alabaster Aurora")**: Pure alabaster parchment canvas (`#f8fafc`), cool executive navy mist, subtle crimson ink blush, and tactile SVG paper weave grain (`grain-desaint-light`).
* **Dark Theme ("Desaint Obsidian Crimson Aurora")**: Deep academic navy-obsidian canvas (`#060b14`), oceanic cobalt pulse, signature crimson ruby eclipse, and fine dark grain (`grain-desaint-dark`).
* **Instant Toggling**: Zero-flash early `<head>` script execution with dual-sync storage keys.
* **High Contrast (WCAG AAA)**: Inter UI typography paired with JetBrains Mono tabular monetary amounts (`GH₵`). Strict preservation of `#0f172a` slate text on amber/warning elements (preventing white-on-yellow contrast bugs).

### Session Security & Anti-Theft Guardrails
* **No Persistent Automatic Logins**: `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` ensures browser session cookies expire upon window exit.
* **Explicit Authentication**: Removed auto-redirects from `/admin/login/`, allowing cashiers and managers to switch roles seamlessly.
* **One-Hour Idle Timeout**: Sessions expire after 60 minutes of inactivity.

---

## 3. Technology Stack

* **Backend**: Python 3.13, Django 5.x
* **Database**: SQLite (Development) / PostgreSQL-ready
* **Frontend**: Offline-first Bootstrap 5.3.3, Vanilla JavaScript (ES6+), Font Awesome 6
* **Analytics Engine**: Chart.js 4.4.1 (Local UMD bundle)
* **Typography**: Inter (Body & UI text) & JetBrains Mono (Prices, SKU codes, Invoices, Tax breakdowns)

---

## 4. Getting Started

### Prerequisites
* Python 3.10+ installed
* Virtual environment configured

### Installation & Local Setup

```bash
# 1. Clone repository
git clone https://github.com/Linkindadaba/desaint.git
cd desaint

# 2. Activate virtual environment
# Windows PowerShell:
.\env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Initialize RBAC roles and default staff accounts
python setup_admin.py

# 6. Seed catalog and sample operational records
python seed_initial_data.py

# 7. Start local development server
python manage.py runserver
```

---

## 5. Default Staff Accounts (RBAC)

| Username | Default Password | Role | Assigned Landing View | Primary Responsibility |
|---|---|---|---|---|
| `admin` | `desaintadmin2026` | `Superuser / CEO` | `/admin/` | Complete operational oversight & raw database |
| `solomon` | `solomon2026` | `CEO` | `/admin/` | Business intelligence, credit recovery, staff management |
| `cashier_sunyani` | `cashier2026` | `Cashier` | `/admin/pos/` | Counter walk-in sales & thermal receipt printing |
| `graphics_lead` | `graphics2026` | `Graphics` | `/admin/customizer/` | Custom book orders & digital proof approvals |
| `dispatch_officer` | `logistics2026` | `Logistics` | `/admin/waybills/` | Inter-regional bus waybill parcel dispatch |

---

## 6. Project Guidelines & Guardrails (`GEMINI.md`)

All modifications to this codebase strictly adhere to the guidelines codified in [`GEMINI.md`](GEMINI.md):
1. **Version Control & Git Safety**: Strict zero-commit policy unless explicitly instructed by the user.
2. **Offline-First Frontend Assets**: Mandatory local bundling of CSS/JS libraries.
3. **Customer Stock Display Policy**: Conceal raw inventory numbers on public catalog pages.
4. **Theme Contrast & Font Hierarchy**: Inter UI with JetBrains Mono monetary figures (`GH₵`); dark mode `.bg-light` container overrides; no white-on-yellow.
5. **Mobile-First E-Commerce UI**: Responsive 2-column mobile catalog (`col-6`), 1:1 square product frames, 2-line title clamps, and executive navy footers.
6. **POS & Thermal Receipt Architecture**: Standalone print routes (`orders:pos_receipt`), `{% block modals %}` root body mounting, and cash tender/change audit logging.
7. **Dual Customer / Staff Access Pattern**: Dynamic template inheritance (`base_template = 'base_admin.html' if is_staff_user else 'base_storefront.html'`).
8. **Business Graph Analytics Standards**: Local Chart.js engine with JetBrains Mono tooltips and accessible color palettes.

---

## 7. License & Attribution

&copy; 2026 **Naito De Saint Enterprise** / **Desaint Stationeries**. All rights reserved.  
Developed and maintained by **SikaDev Solutions**.