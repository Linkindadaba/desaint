# Client Requirements & Discovery Questionnaire
**Client:** Naito De Saint Enterprise (Trading as **Desaint Stationeries**)  
**Contact Person:** Mr. Aseim Solomon (Founder & CEO)  
**Location:** Sunyani, Ghana  
**Prepared by:** SikaDev Software Engineering Team  
**Date:** September 2026  

---

## Instructions
Please complete this requirements form to help us design, architect, and customize the ideal software platform for **Desaint Stationeries**. If any question is not applicable or you prefer our team's recommended best practice, please leave it blank or tick **"Advised by SikaDev"**.

---

## Section 1: Business Identity & Digital Presence

1. **Official Online Domain & Hosting:**
   - [ ] Do you already own a domain name (e.g., `desaintstationeries.com` or `desaintgh.com`)?  
     *Domain Name (if any):* ____________________________________________________
   - [ ] Do you need SikaDev to acquire and configure the domain and business email (`info@...`, `sales@...`)?
     - [ ] Yes, please handle domain & email setup.
     - [ ] No, we will provide existing DNS credentials.

2. **Official Public Contact Information for the Platform:**
   - Customer Service Phone (Voice): ___________________________________________
   - WhatsApp Order Line: _____________________________________________________
   - Public Invoicing / Support Email: _________________________________________
   - Sunyani Store / Warehouse Physical Address: _________________________________
   - Social Media Links (Facebook, Instagram, LinkedIn, TikTok): ____________________

3. **Core Brand Identity Assets:**
   - [ ] High-resolution logo file available (PNG, SVG, or vector PDF).
   - [ ] Brand Colors: Deep Red (`#D90429`), Navy Blue (`#0B2545`), White, Silver.
   - [ ] Preferred Brand Tagline on Web Header:  
     - [ ] *"Quality You See and Trust."*
     - [ ] *"Write. Create. Inspire."*
     - [ ] Both / Rotating

---

## Section 2: Storefront & Customer Journey Scope

4. **Which customer purchasing models should the platform support? (Tick all that apply)**
   - [ ] **B2C Public Retail Store:** Anyone can browse, add items to cart, and checkout (single items, packs, household/student orders).
   - [ ] **B2B Wholesale Portal:** Bookshops, stationery shops, and retail distributors log in to access tiered carton/wholesale bulk pricing.
   - [ ] **Institutional / School Direct Ordering:** Schools request formal proforma invoices, bulk terms, and customization contracts.
   - [ ] **Walk-in / Point of Sale (POS) Mode:** Fast counter checkout for the physical Sunyani store staff.

5. **Customer Registration & Checkout Flow:**
   - [ ] Allow guest checkout (no account required to buy).
   - [ ] Require customer account registration for all orders.
   - [ ] Guest checkout for retail, but mandatory approved account for wholesale & institutional pricing. *(Recommended)*

6. **Stock Visibility Rule:**
   - *Ghana Market Note: Displaying low exact numbers (e.g. "Only 3 left") often discourages institutional buyers who assume you cannot fulfill 100+ units.*
   - [ ] **Status Badges Only:** Show "In Stock", "Available on Order", "Backorder Allowed" *(Recommended)*.
   - [ ] **Exact Count:** Show literal quantities (e.g., "47 units left in Sunyani").

---

## Section 3: School Book Customization & Printing System

7. **Custom Exercise Books & Materials Workflow:**  
   *Desaint Stationeries specializes in custom-branded exercise books for schools across Ghana.* How should schools order their custom books?
   - [ ] **Interactive Online Customizer:** School admin uploads their School Crest/Logo, enters School Name/Motto/Anthem, selects book type (Exercise, Note 1, Graph, Drawing) and quantity, and previews a digital mock-up.
   - [ ] **Custom Request for Quote (RFQ) Form:** School submits their specifications, and your staff manually generates and emails a custom quote with sample proof.
   - [ ] **Both:** Online quote generator with automated preliminary proof + staff sign-off.

8. **Customization Pricing & Minimum Order Quantity (MOQ):**
   - What is the Minimum Order Quantity (MOQ) for custom-printed school exercise books?  
     *MOQ:* _________ copies / packs.
   - Do you charge a fixed plate/die setup fee for new school cover designs?  
     - [ ] Yes (GH¢ ________ per design)
     - [ ] No, cost is factored into unit price.

