# 📊 Sales Data Analysis & Business Intelligence Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-EDA-green)
![API](https://img.shields.io/badge/CoinGecko%20API-Free-green)
![API](https://img.shields.io/badge/REST%20Countries%20API-Free-green)

> A comprehensive sales analytics project that generates KPIs, a 6-panel BI dashboard, cohort heatmaps, and regional breakdowns — enriched with live exchange rates and country metadata from two completely free APIs.

---

## 📌 Project Highlights

| Feature | Detail |
|---|---|
| **Dataset** | 2,500 synthetic transactions across 2 years |
| **KPIs** | Revenue, Profit Margin, AOV, Top Product/Region/Rep |
| **Visuals** | 6-panel dashboard + monthly cohort heatmap |
| **APIs** | CoinGecko + REST Countries — both FREE, no key |

---

## 🌐 API Integrations — Both Completely Free

### 1. CoinGecko Exchange Rates API
```
GET https://api.coingecko.com/api/v3/exchange_rates
```
- Live USD exchange rates vs EUR, GBP, JPY, PKR, AED
- **Cost:** Free | **Key:** None | **Docs:** https://docs.coingecko.com

### 2. REST Countries API
```
GET https://restcountries.com/v3.1/alpha/US
```
- Country region, population, economic metadata
- **Cost:** Free | **Key:** None | **Docs:** https://restcountries.com

> ⚠️ **Security:** No API keys used. `.gitignore` excludes all `.env` files.

---

## 📊 Sample Outputs

| Output | Description |
|---|---|
| `outputs/sales_dashboard.png` | 6-panel BI dashboard |
| `outputs/revenue_heatmap.png` | Year × Month revenue heatmap |
| `outputs/region_summary.csv` | Revenue/profit per region |
| `outputs/sales_data.csv` | Full transaction dataset |
| `outputs/report.json` | KPIs + API data summary |

### Dashboard Panels
1. Monthly Revenue Trend + 3-month rolling average
2. Revenue by Product Category
3. Profit Margin by Region
4. Sales Channel Mix (pie chart)
5. Top Products by Revenue
6. Quarterly Revenue vs Profit + Live Exchange Rates

---

## 🚀 Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/sales-bi-dashboard
cd sales-bi-dashboard

pip install -r requirements.txt
python sales_analysis.py
```

---

## 📁 Project Structure

```
sales-bi-dashboard/
├── sales_analysis.py    # Full EDA + dashboard pipeline
├── requirements.txt
├── .gitignore
├── .env.example
└── outputs/
    ├── sales_dashboard.png
    ├── revenue_heatmap.png
    ├── region_summary.csv
    ├── sales_data.csv
    └── report.json
```

---

## 🧰 Tech Stack

`pandas` · `matplotlib` · `seaborn` · `requests` · `CoinGecko API` · `REST Countries API`

---

## 👤 Author

**Muntaha** — Data Analyst | Data Scientist  
[LinkedIn](#) · [GitHub](#)
