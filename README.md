# 🖼️ FrameCraft Studio - Custom Photo Frame & Print Platform

A full-stack custom photo frame e-commerce web platform built with **Python (Flask)**. Features an interactive 3D live framing visualizer studio, customer account login & Flipkart-style live order stepper tracking, high-resolution photo upload workflow, and a dark cyber-glassmorphic admin fulfillment & 300 DPI print-file download station.

---

## 🌟 Key Features

1. **Occasion Frame Storefront**:
   - Clean theme with responsive search, occasion categories (Wedding, Birthday, Baby, Family, Graduation, Memorial).
   - Hero banner promos, Deals of the Day countdown, discounts, and verified customer ratings.
   - User Registration, Login, and "My Orders" order history with live stepper status updates.
   - Strict login-gated 4-step accordion checkout with Cash on Delivery (COD) and UPI.

2. **Interactive 3D Live Photo Framing Studio (Visualizer)**:
   - Customers upload photos directly (JPG, PNG, WEBP, HEIC up to 32MB).
   - Real-time Canvas rendering with 3D perspective tilt, live pan, zoom (0.5x to 3.0x), crop, and 90° rotation.
   - Realistic Frame Styles: Solid Walnut Wood, Nordic Matte Black, Royal Gold Baroque, Scandinavian Oak, Floating Acrylic Glass, Gallery White Box, Rustic Barnwood, and Canvas Shadow Box.
   - Dynamic Matting / Passe-partout (Museum Off-White, Cream, Charcoal, Black, or None) with bevel edge lighting.
   - Realistic Room Wall Switcher: See the framed photo hanging in a Modern Living Room, Bedroom, Office, or Clean Studio Wall.
   - Real-time price calculation based on chosen dimensions (6x4", 8x10", 12x18", 16x24", 20x30", 24x36").

3. **Admin Print Lab & Order Center (Hot Dark Theme)**:
   - Admin login (`/admin/login`) & Registration (`/admin/register`).
   - Order pipeline with KPI statistics (Pending, Printing, Assembled, Shipped, Delivered).
   - **1-Click High-Res Photo Download (300 DPI)** for physical lab printing.
   - Customer details, shipping address, and WhatsApp contact link.

---

## 🚀 Quickstart

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

- **Storefront**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Live Frame Visualizer**: [http://127.0.0.1:5000/studio](http://127.0.0.1:5000/studio)
- **Track Order Stepper**: [http://127.0.0.1:5000/track-order](http://127.0.0.1:5000/track-order)
- **Admin Hub**: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login) *(Default: `admin` / `admin123`)*