---

## Section 4: Pricing, Quotations & Ghana Tax Compliance

9. **GRA Tax Structure Preference:**
   - [ ] **Non-VAT / Exempt:** Net prices only, no VAT levied.
   - [ ] **GRA Flat Rate Scheme:** 3% Flat Rate + 1% COVID-19 Levy (Total 4%).
   - [ ] **GRA Standard Rate:** 15% VAT + 2.5% NHIL + 2.5% GETFund + 1% COVID Levy (Total ~21.9% effective).
   - [ ] **Multi-Scheme Configurable:** System can generate Standard VAT invoices for corporate/government tenders and retail slips for walk-ins.

10. **Withholding Tax (WHT) for Institutional Procurement:**
    - When supplying government institutions, universities, or large corporate entities in Ghana, do you need automatic invoice deduction for GRA 3% WHT (Goods) or 5% WHVAT?
      - [ ] Yes, auto-calculate Net Payable after WHT deduction.
      - [ ] Not needed right now.

11. **Currency & Payment Channels:**
    - Primary Currency: Ghana Cedis (GH¢ / GHS).
    - Which payment methods must be active at launch?
      - [ ] **MTN Mobile Money & Telecel Cash** (Direct payment via Paystack / Hubtel / local aggregator)
      - [ ] **Manual MoMo / Merchant Till** (Customer transfers to Desaint MoMo number and uploads transaction ID/screenshot)
      - [ ] **Direct Bank Transfer** (Bank account details displayed on proforma invoice)
      - [ ] **Cash on Delivery / Pay on Pickup** (Restricted to Sunyani / trusted schools)
      - [ ] **Credit Terms / Purchase Orders (PO)** (For vetted institutional schools with 30-day payment cycle)

---

## Section 5: Inventory, Warehouse & Logistics

12. **Warehouse & Fulfillment Locations:**
    - How many fulfillment locations do you operate?
      - [ ] Single central warehouse/shop in Sunyani.
      - [ ] Sunyani hub + secondary depots / regional distribution points.  
        *Locations:* ____________________________________________________

13. **Regional Delivery Routes & Logistics Models:**
    - How are orders dispatched to customers in other regions (Bono East, Ahafo, Ashanti, Central, Western North)?
      - [ ] **Bus Terminal Parcel Dispatch:** Dropped at VIP, OA, Imperial, or Metro Mass parcel offices in Sunyani for customer pickup at destination terminal.
      - [ ] **Door-to-Door Courier / Dispatch Rider:** In-city deliveries in Sunyani and surrounding towns.
      - [ ] **Desaint Dedicated Truck / Van Delivery:** Bulk deliveries directly to school campuses.
      - [ ] **In-Store Pickup:** Customer collects at the Sunyani head office.

14. **Shipping Fee Calculation:**
    - [ ] Flat rate based on delivery region/town.
    - [ ] Dynamic calculation based on weight / number of cartons.
    - [ ] "Pay to Courier Upon Collection" (Terminal parcel fee paid by recipient).
    - [ ] Free delivery on institutional orders above GH¢ ______________.

---

## Section 6: Staff Roles & System Permissions

15. **User Roles Needed:**
    - [ ] **Super Admin / CEO (Mr. Solomon):** Full access to sales analytics, margins, customer database, financial reports.
    - [ ] **Sales / Storefront Staff:** Process counter sales, create orders, view catalog.
    - [ ] **Production / Print Manager:** Manage school book custom print orders, design proofs, and print queues.
    - [ ] **Dispatch / Logistics Officer:** Manage waybills, package tracking, parcel dispatch receipts.
    - [ ] **Accountant:** Issue GRA tax invoices, reconcile bank/MoMo payments, track outstanding school credit.

---

## Section 7: Project Timeline & Milestone Targets

16. **Target Launch Date:**
    - Desired Go-Live Date: ___________________________________________________
    - Key Upcoming School Season / Promotional Window: ___________________________

17. **Any Specific Integration or Additional Feature Requests:**
    __________________________________________________________________________
    __________________________________________________________________________
    __________________________________________________________________________

---

### Client Sign-Off & Verification
**Completed by:** ______________________________________  
**Designation:** ________________________________________  
**Signature:** __________________________________________  
**Date:** ______________________________________________  
