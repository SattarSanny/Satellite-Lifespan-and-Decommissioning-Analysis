# 🌌 Satellite Lifespan and Decommissioning Dashboard

**Visualizing Trends and Impacts on Space Sustainability**

This interactive web dashboard explores the lifespan, decommissioning status, and orbital distribution of satellites using real-world launch data. It highlights historical patterns, growing space clutter, and the urgency for sustainable space practices.

---

## 🚀 Features

- 📊 **KDE Lifespan Plot**  
  View how satellite lifespans have changed by launch decade, from the 1950s to 2020s.

- 🛰️ **Active vs Decommissioned Overview**  
  Compare the number of satellites still active vs. those retired per decade.

- 🌍 **Orbit Distribution of Retired Satellites**  
  Identify which orbits (LEO, GEO, etc.) accumulate the most decommissioned satellites.

- 🎨 **Infographic-style Visuals**  
  Integrated space-themed icons and background planets (Earth, Moon, Jupiter, etc.) for a clean and engaging design.

- 📦 **Filters and KPIs**  
  Filter by launch decade, mass range, orbit type, and satellite status. View total counts and averages in real-time.

---

## 🧠 Tech Stack

- **Frontend & Dashboard:** Python, Plotly Dash  
- **Data Processing:** pandas, NumPy, SciPy (KDE)  
- **Visualization:** Plotly Graph Objects & Express  
- **Assets:** PNG planet icons and space elements  
- **Backend Logic:** Filtered callbacks and lifecycle metrics  
- **Dataset:** `satcat.tsv` (Satellite catalog data)

---

## 📁 Project Structure

```
📦 satellite-lifespan-dashboard/
│
├── dashboard.py           # Dash app code
├── satcat.tsv             # Satellite dataset
├── assets/                # Background images and planet icons
│   ├── real_earth.png
│   ├── real_jupiter.png
│   ├── real_moon.png
│   ├── real_neptune.png
│   ├── real_planet.png
│   ├── real_saturn.png
│   └── sat.png
├── 4304_infographic.ipynb # Jupyter notebook (design reference)
├── infographic.pdf        # Final infographic
└── README.md              # This file
```

---

## 📸 Preview

> This project complements a static infographic and supports stakeholder storytelling through dynamic filtering and responsive graphs.

---

## 📢 Authors

- **Abdul Sattar Sanny**  
- **Abrar Faiyaz**

---

## 📜 License

This project is for academic use under COMP 4304 (Memorial University).
