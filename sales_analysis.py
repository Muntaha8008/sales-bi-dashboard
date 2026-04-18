"""
Sales Data Analysis & Business Intelligence Dashboard
======================================================
Full exploratory data analysis pipeline on synthetic sales data,
enriched with live economic indicators from two free public APIs.

Free APIs used:
  1. CoinGecko API   https://api.coingecko.com/api/v3/
     Live crypto/market data for currency context.
     100% FREE | No API key | No account | No credit card

  2. REST Countries API   https://restcountries.com/v3.1/
     Country-level economic metadata.
     100% FREE | No API key | No account | No credit card
"""

import os, json, requests, time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

np.random.seed(42)
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── FREE API 1: CoinGecko (NO KEY NEEDED) ────────────────────────────────────

def fetch_exchange_rates():
    """
    Fetch USD exchange rates vs major currencies from CoinGecko.
    FREE — https://api.coingecko.com | No API key | No account
    Used to contextualise multi-currency sales data.
    Docs: https://www.coingecko.com/api/documentation
    """
    url = "https://api.coingecko.com/api/v3/exchange_rates"
    print("[API] CoinGecko → fetching exchange rates...")
    try:
        r = requests.get(url, timeout=10); r.raise_for_status()
        rates = r.json().get("rates", {})
        selected = {}
        for currency in ["usd", "eur", "gbp", "jpy", "pkr", "aed"]:
            if currency in rates:
                selected[currency.upper()] = {
                    "name": rates[currency]["name"],
                    "value": round(rates[currency]["value"], 4),
                    "type": rates[currency]["type"],
                }
        print(f"[API] ✓ CoinGecko: {len(selected)} exchange rates retrieved")
        return selected
    except Exception as e:
        print(f"[API] CoinGecko fallback ({e})")
        return {"USD":{"name":"US Dollar","value":1.0},
                "EUR":{"name":"Euro","value":0.92},
                "GBP":{"name":"British Pound","value":0.79}}


# ─── FREE API 2: REST Countries (NO KEY NEEDED) ───────────────────────────────

def fetch_region_gdp_context():
    """
    Fetch country region data from REST Countries API.
    FREE — https://restcountries.com | No key | No account
    """
    regions = ["US", "GB", "DE", "JP", "AE"]
    print("[API] REST Countries → fetching regional metadata...")
    results = {}
    for code in regions:
        try:
            r = requests.get(f"https://restcountries.com/v3.1/alpha/{code}",
                             timeout=8); r.raise_for_status()
            d = r.json()[0]
            results[code] = {
                "country": d.get("name",{}).get("common",""),
                "region":  d.get("region",""),
                "population": d.get("population",0),
            }
            time.sleep(0.15)
        except Exception as e:
            print(f"[API] Skipped {code}: {e}")
    print(f"[API] ✓ REST Countries: {len(results)} countries retrieved")
    return results


# ─── SYNTHETIC SALES DATA ─────────────────────────────────────────────────────

PRODUCTS = {
    "Laptop Pro X":     {"category":"Electronics","base_price":1299,"cost":780},
    "Wireless Mouse":   {"category":"Electronics","base_price":45,  "cost":18},
    "USB-C Hub":        {"category":"Electronics","base_price":89,  "cost":32},
    "Office Chair":     {"category":"Furniture",  "base_price":349, "cost":195},
    "Standing Desk":    {"category":"Furniture",  "base_price":599, "cost":340},
    "Notebook A5":      {"category":"Stationery", "base_price":12,  "cost":3},
    "Marker Set":       {"category":"Stationery", "base_price":18,  "cost":6},
    "Python Book":      {"category":"Books",      "base_price":49,  "cost":22},
    "ML Textbook":      {"category":"Books",      "base_price":79,  "cost":35},
    "Headphones Pro":   {"category":"Electronics","base_price":249, "cost":120},
}

REGIONS   = ["North America","Europe","Asia Pacific","Middle East","South Asia"]
CHANNELS  = ["Online","Retail","B2B","Distributor"]
REPS      = [f"Rep_{i:02d}" for i in range(1, 16)]


