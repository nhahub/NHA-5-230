"""
Productivity Prediction Dashboard
Fixed dark theme, sidebar icon navigation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.preprocess import TARGET, TARGET_DISPLAY

st.set_page_config(
    page_title="Productivity Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Fixed dark theme ─────────────────────────────────────────
BG          = "#0f172a"
CARD_BG     = "#1e293b"
CARD_BORDER = "#334155"
TEXT        = "#f1f5f9"
MUTED       = "#94a3b8"
ACCENT      = "#60a5fa"
SIDEBAR_BG  = "linear-gradient(180deg, #020617 0%, #0f172a 100%)"
PLOTLY_TPL  = "plotly_dark"
KPI_SHADOW  = "0 4px 16px rgba(0,0,0,0.35)"

st.html(
    f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
    :root {{ color-scheme: dark; }}
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}
    .main .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }}
    .main h1, .main h2, .main h3, .main p,
    .main .stMarkdown, .main [data-testid="stMetricLabel"],
    .main [data-testid="stMetricValue"],
    .main [data-testid="stWidgetLabel"] {{ color: {TEXT} !important; }}
    .main [data-baseweb="select"] *,
    .main [data-baseweb="input"] * {{ color: {TEXT} !important; }}
    .main [data-baseweb="select"] > div,
    .main [data-baseweb="input"] > div {{
        background-color: {CARD_BG} !important;
        border-color: {CARD_BORDER} !important;
    }}

    .kpi-card {{
        background: {CARD_BG};
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        box-shadow: {KPI_SHADOW};
        border: 1px solid {CARD_BORDER};
        text-align: center;
        height: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }}
    .kpi-card .icon {{
        font-size: 1.55rem;
        color: {ACCENT};
        margin-bottom: 0.45rem;
    }}
    .kpi-card .value {{
        font-size: 1.7rem;
        font-weight: 700;
        color: {TEXT};
        line-height: 1.2;
    }}
    .kpi-card .label {{
        font-size: 0.8rem;
        color: {MUTED};
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 1.28rem;
        font-weight: 650;
        color: {TEXT};
        margin: 1.6rem 0 0.7rem 0;
    }}
    .section-header i {{ color: {ACCENT}; }}

    .pred-box {{
        background: {CARD_BG};
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid {CARD_BORDER};
        box-shadow: {KPI_SHADOW};
        text-align: center;
    }}
    .pred-box .score {{
        font-size: 2.8rem;
        font-weight: 800;
        color: {ACCENT};
        line-height: 1.1;
    }}
    .pred-box .sub {{ color: {MUTED}; margin-top: 0.35rem; font-size: 0.9rem; }}

    [data-testid="stSidebar"] {{
        background: {SIDEBAR_BG} !important;
        border-right: 1px solid {CARD_BORDER};
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: #e2e8f0 !important;
    }}
    [data-testid="stSidebar"] [class*="st-key-nav_"] button {{
        width: 100%;
        min-height: 48px;
        justify-content: flex-start !important;
        text-align: left !important;
        border-radius: 11px !important;
        border: 1px solid rgba(148,163,184,0.24) !important;
        background: rgba(255,255,255,0.055) !important;
        color: #e2e8f0 !important;
        padding: 0.55rem 0.85rem !important;
        margin: 0.12rem 0 !important;
        transition: all 0.16s ease;
    }}
    [data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {{
        border-color: {ACCENT} !important;
        background: rgba(96,165,250,0.16) !important;
        transform: translateX(2px);
    }}
    [data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] {{
        background: {ACCENT} !important;
        border-color: {ACCENT} !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(59,130,246,0.22);
    }}
    [data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] * {{
        color: #ffffff !important;
        fill: #ffffff !important;
    }}
    [data-testid="stSidebar"] [class*="st-key-nav_"] button p {{
        color: inherit !important;
        font-weight: 600;
        margin: 0 !important;
    }}

    .footer {{
        text-align: center;
        color: {MUTED};
        font-size: 0.78rem;
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid {CARD_BORDER};
    }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """,
)


@st.cache_data(show_spinner="Loading data…")
def load_data():
    path = ROOT / "data" / "cleaned.csv"
    if not path.exists():
        path = ROOT / "data" / "productivity_dataset.csv"
    return pd.read_csv(path)


@st.cache_resource(show_spinner="Loading model…")
def load_model():
    return joblib.load(ROOT / "models" / "best_model.joblib")


