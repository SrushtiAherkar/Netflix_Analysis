#!/usr/bin/env python
# coding: utf-8
"""Interactive Streamlit dashboard for the Netflix analysis dataset."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
	page_title="Netflix | Audience Insights",
	page_icon="N",
	layout="wide",
	initial_sidebar_state="expanded",
)

RED = "#e50914"
PALETTE = ["#e50914", "#ff5a5f", "#b20710", "#f5f5f1", "#8c8c8c", "#5a0b10", "#d9a3a5", "#3c3c3c"]

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
	:root { color-scheme: dark; }
	.stApp { background: radial-gradient(ellipse at 76% 0%, #341014 0, #171313 29%, #0b0b0d 66%); }
	[data-testid="stHeader"] { background: transparent; }
	[data-testid="stSidebar"] { background: #111113; border-right: 1px solid #292326; }
	[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] input { font-family: 'DM Sans', sans-serif; }
	.block-container { max-width: 1440px; padding-top: 2.1rem; padding-bottom: 3rem; }
	h1, h2, h3, p, label, [data-testid="stMetricValue"] { font-family: 'DM Sans', sans-serif; }
	.hero { display:flex; align-items:center; gap:18px; margin: 0 0 26px; }
	.brand-mark { display:flex; align-items:center; justify-content:center; width:54px; height:62px;
		color:#fff; background:linear-gradient(145deg,#ff2631,#b20710); border-radius:14px;
		font-family:'Manrope',sans-serif; font-weight:800; font-size:35px; box-shadow:0 10px 35px #e5091438; }
	.eyebrow { color:#ff6970; letter-spacing:.17em; font-weight:700; font-size:11px; text-transform:uppercase; margin:0 0 5px; }
	.hero h1 { font-family:'Manrope',sans-serif; font-size:clamp(27px,3vw,39px); font-weight:800; letter-spacing:-.04em; margin:0; color:#fff; }
	.hero p { color:#a9a2a3; margin:5px 0 0; font-size:14px; }
	.section-label { color:#aaa3a4; font-size:12px; letter-spacing:.12em; text-transform:uppercase; font-weight:700; margin:0 0 12px; }
	[data-testid="stMetric"] { background:linear-gradient(145deg,#1d191b,#141315); border:1px solid #30272a;
		border-radius:14px; padding:17px 20px; }
	[data-testid="stMetricLabel"] { color:#aaa3a4; font-size:12px; white-space:nowrap; }
	[data-testid="stMetricValue"] { color:#fff; font-weight:700; font-size:24px; line-height:1.2; }
	div[data-testid="stPlotlyChart"] { background:#141315; border:1px solid #30272a; border-radius:16px; padding:10px 12px 2px; }
	div[data-testid="stSelectbox"] label, div[data-testid="stMultiSelect"] label, div[data-testid="stDateInput"] label { color:#e8e3e3; font-weight:600; }
	[data-testid="stCaptionContainer"] { color:#91898b; }
	.sidebar-brand { color:#fff; font-family:'Manrope',sans-serif; font-weight:800; font-size:19px; letter-spacing:-.03em; }
	.sidebar-brand span { color:#e50914; }
	.sidebar-note { color:#8e888a; font-size:12px; line-height:1.5; margin-top:7px; }
	hr { border-color:#30272a; }
	</style>
	""",
	unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
	"""Load the CSV stored alongside this Streamlit app."""
	data_path = Path(__file__).resolve().with_name("netflix.csv")
	data = pd.read_csv(data_path)
	data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
	return data


try:
	netflix = load_data()
except (FileNotFoundError, pd.errors.ParserError) as error:
	st.error(f"Couldn't load netflix.csv next to this app. Details: {error}")
	st.stop()

required_columns = {
	"Region", "Subscription_Plan", "Rating", "Category", "Monthly_Revenue", "Watch_Date"
}
missing_columns = required_columns.difference(netflix.columns)
if missing_columns:
	st.error(f"The dataset is missing required columns: {', '.join(sorted(missing_columns))}")
	st.stop()

