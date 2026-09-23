/**
 * =======================================================================
 * SIKADEV AUTOMATED GOOGLE FORM GENERATOR
 * Client: Naito De Saint Enterprise (Desaint Stationeries)
 * Target: Mr. Aseim Solomon, Sunyani, Ghana
 * Prepared by: SikaDev Software Engineering Team
 * =======================================================================
 * 
 * QUICK INSTRUCTIONS:
 * 1. Open your browser and go to: https://script.new
 * 2. Select and delete any default code inside the editor.
 * 3. Copy and paste this ENTIRE code block into the editor.
 * 4. Click the "Save" icon (Floppy disk), then click the "Run" button (Play icon).
 * 5. If Google asks for authorization, click "Review Permissions" -> Choose your account -> "Advanced" -> "Go to Untitled project (unsafe)" -> "Allow".
 * 6. The script runs in ~3 seconds and prints your live Google Form links in the "Execution Log" below!
 * =======================================================================
 */

function createDesaintStationeriesDiscoveryForm() {
  const formTitle = "Desaint Stationeries — Digital Platform Requirements";
  const formDescription = 
    "Prepared by SikaDev Software Engineering Team for Naito De Saint Enterprise (Mr. Aseim Solomon).\n\n" +
    "This discovery questionnaire helps SikaDev tailor, architect, and configure the digital platform, " +
    "wholesale portal, school book customization workflow, and inventory systems for Desaint Stationeries.\n\n" +
    "Head Office: Sunyani, Bono Region, Ghana | Brand Motto: Quality You See and Trust.";

  // Create Google Form
  const form = FormApp.create(formTitle);
  form.setDescription(formDescription);
  form.setConfirmationMessage(
    "Thank you Mr. Solomon! Your requirements have been received by SikaDev Software Engineering. " +
    "Our team will review your selections and prepare the architecture and milestone roadmap."
  );
  form.setAllowResponseEdits(true);
  form.setProgressBar(true);

  // ==========================================
  // SECTION 1: CORPORATE IDENTITY & CONTACTS
  // ==========================================
  const sec1 = form.addPageBreakItem();
  sec1.setTitle("Section 1: Corporate Identity & Contacts");
  sec1.setHelpText("Basic business credentials and public contact information.");

  form.addTextItem()
    .setTitle("1. Registered Business Name")
    .setHelpText("Official registered legal name (e.g. Naito De Saint Enterprise)")
    .setRequired(true);

  form.addTextItem()
    .setTitle("2. Trading Brand Name")
    .setHelpText("Customer-facing brand name (e.g. Desaint Stationeries)")
    .setRequired(true);

  form.addTextItem()
    .setTitle("3. Founder & CEO Name")
    .setHelpText("e.g. Mr. Aseim Solomon")
    .setRequired(true);

  form.addTextItem()
    .setTitle("4. Head Office / Primary Store Location")
    .setHelpText("e.g. Sunyani, Bono Region, Ghana")
    .setRequired(true);

  form.addTextItem()
    .setTitle("5. Primary Customer Service Phone (Voice)")
    .setHelpText("e.g. +233 20 015 2394")
    .setRequired(true);

  form.addTextItem()
    .setTitle("6. WhatsApp Sales / Orders Line")
    .setHelpText("e.g. +233 24 606 5822")
    .setRequired(true);

  form.addTextItem()
    .setTitle("7. Official Public Email")
    .setHelpText("e.g. Naitodesaint35@gmail.com")
    .setRequired(true);

  const domainItem = form.addMultipleChoiceItem();
  domainItem.setTitle("8. Website Domain & Business Email Setup")
    .setHelpText("Do you already have a domain registered, or should SikaDev procure it?")
    .setChoiceValues([
      "I already own a domain (I will provide DNS details)",
      "SikaDev should register the domain (e.g. desaintstationeries.com) & set up business emails",
      "Advised by SikaDev"
    ])
    .setRequired(true);

  // ==========================================
  // SECTION 2: SALES CHANNELS & STOREFRONT SCOPE
  // ==========================================
  const sec2 = form.addPageBreakItem();
  sec2.setTitle("Section 2: Sales Channels & Customer Journey");
  sec2.setHelpText("Define which customer purchasing channels must be activated on the platform.");

  const channelsItem = form.addCheckboxItem();
  channelsItem.setTitle("9. Which sales channels should be activated? (Select all that apply)")
    .setChoiceValues([
      "B2C Public Retail Storefront (General public, parents, teachers, and students)",
      "B2B Wholesale Portal (Carton/bulk tier pricing for bookshops & retail distributors with secure login)",
      "Institutional / School Supply (Formal proforma invoices, bulk term supply contracts, and RFQs)",
      "Physical Store Point of Sale / POS (Fast counter sales & receipt generation for Sunyani shop staff)"
    ])
    .setRequired(true);

  const stockPolicyItem = form.addMultipleChoiceItem();
  stockPolicyItem.setTitle("10. Public Stock Count Visibility Policy")
    .setHelpText("Strategic note: Displaying exact low counts (e.g. '4 units left') discourages institutional buyers who need 200+ units.")
    .setChoiceValues([
      "Status Badges Only: 'In Stock', 'Available on Order', 'Backorder Allowed' (Recommended by SikaDev)",
      "Literal Numeric Count: Show exact physical count (e.g. '47 packs remaining in Sunyani')"
    ])
    .setRequired(true);

  // ==========================================
  // SECTION 3: SCHOOL CUSTOMIZATION & PRINTING
  // ==========================================
  const sec3 = form.addPageBreakItem();
  sec3.setTitle("Section 3: School Book Customization & Printing System");
  sec3.setHelpText("Desaint Stationeries specializes in custom-branded exercise books for schools across Ghana.");

  const customItem = form.addMultipleChoiceItem();
  customItem.setTitle("11. How should school proprietors submit custom exercise book orders?")
    .setChoiceValues([
      "Interactive Web Configurator: Upload school crest/logo, select ruling & page count, preview mock-up (Recommended)",
      "Request for Quote (RFQ) Form: School fills simple specs, staff generates and emails manual quote",
      "Both: Online quote generator with automated preliminary proof + staff sign-off"
    ])
    .setRequired(true);

  form.addTextItem()
    .setTitle("12. Minimum Order Quantity (MOQ) for Custom-Branded Exercise Books")
    .setHelpText("Minimum number of copies required per school design print run (e.g. 500 copies)")
    .setRequired(true);

  const plateFeeItem = form.addMultipleChoiceItem();
  plateFeeItem.setTitle("13. Plate / Die Graphic Setup Fee Policy")
    .setChoiceValues([
      "Included in Unit Cost (No upfront plate charge for the school)",
      "One-Time Setup Fee (e.g. GH¢ 150 per new school cover design)",
      "Free if order exceeds 1,000 copies, otherwise billed"
    ])
    .setRequired(true);

  const bookTypesItem = form.addCheckboxItem();
  bookTypesItem.setTitle("14. Supported Book Ruling Categories for Customization")
    .setChoiceValues([
      "Standard Exercise Books (40, 60, 80 pages - Single / Broad line)",
      "Note 1 & Note 3 Books (120 to 200 pages - Hard / Soft cover)",
      "Pre-School & Kindergarten Books (Double line, square grid, tracing, drawing sheets)",
      "Graph & Sketch Books (Science & mathematical drawing books)"
    ])
    .setRequired(true);

  const designItem = form.addMultipleChoiceItem();
  designItem.setTitle("15. Graphic Design Studio & Digital Proofing Workflow")
    .setHelpText("Desaint Stationeries provides in-house creative design for school crests, cover artwork, and corporate branding.")
    .setChoiceValues([
      "Yes, digital Proofing Portal needed: Staff uploads PDF/image proof, school reviews and signs off before printing (Recommended)",
      "Yes, offer graphic design but handle approvals manually over WhatsApp / in person",
      "Only basic artwork adjustments needed"
    ])
    .setRequired(true);

  const importItem = form.addMultipleChoiceItem();
  importItem.setTitle("16. Importation Supply Chain & Landed Cost Tracking")
    .setHelpText("For goods imported from overseas factories (China, India, etc.) arriving via Tema port.")
    .setChoiceValues([
      "Yes, Landed Cost Calculator needed: Track container consignments, FX rates (USD/RMB to GHS), customs duty & freight allocation to unit cost",
      "Standard local supplier purchase orders only",
      "Manage importation spreadsheets separately for now"
    ])
    .setRequired(true);

  const generalSuppliesItem = form.addCheckboxItem();
  generalSuppliesItem.setTitle("17. Additional Product Verticals & General Supplies ('And More')")
    .setHelpText("Select all additional non-book supply categories Desaint handles:")
    .setChoiceValues([
      "Promotional Merchandise (Branded school bags, water bottles, pens, customized lacoste/uniforms)",
      "School ID Cards, Badges & Lanyards",
      "Teaching & Learning Materials / Science Lab Kits",
      "General Corporate & Institutional Office Supplies"
    ])
    .setRequired(true);

  // ==========================================
  // SECTION 4: GHANA TAX & PAYMENT RAILS
  // ==========================================
  const sec4 = form.addPageBreakItem();
  sec4.setTitle("Section 4: Pricing, Invoicing & Ghana Tax Compliance");
  sec4.setHelpText("Tax handling compliant with GRA regulations and local payment channels.");

  const taxItem = form.addMultipleChoiceItem();
  taxItem.setTitle("18. GRA Tax Invoicing Preference")
    .setChoiceValues([
      "Dual Mode: GRA Standard VAT for Institutional/Tenders + Retail Slip for Walk-ins (Recommended)",
      "GRA Standard Rate (15% VAT + 2.5% NHIL + 2.5% GETFund + 1% COVID Levy)",
      "GRA Flat Rate Scheme (3% Flat + 1% COVID = 4%)",
      "Non-VAT Registered / Exempt (Net sales receipts only)"
    ])
    .setRequired(true);

  const whtItem = form.addMultipleChoiceItem();
  whtItem.setTitle("19. Statutory Withholding Tax (3% WHT / 5% WHVAT) for Institutional Supply")
    .setHelpText("Under Ghana Act 896, government and institutional buyers withhold tax at source.")
    .setChoiceValues([
      "Yes, auto-calculate Net Payable after 3% WHT deduction on institutional invoices (Recommended)",
      "Not needed at launch"
    ])
    .setRequired(true);

  const paymentItem = form.addCheckboxItem();
  paymentItem.setTitle("20. Required Payment Channels")
    .setChoiceValues([
      "Automated Mobile Money (MTN MoMo & Telecel Cash via Paystack / Hubtel gateway)",
      "Manual MoMo Merchant Till / Phone Number (Customer enters transaction ID for verification)",
      "Direct Bank Transfer (Bank account details displayed on proformas)",
      "Cash on Delivery / In-Store Cash Counter (Physical settlement in Sunyani)",
      "Credit Terms / 30-Day Purchase Orders (For vetted institutional schools)"
    ])
    .setRequired(true);

  // ==========================================
  // SECTION 5: REGIONAL LOGISTICS & DISPATCH
  // ==========================================
  const sec5 = form.addPageBreakItem();
  sec5.setTitle("Section 5: Regional Logistics & Delivery Models");
  sec5.setHelpText("Moving goods from the Sunyani hub to Bono, Ashanti, Central and nationwide customers.");

  const shippingItem = form.addCheckboxItem();
  shippingItem.setTitle("21. Active Fulfillment & Delivery Methods")
    .setChoiceValues([
      "Bus Terminal Parcel Dispatch (VIP, OA, Imperial, Metro Mass parcels from Sunyani)",
      "Direct Institutional Truck / Van Delivery (Desaint delivery vehicle transports bulk cartons to campus)",
      "In-Store Customer Pickup (Collection at Sunyani head office)",
      "Local City Courier / Dispatch Rider (Fast door-to-door delivery within Sunyani metropolis)"
    ])
    .setRequired(true);

  form.addTextItem()
    .setTitle("22. Priority Focus Regions")
    .setHelpText("e.g. Bono, Bono East, Ahafo, Ashanti, Central, Western North")
    .setRequired(true);

  // ==========================================
  // SECTION 6: TIMELINE & SPECIAL NOTES
  // ==========================================
  const sec6 = form.addPageBreakItem();
  sec6.setTitle("Section 6: Launch Targets & Custom Notes");

  form.addTextItem()
    .setTitle("23. Desired Go-Live Target Date / Upcoming School Term Window")
    .setHelpText("e.g. Ahead of Next Term Resumption or specific date");

  form.addParagraphTextItem()
    .setTitle("24. Additional Notes or Specific Feature Requests for SikaDev")
    .setHelpText("Any special integrations, custom report layouts, or specific operational requirements from Mr. Solomon.");

  // Output URLs to execution log
  const editUrl = form.getEditUrl();
  const publishedUrl = form.getPublishedUrl();

  Logger.log("=================================================");
  Logger.log("✅ GOOGLE FORM CREATED SUCCESSFULLY BY SIKADEV!");
  Logger.log("=================================================");
  Logger.log("🔗 EDIT / ADMIN URL (for SikaDev to manage):");
  Logger.log(editUrl);
  Logger.log("-------------------------------------------------");
  Logger.log("📱 CLIENT SHAREABLE URL (Send to Mr. Solomon):");
  Logger.log(publishedUrl);
  Logger.log("=================================================");
}