@st.cache_data
def load_meta():
    return json.loads((ROOT / "models" / "meta.json").read_text())


@st.cache_data
def load_comparison():
    return pd.read_csv(ROOT / "models" / "model_comparison.csv")


df = load_data()
model = load_model()
meta = load_meta()
comparison = load_comparison()


def section(icon: str, title: str):
    st.markdown(
        f'<div class="section-header"><i class="fa-solid {icon}"></i> {title}</div>',
        unsafe_allow_html=True,
    )


def kpi(icon: str, value: str, label: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="icon"><i class="fa-solid {icon}"></i></div>
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>
    """


def apply_layout(fig, height=400):
    axis_text = "#e2e8f0"
    axis_muted = "#cbd5e1"
    grid = "#334155"
    fig.update_layout(
        template=PLOTLY_TPL,
        height=height,
        margin=dict(l=16, r=16, t=36, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=13, color=TEXT),
        title_font=dict(color=TEXT),
        legend=dict(font=dict(color=axis_text, size=12)),
        coloraxis_colorbar=dict(
            tickfont=dict(color=axis_text, size=11),
            title_font=dict(color=axis_text, size=12),
            outlinecolor=grid,
        ),
    )
    fig.update_xaxes(
        title_font=dict(color=axis_text, size=12),
        tickfont=dict(color=axis_muted, size=11),
        gridcolor=grid, zerolinecolor=grid, linecolor=grid,
    )
    fig.update_yaxes(
        title_font=dict(color=axis_text, size=12),
        tickfont=dict(color=axis_muted, size=11),
        gridcolor=grid, zerolinecolor=grid, linecolor=grid,
    )
    fig.update_annotations(font=dict(color=axis_text))
    return fig


# ── Sidebar navigation ───────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 0.6rem 0 1rem 0;">
            <i class="fa-solid fa-bolt" style="font-size:2.1rem; color:#60a5fa;"></i>
            <h2 style="margin:0.4rem 0 0 0; color:white; font-size:1.25rem;">Productivity</h2>
            <p style="margin:0; font-size:0.72rem; color:#94a3b8;">Expected Score Predictor</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_items = [
        ("Overview", "dashboard"),
        ("Exploratory Insights", "query_stats"),
        ("Correlations", "insights"),
        ("Job & Platform", "work"),
        ("Digital Habits", "smartphone"),
        ("Wellbeing", "favorite"),
        ("Key Insights", "lightbulb"),
        ("Recommendations", "task_alt"),
        ("Predict", "psychology"),
    ]
    if "page" not in st.session_state:
        st.session_state.page = "Overview"

    def set_page(selected_page):
        st.session_state.page = selected_page

    for nav_label, nav_icon in nav_items:
        nav_key = "nav_" + nav_label.lower().replace(" ", "_").replace("&", "and")
        st.button(
            nav_label,
            icon=f":material/{nav_icon}:",
            key=nav_key,
            type="primary" if st.session_state.page == nav_label else "secondary",
            use_container_width=True,
            on_click=set_page,
            args=(nav_label,),
        )

    page = st.session_state.page
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.72rem; color:#64748b; padding:0.8rem 0.4rem 0;">
        Survey lifestyle signals<br>
        Expected productivity view
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Overview ─────────────────────────────────────────────────
if page == "Overview":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-gauge-high" style="color:{ACCENT};"></i>
            Productivity Overview
        </h1>
        <p style="color:{MUTED}; margin-top:0; margin-bottom:1.2rem;">
            Supervised models predicting expected productivity from work and lifestyle signals.
        </p>
        """,
        unsafe_allow_html=True,
    )

    n = len(df)
    mean_act = df[TARGET].mean()
    mean_stress = df["stress_level"].mean()
    mean_sleep = df["sleep_hours"].mean()
    mean_sm = df["daily_social_media_time"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi("fa-users", f"{n:,}", "Records"), unsafe_allow_html=True)
    c2.markdown(kpi("fa-bullseye", f"{mean_act:.1f}", "Mean Productivity"), unsafe_allow_html=True)
    c3.markdown(kpi("fa-brain", f"{mean_stress:.1f}", "Mean Stress"), unsafe_allow_html=True)
    c4.markdown(kpi("fa-bed", f"{mean_sleep:.1f} h", "Mean Sleep"), unsafe_allow_html=True)
    c5.markdown(kpi("fa-mobile-screen", f"{mean_sm:.1f} h", "Social Media"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        section("fa-chart-column", "Target distribution")
        fig = px.histogram(df, x=TARGET, nbins=16, labels={TARGET: TARGET_DISPLAY})
        fig.update_traces(marker_color=ACCENT)
        fig = apply_layout(fig, 360)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        section("fa-briefcase", "Records by job type")
        jc = df["job_type"].value_counts().reset_index()
        jc.columns = ["job_type", "count"]
        fig = px.bar(jc, x="job_type", y="count", color="count", color_continuous_scale="Blues")
        fig = apply_layout(fig, 360)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    section("fa-share-nodes", "Preferred platforms")
    pc = df["social_platform_preference"].value_counts().reset_index()
    pc.columns = ["platform", "count"]
    fig = px.pie(
        pc, names="platform", values="count", hole=0.45,
        color_discrete_sequence=["#0b3c78", "#145da0", "#1976b9", "#268bd2", "#5aa9e6", "#8ecae6"],
    )
    fig = apply_layout(fig, 380)
    st.plotly_chart(fig, use_container_width=True)


# ── Exploratory Insights ─────────────────────────────────────
elif page == "Exploratory Insights":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-magnifying-glass-chart" style="color:{ACCENT};"></i>
            Exploratory Insights
        </h1>
        <p style="color:{MUTED};">Key distributions across the survey sample.</p>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        section("fa-user", "Age distribution")
        fig = px.histogram(df, x="age", nbins=20)
        fig.update_traces(marker_color=ACCENT)
        fig = apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        section("fa-clock", "Work hours per day")
        fig = px.histogram(df, x="work_hours_per_day", nbins=16)
        fig.update_traces(marker_color="#5aa9e6")
        fig = apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)

    section("fa-face-meh", "Stress level counts")
    sc = df["stress_level"].value_counts().sort_index().reset_index()
    sc.columns = ["stress_level", "count"]
    fig = px.bar(sc, x="stress_level", y="count")
    fig.update_traces(marker_color="#268bd2")
    fig = apply_layout(fig, 360)
    st.plotly_chart(fig, use_container_width=True)

    section("fa-venus-mars", "Gender mix")
    gc = df["gender"].value_counts().reset_index()
    gc.columns = ["gender", "count"]
    fig = px.pie(gc, names="gender", values="count", hole=0.4,
                 color_discrete_sequence=["#145da0", "#5aa9e6", "#8ecae6"])
    fig = apply_layout(fig, 360)
    st.plotly_chart(fig, use_container_width=True)


# ── Correlations ─────────────────────────────────────────────
elif page == "Correlations":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-link" style="color:{ACCENT};"></i>
            Feature–Target Correlations
        </h1>
        """,
        unsafe_allow_html=True,
    )
    section("fa-chart-bar", "Correlation with expected productivity")
    num_cols = df.select_dtypes(include="number").columns.tolist()
    corr = df[num_cols].corr()[TARGET].drop(TARGET).sort_values()
    fig = px.bar(
        x=corr.values, y=corr.index, orientation="h",
        color=corr.values, color_continuous_scale="RdBu_r",
        labels={"x": f"Correlation with {TARGET_DISPLAY}", "y": ""},
    )
    fig = apply_layout(fig, 520)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    section("fa-table-cells", "Numeric correlation heatmap")
    cols = [c for c in num_cols if c != TARGET][:12] + [TARGET]
    cm = df[cols].corr()
    fig = px.imshow(cm, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
    fig = apply_layout(fig, 520)
    st.plotly_chart(fig, use_container_width=True)


# ── Job & Platform ───────────────────────────────────────────
elif page == "Job & Platform":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-briefcase" style="color:{ACCENT};"></i>
            Job Type & Platform
        </h1>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        section("fa-briefcase", "Productivity by job type")
        fig = px.box(df, x="job_type", y=TARGET, color="job_type")
        fig = apply_layout(fig, 400)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=TARGET_DISPLAY)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        section("fa-share-nodes", "Mean productivity by platform")
        plat = df.groupby("social_platform_preference")[TARGET].mean().sort_values().reset_index()
        fig = px.bar(
            plat, x=TARGET, y="social_platform_preference", orientation="h",
            color=TARGET, color_continuous_scale="Blues",
        )
        fig = apply_layout(fig, 400)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Mean productivity", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    section("fa-table", "Job type summary")
    summary = (
        df.groupby("job_type")[TARGET]
        .agg(["count", "mean", "median", "std"])
        .round(2)
        .sort_values("mean", ascending=False)
        .reset_index()
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ── Digital Habits ───────────────────────────────────────────
elif page == "Digital Habits":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-mobile-screen" style="color:{ACCENT};"></i>
            Digital Habits
        </h1>
        """,
        unsafe_allow_html=True,
    )
    section("fa-mobile-screen", "Social media time vs productivity")
    sample = df.sample(min(3000, len(df)), random_state=1)
    fig = px.scatter(
        sample, x="daily_social_media_time", y=TARGET, color="stress_level",
        opacity=0.45,
        labels={"daily_social_media_time": "Social media (h/day)", TARGET: TARGET_DISPLAY},
    )
    fig = apply_layout(fig, 420)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        section("fa-bell", "Notifications distribution")
        fig = px.histogram(df, x="number_of_notifications", nbins=30)
        fig.update_traces(marker_color=ACCENT)
        fig = apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        section("fa-moon", "Screen time before sleep")
        sc = df["screen_time_before_sleep"].value_counts().sort_index().reset_index()
        sc.columns = ["hours", "count"]
        fig = px.bar(sc, x="hours", y="count")
        fig.update_traces(marker_color="#5aa9e6")
        fig = apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        section("fa-toggle-on", "Focus apps")
        tmp = df.groupby("uses_focus_apps")[TARGET].mean().reset_index()
        tmp["uses_focus_apps"] = tmp["uses_focus_apps"].map({0: "No", 1: "Yes", False: "No", True: "Yes"})
        fig = px.bar(tmp, x="uses_focus_apps", y=TARGET, color="uses_focus_apps",
                     color_discrete_sequence=["#64748b", ACCENT])
        fig = apply_layout(fig, 320)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=f"Mean {TARGET_DISPLAY}")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        section("fa-shield-halved", "Digital wellbeing")
        tmp = df.groupby("has_digital_wellbeing_enabled")[TARGET].mean().reset_index()
        tmp["has_digital_wellbeing_enabled"] = tmp["has_digital_wellbeing_enabled"].map(
            {0: "No", 1: "Yes", False: "No", True: "Yes"}
        )
        fig = px.bar(tmp, x="has_digital_wellbeing_enabled", y=TARGET,
                     color="has_digital_wellbeing_enabled",
                     color_discrete_sequence=["#64748b", ACCENT])
        fig = apply_layout(fig, 320)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=f"Mean {TARGET_DISPLAY}")
        st.plotly_chart(fig, use_container_width=True)