st.sidebar.markdown('<div class="sidebar-brand"><span>N</span>FLIX INSIGHTS</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-note">Explore the audience and revenue metrics from the analysis.</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
chart_titles = {
	"Region-wise revenue": "Regional revenue",
	"Subscription plan-wise rating": "Ratings by subscription plan",
	"Rating distribution": "Rating distribution",
	"Category-wise revenue": "Revenue by category",
}
selected_chart = st.sidebar.selectbox("FOCUS CHART", list(chart_titles))

date_min = netflix["Watch_Date"].min().date()
date_max = netflix["Watch_Date"].max().date()
date_range = st.sidebar.date_input(
	"WATCH DATE RANGE",
	value=(date_min, date_max),
	min_value=date_min,
	max_value=date_max,
)
regions = sorted(netflix["Region"].dropna().unique().tolist())
plans = sorted(netflix["Subscription_Plan"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("REGION", regions, default=regions)
selected_plans = st.sidebar.multiselect("SUBSCRIPTION PLAN", plans, default=plans)
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-note">Built from the charts and metrics in AJ30sept.py.</div>', unsafe_allow_html=True)

filtered = netflix.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
	start_date, end_date = date_range
	filtered = filtered[filtered["Watch_Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1))]
if selected_regions:
	filtered = filtered[filtered["Region"].isin(selected_regions)]
if selected_plans:
	filtered = filtered[filtered["Subscription_Plan"].isin(selected_plans)]

st.markdown(
	'<div class="hero"><div class="brand-mark">N</div><div><div class="eyebrow">Audience intelligence · 2026</div>'
	'<h1>Netflix data, at a glance.</h1><p>A focused look at viewing behavior, ratings and revenue.</p></div></div>',
	unsafe_allow_html=True,
)

if filtered.empty:
	st.warning("No records match those filters. Update the sidebar filters to see the chart.")
	st.stop()

metric_columns = st.columns(4)
metric_columns[0].metric("Rows", f"{len(filtered):,}")
revenue_total = filtered["Monthly_Revenue"].sum()
watch_minutes = filtered["Watch_Time_Minutes"].sum() if "Watch_Time_Minutes" in filtered else None
metric_columns[1].metric("Revenue", f"${revenue_total / 1000:.1f}K", help=f"Exact filtered total: ${revenue_total:,.0f}")
metric_columns[2].metric("Avg rating", f"{filtered['Rating'].mean():.1f} / 5")
metric_columns[3].metric("Watch time", f"{watch_minutes / 1000:.1f}K min" if watch_minutes is not None else "—", help=f"Exact filtered total: {watch_minutes:,} minutes" if watch_minutes is not None else None)

st.markdown("<br><div class='section-label'>Selected analysis</div>", unsafe_allow_html=True)
heading, detail = st.columns([3, 1])
heading.subheader(chart_titles[selected_chart])
detail.caption(f"{len(filtered):,} matching records")

if selected_chart == "Region-wise revenue":
	chart_data = filtered.groupby("Region", as_index=False)["Monthly_Revenue"].sum().sort_values("Monthly_Revenue", ascending=True)
	figure = px.bar(chart_data, x="Monthly_Revenue", y="Region", orientation="h", text_auto="$,.0f", color="Monthly_Revenue", color_continuous_scale=["#5a0b10", RED])
	figure.update_layout(coloraxis_showscale=False, xaxis_title="Monthly revenue", yaxis_title="", xaxis_tickprefix="$", xaxis_tickformat=",.0f")
	note = "Total monthly revenue across the selected regions."
elif selected_chart == "Subscription plan-wise rating":
	chart_data = filtered.groupby("Subscription_Plan", as_index=False)["Rating"].sum().sort_values("Rating", ascending=False)
	figure = px.pie(chart_data, names="Subscription_Plan", values="Rating", hole=0.62, color_discrete_sequence=PALETTE)
	figure.update_traces(textposition="outside", textinfo="label+percent", hole=0.62, marker_line_color="#141315", marker_line_width=3)
	figure.update_layout(showlegend=True, legend_title_text="Subscription plan", annotations=[dict(text=f"{chart_data['Rating'].sum():,}<br><span style='font-size:11px'>rating points</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=21, color="white"))])
	note = "Sum of customer ratings grouped by subscription plan, matching the original analysis."
elif selected_chart == "Rating distribution":
	chart_data = filtered["Rating"].value_counts().sort_index().rename_axis("Rating").reset_index(name="Customers")
	figure = px.bar(chart_data, x="Rating", y="Customers", text_auto=True, color="Rating", color_continuous_scale=["#5a0b10", RED])
	figure.update_layout(coloraxis_showscale=False, xaxis_title="Rating (out of 5)", yaxis_title="Number of records", xaxis=dict(dtick=1))
	note = "Number of customer records at each rating."
else:
	chart_data = filtered.groupby("Category", as_index=False)["Monthly_Revenue"].sum().sort_values("Monthly_Revenue", ascending=True)
	figure = px.bar(chart_data, x="Monthly_Revenue", y="Category", orientation="h", text_auto="$,.0f", color="Monthly_Revenue", color_continuous_scale=["#5a0b10", RED])
	figure.update_layout(coloraxis_showscale=False, xaxis_title="Monthly revenue", yaxis_title="", xaxis_tickprefix="$", xaxis_tickformat=",.0f")
	note = "Total monthly revenue by content category."

figure.update_layout(
	template="plotly_dark",
	paper_bgcolor="rgba(0,0,0,0)",
	plot_bgcolor="rgba(0,0,0,0)",
	font=dict(family="DM Sans, sans-serif", color="#f5f5f1", size=13),
	margin=dict(l=24, r=30, t=24, b=25),
	height=440,
	hoverlabel=dict(bgcolor="#1d191b", bordercolor=RED, font_color="white"),
)
figure.update_xaxes(showgrid=True, gridcolor="#30272a", zerolinecolor="#51474a")
figure.update_yaxes(showgrid=False, zeroline=False)
st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
st.caption(note)
# In[ ]:




