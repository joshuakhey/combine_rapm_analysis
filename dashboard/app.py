import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go          # NOTE: never shadow this with a local var named "go"
import numpy as np

st.set_page_config(
    page_title="NBA Combine Intelligence",
    layout="wide",
    page_icon="🏀",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap');

/* ── Cream background everywhere ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main,
.main, .block-container {
  background-color: #ede8dc !important;
  color: #1a1712 !important;
}
.block-container { padding-top: 1.5rem; max-width: 1200px; }

/* ── All text dark by default ── */
html, body, [class*="css"], p, span, label, li {
  font-family: 'Barlow', sans-serif;
  color: #1a1712;
}
h1, h2, h3, h4 {
  font-family: 'Barlow Condensed', sans-serif !important;
  letter-spacing: .03em;
  color: #1a1e38 !important;
}

/* ── Sidebar shell ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div {
  background: #1a1e38 !important;
  border-right: 3px solid #c9a53a !important;
}

/* ── Sidebar nav buttons: WHITE text, clearly readable ── */
section[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: none !important;
  border-left: 3px solid transparent !important;
  border-radius: 0 6px 6px 0 !important;
  color: rgba(255,255,255,0.75) !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  letter-spacing: .1em !important;
  text-transform: uppercase !important;
  text-align: left !important;
  padding: 9px 14px !important;
  width: 100% !important;
  box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  color: #fff !important;
  background: rgba(255,255,255,0.08) !important;
  border-left-color: rgba(201,165,58,0.5) !important;
}
/* Wipe out any default button border/shadow Streamlit adds */
section[data-testid="stSidebar"] .stButton > button:focus,
section[data-testid="stSidebar"] .stButton > button:active {
  box-shadow: none !important;
  border-color: transparent !important;
  outline: none !important;
}

/* ── Sidebar labels & selectbox ── */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
  color: rgba(255,255,255,0.5) !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 11px !important; font-weight: 700 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
  background: rgba(255,255,255,0.1) !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div > div,
section[data-testid="stSidebar"] .stSelectbox span {
  color: #fff !important;
}
section[data-testid="stSidebar"] .stSelectbox svg { fill: rgba(255,255,255,0.5) !important; }

/* ── Main area inputs: text input matches selectbox exactly ── */
[data-testid="stTextInput"] > div > div,
[data-testid="stTextInput"] input {
  background: rgba(237, 232, 220, 1) !important;
  border: 1px solid rgba(26,30,56,0.2) !important;
  border-radius: 6px !important;
  color: #1a1712 !important;
  font-family: 'Barlow', sans-serif !important;
  font-size: 14px !important;
}
[data-testid="stTextInput"] input::placeholder { color: rgba(26,30,56,0.4) !important; }
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 11px !important; letter-spacing: .14em !important;
  text-transform: uppercase !important;
  color: #1a1e38 !important; font-weight: 700 !important;
}
[data-testid="stSelectbox"] > div > div {
  background: rgba(237, 232, 220, 1) !important;
  border: 1px solid rgba(26,30,56,0.2) !important;
  border-radius: 6px !important; color: #1a1712 !important;
}
[data-testid="stSelectbox"] > div > div > div,
[data-testid="stSelectbox"] span { color: #1a1712 !important; }

/* ── Tooltip / help icon: visible ── */
[data-testid="stTooltipIcon"] svg {
  fill: rgba(26,30,56,0.55) !important;
  width: 15px !important; height: 15px !important;
}
[data-testid="stTooltipIcon"]:hover svg { fill: #1a1e38 !important; }
[data-baseweb="tooltip"] [role="tooltip"] {
  background: #1a1e38 !important; color: #fff !important;
  font-family: 'Barlow', sans-serif !important; font-size: 12px !important;
  border-radius: 6px !important; padding: 8px 12px !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
  background: rgba(237, 232, 220, 1) !important;
  border: 1px solid rgba(26,30,56,0.15) !important;
  border-radius: 8px !important; padding: 14px 18px !important;
}
[data-testid="metric-container"] label {
  color: rgba(26,30,56,0.5) !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 11px !important; letter-spacing: .14em !important; text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: #1a1e38 !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 28px !important; font-weight: 700 !important;
}

/* ── Inner tabs ── */
.stTabs [data-baseweb="tab-list"] {
  border-bottom: 2px solid rgba(26,30,56,0.2) !important;
  background: transparent !important; gap: 0;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 13px !important; font-weight: 700 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  color: rgba(26,30,56,0.45) !important;
  border: none !important; padding: 8px 20px !important;
  background: transparent !important; border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
  color: #1a1e38 !important;
  border-bottom: 3px solid #c9a53a !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 16px; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* ── Misc ── */
hr { border-color: rgba(26,30,56,0.15); margin: 16px 0; }
.stCaption, .stCaption p { color: rgba(26,30,56,0.5) !important; font-size: 12px !important; }

/* ── Custom classes ── */
.section-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
  color: rgba(26,30,56,0.5);
  margin-bottom: 10px; padding-bottom: 6px;
  border-bottom: 1px solid rgba(26,30,56,0.15);
}
.rapm-hero {
  background: transparent;
  border: 1px solid rgba(26,30,56,0.2);
  border-radius: 10px; padding: 22px 28px; text-align: center;
}
.rapm-hero .label {
  font-family: 'Barlow Condensed', sans-serif; font-size: 11px;
  letter-spacing: .16em; text-transform: uppercase;
  color: rgba(26,30,56,0.45); margin-bottom: 4px;
}
.rapm-hero .value {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 60px; font-weight: 900; line-height: 1; margin-bottom: 4px;
}
.rapm-hero .sub { font-size: 13px; color: rgba(26,30,56,0.5); }
.val-pos { color: #4a7c59 !important; }
.val-neg { color: #b03a2e !important; }
.val-neu { color: #c9a53a !important; }

.player-card {
  background: rgba(26,30,56,0.05); border: 1px solid rgba(26,30,56,0.12);
  border-left: 3px solid #1a1e38; border-radius: 6px;
  padding: 10px 14px; margin-bottom: 6px;
}
.player-card .pname {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 16px; font-weight: 700; color: #1a1e38;
}
.player-card .pmeta { font-size: 11px; color: rgba(26,30,56,0.5); margin-top: 1px; }
.player-card .prapm {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 17px; font-weight: 800; float: right; margin-top: -1px;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df      = pd.read_csv("data/combine_rapm.csv")
    summary = pd.read_csv("data/model_summary.csv")
    box = pd.read_csv("data/boxscore_per36.csv")
    imp = {
        "Guard": pd.read_csv("data/importance_guard.csv"),
        "Wing":  pd.read_csv("data/importance_wing.csv"),
        "Big":   pd.read_csv("data/importance_big.csv"),
    }
    with open("data/feature_labels.json") as f:
        labels = json.load(f)
    return df, summary, imp, labels, box

df, summary, importance_dfs, labels, boxscore = load_data()

POSITIONS       = ["Guard", "Wing", "Big"]
LOWER_IS_BETTER = {"LANE", "SHUTTLE", "SPRINT"}
BOX_LOWER       = {"tov_per36"}
BOX_RADAR = {
    "Guard": {"pts_per36":"Pts/36","ast_per36":"Ast/36","stl_per36":"Stl/36",
              "3p_pct":"3P%","ft_pct":"FT%","tov_per36":"Tov/36"},
    "Wing":  {"pts_per36":"Pts/36","reb_per36":"Reb/36","ast_per36":"Ast/36",
              "stl_per36":"Stl/36","blk_per36":"Blk/36","3p_pct":"3P%"},
    "Big":   {"pts_per36":"Pts/36","reb_per36":"Reb/36","blk_per36":"Blk/36",
              "fg_pct":"FG%","ast_per36":"Ast/36","stl_per36":"Stl/36"},
}
PLOT_BG   = "rgba(0,0,0,0)"
GRID_COL  = "rgba(26,30,56,0.1)"
FONT_DICT = dict(family="Barlow, sans-serif", color="#1a1712")

def fmt_name(s):
    if ", " in str(s):
        last, first = s.split(", ", 1)
        return f"{first} {last}"
    return s

def pct_in_group(feat, val, grp_df, lower_better=False):
    pct = (grp_df[feat].dropna() < val).mean() * 100
    return 100 - pct if lower_better else pct

def add_combine_scores(df, importance_dfs, labels):
    df = df.copy()
    df["combine_score"] = np.nan
    for group in POSITIONS:
        idx = df["pos_group"] == group
        sub = df[idx].copy()
        imp = importance_dfs[group].set_index("feature")["importance"]
        feat_stats = {}
        for feat in labels.keys():
            if feat not in imp.index or feat not in sub.columns:
                continue
            w = max(float(imp.get(feat, 0)), 0)
            if w == 0:
                continue
            col = sub[feat].dropna()
            if len(col) < 5 or col.std() == 0:
                continue
            feat_stats[feat] = (w, col.mean(), col.std(), feat in LOWER_IS_BETTER)
        scores = []
        for _, row in sub.iterrows():
            s, tw = 0.0, 0.0
            for feat, (w, mu, sigma, inv) in feat_stats.items():
                v = row.get(feat)
                if pd.isna(v):
                    continue
                z = ((v - mu) / sigma) * (-1 if inv else 1)
                s += w * z; tw += w
            scores.append(s / tw if tw > 0 else np.nan)
        df.loc[idx, "combine_score"] = scores
    return df

df = add_combine_scores(df, importance_dfs, labels)

# ── Session state navigation ──────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Key Insights"

def set_page(p):          # NOTE: NOT named "go" — that name is taken by plotly.graph_objects
    st.session_state["page"] = p

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown(
        "<div style='padding:4px 12px 18px'>"
        "<div style='font-family:Barlow Condensed,sans-serif;font-size:30px;font-weight:900;"
        "color:#c9a53a;letter-spacing:.06em;line-height:1.1'>NBA</div>"
        "<div style='font-family:Barlow Condensed,sans-serif;font-size:10px;font-weight:700;"
        "color:rgba(255,255,255,.4);letter-spacing:.22em;text-transform:uppercase;"
        "margin-bottom:10px'>Combine Intelligence</div>"
        "<div style='height:2px;background:linear-gradient(to right,#c9a53a,rgba(201,165,58,.05));border-radius:1px'></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Navigation
    nav_items = [("📊", "Key Insights"), ("🔬", "Feature Importance"), ("🔍", "Player Lookup")]
    for icon, label in nav_items:
        active = st.session_state["page"] == label
        if active:
            # Active state: rendered as styled HTML (no button interaction needed)
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;"
                f"border-left:3px solid #c9a53a;background:rgba(201,165,58,.12);"
                f"border-radius:0 6px 6px 0;padding:9px 14px;margin-bottom:2px'>"
                f"<span style='font-size:15px'>{icon}</span>"
                f"<span style='font-family:Barlow Condensed,sans-serif;font-size:13px;"
                f"font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#c9a53a'>"
                f"{label}</span></div>",
                unsafe_allow_html=True,
            )
        else:
            # Inactive state: real button
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                set_page(label)
                st.rerun()

    # Position group — 3 buttons, no dropdown overflow
    if st.session_state["page"] == "Key Insights":
        if "pos_filter" not in st.session_state:
            st.session_state["pos_filter"] = "Guard"
        st.markdown(
            "<div style='margin:18px 0 8px 4px;font-family:Barlow Condensed,sans-serif;"
            "font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;"
            "color:rgba(255,255,255,.4)'>Position Group</div>",
            unsafe_allow_html=True,
        )
        p1, p2, p3 = st.columns(3)
        for col, pos in zip([p1, p2, p3], POSITIONS):
            active_pos = st.session_state["pos_filter"] == pos
            if active_pos:
                col.markdown(
                    f"<div style='text-align:center;background:#c9a53a;border-radius:5px;"
                    f"padding:5px 2px;font-family:Barlow Condensed,sans-serif;"
                    f"font-size:12px;font-weight:700;letter-spacing:.08em;"
                    f"color:#1a1e38;cursor:default'>{pos}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if col.button(pos, key=f"pos_{pos}", use_container_width=True):
                    st.session_state["pos_filter"] = pos
                    st.rerun()
        pos_filter = st.session_state["pos_filter"]

    # Footer note — normal flow, not absolute-positioned
    st.markdown(
        "<div style='margin-top:40px;padding:0 12px;"
        "font-size:10px;color:rgba(255,255,255,.18);font-family:Barlow,sans-serif'>"
        "Career +/− per 36 min · mean-centred · ~2000–present</div>",
        unsafe_allow_html=True,
    )

page = st.session_state["page"]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: KEY INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
if page == "Key Insights":
    st.markdown(
        "<h1 style='font-size:34px;margin-bottom:2px'>What Does the Draft Combine Actually Tell Us?</h1>"
        "<p style='color:rgba(26,30,56,.5);font-size:14px;margin-bottom:20px'>"
        "Career +/− per 36 min (mean-centred) vs pre-draft physical measurements · ~2000–present</p>",
        unsafe_allow_html=True,
    )

    sub     = df[df["pos_group"] == st.session_state.get("pos_filter","Guard")].dropna(subset=["career_avg_total_rapm","combine_score"])
    imp_df  = importance_dfs[st.session_state.get("pos_filter","Guard")]
    best_r2 = summary[summary["position"] == st.session_state.get("pos_filter","Guard")]["mean_r2"].max()
    top_feat = imp_df[imp_df["importance"] > 0].sort_values("importance", ascending=False)
    top_lbl  = labels.get(top_feat.iloc[0]["feature"], top_feat.iloc[0]["feature"]) if len(top_feat) else "—"
    corr     = sub[["combine_score","career_avg_total_rapm"]].corr().iloc[0,1] if len(sub) > 5 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Players sampled", len(sub))
    m2.metric("Variance explained (R²)", f"{best_r2:.3f}")
    m3.metric("Top predictive metric", top_lbl)
    m4.metric("Combine score correlation", f"{corr:.2f}")

    st.markdown("---")
    col_scatter, col_cards = st.columns([3, 2])

    with col_scatter:
        st.markdown("<div class='section-label'>Composite Combine Score vs Career Impact</div>",
                    unsafe_allow_html=True)
        score_hi = sub["combine_score"].quantile(0.67)
        score_lo = sub["combine_score"].quantile(0.33)
        rapm_hi  = sub["career_avg_total_rapm"].quantile(0.67)
        rapm_lo  = sub["career_avg_total_rapm"].quantile(0.33)

        def bucket(r):
            hi_s = r["combine_score"] >= score_hi; lo_s = r["combine_score"] <= score_lo
            hi_r = r["career_avg_total_rapm"] >= rapm_hi; lo_r = r["career_avg_total_rapm"] <= rapm_lo
            if hi_s and hi_r: return "Blueprint Star"
            if hi_s and lo_r: return "Combine Miss"
            if lo_s and hi_r: return "Hidden Gem"
            return "Average"

        sub = sub.copy()
        sub["type"] = sub.apply(bucket, axis=1)
        color_map = {"Blueprint Star":"#4a7c59","Combine Miss":"#b03a2e",
                     "Hidden Gem":"#c9a53a","Average":"rgba(26,30,56,0.2)"}
        size_map  = {"Blueprint Star":9,"Combine Miss":9,"Hidden Gem":9,"Average":5}

        scatter_fig = go.Figure()
        for btype, color in color_map.items():
            mask = sub["type"] == btype
            scatter_fig.add_trace(go.Scatter(
                x=sub[mask]["combine_score"], y=sub[mask]["career_avg_total_rapm"],
                mode="markers", name=btype,
                text=sub[mask]["PLAYER"].apply(fmt_name),
                customdata=sub[mask][["YEAR","seasons_in_nba"]],
                hovertemplate="<b>%{text}</b> (%{customdata[0]})<br>"
                              "Combine: %{x:.2f}σ · Career +/−: %{y:+.2f}<extra></extra>",
                marker=dict(color=color, size=size_map[btype], opacity=0.9, line=dict(width=0)),
            ))
        scatter_fig.add_hline(y=0, line_dash="dot", line_color="rgba(26,30,56,.18)", line_width=1)
        scatter_fig.add_vline(x=0, line_dash="dot", line_color="rgba(26,30,56,.18)", line_width=1)
        scatter_fig.update_layout(
            xaxis_title="Composite Combine Score (σ from position avg)",
            yaxis_title="Career +/− per 36 (centred)",
            height=430, paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, font=FONT_DICT,
            legend=dict(orientation="h", y=-0.2, bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#1a1712", size=11)),
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, color="#1a1712",
                       tickfont=dict(color="#1a1712"), title_font=dict(color="#1a1712")),
            yaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, color="#1a1712",
                       tickfont=dict(color="#1a1712"), title_font=dict(color="#1a1712")),
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

    with col_cards:
        def player_cards(rows, color, border):
            for _, r in rows.iterrows():
                rapm = r["career_avg_total_rapm"]
                st.markdown(
                    f"<div class='player-card' style='border-left-color:{border}'>"
                    f"<span class='prapm' style='color:{color}'>{rapm:+.1f}</span>"
                    f"<div class='pname'>{fmt_name(r['PLAYER'])}</div>"
                    f"<div class='pmeta'>{int(r['YEAR'])} draft · {int(r['seasons_in_nba'])} seasons"
                    f" · combine: {r['combine_score']:+.2f}σ</div></div>",
                    unsafe_allow_html=True,
                )
        stars  = sub[sub["type"]=="Blueprint Star"].nlargest(4,"career_avg_total_rapm")
        misses = sub[sub["type"]=="Combine Miss"].nsmallest(4,"career_avg_total_rapm")
        gems   = sub[sub["type"]=="Hidden Gem"].nlargest(4,"career_avg_total_rapm")

        st.markdown("<div class='section-label'>📈 Blueprint Stars — elite combine → top career</div>", unsafe_allow_html=True)
        player_cards(stars, "#4a7c59", "#4a7c59")
        st.markdown("<div class='section-label' style='margin-top:14px'>⚠️ Combine Misses — elite measurables, underperformed</div>", unsafe_allow_html=True)
        player_cards(misses, "#b03a2e", "#b03a2e")
        st.markdown("<div class='section-label' style='margin-top:14px'>💎 Hidden Gems — modest combine, overperformed</div>", unsafe_allow_html=True)
        player_cards(gems, "#c9a53a", "#c9a53a")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FEATURE IMPORTANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Feature Importance":
    st.markdown(
        "<h1 style='font-size:34px;margin-bottom:2px'>Which Combine Metrics Actually Matter?</h1>"
        "<p style='color:rgba(26,30,56,.5);font-size:14px;margin-bottom:20px'>"
        "Random Forest permutation importance — R² drop when each feature is shuffled</p>",
        unsafe_allow_html=True,
    )
    inner_tabs = st.tabs(POSITIONS)
    for tab, group in zip(inner_tabs, POSITIONS):
        with tab:
            imp = importance_dfs[group].copy()
            imp["label"] = imp["feature"].map(labels).fillna(imp["feature"])
            imp = imp.sort_values("importance", ascending=True)
            bar_fig = go.Figure(go.Bar(
                x=imp["importance"], y=imp["label"], orientation="h",
                error_x=dict(type="data", array=imp["std"].tolist(), color="rgba(26,30,56,0.2)"),
                marker_color=["#1a1e38" if v > 0.001 else "rgba(26,30,56,0.2)"
                              for v in imp["importance"]],
                text=[f"{v:+.3f}" if abs(v) > 0.001 else "" for v in imp["importance"]],
                textposition="outside",
                textfont=dict(size=11, family="Barlow, sans-serif", color="#1a1712"),
            ))
            bar_fig.add_vline(x=0, line_color="rgba(26,30,56,0.2)", line_width=1)
            bar_fig.update_layout(
                xaxis_title="R² change when feature shuffled", height=500,
                paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, font=FONT_DICT,
                margin=dict(l=10,r=80,t=20,b=20),
                xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL,
                           tickfont=dict(color="#1a1712"), title_font=dict(color="#1a1712")),
                yaxis=dict(gridcolor=GRID_COL, tickfont=dict(color="#1a1712")),
            )
            st.plotly_chart(bar_fig, use_container_width=True)
            st.caption("Navy bars = positive contribution. Grey ≈ noise. Error bars = variance over 20 permutation repeats.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PLAYER LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Player Lookup":
    st.markdown("<h1 style='font-size:34px;margin-bottom:16px'>Player Lookup</h1>",
                unsafe_allow_html=True)

    all_players = (
        df[["PLAYER","pos_group"]].drop_duplicates("PLAYER")
        .assign(sort_key=lambda d: d["PLAYER"].str.split(", ").str[0].str.upper())
        .sort_values("sort_key")
    )
    search   = st.text_input("Search by last name", "",
                             placeholder="e.g. Durant, Curry, James…").strip().lower()
    filtered = all_players[all_players["PLAYER"].str.lower().str.contains(search)] if search else all_players

    if filtered.empty:
        st.warning("No players match that search.")
        st.stop()

    display_names = [fmt_name(p) for p in filtered["PLAYER"].tolist()]
    raw_names     = filtered["PLAYER"].tolist()
    selected_disp = st.selectbox(
        f"{len(filtered)} player{'s' if len(filtered)!=1 else ''} found",
        display_names,
    )
    selected_raw = raw_names[display_names.index(selected_disp)]

    row    = df[df["PLAYER"] == selected_raw].iloc[0]
    group  = row["pos_group"]
    grp_df = df[df["pos_group"] == group]
    imp    = importance_dfs[group]

    st.markdown("---")

    # ── RAPM hero ─────────────────────────────────────────────────────────────
    rapm     = row["career_avg_total_rapm"]
    rapm_pct = (grp_df["career_avg_total_rapm"] < rapm).mean() * 100
    val_cls  = "val-pos" if rapm >= 1.5 else ("val-neg" if rapm <= -1.5 else "val-neu")

    hero_col, info_col = st.columns([1, 2])
    with hero_col:
        st.markdown(
            f"<div class='rapm-hero'>"
            f"<div class='label'>Career +/− per 36 min</div>"
            f"<div class='value {val_cls}'>{rapm:+.2f}</div>"
            f"<div class='sub'>Top <b>{100-rapm_pct:.0f}%</b> of {group}s in sample</div>"
            f"</div>", unsafe_allow_html=True,
        )
    with info_col:
        c1,c2,c3 = st.columns(3)
        c1.metric("Draft Year", int(row["YEAR"]))
        c2.metric("Position",   row["POS"])
        c3.metric("NBA Seasons",int(row["seasons_in_nba"]))
        c4,c5,c6 = st.columns(3)
        dr = row.get("draftRound",  float("nan"))
        dn = row.get("draftNumber", float("nan"))
        cs = row.get("combine_score", float("nan"))
        c4.metric("Draft Round",   int(dr) if not pd.isna(dr) else "—")
        c5.metric("Draft Pick",    int(dn) if not pd.isna(dn) else "—")
        c6.metric("Combine Score", f"{cs:+.2f}σ" if not pd.isna(cs) else "—",
                  help="Importance-weighted z-score vs position peers")

    st.markdown("---")

    # ── Combine table + deviation bars ────────────────────────────────────────
    tbl_col, bar_col = st.columns([1, 1])

    feat_rows, bar_data = [], []
    for feat, lbl in labels.items():
        if feat not in row.index or pd.isna(row[feat]):
            continue
        pv  = float(row[feat])
        avg = grp_df[feat].mean()
        std = grp_df[feat].std()
        low = feat in LOWER_IS_BETTER
        pct = pct_in_group(feat, pv, grp_df, lower_better=low)
        if pct >= 75:   tier = "🟢"
        elif pct >= 50: tier = "🟡"
        elif pct >= 25: tier = "🟠"
        else:           tier = "🔴"
        feat_rows.append({"Metric": lbl, "Value": round(pv,2),
                          "Pos. Avg": round(avg,2), "Pct": f"{tier} {pct:.0f}th"})
        if std > 0:
            bar_data.append({"Metric": lbl, "delta": ((pv-avg)/std)*(-1 if low else 1)})

    with tbl_col:
        st.markdown("<div class='section-label'>Combine Measurements</div>", unsafe_allow_html=True)
        # Build as HTML so text colors match the bar chart (green above avg, red below)
        rows_html = ""
        for r in feat_rows:
            delta_row = next((d for d in bar_data if d["Metric"] == r["Metric"]), None)
            if delta_row and delta_row["delta"] >= 0:
                val_color = "#4a7c59"
            elif delta_row:
                val_color = "#b03a2e"
            else:
                val_color = "#1a1712"
            rows_html += (
                f"<tr>"
                f"<td style='padding:7px 10px;border-bottom:1px solid rgba(26,30,56,0.08);"
                f"font-size:13px;color:#1a1712'>{r['Metric']}</td>"
                f"<td style='padding:7px 10px;border-bottom:1px solid rgba(26,30,56,0.08);"
                f"font-size:13px;font-weight:600;color:{val_color};text-align:right'>{r['Value']}</td>"
                f"<td style='padding:7px 10px;border-bottom:1px solid rgba(26,30,56,0.08);"
                f"font-size:13px;color:rgba(26,30,56,0.45);text-align:right'>{r['Pos. Avg']}</td>"
                f"<td style='padding:7px 10px;border-bottom:1px solid rgba(26,30,56,0.08);"
                f"font-size:13px;text-align:right'>{r['Pct']}</td>"
                f"</tr>"
            )
        st.markdown(
            f"<div style='border:1px solid rgba(26,30,56,0.15);border-radius:8px;overflow:hidden'>"
            f"<table style='width:100%;border-collapse:collapse;background:transparent'>"
            f"<thead><tr>"
            f"<th style='padding:8px 10px;background:rgba(26,30,56,0.07);font-family:Barlow Condensed,sans-serif;"
            f"font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:rgba(26,30,56,0.6);text-align:left'>Metric</th>"
            f"<th style='padding:8px 10px;background:rgba(26,30,56,0.07);font-family:Barlow Condensed,sans-serif;"
            f"font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:rgba(26,30,56,0.6);text-align:right'>Value</th>"
            f"<th style='padding:8px 10px;background:rgba(26,30,56,0.07);font-family:Barlow Condensed,sans-serif;"
            f"font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:rgba(26,30,56,0.6);text-align:right'>Pos. Avg</th>"
            f"<th style='padding:8px 10px;background:rgba(26,30,56,0.07);font-family:Barlow Condensed,sans-serif;"
            f"font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:rgba(26,30,56,0.6);text-align:right'>Pct</th>"
            f"</tr></thead>"
            f"<tbody>{rows_html}</tbody>"
            f"</table></div>",
            unsafe_allow_html=True,
        )

    with bar_col:
        st.markdown("<div class='section-label'>vs. Position Average (σ)</div>", unsafe_allow_html=True)
        bar_df = pd.DataFrame(bar_data).sort_values("delta")
        dev_fig = go.Figure(go.Bar(
            x=bar_df["delta"], y=bar_df["Metric"], orientation="h",
            marker_color=["#4a7c59" if v >= 0 else "#b03a2e" for v in bar_df["delta"]],
            text=[f"{v:+.2f}σ" for v in bar_df["delta"]],
            textposition="outside",
            textfont=dict(size=10, family="Barlow, sans-serif", color="#1a1712"),
        ))
        dev_fig.add_vline(x=0, line_color="rgba(26,30,56,0.3)", line_width=1.5)
        dev_fig.update_layout(
            xaxis_title="Std deviations from position average", height=420,
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, font=FONT_DICT,
            margin=dict(l=10,r=70,t=10,b=10), showlegend=False,
            xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL,
                       tickfont=dict(color="#1a1712"), title_font=dict(color="#1a1712")),
            yaxis=dict(gridcolor=GRID_COL, tickfont=dict(color="#1a1712")),
        )
        st.plotly_chart(dev_fig, use_container_width=True)

    # ── Radar: box score production ───────────────────────────────────────────
    st.markdown("---")
    radar_col, strength_col = st.columns([3, 2])

    with radar_col:
        st.markdown("<div class='section-label'>Career Box Score Production vs Position Average</div>",
                    unsafe_allow_html=True)
        player_id = str(row.get("personId",""))
        box_stats = BOX_RADAR.get(group, {})

        if boxscore.empty or player_id not in boxscore["personId"].values:
            st.markdown(
                "<div style='background:rgba(26,30,56,0.05);border:1px solid rgba(26,30,56,0.15);"
                "border-left:3px solid #c9a53a;border-radius:6px;padding:16px 20px;"
                "font-size:13px;color:#1a1e38'>"
                "⚠️ <b>Box score data not found</b><br><br>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            player_box = boxscore[boxscore["personId"] == player_id].iloc[0]
            grp_box    = boxscore[boxscore["personId"].isin(grp_df["personId"].astype(str))]
            rlabels, player_pcts, avg_pcts = [], [], []
            for stat, stat_lbl in box_stats.items():
                if stat not in player_box.index or pd.isna(player_box[stat]):
                    continue
                low = stat in BOX_LOWER
                pct = pct_in_group(stat, float(player_box[stat]), grp_box, lower_better=low)
                rlabels.append(stat_lbl); player_pcts.append(pct); avg_pcts.append(50.0)

            if len(rlabels) >= 3:
                radar_fig = go.Figure()
                radar_fig.add_trace(go.Scatterpolar(
                    r=avg_pcts+[avg_pcts[0]], theta=rlabels+[rlabels[0]],
                    fill="toself", name=f"Avg {group}",
                    fillcolor="rgba(26,30,56,0.07)",
                    line=dict(color="#1a1e38", width=1.5, dash="dot"),
                ))
                radar_fig.add_trace(go.Scatterpolar(
                    r=player_pcts+[player_pcts[0]], theta=rlabels+[rlabels[0]],
                    fill="toself", name=fmt_name(selected_raw),
                    fillcolor="rgba(201,165,58,0.2)",
                    line=dict(color="#c9a53a", width=2.5),
                ))
                radar_fig.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0,100], ticksuffix="%",
                                        tickfont=dict(size=9, color="#1a1e38"),
                                        gridcolor="rgba(26,30,56,0.1)"),
                        angularaxis=dict(gridcolor="rgba(26,30,56,0.08)",
                                         tickfont=dict(size=11, color="#1a1e38",
                                                       family="Barlow Condensed, sans-serif")),
                    ),
                    paper_bgcolor=PLOT_BG, showlegend=True, height=380,
                    legend=dict(orientation="h", y=-0.12, font_size=11,
                                bgcolor="rgba(0,0,0,0)", font_color="#1a1712"),
                    margin=dict(l=30,r=30,t=20,b=30), font=FONT_DICT,
                )
                st.plotly_chart(radar_fig, use_container_width=True)
            else:
                st.info("Not enough box score data for this player.")

    