# ── Wellbeing ────────────────────────────────────────────────
elif page == "Wellbeing":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-heart-pulse" style="color:{ACCENT};"></i>
            Wellbeing Signals
        </h1>
        """,
        unsafe_allow_html=True,
    )
    section("fa-bed", "Sleep, burnout and offline hours")
    fig = go.Figure()
    for col, name in [
        ("sleep_hours", "Sleep hours"),
        ("days_feeling_burnout_per_month", "Burnout days"),
        ("weekly_offline_hours", "Offline hours"),
    ]:
        tmp = df.groupby(col)[TARGET].mean().reset_index()
        fig.add_trace(go.Scatter(x=tmp[col], y=tmp[TARGET], mode="lines+markers", name=name))
    fig = apply_layout(fig, 400)
    fig.update_layout(xaxis_title="Value", yaxis_title=f"Mean {TARGET_DISPLAY}")
    st.plotly_chart(fig, use_container_width=True)

    section("fa-fire", "Stress × work hours")
    pivot = df.pivot_table(
        values=TARGET, index="stress_level",
        columns="work_hours_per_day", aggfunc="mean",
    )
    fig = px.imshow(
        pivot, aspect="auto", color_continuous_scale="YlOrRd_r",
        labels=dict(color=f"Mean {TARGET_DISPLAY}"),
    )
    fig = apply_layout(fig, 420)
    st.plotly_chart(fig, use_container_width=True)

    section("fa-mug-hot", "Coffee consumption vs productivity")
    coffee = df.groupby("coffee_consumption_per_day")[TARGET].mean().reset_index()
    fig = px.bar(coffee, x="coffee_consumption_per_day", y=TARGET)
    fig.update_traces(marker_color=ACCENT)
    fig = apply_layout(fig, 340)
    fig.update_layout(xaxis_title="Cups / day", yaxis_title=f"Mean {TARGET_DISPLAY}")
    st.plotly_chart(fig, use_container_width=True)


# ── Predict ──────────────────────────────────────────────────

# ── Key Insights ─────────────────────────────────────────────
elif page == "Key Insights":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-lightbulb" style="color:{ACCENT};"></i>
            Key Insights
        </h1>
        <p style="color:{MUTED};">Patterns that show up consistently in the survey data.</p>
        """,
        unsafe_allow_html=True,
    )

    num = df.select_dtypes(include="number")
    corr = num.corr()[TARGET].drop(TARGET).sort_values()
    top_pos = corr.tail(3)
    top_neg = corr.head(3)

    section("fa-arrow-trend-up", "Strongest positive links")
    for name, val in top_pos.items():
        st.markdown(f"- **{name}**: correlation {val:.2f} with expected productivity")

    section("fa-arrow-trend-down", "Strongest negative links")
    for name, val in top_neg.items():
        st.markdown(f"- **{name}**: correlation {val:.2f} with expected productivity")

    section("fa-briefcase", "Job type snapshot")
    job = (
        df.groupby("job_type")[TARGET]
        .agg(mean="mean", n="count")
        .sort_values("mean", ascending=False)
        .round(2)
    )
    best_job, worst_job = job.index[0], job.index[-1]
    st.markdown(
        f"Highest average productivity: **{best_job}** ({job.loc[best_job, 'mean']:.2f}). "
        f"Lowest: **{worst_job}** ({job.loc[worst_job, 'mean']:.2f})."
    )
    st.dataframe(job.reset_index(), use_container_width=True, hide_index=True)

    section("fa-share-nodes", "Platform snapshot")
    plat = df.groupby("social_platform_preference")[TARGET].mean().sort_values(ascending=False).round(2)
    st.markdown(
        f"Preferred platform with the highest mean score: **{plat.index[0]}** ({plat.iloc[0]:.2f}). "
        f"Lowest: **{plat.index[-1]}** ({plat.iloc[-1]:.2f})."
    )

    section("fa-heart-pulse", "Wellbeing signals")
    high_stress = df[df["stress_level"] >= 6][TARGET].mean()
    low_stress = df[df["stress_level"] <= 2][TARGET].mean()
    high_burn = df[df["days_feeling_burnout_per_month"] >= 8][TARGET].mean()
    low_burn = df[df["days_feeling_burnout_per_month"] <= 1][TARGET].mean()
    st.markdown(
        f"""
- Low stress (≤2) mean productivity: **{low_stress:.2f}** · high stress (≥6): **{high_stress:.2f}**
- Low burnout (≤1 day/month): **{low_burn:.2f}** · high burnout (≥8): **{high_burn:.2f}**
- Focus apps users mean: **{df.loc[df['uses_focus_apps'].astype(int)==1, TARGET].mean():.2f}** · non-users: **{df.loc[df['uses_focus_apps'].astype(int)==0, TARGET].mean():.2f}**
        """
    )