def generate_sales_data(n=2500):
    """Generate 2 years of realistic synthetic sales transactions."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)

    products = list(PRODUCTS.keys())
    product_weights = [0.12,0.18,0.12,0.08,0.06,0.12,0.08,0.10,0.07,0.07]

    dates      = [start_date + timedelta(days=int(np.random.exponential(0.8)*i % 730))
                  for i in range(1, n+1)]
    prod_names = np.random.choice(products, n, p=product_weights)
    regions    = np.random.choice(REGIONS,   n, p=[.35,.28,.20,.10,.07])
    channels   = np.random.choice(CHANNELS,  n, p=[.42,.30,.20,.08])
    reps       = np.random.choice(REPS, n)
    quantities = np.random.randint(1, 25, n)

    rows = []
    for i in range(n):
        p     = PRODUCTS[prod_names[i]]
        price = p["base_price"] * np.random.uniform(0.85, 1.15)
        cost  = p["cost"] * np.random.uniform(0.90, 1.10)
        qty   = quantities[i]
        rows.append({
            "order_id":      f"ORD-{10000+i}",
            "date":           sorted(dates)[i],
            "product":        prod_names[i],
            "category":       p["category"],
            "region":         regions[i],
            "channel":        channels[i],
            "sales_rep":      reps[i],
            "quantity":       qty,
            "unit_price":     round(price, 2),
            "unit_cost":      round(cost, 2),
            "revenue":        round(price * qty, 2),
            "cogs":           round(cost  * qty, 2),
        })

    df = pd.DataFrame(rows)
    df["profit"]        = (df["revenue"] - df["cogs"]).round(2)
    df["profit_margin"] = (df["profit"] / df["revenue"] * 100).round(2)
    df["month"]         = df["date"].dt.to_period("M").astype(str)
    df["quarter"]       = df["date"].dt.to_period("Q").astype(str)
    df["year"]          = df["date"].dt.year
    df["weekday"]       = df["date"].dt.day_name()
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ─── ANALYSIS FUNCTIONS ───────────────────────────────────────────────────────

def compute_kpis(df):
    kpis = {
        "total_revenue":      round(df["revenue"].sum(), 2),
        "total_profit":       round(df["profit"].sum(), 2),
        "avg_profit_margin":  round(df["profit_margin"].mean(), 2),
        "total_orders":       len(df),
        "total_units_sold":   int(df["quantity"].sum()),
        "avg_order_value":    round(df["revenue"].mean(), 2),
        "top_product":        df.groupby("product")["revenue"].sum().idxmax(),
        "top_region":         df.groupby("region")["revenue"].sum().idxmax(),
        "top_channel":        df.groupby("channel")["revenue"].sum().idxmax(),
        "top_rep":            df.groupby("sales_rep")["revenue"].sum().idxmax(),
    }
    print("\n" + "="*50)
    print("  KEY PERFORMANCE INDICATORS")
    print("="*50)
    for k, v in kpis.items():
        print(f"  {k:<25} {v}")
    return kpis


# ─── VISUALISATIONS ───────────────────────────────────────────────────────────

def plot_dashboard(df, kpis, exchange_rates):
    """Full 6-panel business intelligence dashboard."""
    fig = plt.figure(figsize=(18, 14))
    gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.42, wspace=0.38)
    fig.suptitle("Sales Business Intelligence Dashboard",
                 fontsize=17, fontweight="bold", y=0.98)

    PALETTE = ["#1565C0","#43A047","#E53935","#FB8C00","#8E24AA","#00ACC1"]

    # ── Panel 1: Monthly Revenue Trend ──
    ax1 = fig.add_subplot(gs[0, :2])
    monthly = df.groupby("month")["revenue"].sum().reset_index()
    monthly["rolling3"] = monthly["revenue"].rolling(3, min_periods=1).mean()
    ax1.bar(range(len(monthly)), monthly["revenue"],
            color="#1565C0", alpha=0.6, label="Monthly Revenue")
    ax1.plot(range(len(monthly)), monthly["rolling3"],
             color="#E53935", linewidth=2.5, label="3-Month Rolling Avg")
    ax1.set_title("Monthly Revenue Trend", fontsize=12, fontweight="bold")
    ax1.set_xticks(range(0, len(monthly), 3))
    ax1.set_xticklabels(monthly["month"].iloc[::3], rotation=30, ha="right", fontsize=8)
    ax1.set_ylabel("Revenue ($)"); ax1.legend(fontsize=9); ax1.grid(axis="y", alpha=.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.0f}"))

    # ── Panel 2: Revenue by Category ──
    ax2 = fig.add_subplot(gs[0, 2])
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=True)
    ax2.barh(cat_rev.index, cat_rev.values,
             color=PALETTE[:len(cat_rev)], edgecolor="white")
    ax2.set_title("Revenue by Category", fontsize=12, fontweight="bold")
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
    ax2.grid(axis="x", alpha=.3)

    # ── Panel 3: Profit Margin by Region ──
    ax3 = fig.add_subplot(gs[1, 0])
    reg_margin = df.groupby("region")["profit_margin"].mean().sort_values()
    bars = ax3.barh(reg_margin.index, reg_margin.values,
                    color=["#E53935" if v<20 else "#43A047" for v in reg_margin.values],
                    edgecolor="white")
    ax3.set_title("Avg Profit Margin by Region", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Margin (%)"); ax3.grid(axis="x", alpha=.3)

    # ── Panel 4: Sales Channel Mix ──
    ax4 = fig.add_subplot(gs[1, 1])
    channel_rev = df.groupby("channel")["revenue"].sum()
    ax4.pie(channel_rev, labels=channel_rev.index, autopct="%1.1f%%",
            colors=PALETTE[:len(channel_rev)], startangle=90,
            wedgeprops={"edgecolor":"white","linewidth":1.5})
    ax4.set_title("Revenue by Sales Channel", fontsize=12, fontweight="bold")

    # ── Panel 5: Top 10 Products by Revenue ──
    ax5 = fig.add_subplot(gs[1, 2])
    top_prod = df.groupby("product")["revenue"].sum().sort_values(ascending=True).tail(8)
    ax5.barh(top_prod.index, top_prod.values, color="#43A047", edgecolor="white")
    ax5.set_title("Revenue by Product", fontsize=12, fontweight="bold")
    ax5.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
    ax5.grid(axis="x", alpha=.3)

    # ── Panel 6: Quarterly Profit vs Revenue ──
    ax6 = fig.add_subplot(gs[2, :2])
    qtr = df.groupby("quarter").agg(revenue=("revenue","sum"),
                                     profit=("profit","sum")).reset_index()
    x = range(len(qtr))
    w = 0.38
    ax6.bar([i-w/2 for i in x], qtr["revenue"], w, label="Revenue",
            color="#1565C0", alpha=.8)
    ax6.bar([i+w/2 for i in x], qtr["profit"], w, label="Profit",
            color="#43A047", alpha=.8)
    ax6.set_xticks(x); ax6.set_xticklabels(qtr["quarter"], rotation=30, ha="right")
    ax6.set_title("Quarterly Revenue vs Profit", fontsize=12, fontweight="bold")
    ax6.set_ylabel("Amount ($)"); ax6.legend(); ax6.grid(axis="y", alpha=.3)
    ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))

    # ── Panel 7: Exchange Rate Context (from CoinGecko API) ──
    ax7 = fig.add_subplot(gs[2, 2])
    if exchange_rates:
        currencies = list(exchange_rates.keys())[:5]
        values     = [1/exchange_rates[c]["value"] for c in currencies
                      if exchange_rates[c]["value"] > 0]
        ax7.bar(currencies[:len(values)], values[:len(values)],
                color="#8E24AA", edgecolor="white")
        ax7.set_title("Currency Context\n(CoinGecko API — Live)",
                      fontsize=11, fontweight="bold")
        ax7.set_ylabel("1 unit → USD"); ax7.grid(axis="y", alpha=.3)
    else:
        ax7.text(0.5, 0.5, "Exchange rate\ndata unavailable",
                 ha="center", va="center", transform=ax7.transAxes)
        ax7.set_title("Exchange Rate Context")

    plt.savefig(f"{OUTPUT_DIR}/sales_dashboard.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] sales_dashboard.png saved → {OUTPUT_DIR}/")


def plot_cohort_heatmap(df):
    """Monthly cohort revenue heatmap."""
    df["month_num"] = df["date"].dt.month
    df["year"]      = df["date"].dt.year
    pivot = df.pivot_table(values="revenue", index="year",
                           columns="month_num", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu",
                ax=ax, linewidths=.5, cbar_kws={"label":"Revenue ($)"})
    ax.set_title("Revenue Heatmap — Year × Month",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Year")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/revenue_heatmap.png", dpi=150)
    plt.close()
    print(f"[PLOT] revenue_heatmap.png saved")


def save_summary_tables(df, kpis, exchange_rates, region_data):
    df.to_csv(f"{OUTPUT_DIR}/sales_data.csv", index=False)

    region_summary = (df.groupby("region")
                      .agg(total_revenue=("revenue","sum"),
                           total_profit=("profit","sum"),
                           orders=("order_id","count"),
                           avg_margin=("profit_margin","mean"))
                      .round(2).reset_index())
    region_summary.to_csv(f"{OUTPUT_DIR}/region_summary.csv", index=False)

    report = {
        "generated_at":   datetime.now().isoformat(),
        "kpis":           kpis,
        "exchange_rates": exchange_rates,
        "region_context": region_data,
        "apis_used": [
            {"name":"CoinGecko API","url":"https://api.coingecko.com","key_required":False},
            {"name":"REST Countries API","url":"https://restcountries.com","key_required":False},
        ],
    }
    with open(f"{OUTPUT_DIR}/report.json","w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"[OUTPUT] Reports saved → {OUTPUT_DIR}/")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("="*55)
    print("  Sales EDA & Business Intelligence Dashboard")
    print("="*55)

    # Free API calls
    exchange_rates = fetch_exchange_rates()
    region_data    = fetch_region_gdp_context()

    # Generate data
    df = generate_sales_data(2500)
    print(f"\n[DATA] {len(df)} transactions | "
          f"${df['revenue'].sum():,.0f} total revenue | "
          f"{df['date'].min().date()} → {df['date'].max().date()}")

    # KPIs
    kpis = compute_kpis(df)

    # Plots
    plot_dashboard(df, kpis, exchange_rates)
    plot_cohort_heatmap(df)

    # Save
    save_summary_tables(df, kpis, exchange_rates, region_data)

    print(f"\n{'='*55}")
    print(f"  Total Revenue  : ${kpis['total_revenue']:,.2f}")
    print(f"  Total Profit   : ${kpis['total_profit']:,.2f}")
    print(f"  Avg Margin     : {kpis['avg_profit_margin']}%")
    print(f"  Top Product    : {kpis['top_product']}")
    print(f"  Outputs        → {OUTPUT_DIR}/")
    print("="*55)
