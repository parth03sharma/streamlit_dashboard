"""
Sales Analytics Dashboard  ·  Sept–Oct 2025
Run:  streamlit run sales_dashboard.py
Requires: streamlit plotly pandas numpy
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS  — light theme, vibrant accents
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F5F7FA;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
[data-testid="stSidebar"] label { color: #334155 !important; font-weight: 500; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 20px 13px 20px;
    box-shadow: 0 1px 6px rgba(15,23,42,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 6px 22px rgba(99,102,241,0.14);
    transform: translateY(-2px);
}
[data-testid="metric-container"] label {
    color: #64748B !important;
    font-size: 0.70rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.76rem !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 5px 6px;
    gap: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent;
    border-radius: 9px;
    color: #64748B !important;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 8px 16px;
    border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: #FFFFFF !important;
    font-weight: 700;
}

/* ── Section headers ── */
.sec-head {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1E293B;
    margin: 1.4rem 0 0.5rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid #E0E7FF;
    letter-spacing: -0.01em;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR SYSTEM  — vibrant, diverse, pop-y
# ─────────────────────────────────────────────────────────────────────────────
# Primary pair (dual-axis / two-series)
C1   = "#6366F1"   # vivid indigo
C2   = "#F59E0B"   # vivid amber
DARK = "#1E293B"   # near-black for titles

# Rich 10-colour categorical palette
CAT10 = ["#6366F1","#F59E0B","#10B981","#EF4444","#3B82F6",
          "#EC4899","#14B8A6","#F97316","#8B5CF6","#06B6D4"]

# Sequential scales — all distinct, all vibrant
SEQ_INDIGO  = [[0,"#EEF2FF"],[0.5,"#6366F1"],[1,"#312E81"]]   # pale indigo → deep indigo
SEQ_TEAL    = [[0,"#F0FDFA"],[0.5,"#14B8A6"],[1,"#134E4A"]]   # pale teal  → deep teal
SEQ_ORANGE  = [[0,"#FFF7ED"],[0.5,"#F97316"],[1,"#7C2D12"]]   # pale orange → deep orange
SEQ_PINK    = [[0,"#FDF2F8"],[0.5,"#EC4899"],[1,"#831843"]]   # pale pink  → deep pink
SEQ_GREEN   = [[0,"#F0FDF4"],[0.5,"#10B981"],[1,"#064E3B"]]   # pale green → deep green

# TEMPERATURE GRADIENT for geographic charts
# Dark navy (cold/low) → cyan → yellow → red (hot/high)
TEMP_GEO    = [[0,"#1E3A5F"],[0.25,"#0EA5E9"],[0.55,"#FCD34D"],[0.8,"#F97316"],[1,"#DC2626"]]

# Gradient for age charts: lightest to darkest indigo
AGE_GRAD    = [[0,"#C7D2FE"],[0.33,"#818CF8"],[0.66,"#4F46E5"],[1,"#1E1B4B"]]
AGE_COLOURS = ["#C7D2FE","#818CF8","#4F46E5","#1E1B4B"]

# Diverging for heatmap
DIV_PG = [[0,"#EC4899"],[0.5,"#F5F7FA"],[1,"#6366F1"]]

def CL(title="", height=360):
    """Shared clean light chart layout."""
    return dict(
        title=dict(text=title, font=dict(size=14, color=DARK, family="Inter")),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(color="#334155", family="Inter, sans-serif", size=12),
        height=height,
        margin=dict(t=46 if title else 24, b=20, l=10, r=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(showgrid=False, linecolor="#E2E8F0", tickcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", tickcolor="#E2E8F0"),
    )

def CL2(title="", height=360):
    """Variant without legend (avoids duplicate key when caller also sets legend)."""
    d = CL(title, height)
    d.pop("legend", None)
    return d

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#4F46E5,#8B5CF6);
                padding:22px 18px;border-radius:0 0 16px 16px;
                margin:-1rem -1rem 1.5rem -1rem;">
        <div style="font-size:1.3rem;font-weight:800;color:#fff;letter-spacing:-0.02em;">
            📊 Sales Analytics
        </div>
        <div style="font-size:0.7rem;color:rgba(255,255,255,0.6);margin-top:3px;
                    text-transform:uppercase;letter-spacing:0.08em;">
            Business Intelligence Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type="csv",
                                help="Upload comprehensive_sales_data_sept_oct_2025.csv")
    st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load(file):
    df = pd.read_csv(file)
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    df["Order_Date"]    = pd.to_datetime(df["Order_Date"],    errors="coerce")
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"], errors="coerce")
    df["Order_Hour"]    = df["Order_Time"].str[:2].astype(int, errors="ignore")
    df["Order_Month"]   = df["Order_Date"].dt.month_name()
    df["Order_DOW"]     = df["Order_Date"].dt.day_name()
    for c in ["Quantity","Unit_Price_INR","Discount_Percent","Discount_Amount_INR",
              "Tax_Amount_INR","Total_Amount_INR","Shipping_Cost_INR",
              "Days_to_Deliver","Customer_Age","Customer_Lifetime_Orders","Customer_Rating"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

if uploaded is None:
    st.markdown("""
    <div style="text-align:center;padding:100px 40px;">
        <div style="font-size:4rem;">📂</div>
        <h2 style="color:#1E293B;margin:16px 0 8px;">Welcome to Sales Analytics</h2>
        <p style="color:#64748B;font-size:1rem;">
            Upload <b>comprehensive_sales_data_sept_oct_2025.csv</b> from the sidebar to begin.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = load(uploaded)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")

    def ms(label, col):
        opts = sorted(df[col].dropna().unique().tolist())
        return st.multiselect(label, opts, default=opts, key=f"f_{col}")

    sel_seg    = ms("Customer Segment",  "Customer_Segment")
    sel_cat    = ms("Product Category",  "Product_Category")
    sel_status = ms("Order Status",      "Order_Status")
    sel_pay    = ms("Payment Method",    "Payment_Method")
    sel_ch     = ms("Sales Channel",     "Sales_Channel")
    sel_gender = ms("Gender",            "Customer_Gender")
    st.markdown("---")
    date_min = df["Order_Date"].min().date()
    date_max = df["Order_Date"].max().date()
    d1, d2   = st.date_input("Date Range", value=(date_min, date_max),
                              min_value=date_min, max_value=date_max)

# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
f = df[
    df["Customer_Segment"].isin(sel_seg) &
    df["Product_Category"].isin(sel_cat) &
    df["Order_Status"].isin(sel_status) &
    df["Payment_Method"].isin(sel_pay) &
    df["Sales_Channel"].isin(sel_ch) &
    df["Customer_Gender"].isin(sel_gender) &
    (df["Order_Date"].dt.date >= d1) &
    (df["Order_Date"].dt.date <= d2)
].copy()

# ─────────────────────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────────────────────
total_rev    = f["Total_Amount_INR"].sum()
total_ord    = len(f)
avg_ord_val  = f["Total_Amount_INR"].mean()
uniq_cust    = f["Customer_ID"].nunique()
units_sold   = f["Quantity"].sum()
avg_rating   = f["Customer_Rating"].mean()
avg_del_days = f["Days_to_Deliver"].mean()
total_disc   = f["Discount_Amount_INR"].sum()
delivery_pct = (f["Order_Status"] == "Delivered").mean() * 100
new_cust_pct = (f["First_Time_Customer"] == "Yes").mean() * 100

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:14px 0 10px 0;border-bottom:2px solid #E0E7FF;margin-bottom:14px;">
  <div>
    <h1 style="margin:0;font-size:1.65rem;font-weight:800;color:#1E293B;
               letter-spacing:-0.03em;">📊 Sales Analytics Dashboard</h1>
    <p style="margin:3px 0 0;color:#64748B;font-size:0.83rem;">
        Sept–Oct 2025 &nbsp;·&nbsp; <b>{total_ord:,}</b> orders &nbsp;·&nbsp;
        <b>{uniq_cust:,}</b> customers &nbsp;·&nbsp; Filtered view
    </p>
  </div>
  <div style="text-align:right;">
    <div style="font-size:1.6rem;font-weight:800;
                background:linear-gradient(135deg,#6366F1,#8B5CF6);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        ₹{total_rev:,.0f}
    </div>
    <div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;
                letter-spacing:0.07em;">Total Revenue</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5,t6 = st.tabs([
    "🏠  Overview",
    "📈  Sales Trends",
    "📦  Product Insights",
    "👥  Customer Analytics",
    "🗺️  Geographic",
    "⚙️  Operations & Quality",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("💰 Revenue",      f"₹{total_rev:,.0f}",   f"₹{total_rev/1e6:.2f}M total")
    k2.metric("📦 Orders",       f"{total_ord:,}",        f"{units_sold:,} units sold")
    k3.metric("💳 Avg Order",    f"₹{avg_ord_val:,.0f}",  "per transaction")
    k4.metric("👥 Customers",    f"{uniq_cust:,}",        f"{new_cust_pct:.0f}% first-time")
    k5.metric("⭐ Avg Rating",   f"{avg_rating:.2f}/5",   f"{delivery_pct:.0f}% delivered")
    k6.metric("🚚 Avg Delivery", f"{avg_del_days:.1f}d",  f"₹{total_disc:,.0f} discounts")

    st.markdown("")

    # ── Full-width daily revenue ──
    st.markdown('<div class="sec-head">Daily Revenue Trend</div>', unsafe_allow_html=True)
    daily = (f.groupby(f["Order_Date"].dt.date)
              .agg(Revenue=("Total_Amount_INR","sum"), Orders=("Order_ID","count"))
              .reset_index().rename(columns={"Order_Date":"Date"}))
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Revenue"],
        mode="lines+markers",
        line=dict(color=C1, width=2.5),
        marker=dict(size=5, color=C1),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
        name="Revenue (₹)",
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig_daily.update_layout(**CL("", 280))
    st.plotly_chart(fig_daily, use_container_width=True)

    c1,c2,c3 = st.columns([2,1.5,1.5])

    with c1:
        st.markdown('<div class="sec-head">Revenue vs Orders — Dual Axis</div>', unsafe_allow_html=True)
        fig_dual = make_subplots(specs=[[{"secondary_y":True}]])
        fig_dual.add_trace(go.Bar(
            x=daily["Date"], y=daily["Orders"],
            name="Orders", marker_color="rgba(245,158,11,0.28)",
            hovertemplate="%{y} orders<extra></extra>",
        ), secondary_y=False)
        fig_dual.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Revenue"],
            mode="lines", name="Revenue",
            line=dict(color=C1, width=2.5),
            hovertemplate="₹%{y:,.0f}<extra></extra>",
        ), secondary_y=True)
        fig_dual.update_layout(**CL("",340))
        fig_dual.update_yaxes(title_text="Orders",    secondary_y=False, gridcolor="#F1F5F9")
        fig_dual.update_yaxes(title_text="Revenue ₹", secondary_y=True,  showgrid=False,
                              tickfont=dict(color=C1))
        st.plotly_chart(fig_dual, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-head">Order Status</div>', unsafe_allow_html=True)
        st_d = f["Order_Status"].value_counts().reset_index()
        st_d.columns = ["Status","Count"]
        fig_stat = px.pie(st_d, names="Status", values="Count", hole=0.55,
                          color="Status",
                          color_discrete_map={"Delivered":"#10B981","Processing":"#F59E0B",
                                              "In Transit":"#6366F1"})
        fig_stat.update_traces(textposition="outside", textinfo="label+percent",
                               pull=[0.04,0.02,0.02])
        fig_stat.update_layout(**CL("",340))
        st.plotly_chart(fig_stat, use_container_width=True)

    with c3:
        st.markdown('<div class="sec-head">Customer Segments</div>', unsafe_allow_html=True)
        seg_kpi = f.groupby("Customer_Segment").agg(Revenue=("Total_Amount_INR","sum")).reset_index()
        fig_seg = px.bar(seg_kpi, x="Customer_Segment", y="Revenue",
                         color="Customer_Segment",
                         color_discrete_map={"Regular":"#6366F1","Premium":"#EC4899"},
                         text=seg_kpi["Revenue"].apply(lambda x: f"₹{x/1e3:.0f}K"),
                         labels={"Revenue":"Revenue (₹)","Customer_Segment":""})
        fig_seg.update_traces(textposition="outside", textfont_size=12)
        fig_seg.update_layout(**CL("",340), showlegend=False)
        st.plotly_chart(fig_seg, use_container_width=True)

    c4,c5 = st.columns(2)
    with c4:
        st.markdown('<div class="sec-head">Revenue by Payment Method</div>', unsafe_allow_html=True)
        pay = f.groupby("Payment_Method")["Total_Amount_INR"].sum().sort_values().reset_index()
        fig_pay = px.bar(pay, x="Total_Amount_INR", y="Payment_Method", orientation="h",
                         color="Total_Amount_INR", color_continuous_scale=SEQ_INDIGO,
                         text=pay["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"),
                         labels={"Total_Amount_INR":"Revenue (₹)","Payment_Method":""})
        fig_pay.update_traces(textposition="outside")
        fig_pay.update_layout(**CL("",300), coloraxis_showscale=False)
        st.plotly_chart(fig_pay, use_container_width=True)

    with c5:
        st.markdown('<div class="sec-head">Revenue by Sales Channel</div>', unsafe_allow_html=True)
        ch = f.groupby("Sales_Channel")["Total_Amount_INR"].sum().reset_index()
        fig_ch = px.pie(ch, names="Sales_Channel", values="Total_Amount_INR", hole=0.52,
                        color="Sales_Channel",
                        color_discrete_map={"Mobile App":"#6366F1","Website":"#F59E0B"})
        fig_ch.update_traces(textposition="outside", textinfo="label+percent")
        fig_ch.update_layout(**CL("",300))
        st.plotly_chart(fig_ch, use_container_width=True)

    # ── NEW: Radar chart — avg metrics by customer segment ──
    st.markdown('<div class="sec-head">Segment Radar — Avg KPIs Comparison</div>', unsafe_allow_html=True)
    radar_cols = ["Total_Amount_INR","Discount_Percent","Customer_Rating",
                  "Quantity","Days_to_Deliver","Customer_Lifetime_Orders"]
    radar_labels = ["Avg Order (₹)","Discount %","Rating","Qty/Order","Delivery Days","Lifetime Orders"]
    seg_r = f.groupby("Customer_Segment")[radar_cols].mean().reset_index()
    # Normalise to 0-1
    seg_norm = seg_r.copy()
    for col in radar_cols:
        rng = seg_norm[col].max() - seg_norm[col].min()
        seg_norm[col] = (seg_norm[col] - seg_norm[col].min()) / (rng if rng else 1)
    fig_radar = go.Figure()
    radar_colours      = {"Regular": "#6366F1",               "Premium": "#EC4899"}
    radar_fill_colours = {"Regular": "rgba(99,102,241,0.15)", "Premium": "rgba(236,72,153,0.15)"}
    for _, row in seg_norm.iterrows():
        seg  = row["Customer_Segment"]
        vals = [row[c] for c in radar_cols] + [row[radar_cols[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=radar_labels + [radar_labels[0]],
            fill="toself", name=seg,
            line=dict(color=radar_colours.get(seg, C1), width=2),
            fillcolor=radar_fill_colours.get(seg, "rgba(99,102,241,0.15)"),
        ))
    fig_radar.update_layout(
        **CL2("",360),
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], showticklabels=False,
                            gridcolor="#E2E8F0"),
            angularaxis=dict(gridcolor="#E2E8F0"),
            bgcolor="#F8FAFC",
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · SALES TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    c1,c2,c3,c4 = st.columns(4)
    sept = f[f["Order_Date"].dt.month==9]["Total_Amount_INR"].sum()
    oct_ = f[f["Order_Date"].dt.month==10]["Total_Amount_INR"].sum()
    c1.metric("📅 September Revenue", f"₹{sept:,.0f}")
    c2.metric("📅 October Revenue",   f"₹{oct_:,.0f}")
    c3.metric("🏷️ Avg Discount",      f"{f['Discount_Percent'].mean():.1f}%")
    c4.metric("💸 Total Discounts",   f"₹{total_disc:,.0f}")

    # Sept vs Oct
    st.markdown('<div class="sec-head">September vs October — Daily Revenue</div>', unsafe_allow_html=True)
    f["Day"]  = f["Order_Date"].dt.day
    mo_day    = f.groupby(["Order_Month","Day"])["Total_Amount_INR"].sum().reset_index()
    fig_mo    = go.Figure()
    for month, color, dash in [("September","#6366F1","solid"),("October","#F59E0B","dot")]:
        d = mo_day[mo_day["Order_Month"]==month]
        fig_mo.add_trace(go.Scatter(
            x=d["Day"], y=d["Total_Amount_INR"], mode="lines+markers",
            name=month, line=dict(color=color, width=2.5, dash=dash),
            marker=dict(size=6, color=color),
            hovertemplate=f"<b>{month} Day %{{x}}</b><br>₹%{{y:,.0f}}<extra></extra>",
        ))
    fig_mo.update_layout(**CL("",320))
    fig_mo.update_xaxes(title="Day of Month")
    fig_mo.update_yaxes(title="Revenue (₹)")
    st.plotly_chart(fig_mo, use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-head">Revenue by Day of Week</div>', unsafe_allow_html=True)
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = f.groupby("Order_DOW")["Total_Amount_INR"].sum().reindex(dow_order).reset_index()
        dow.columns = ["DOW","Revenue"]
        fig_dow = px.bar(dow, x="DOW", y="Revenue",
                         color="Revenue", color_continuous_scale=SEQ_INDIGO,
                         labels={"DOW":"","Revenue":"Revenue (₹)"},
                         text=dow["Revenue"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_dow.update_traces(textposition="outside")
        fig_dow.update_layout(**CL("",340), coloraxis_showscale=False)
        st.plotly_chart(fig_dow, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-head">Orders & Revenue by Hour of Day</div>', unsafe_allow_html=True)
        hourly = f.groupby("Order_Hour").agg(
            Orders=("Order_ID","count"), Revenue=("Total_Amount_INR","sum")).reset_index()
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Bar(
            x=hourly["Order_Hour"], y=hourly["Orders"],
            marker_color="#F59E0B", name="Orders", opacity=0.75))
        fig_hr.add_trace(go.Scatter(
            x=hourly["Order_Hour"], y=hourly["Revenue"],
            mode="lines+markers", yaxis="y2", name="Revenue",
            line=dict(color=C1, width=2.2), marker=dict(size=5)))
        fig_hr.update_layout(
            **CL("",340),
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        title="Revenue (₹)", tickfont=dict(color=C1)),
            xaxis_title="Hour of Day")
        st.plotly_chart(fig_hr, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="sec-head">Discount Tier — Revenue & Orders</div>', unsafe_allow_html=True)
        disc_g = f.groupby("Discount_Percent").agg(
            Revenue=("Total_Amount_INR","sum"), Orders=("Order_ID","count")).reset_index()
        fig_disc = go.Figure()
        fig_disc.add_trace(go.Bar(
            x=disc_g["Discount_Percent"].astype(str)+" %", y=disc_g["Revenue"],
            marker_color="#F59E0B", name="Revenue", opacity=0.8))
        fig_disc.add_trace(go.Scatter(
            x=disc_g["Discount_Percent"].astype(str)+" %", y=disc_g["Orders"],
            mode="lines+markers", yaxis="y2", name="Orders",
            line=dict(color=C1, width=2.5), marker=dict(size=8)))
        fig_disc.update_layout(
            **CL("",340),
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        title="Orders", tickfont=dict(color=C1)))
        st.plotly_chart(fig_disc, use_container_width=True)

    with c4:
        st.markdown('<div class="sec-head">Revenue by Shipping Method</div>', unsafe_allow_html=True)
        ship = f.groupby("Shipping_Method")["Total_Amount_INR"].sum().reset_index()
        fig_ship = px.bar(ship, x="Shipping_Method", y="Total_Amount_INR",
                          color="Shipping_Method",
                          color_discrete_map={"Express":"#6366F1","Standard":"#14B8A6"},
                          text=ship["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"),
                          labels={"Total_Amount_INR":"Revenue (₹)","Shipping_Method":""})
        fig_ship.update_traces(textposition="outside")
        fig_ship.update_layout(**CL("",340), showlegend=False)
        st.plotly_chart(fig_ship, use_container_width=True)

    c5,c6 = st.columns(2)
    with c5:
        st.markdown('<div class="sec-head">Revenue by Referral Source</div>', unsafe_allow_html=True)
        ref = f.groupby("Referral_Source")["Total_Amount_INR"].sum().sort_values(ascending=False).reset_index()
        fig_ref = px.bar(ref, x="Referral_Source", y="Total_Amount_INR",
                         color="Total_Amount_INR", color_continuous_scale=SEQ_TEAL,
                         labels={"Total_Amount_INR":"Revenue (₹)","Referral_Source":""},
                         text=ref["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_ref.update_traces(textposition="outside")
        fig_ref.update_layout(**CL("",340), coloraxis_showscale=False)
        st.plotly_chart(fig_ref, use_container_width=True)

    with c6:
        st.markdown('<div class="sec-head">Top 12 Marketing Campaigns</div>', unsafe_allow_html=True)
        camp = (f.groupby("Marketing_Campaign")["Total_Amount_INR"]
                 .sum().nlargest(12).sort_values().reset_index())
        fig_camp = px.bar(camp, x="Total_Amount_INR", y="Marketing_Campaign", orientation="h",
                          color="Total_Amount_INR", color_continuous_scale=SEQ_PINK,
                          labels={"Total_Amount_INR":"Revenue (₹)","Marketing_Campaign":""},
                          text=camp["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_camp.update_traces(textposition="outside")
        fig_camp.update_layout(**CL("",400), coloraxis_showscale=False)
        st.plotly_chart(fig_camp, use_container_width=True)

    # ── NEW: Waterfall — cumulative revenue build Sept→Oct ──
    st.markdown('<div class="sec-head">Cumulative Revenue Waterfall — Weekly Build</div>', unsafe_allow_html=True)
    f["Week_Label"] = "W" + f["Order_Date"].dt.isocalendar().week.astype(str)
    wk = f.groupby("Week_Label")["Total_Amount_INR"].sum().reset_index().sort_values("Week_Label")
    wk_vals  = wk["Total_Amount_INR"].tolist()
    wk_types = ["relative"] * len(wk_vals)
    wk_types[-1] = "total"
    fig_wf = go.Figure(go.Waterfall(
        x=wk["Week_Label"].tolist(), y=wk_vals, measure=wk_types,
        connector=dict(line=dict(color="#CBD5E1", width=1)),
        increasing=dict(marker=dict(color="#10B981")),
        decreasing=dict(marker=dict(color="#EF4444")),
        totals=dict(marker=dict(color="#6366F1")),
        text=[f"₹{v/1e3:.0f}K" for v in wk_vals],
        textposition="outside",
    ))
    fig_wf.update_layout(**CL("",320))
    fig_wf.update_yaxes(title="Revenue (₹)")
    st.plotly_chart(fig_wf, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · PRODUCT INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📂 Categories",     f"{f['Product_Category'].nunique()}")
    c2.metric("🛍️ Unique Products", f"{f['Product_Name'].nunique()}")
    c3.metric("📊 Avg Qty/Order",   f"{f['Quantity'].mean():.2f}")
    c4.metric("💰 Avg Unit Price",  f"₹{f['Unit_Price_INR'].mean():,.0f}")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-head">Top 10 Products — Revenue</div>', unsafe_allow_html=True)
        tp = f.groupby("Product_Name")["Total_Amount_INR"].sum().nlargest(10).sort_values().reset_index()
        fig_tp = px.bar(tp, x="Total_Amount_INR", y="Product_Name", orientation="h",
                        color="Total_Amount_INR", color_continuous_scale=SEQ_INDIGO,
                        labels={"Total_Amount_INR":"Revenue (₹)","Product_Name":""},
                        text=tp["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_tp.update_traces(textposition="outside")
        fig_tp.update_layout(**CL("",400), coloraxis_showscale=False)
        st.plotly_chart(fig_tp, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-head">Top 10 Products — Units Sold</div>', unsafe_allow_html=True)
        tv = f.groupby("Product_Name")["Quantity"].sum().nlargest(10).sort_values().reset_index()
        fig_tv = px.bar(tv, x="Quantity", y="Product_Name", orientation="h",
                        color="Quantity", color_continuous_scale=SEQ_ORANGE,
                        labels={"Quantity":"Units Sold","Product_Name":""},
                        text=tv["Quantity"])
        fig_tv.update_traces(textposition="outside")
        fig_tv.update_layout(**CL("",400), coloraxis_showscale=False)
        st.plotly_chart(fig_tv, use_container_width=True)

    cat = f.groupby("Product_Category").agg(
        Revenue=("Total_Amount_INR","sum"),
        Orders=("Order_ID","count"),
        Units=("Quantity","sum"),
        AvgRating=("Customer_Rating","mean"),
        AvgPrice=("Unit_Price_INR","mean"),
    ).reset_index().sort_values("Revenue", ascending=False)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="sec-head">Category Revenue (Top 15)</div>', unsafe_allow_html=True)
        cr = cat.head(15).sort_values("Revenue")
        fig_cr = px.bar(cr, x="Revenue", y="Product_Category", orientation="h",
                        color="Revenue", color_continuous_scale=SEQ_INDIGO,
                        labels={"Revenue":"Revenue (₹)","Product_Category":""},
                        text=cr["Revenue"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_cr.update_traces(textposition="outside")
        fig_cr.update_layout(**CL("",440), coloraxis_showscale=False)
        st.plotly_chart(fig_cr, use_container_width=True)

    with c4:
        st.markdown('<div class="sec-head">Category Orders (Top 15)</div>', unsafe_allow_html=True)
        co = cat.sort_values("Orders",ascending=False).head(15).sort_values("Orders")
        fig_co = px.bar(co, x="Orders", y="Product_Category", orientation="h",
                        color="Orders", color_continuous_scale=SEQ_TEAL,
                        labels={"Orders":"# Orders","Product_Category":""},
                        text=co["Orders"])
        fig_co.update_traces(textposition="outside")
        fig_co.update_layout(**CL("",440), coloraxis_showscale=False)
        st.plotly_chart(fig_co, use_container_width=True)

    # Treemap
    st.markdown('<div class="sec-head">Category Revenue Treemap</div>', unsafe_allow_html=True)
    fig_tree = px.treemap(cat, path=["Product_Category"], values="Revenue",
                          color="Revenue",
                          color_continuous_scale=[[0,"#EEF2FF"],[0.5,"#6366F1"],[1,"#312E81"]],
                          hover_data={"Orders":True,"AvgRating":":.2f"})
    fig_tree.update_layout(**CL("",380), coloraxis_showscale=False)
    fig_tree.update_traces(textfont_size=12, textinfo="label+value")
    st.plotly_chart(fig_tree, use_container_width=True)

    # Bubble chart
    st.markdown('<div class="sec-head">Category Revenue vs Avg Rating — Bubble Chart</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(cat, x="AvgRating", y="Revenue", size="Orders",
                        color="Units", color_continuous_scale=SEQ_ORANGE,
                        text="Product_Category",
                        labels={"AvgRating":"Avg Rating","Revenue":"Revenue (₹)","Units":"Units Sold"},
                        hover_data={"AvgPrice":":.0f","Orders":True})
    fig_sc.update_traces(textposition="top center", textfont_size=9)
    fig_sc.update_layout(**CL("",440))
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── NEW: Funnel — top 8 categories by conversion (orders → units) ──
    st.markdown('<div class="sec-head">Top 8 Categories — Orders vs Units Funnel</div>', unsafe_allow_html=True)
    top8 = cat.nlargest(8,"Revenue").sort_values("Orders")
    fig_fun = go.Figure()
    fig_fun.add_trace(go.Bar(
        y=top8["Product_Category"], x=top8["Orders"],
        orientation="h", name="Orders",
        marker=dict(color=top8["Orders"],
                    colorscale=SEQ_INDIGO, showscale=False),
        text=top8["Orders"], textposition="inside",
        textfont=dict(color="white")))
    fig_fun.add_trace(go.Bar(
        y=top8["Product_Category"], x=top8["Units"],
        orientation="h", name="Units Sold",
        marker=dict(color=top8["Units"],
                    colorscale=SEQ_ORANGE, showscale=False),
        text=top8["Units"], textposition="inside",
        textfont=dict(color="white")))
    fig_fun.update_layout(**CL("",380), barmode="overlay", xaxis_title="Count")
    st.plotly_chart(fig_fun, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · CUSTOMER ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("⭐ Avg Rating",         f"{avg_rating:.2f} / 5")
    c2.metric("🔄 Avg Lifetime Orders", f"{f['Customer_Lifetime_Orders'].mean():.1f}")
    c3.metric("🆕 First-Time Buyers",  f"{(f['First_Time_Customer']=='Yes').sum():,}")
    c4.metric("👤 Avg Customer Age",   f"{f['Customer_Age'].mean():.0f} yrs")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-head">New vs Returning — Revenue by Month</div>', unsafe_allow_html=True)
        ftc = f.groupby(["Order_Month","First_Time_Customer"])["Total_Amount_INR"].sum().reset_index()
        fig_ftc = px.bar(ftc, x="Order_Month", y="Total_Amount_INR",
                         color="First_Time_Customer",
                         color_discrete_map={"No":"#6366F1","Yes":"#10B981"},
                         barmode="group",
                         labels={"Total_Amount_INR":"Revenue (₹)","First_Time_Customer":"Type",
                                 "Order_Month":"Month"})
        fig_ftc.update_layout(**CL("",340))
        st.plotly_chart(fig_ftc, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-head">Revenue by Gender & Segment</div>', unsafe_allow_html=True)
        gs = f.groupby(["Customer_Gender","Customer_Segment"])["Total_Amount_INR"].sum().reset_index()
        fig_gs = px.bar(gs, x="Customer_Gender", y="Total_Amount_INR",
                        color="Customer_Segment",
                        color_discrete_map={"Regular":"#6366F1","Premium":"#EC4899"},
                        barmode="stack",
                        labels={"Total_Amount_INR":"Revenue (₹)","Customer_Gender":"",
                                "Customer_Segment":"Segment"})
        fig_gs.update_layout(**CL("",340))
        st.plotly_chart(fig_gs, use_container_width=True)

    # Age group — gradient
    st.markdown('<div class="sec-head">Age Group Analysis</div>', unsafe_allow_html=True)
    f["Age_Group"] = pd.cut(f["Customer_Age"], bins=[20,30,40,50,60],
                            labels=["20–30","30–40","40–50","50+"])
    age_order = ["20–30","30–40","40–50","50+"]

    c3,c4,c5 = st.columns(3)
    with c3:
        fig_age = px.histogram(f, x="Customer_Age", nbins=15,
                               color_discrete_sequence=[C1],
                               labels={"Customer_Age":"Age","count":"Customers"})
        fig_age.update_traces(
            marker=dict(color=list(range(15)), colorscale=AGE_GRAD,
                        line=dict(color="white", width=0.6)))
        fig_age.update_layout(**CL("Age Distribution",320))
        st.plotly_chart(fig_age, use_container_width=True)

    with c4:
        ag = f.groupby("Age_Group", observed=True)["Total_Amount_INR"].sum().reindex(age_order).reset_index()
        fig_agr = go.Figure(go.Bar(
            x=ag["Age_Group"], y=ag["Total_Amount_INR"],
            marker_color=AGE_COLOURS,
            text=ag["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"))
        fig_agr.update_layout(**CL("Revenue by Age Group",320))
        fig_agr.update_yaxes(title="Revenue (₹)")
        st.plotly_chart(fig_agr, use_container_width=True)

    with c5:
        ag_rat = f.groupby("Age_Group", observed=True)["Customer_Rating"].mean().reindex(age_order).reset_index()
        fig_arat = go.Figure(go.Bar(
            x=ag_rat["Age_Group"], y=ag_rat["Customer_Rating"],
            marker_color=AGE_COLOURS,
            text=ag_rat["Customer_Rating"].apply(lambda x: f"{x:.2f}"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Rating: %{y:.2f}<extra></extra>"))
        fig_arat.update_layout(**CL("Avg Rating by Age Group",320))
        fig_arat.update_yaxes(title="Avg Rating", range=[0,5.5])
        st.plotly_chart(fig_arat, use_container_width=True)

    c6,c7 = st.columns(2)
    with c6:
        st.markdown('<div class="sec-head">Lifetime Orders — Loyalty Band Breakdown</div>', unsafe_allow_html=True)
        f["LTO_Band"] = pd.cut(f["Customer_Lifetime_Orders"], bins=[0,3,7,12,20],
                               labels=["1–3 (New)","4–7 (Growing)","8–12 (Loyal)","13–20 (Champion)"])
        lto_order = ["1–3 (New)","4–7 (Growing)","8–12 (Loyal)","13–20 (Champion)"]
        lto_g = (f.groupby(["LTO_Band","Customer_Segment"], observed=True)
                  .agg(Customers=("Customer_ID","nunique")).reset_index())
        lto_g["LTO_Band"] = pd.Categorical(lto_g["LTO_Band"], categories=lto_order, ordered=True)
        lto_g = lto_g.sort_values("LTO_Band")
        fig_lto = px.bar(lto_g, x="LTO_Band", y="Customers",
                         color="Customer_Segment",
                         color_discrete_map={"Regular":"#6366F1","Premium":"#EC4899"},
                         barmode="stack", text="Customers",
                         labels={"LTO_Band":"Loyalty Band","Customers":"# Customers"})
        fig_lto.update_traces(textposition="inside", textfont_size=11)
        fig_lto.update_layout(**CL("",360))
        st.plotly_chart(fig_lto, use_container_width=True)

    with c7:
        st.markdown('<div class="sec-head">Referral Source — Customers & Revenue</div>', unsafe_allow_html=True)
        ref_c = f.groupby("Referral_Source").agg(
            Customers=("Customer_ID","nunique"),
            Revenue=("Total_Amount_INR","sum")).reset_index().sort_values("Customers", ascending=False)
        fig_ref2 = go.Figure()
        fig_ref2.add_trace(go.Bar(
            x=ref_c["Referral_Source"], y=ref_c["Customers"],
            marker_color="#F59E0B", name="Customers", opacity=0.85))
        fig_ref2.add_trace(go.Scatter(
            x=ref_c["Referral_Source"], y=ref_c["Revenue"],
            mode="lines+markers", yaxis="y2", name="Revenue",
            line=dict(color=C1, width=2.5), marker=dict(size=7)))
        fig_ref2.update_layout(
            **CL("",360),
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        title="Revenue (₹)", tickfont=dict(color=C1)))
        st.plotly_chart(fig_ref2, use_container_width=True)

    # ── NEW: Violin — order value distribution by segment ──
    st.markdown('<div class="sec-head">Order Value Distribution by Segment — Violin</div>', unsafe_allow_html=True)
    fig_vio = px.violin(f, x="Customer_Segment", y="Total_Amount_INR",
                        color="Customer_Segment",
                        color_discrete_map={"Regular":"#6366F1","Premium":"#EC4899"},
                        box=True, points="outliers",
                        labels={"Total_Amount_INR":"Order Value (₹)","Customer_Segment":""})
    fig_vio.update_layout(**CL("",360), showlegend=False)
    st.plotly_chart(fig_vio, use_container_width=True)

    # Segment summary table
    st.markdown('<div class="sec-head">Segment Summary Table</div>', unsafe_allow_html=True)
    seg_sum = f.groupby("Customer_Segment").agg(
        Customers=("Customer_ID","nunique"),
        Orders=("Order_ID","count"),
        Revenue=("Total_Amount_INR","sum"),
        Avg_Order=("Total_Amount_INR","mean"),
        Avg_Rating=("Customer_Rating","mean"),
        Avg_Discount=("Discount_Percent","mean"),
    ).reset_index()
    seg_sum["Revenue"]      = seg_sum["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    seg_sum["Avg_Order"]    = seg_sum["Avg_Order"].apply(lambda x: f"₹{x:,.0f}")
    seg_sum["Avg_Rating"]   = seg_sum["Avg_Rating"].apply(lambda x: f"{x:.2f}")
    seg_sum["Avg_Discount"] = seg_sum["Avg_Discount"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(seg_sum, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 · GEOGRAPHIC
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    c1,c2,c3 = st.columns(3)
    c1.metric("🏙️ Cities Served",  f"{f['Customer_City'].nunique()}")
    c2.metric("🗺️ States Covered", f"{f['Customer_State'].nunique()}")
    c3.metric("🌍 Countries",       f"{f['Customer_Country'].nunique()}")

    state = f.groupby("Customer_State").agg(
        Revenue=("Total_Amount_INR","sum"),
        Orders=("Order_ID","count"),
        Customers=("Customer_ID","nunique"),
        AvgRating=("Customer_Rating","mean"),
        AvgDelivery=("Days_to_Deliver","mean"),
    ).reset_index().sort_values("Revenue", ascending=False)

    # NOTE: ALL geographic charts use TEMP_GEO (dark=low → cyan → yellow → red=high)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-head">Top 15 States — Revenue</div>', unsafe_allow_html=True)
        sr = state.head(15).sort_values("Revenue")
        fig_sr = px.bar(sr, x="Revenue", y="Customer_State", orientation="h",
                        color="Revenue", color_continuous_scale=TEMP_GEO,
                        labels={"Revenue":"Revenue (₹)","Customer_State":""},
                        text=sr["Revenue"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_sr.update_traces(textposition="outside")
        fig_sr.update_layout(**CL("",440), coloraxis_showscale=True,
                             coloraxis_colorbar=dict(title="₹", thickness=12, len=0.6))
        st.plotly_chart(fig_sr, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-head">Top 15 States — Orders</div>', unsafe_allow_html=True)
        so = state.sort_values("Orders",ascending=False).head(15).sort_values("Orders")
        fig_so = px.bar(so, x="Orders", y="Customer_State", orientation="h",
                        color="Orders", color_continuous_scale=TEMP_GEO,
                        labels={"Orders":"Orders","Customer_State":""},
                        text=so["Orders"])
        fig_so.update_traces(textposition="outside")
        fig_so.update_layout(**CL("",440), coloraxis_showscale=True,
                             coloraxis_colorbar=dict(title="Orders", thickness=12, len=0.6))
        st.plotly_chart(fig_so, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="sec-head">Top 15 Cities — Revenue</div>', unsafe_allow_html=True)
        city = f.groupby("Customer_City")["Total_Amount_INR"].sum().nlargest(15).sort_values().reset_index()
        fig_ci = px.bar(city, x="Total_Amount_INR", y="Customer_City", orientation="h",
                        color="Total_Amount_INR", color_continuous_scale=TEMP_GEO,
                        labels={"Total_Amount_INR":"Revenue (₹)","Customer_City":""},
                        text=city["Total_Amount_INR"].apply(lambda x: f"₹{x/1e3:.0f}K"))
        fig_ci.update_traces(textposition="outside")
        fig_ci.update_layout(**CL("",440), coloraxis_showscale=True,
                             coloraxis_colorbar=dict(title="₹", thickness=12, len=0.6))
        st.plotly_chart(fig_ci, use_container_width=True)

    with c4:
        st.markdown('<div class="sec-head">Top 15 Cities — Orders</div>', unsafe_allow_html=True)
        city_o = f.groupby("Customer_City")["Order_ID"].count().nlargest(15).sort_values().reset_index()
        city_o.columns = ["City","Orders"]
        fig_cio = px.bar(city_o, x="Orders", y="City", orientation="h",
                         color="Orders", color_continuous_scale=TEMP_GEO,
                         labels={"Orders":"# Orders","City":""},
                         text=city_o["Orders"])
        fig_cio.update_traces(textposition="outside")
        fig_cio.update_layout(**CL("",440), coloraxis_showscale=True,
                              coloraxis_colorbar=dict(title="Orders", thickness=12, len=0.6))
        st.plotly_chart(fig_cio, use_container_width=True)

    c5,c6 = st.columns(2)
    with c5:
        st.markdown('<div class="sec-head">State Avg Rating (Top 12)</div>', unsafe_allow_html=True)
        srat = state.sort_values("AvgRating",ascending=False).head(12).sort_values("AvgRating")
        fig_srat = px.bar(srat, x="AvgRating", y="Customer_State", orientation="h",
                          color="AvgRating", color_continuous_scale=TEMP_GEO,
                          range_x=[0,5],
                          labels={"AvgRating":"Avg Rating","Customer_State":""},
                          text=srat["AvgRating"].apply(lambda x: f"{x:.2f}"))
        fig_srat.update_traces(textposition="outside")
        fig_srat.update_layout(**CL("",440), coloraxis_showscale=True,
                               coloraxis_colorbar=dict(title="Rating", thickness=12, len=0.6))
        st.plotly_chart(fig_srat, use_container_width=True)

    with c6:
        st.markdown('<div class="sec-head">State Avg Delivery Days (Top 12)</div>', unsafe_allow_html=True)
        sdel = state.sort_values("AvgDelivery",ascending=False).head(12).sort_values("AvgDelivery")
        fig_sdel = px.bar(sdel, x="AvgDelivery", y="Customer_State", orientation="h",
                          color="AvgDelivery", color_continuous_scale=TEMP_GEO,
                          labels={"AvgDelivery":"Avg Delivery Days","Customer_State":""},
                          text=sdel["AvgDelivery"].apply(lambda x: f"{x:.1f}d"))
        fig_sdel.update_traces(textposition="outside")
        fig_sdel.update_layout(**CL("",440), coloraxis_showscale=True,
                               coloraxis_colorbar=dict(title="Days", thickness=12, len=0.6))
        st.plotly_chart(fig_sdel, use_container_width=True)

    # ── NEW: Sunburst — State → City revenue hierarchy ──
    st.markdown('<div class="sec-head">State → City Revenue Hierarchy — Sunburst</div>', unsafe_allow_html=True)
    geo_h = (f.groupby(["Customer_State","Customer_City"])["Total_Amount_INR"]
              .sum().reset_index())
    # Limit to top 8 states for readability
    top8_states = state.head(8)["Customer_State"].tolist()
    geo_h = geo_h[geo_h["Customer_State"].isin(top8_states)]
    fig_sun = px.sunburst(geo_h, path=["Customer_State","Customer_City"],
                          values="Total_Amount_INR",
                          color="Total_Amount_INR",
                          color_continuous_scale=TEMP_GEO,
                          labels={"Total_Amount_INR":"Revenue (₹)"})
    fig_sun.update_layout(**CL("",480), coloraxis_showscale=False)
    fig_sun.update_traces(textfont_size=11)
    st.plotly_chart(fig_sun, use_container_width=True)

    st.markdown('<div class="sec-head">State-Level Summary Table</div>', unsafe_allow_html=True)
    sd = state.copy()
    sd["Revenue"]     = sd["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    sd["AvgRating"]   = sd["AvgRating"].apply(lambda x: f"{x:.2f}")
    sd["AvgDelivery"] = sd["AvgDelivery"].apply(lambda x: f"{x:.1f}d")
    st.dataframe(sd, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 · OPERATIONS & QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with t6:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🚚 Avg Delivery Days", f"{avg_del_days:.1f}d")
    c2.metric("✅ Delivery Rate",     f"{delivery_pct:.1f}%")
    c3.metric("💰 Tax Collected",     f"₹{f['Tax_Amount_INR'].sum():,.0f}")
    c4.metric("📬 Shipping Revenue",  f"₹{f['Shipping_Cost_INR'].sum():,.0f}")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-head">Rating Distribution</div>', unsafe_allow_html=True)
        rat_d = f["Customer_Rating"].value_counts().sort_index().reset_index()
        rat_d.columns = ["Rating","Count"]
        fig_rat = px.bar(rat_d, x="Rating", y="Count",
                         color="Rating",
                         color_discrete_map={3.0:"#F59E0B", 4.0:"#6366F1", 5.0:"#10B981"},
                         labels={"Rating":"Stars","Count":"Reviews"},
                         text="Count")
        fig_rat.update_traces(textposition="outside")
        fig_rat.update_layout(**CL("",320), showlegend=False)
        st.plotly_chart(fig_rat, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-head">Delivery Days Distribution</div>', unsafe_allow_html=True)
        fig_del = px.histogram(f.dropna(subset=["Days_to_Deliver"]),
                               x="Days_to_Deliver", nbins=12,
                               color_discrete_sequence=["#6366F1"],
                               labels={"Days_to_Deliver":"Days to Deliver","count":"Orders"})
        fig_del.update_traces(marker_line_color="white", marker_line_width=0.8)
        fig_del.update_layout(**CL("",320))
        st.plotly_chart(fig_del, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="sec-head">Express vs Standard — Delivery Stats</div>', unsafe_allow_html=True)
        del_stats = (f.dropna(subset=["Days_to_Deliver"])
                      .groupby("Shipping_Method")["Days_to_Deliver"]
                      .agg(Median="median", Mean="mean", Max="max").reset_index())
        fig_del_grp = go.Figure()
        for metric, colour in zip(["Median","Mean","Max"],["#10B981","#6366F1","#EF4444"]):
            fig_del_grp.add_trace(go.Bar(
                name=metric,
                x=del_stats["Shipping_Method"], y=del_stats[metric],
                marker_color=colour,
                text=del_stats[metric].apply(lambda x: f"{x:.1f}d"),
                textposition="outside"))
        fig_del_grp.update_layout(**CL("",360), barmode="group", yaxis_title="Days")
        st.plotly_chart(fig_del_grp, use_container_width=True)

    with c4:
        st.markdown('<div class="sec-head">Avg Rating by Product Category</div>', unsafe_allow_html=True)
        cr2 = (f.groupby("Product_Category")["Customer_Rating"]
                .mean().sort_values(ascending=False).head(12).sort_values().reset_index())
        fig_cr2 = px.bar(cr2, x="Customer_Rating", y="Product_Category", orientation="h",
                         color="Customer_Rating",
                         color_continuous_scale=SEQ_GREEN,
                         range_x=[0,5],
                         labels={"Customer_Rating":"Avg Rating","Product_Category":""},
                         text=cr2["Customer_Rating"].apply(lambda x: f"{x:.2f}"))
        fig_cr2.update_traces(textposition="outside")
        fig_cr2.update_layout(**CL("",400), coloraxis_showscale=False)
        st.plotly_chart(fig_cr2, use_container_width=True)

    # Payment completion 100% stacked
    st.markdown('<div class="sec-head">Payment Completion Rate by Method</div>', unsafe_allow_html=True)
    ps_raw = f.groupby(["Payment_Method","Payment_Status"])["Total_Amount_INR"].sum().reset_index()
    ps_tot = ps_raw.groupby("Payment_Method")["Total_Amount_INR"].sum().reset_index()
    ps_raw = ps_raw.merge(ps_tot, on="Payment_Method", suffixes=("","_total"))
    ps_raw["Pct"] = ps_raw["Total_Amount_INR"] / ps_raw["Total_Amount_INR_total"] * 100
    fig_ps = go.Figure()
    for status, colour in [("Completed","#10B981"),("Pending","#F59E0B")]:
        d = ps_raw[ps_raw["Payment_Status"]==status]
        fig_ps.add_trace(go.Bar(
            name=status, x=d["Payment_Method"], y=d["Pct"],
            marker_color=colour,
            text=d["Pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="inside",
            textfont=dict(color="white", size=12),
            hovertemplate="<b>%{x}</b> — "+status+"<br>%{y:.1f}%<extra></extra>"))
    fig_ps.update_layout(**CL2("",320), barmode="stack",
                         yaxis_title="Share of Revenue (%)", yaxis_range=[0,110])
    fig_ps.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                     y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_ps, use_container_width=True)

    # Correlation heatmap
    st.markdown('<div class="sec-head">Numeric Feature Correlation Heatmap</div>', unsafe_allow_html=True)
    num_cols = ["Quantity","Unit_Price_INR","Discount_Percent","Total_Amount_INR",
                "Days_to_Deliver","Customer_Rating","Customer_Age",
                "Customer_Lifetime_Orders","Shipping_Cost_INR"]
    corr = f[[c for c in num_cols if c in f.columns]].corr()
    fig_corr = px.imshow(corr, color_continuous_scale=DIV_PG,
                         zmin=-1, zmax=1, aspect="auto", text_auto=".2f")
    fig_corr.update_layout(**CL("",480))
    fig_corr.update_traces(textfont_size=11)
    st.plotly_chart(fig_corr, use_container_width=True)

    # ── NEW: Scatter — tax vs order value coloured by shipping method ──
    st.markdown('<div class="sec-head">Tax Amount vs Order Value — by Shipping Method</div>', unsafe_allow_html=True)
    fig_tax = px.scatter(f.sample(min(400, len(f)), random_state=42),
                         x="Total_Amount_INR", y="Tax_Amount_INR",
                         color="Shipping_Method",
                         color_discrete_map={"Express":"#6366F1","Standard":"#14B8A6"},
                         size="Quantity", opacity=0.65,
                         labels={"Total_Amount_INR":"Order Value (₹)",
                                 "Tax_Amount_INR":"Tax (₹)",
                                 "Shipping_Method":"Method"})
    fig_tax.update_layout(**CL("",400))
    st.plotly_chart(fig_tax, use_container_width=True)

    st.markdown("")
    csv_out = f.to_csv(index=False).encode("utf-8")
    st.download_button(
        "💾 Download Filtered Dataset",
        csv_out,
        f"filtered_sales_{len(f)}_rows.csv",
        "text/csv")
