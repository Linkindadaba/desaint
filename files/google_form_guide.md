# SikaDev — Automated Google Form Setup Guide
**Client:** Naito De Saint Enterprise (Desaint Stationeries)  
**Target:** Mr. Aseim Solomon (Sunyani, Ghana)  
**Developer:** SikaDev Software Engineering  

---

## Method 1: The 10-Second Auto-Generator (Recommended) ⚡

We wrote a Google Apps Script that automatically builds the entire multi-page form with all 21 questions, sections, and default values inside your own Google Drive in under 10 seconds.

### Steps:
1. Open your browser and navigate to: **[https://script.new](https://script.new)**  
   *(Make sure you are signed into your preferred Google account).*
2. In the code window that opens, **select all existing text (`Ctrl + A`) and delete it**.
3. Open the file **[`create_google_form.gs`](file:///c:/Users/USER/Desktop/py_env/desaint-stationeries/create_google_form.gs)** on your computer, copy all the code, and paste it into the script editor.
4. Click the **💾 Save** button at the top (or press `Ctrl + S`).
5. Click the **▶ Run** button at the toolbar.
6. Google will show a quick one-time authorization popup:
   - Click **Review Permissions**
   - Select your Google account
   - Click **Advanced** (at the bottom left of the modal)
   - Click **"Go to Untitled project (unsafe)"** *(standard Google warning for personal scripts)*
   - Click **Allow**
7. Look at the **Execution Log** at the bottom of the screen:
   - You will see two links:
     - 🔗 **Admin / Edit URL:** Where you can edit, customize, or view responses.
     - 📱 **Client Shareable URL:** The direct link you copy and send to Mr. Solomon via WhatsApp or Email!

---

## Method 2: Link Form Responses to Google Sheets 📊

Once Mr. Solomon begins submitting his answers:
1. Open the form using your **Admin / Edit URL**.
2. Click the **"Responses"** tab at the top.
3. Click the green **"Link to Sheets"** icon.
4. Click **"Create"**.
5. You now have a live, real-time Google Sheet tracking all specifications submitted by the client!

---

## What the Google Form Contains:
- **Section 1: Corporate Identity & Contacts** (Pre-fills Naito De Saint Enterprise, Desaint Stationeries, Sunyani, phones, email).
- **Section 2: Sales Channels & Customer Journey** (B2C Retail, B2B Wholesale, Institutional School Supply, POS).
- **Section 3: School Book Customization & Printing System** (Online customizer vs RFQ, MOQs, cover plate fees, ruling types).
- **Section 4: Pricing, Invoicing & Ghana Tax Compliance** (GRA VAT schemes, 3% WHT Act 896, MoMo/Bank).
- **Section 5: Regional Logistics & Delivery** (VIP/OA bus parcel, direct school truck delivery, city courier, Bono/Ashanti regions).
- **Section 6: Launch Targets & Custom Notes** (Term dates, specific feature requests).