# ── Recommendations ──────────────────────────────────────────
elif page == "Recommendations":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-clipboard-check" style="color:{ACCENT};"></i>
            Recommendations
        </h1>
        <p style="color:{MUTED};">Practical actions suggested by the observed patterns.</p>
        """,
        unsafe_allow_html=True,
    )

    cards = [
        ("fa-bed", "#38bdf8", "Protect sleep and offline time",
         "People with more sleep and weekly offline hours tend to report higher productivity. Encourage clear offline blocks and a consistent sleep window."),
        ("fa-brain", "#f87171", "Treat sustained stress as a priority",
         "High stress and frequent burnout days line up with lower scores. Short check-ins and workload reviews help before performance drops further."),
        ("fa-mobile-screen", "#a78bfa", "Cap noisy digital habits",
         "Heavy notification load and long social-media sessions often sit with lower productivity. Notification batching and focus modes are low-cost experiments."),
        ("fa-toggle-on", "#34d399", "Promote focus tooling where it helps",
         "Respondents who use focus apps or digital wellbeing settings show a modest edge. Offer optional tooling rather than mandates."),
        ("fa-briefcase", "#fbbf24", "Segment support by job context",
         "Average scores differ across job types. Coaching and workload policies work better when they respect those differences instead of a single blanket rule."),
        ("fa-comments", "#60a5fa", "Close the perception gap",
         "Perceived productivity tracks actual scores but not perfectly. Pair self-ratings with simple outcome measures so teams do not optimise for feeling busy only."),
    ]
    for icon, color, title, body in cards:
        st.markdown(
            f"""
            <div style="background:{CARD_BG};border:1px solid {CARD_BORDER};border-left:5px solid {color};
                        border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:0.85rem;box-shadow:{KPI_SHADOW};">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;">
                    <i class="fa-solid {icon}" style="color:{color};"></i>
                    <strong style="color:{TEXT};font-size:1.05rem;">{title}</strong>
                </div>
                <p style="margin:0;color:{MUTED};line-height:1.55;">{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif page == "Predict":
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{TEXT};">
            <i class="fa-solid fa-wand-magic-sparkles" style="color:{ACCENT};"></i>
            Predict Expected Productivity
        </h1>
        <p style="color:{MUTED};">
            Adjust the inputs to estimate expected productivity.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("predict_form"):
        st.markdown("##### Demographics & work")
        a, b, c = st.columns(3)
        age = a.slider("Age", 18, 65, 32)
        gender = b.selectbox("Gender", ["Male", "Female", "Other"])
        job_type = c.selectbox("Job type", sorted(df["job_type"].dropna().unique().tolist()))

        a, b, c = st.columns(3)
        work_hours = a.slider("Work hours / day", 2.0, 12.0, 8.0, 0.5)
        job_sat = b.slider("Job satisfaction", 4, 9, 8)
        perceived = c.slider("Perceived productivity", 2, 10, 7)

        st.markdown("##### Digital habits")
        a, b, c = st.columns(3)
        sm_time = a.slider("Daily social media (h)", 0.0, 10.0, 2.0, 0.5)
        platform = b.selectbox(
            "Preferred platform",
            sorted(df["social_platform_preference"].dropna().unique().tolist()),
        )
        notifications = c.slider("Notifications / day", 10, 200, 60)

        a, b, c = st.columns(3)
        screen_before = a.slider("Screen before sleep (h)", 0, 4, 1)
        focus_apps = b.selectbox("Uses focus apps", [True, False])
        wellbeing = c.selectbox("Digital wellbeing on", [True, False])

        st.markdown("##### Wellbeing")
        a, b, c, d = st.columns(4)
        stress = a.slider("Stress", 1, 9, 3)
        sleep = b.slider("Sleep hours", 4.0, 10.0, 7.0, 0.5)
        burnout = c.slider("Burnout days / month", 0, 20, 2)
        offline = d.slider("Weekly offline hours", 2, 31, 15)

        a, b = st.columns(2)
        breaks = a.slider("Breaks during work", 0, 7, 3)
        coffee = b.slider("Coffee / day", 0, 5, 2)

        submitted = st.form_submit_button("Run prediction", use_container_width=True)

    if submitted:
        row = pd.DataFrame([{
            "age": age,
            "gender": gender,
            "job_type": job_type,
            "daily_social_media_time": sm_time,
            "social_platform_preference": platform,
            "number_of_notifications": notifications,
            "work_hours_per_day": work_hours,
            "perceived_productivity_score": perceived,
            "stress_level": stress,
            "sleep_hours": sleep,
            "screen_time_before_sleep": screen_before,
            "breaks_during_work": breaks,
            "uses_focus_apps": int(focus_apps),
            "has_digital_wellbeing_enabled": int(wellbeing),
            "coffee_consumption_per_day": coffee,
            "days_feeling_burnout_per_month": burnout,
            "weekly_offline_hours": offline,
            "job_satisfaction_score": job_sat,
        }])
        pred = float(np.clip(model.predict(row)[0], 3, 10))
        st.markdown(
            f"""
            <div class="pred-box">
                <div style="color:{MUTED};font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;">
                    {TARGET_DISPLAY}
                </div>
                <div class="score">{pred:.2f}</div>
                <div class="sub">Scale 3 – 10</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred,
            gauge={
                "axis": {"range": [3, 10]},
                "bar": {"color": ACCENT},
                "steps": [
                    {"range": [3, 5], "color": "#7f1d1d"},
                    {"range": [5, 7.5], "color": "#78350f"},
                    {"range": [7.5, 10], "color": "#14532d"},
                ],
            },
            title={"text": TARGET_DISPLAY},
        ))
        fig = apply_layout(fig, 280)
        st.plotly_chart(fig, use_container_width=True)


st.markdown(
    f"""
    <div class="footer">
        Productivity analytics · Expected productivity predictor
    </div>
    """,
    unsafe_allow_html=True,
)
