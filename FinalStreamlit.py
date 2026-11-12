"""
Singapore Birth Rate Dashboard

Run:   pip install streamlit plotly pandas numpy scipy
       streamlit run FinalStreamlit.py

Keep this file in the SAME folder as these CSVs:
    births_fertility_clean_full.csv
    marriage_rate_2000_2025_clean.csv
    CleanedEducation.csv
    housing_affordability_analysis.csv
    processed_fertility_lfpr_data.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

try:
    from scipy.stats import t as tdist
except Exception:
    tdist = None

st.set_page_config(page_title="Singapore Birth Rate", page_icon="🇸🇬", layout="wide")

# ---- force a light theme, even if the computer is in dark mode ----------
try:
    for _k, _v in {"base": "light", "primaryColor": "#ff7a59", "backgroundColor": "#f6f8fd",
                   "secondaryBackgroundColor": "#eaeffa", "textColor": "#17233b"}.items():
        st._config.set_option(f"theme.{_k}", _v)
except Exception:
    pass
if "themed" not in st.session_state:
    st.session_state["themed"] = True
    st.rerun()

# =====================================================================
# Colour system
#   One colour per entity, used everywhere (chart, card, chip).
#   Categorical hues come from a palette validated for colour-blind safety.
# =====================================================================
INK, MUTED = "#17233b", "#5d6b82"
C_TFR, C_MAR, C_EDU = "#12355b", "#eb6834", "#6250d6"
C_INC, C_HDB, C_RAT, C_LFP = "#2a78d6", "#eda100", "#1baf7a", "#d55181"
YES, NOC, CTX = "#0f9d58", "#7a82b8", "#2a78d6"
BAND = "rgba(98,80,214,0.07)"
FONT = "Plus Jakarta Sans, system-ui, -apple-system, Segoe UI, sans-serif"
BLUE_RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#14468a", "#0d366b"]  # light to dark


def rgba(h, a):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
.stApp{font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  background:radial-gradient(900px 420px at 92% -8%,#e6defd 0%,rgba(230,222,253,0) 60%),
             radial-gradient(800px 420px at -8% 6%,#d7ecff 0%,rgba(215,236,255,0) 60%),#f6f8fd;}
h1,h2,h3,h4,h5{font-family:'Plus Jakarta Sans',system-ui,sans-serif !important;letter-spacing:-0.01em;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1500px;padding:1.2rem 2rem 3rem 2rem;}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"]{background:linear-gradient(190deg,#0b2a55 0%,#173a82 48%,#4a2fa3 100%);border-right:none;}
section[data-testid="stSidebar"] *{color:#eaf0ff;}
section[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.18);}
.brand{display:flex;gap:12px;align-items:center;margin:6px 0 18px 0;}
.brand .logo{font-size:1.9rem;background:rgba(255,255,255,.14);border-radius:14px;width:52px;height:52px;
  display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.25);}
.brand .bt{font-weight:800;font-size:1.15rem;line-height:1.15;color:#fff;}
.brand .bs{font-size:.74rem;opacity:.75;margin-top:3px;}
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:.4rem;width:100%;align-items:stretch;}
section[data-testid="stSidebar"] div[role="radiogroup"]>div{width:100%;}
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]{display:flex;box-sizing:border-box;}
section[data-testid="stSidebar"] [data-testid="stElementContainer"],section[data-testid="stSidebar"] [data-testid="stRadio"],section[data-testid="stSidebar"] [data-testid="stRadio"]>div,section[data-testid="stSidebar"] [data-testid="stRadioGroup"]{width:100% !important;max-width:100% !important;}
section[data-testid="stSidebar"] label[data-testid="stRadioOption"],
section[data-testid="stSidebar"] div[role="radiogroup"]>label{width:100%;padding:.55rem .85rem;border-radius:12px;
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.10);transition:all .15s;cursor:pointer;}
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover,
section[data-testid="stSidebar"] div[role="radiogroup"]>label:hover{background:rgba(255,255,255,.17);}
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]>div>div:first-child,
section[data-testid="stSidebar"] div[role="radiogroup"]>label>div:first-child{display:none;}
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked),
section[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked){
  background:linear-gradient(90deg,#ff7a59,#ffb347);border-color:transparent;box-shadow:0 8px 20px rgba(255,122,89,.38);}
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) *,
section[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) *{color:#2b1200 !important;font-weight:700;}
section[data-testid="stSidebar"] [data-testid="stSliderThumbValue"],
section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] [data-testid="stTickBarMax"]{color:#fff !important;}
.sbnote{font-size:.76rem;opacity:.78;line-height:1.5;}
section[data-testid="stSidebar"] .stButton button{background:rgba(255,255,255,.10)!important;color:#fff!important;
border:1px solid rgba(255,255,255,.22)!important;border-radius:999px!important;font-weight:600;justify-content:flex-start;padding:.3rem .9rem}
section[data-testid="stSidebar"] .stButton button:hover{background:rgba(255,255,255,.22)!important;border-color:#fff!important}
section[data-testid="stSidebar"] .stButton button p{color:#fff!important}
.key{display:flex;gap:8px;align-items:center;font-size:.8rem;margin:4px 0;}
.key i{width:11px;height:11px;border-radius:50%;display:inline-block;}

/* ---------- hero ---------- */
.hero{border-radius:22px;padding:26px 30px 22px 30px;color:#fff;position:relative;overflow:hidden;margin-bottom:22px;
  background:radial-gradient(circle at 93% 6%,rgba(255,122,89,.70),rgba(255,122,89,0) 36%),
             radial-gradient(circle at 62% 130%,rgba(14,154,167,.75),rgba(14,154,167,0) 48%),
             linear-gradient(118deg,#0b2a55 0%,#1c4fa0 52%,#4a2fa3 100%);
  box-shadow:0 20px 44px rgba(28,60,140,.28);}
.hero:after{content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;
  border:1px solid rgba(255,255,255,.16);box-shadow:0 0 0 38px rgba(255,255,255,.04),0 0 0 80px rgba(255,255,255,.03);}
.hero h1{color:#fff !important;font-size:2.15rem !important;font-weight:800;margin:0 0 4px 0;padding:0;}
.hero .sub{opacity:.88;font-size:1rem;max-width:760px;margin-bottom:16px;}
.hgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;position:relative;z-index:2;}
.gchip{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.26);border-radius:16px;padding:11px 15px;
  backdrop-filter:blur(8px);}
.gchip .l{font-size:.76rem;opacity:.82;}
.gchip .v{font-size:clamp(1.25rem,1.9vw,1.85rem);font-weight:800;line-height:1.2;}
.gchip .d{font-size:.78rem;opacity:.85;font-weight:600;}

/* ---------- sections, cards, pills ---------- */
.sec{display:flex;gap:12px;align-items:center;margin:26px 0 12px 0;}
.sec .bar{width:7px;height:34px;border-radius:6px;background:linear-gradient(180deg,#ff7a59,#6250d6);}
.sec .st{font-size:1.3rem;font-weight:800;color:#17233b;line-height:1.2;}
.sec .ss{font-size:.86rem;color:#5d6b82;}
.kc{display:flex;gap:13px;align-items:center;border-radius:18px;padding:14px 16px;margin-bottom:12px;border:1px solid #e3e8f3;
  background:linear-gradient(135deg,var(--bg) 0%,#ffffff 72%);box-shadow:0 6px 16px rgba(28,52,110,.07);}
.kc .ic{flex:none;width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;
  font-size:1.35rem;background:var(--ic);}
.kc .t{font-size:.8rem;color:#5d6b82;font-weight:600;}
.kc .v{font-size:clamp(1.2rem,1.7vw,1.7rem);font-weight:800;color:#17233b;line-height:1.2;}
.kc .s{font-size:.78rem;font-weight:700;}
.meter{height:7px;border-radius:5px;background:#e8ecf5;margin-top:7px;position:relative;}
.meter i{display:block;height:7px;border-radius:5px;}
.meter b{position:absolute;top:-4px;width:2px;height:15px;background:#17233b;border-radius:2px;}
.pill{display:inline-block;padding:3px 11px;border-radius:999px;font-size:.78rem;font-weight:700;margin:2px 5px 2px 0;}
.callout{border-radius:14px;padding:12px 16px;margin:6px 0 14px 0;font-size:.95rem;border-left:5px solid var(--c);
  background:linear-gradient(90deg,var(--bg),rgba(255,255,255,.9));color:#17233b;}
.tk{border-radius:20px;padding:22px 24px;color:#fff;min-height:330px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;
  background:radial-gradient(circle at 100% 0%,rgba(255,255,255,.22),rgba(255,255,255,0) 45%),var(--g);
  box-shadow:0 14px 30px rgba(28,52,110,.2);}
.tk .big{font-size:3.1rem;font-weight:800;line-height:1.05;margin:4px 0 2px 0;}
.tk .cap{font-size:1rem;opacity:.92;margin-bottom:14px;}
.tk .chip{display:inline-block;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.3);border-radius:999px;
  padding:4px 12px;margin:3px 5px 3px 0;font-size:.82rem;font-weight:700;}
.fpanel{border-radius:20px;overflow:hidden;border:1px solid #e3e8f3;background:#fff;box-shadow:0 8px 22px rgba(28,52,110,.09);}
.fhead{padding:16px 18px;color:#fff;font-weight:800;font-size:1.1rem;
  background:linear-gradient(120deg,#0b2a55,#4a2fa3 70%,#ff7a59 130%);}
.fhead small{display:block;font-weight:500;opacity:.8;font-size:.78rem;margin-top:2px;}
.fgroup{display:flex;gap:8px;align-items:center;font-size:.8rem;font-weight:800;color:#334155;margin:14px 0 4px 0;}
.fgroup i{width:10px;height:10px;border-radius:50%;display:inline-block;}
.fdetail{border-radius:20px;padding:20px 24px;background:#fff;border:1px solid #e3e8f3;
  box-shadow:0 8px 22px rgba(28,52,110,.09);margin-bottom:12px;border-top:6px solid var(--c);}
.fdetail h3{margin:6px 0 4px 0;font-size:1.5rem;font-weight:800;color:#17233b;}
.fdetail p{margin:0;color:#334155;font-size:1rem;}

/* ---------- widgets in the main area ---------- */
[data-testid="stMain"] div[role="radiogroup"]{gap:.45rem;flex-wrap:wrap;}
[data-testid="stMain"] label[data-testid="stRadioOption"],
[data-testid="stMain"] div[role="radiogroup"]>label{background:#fff;border:1px solid #d9e0ee;padding:.42rem 1rem;
  border-radius:999px;transition:all .15s;box-shadow:0 2px 6px rgba(28,52,110,.05);cursor:pointer;}
[data-testid="stMain"] label[data-testid="stRadioOption"]:hover,
[data-testid="stMain"] div[role="radiogroup"]>label:hover{border-color:#6250d6;}
[data-testid="stMain"] label[data-testid="stRadioOption"]>div>div:first-child,
[data-testid="stMain"] div[role="radiogroup"]>label>div:first-child{display:none;}
[data-testid="stMain"] label[data-testid="stRadioOption"]:has(input:checked),
[data-testid="stMain"] div[role="radiogroup"]>label:has(input:checked){
  background:linear-gradient(90deg,#1c4fa0,#6250d6);border-color:transparent;box-shadow:0 8px 18px rgba(98,80,214,.32);}
[data-testid="stMain"] label[data-testid="stRadioOption"]:has(input:checked) *,
[data-testid="stMain"] div[role="radiogroup"]>label:has(input:checked) *{color:#fff !important;font-weight:700;}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-radius:18px;border:1px solid #e3e8f3;
  box-shadow:0 8px 22px rgba(28,52,110,.08);}
button[data-testid="stBaseButton-secondary"]{background:#fff;border:1px solid #dbe2f0;border-left:5px solid #c7cff0;
  border-radius:12px;min-height:2.6rem;height:auto;padding:.45rem .8rem;text-align:left;justify-content:flex-start;
  box-shadow:0 2px 6px rgba(28,52,110,.05);transition:all .15s;}
button[data-testid="stBaseButton-secondary"]:hover{border-left-color:#ff7a59;transform:translateX(2px);}
button[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#1c4fa0,#6250d6);border:none;
  border-left:5px solid #ff7a59;border-radius:12px;min-height:2.6rem;height:auto;padding:.45rem .8rem;
  text-align:left;justify-content:flex-start;box-shadow:0 8px 18px rgba(98,80,214,.32);}
button[data-testid="stBaseButton-secondary"] p,button[data-testid="stBaseButton-primary"] p{white-space:normal;text-align:left;font-weight:600;}
button[data-testid="stBaseButton-primary"] p{color:#fff !important;}
@media (max-width:1300px){
  .block-container{padding:.8rem 1rem 2rem 1rem;}
  .hero{padding:20px 20px 16px 20px;}
  .hero h1{font-size:1.7rem !important;}
  .tk .big{font-size:2.4rem;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def stretch(fn, *args, **kw):
    """Full-width widget that works on old and new Streamlit versions."""
    try:
        return fn(*args, width="stretch", **kw)
    except TypeError:
        return fn(*args, use_container_width=True, **kw)


def html(s):
    st.markdown(" ".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


# =====================================================================
# Data (straight from the CSVs)
# =====================================================================
FOLDER = Path(__file__).resolve().parent
FILES = ["births_fertility_clean_full.csv", "marriage_rate_2000_2025_clean.csv",
         "CleanedEducation.csv", "housing_affordability_analysis.csv",
         "processed_fertility_lfpr_data.csv"]
missing = [f for f in FILES if not (FOLDER / f).exists()]
if missing:
    st.error("Missing files in the same folder as this script: " + ", ".join(missing))
    st.stop()

AGES = ["15_19", "20_24", "25_29", "30_34", "35_39", "40_44", "45_49"]
QSHORT = {"q_none": "No qual.", "q_primary": "Primary", "q_secondary": "Secondary",
          "q_high": "High school", "q_diploma": "Diploma", "university": "University"}
QUAL = {"q_none": "No qualification / lower primary", "q_primary": "Primary", "q_secondary": "Secondary",
        "q_high": "High school", "q_diploma": "Diploma", "university": "University"}


@st.cache_data
def load():
    f = pd.read_csv(FOLDER / FILES[0], encoding="utf-8-sig")
    fert = f.iloc[:, :9].copy()
    fert.columns = ["Year", "TFR"] + ["asfr_" + a for a in AGES]
    fert["births"] = f["Resident Live-Births"]
    mar = pd.read_csv(FOLDER / FILES[1])
    mar.columns = ["Year", "marriage"]
    edu = pd.read_csv(FOLDER / FILES[2]).rename(columns={
        "No Qualification/Lower Primary": "q_none", "Primary": "q_primary", "Secondary": "q_secondary",
        "High School": "q_high", "Diploma": "q_diploma", "University": "university"})
    edu = edu[["Year"] + list(QUAL)]
    hou = pd.read_csv(FOLDER / FILES[3]).rename(columns={
        "resident_employed_households_median_monthly_employment_income": "income",
        "hdb_4room_resale_price_median": "hdb_price",
        "hdb_4room_price_to_income_ratio": "price_income_ratio"})
    hou = hou[["Year", "income", "hdb_price", "price_income_ratio"]]
    lf = pd.read_csv(FOLDER / FILES[4]).rename(columns={"Female_LFPR": "female_lfpr"})
    lf = lf[["Year", "female_lfpr", "LFPR_25_29", "LFPR_30_34", "LFPR_35_39"]]
    d = fert
    for t in [mar, edu, hou, lf]:
        d = d.merge(t, on="Year")
    d["Year"] = d["Year"].astype(int)
    return d.sort_values("Year").set_index("Year")


DF = load()
CHG = (DF.drop(columns=["births"]).pct_change().replace([np.inf, -np.inf], np.nan).dropna()) * 100

FACTORS = ["marriage", "university", "income", "hdb_price", "price_income_ratio", "female_lfpr"]
NAME = {"TFR": "TFR", "marriage": "Crude marriage rate", "university": "University share (%)",
        "income": "Median household income", "hdb_price": "4-room HDB resale price",
        "price_income_ratio": "Price-to-income ratio", "female_lfpr": "Female labour force participation",
        "LFPR_25_29": "Female LFPR, age 25-29", "LFPR_30_34": "Female LFPR, age 30-34",
        "LFPR_35_39": "Female LFPR, age 35-39", "asfr_25_29": "Fertility, age 25-29",
        "asfr_30_34": "Fertility, age 30-34", "asfr_35_39": "Fertility, age 35-39"}
SHORT = {"marriage": "Marriage", "university": "Education", "income": "Income",
         "hdb_price": "HDB price", "price_income_ratio": "Price/income", "female_lfpr": "Female LFPR"}
COLOR = {"TFR": C_TFR, "marriage": C_MAR, "university": C_EDU, "income": C_INC, "hdb_price": C_HDB,
         "price_income_ratio": C_RAT, "female_lfpr": C_LFP, "LFPR_25_29": C_LFP, "LFPR_30_34": C_LFP,
         "LFPR_35_39": C_LFP}
ICON = {"marriage": "💍", "university": "🎓", "income": "💰", "hdb_price": "🏠",
        "price_income_ratio": "⚖️", "female_lfpr": "👩‍💼"}

# =====================================================================
# Sidebar: brand, menu, global year filter
# =====================================================================
PAGE_NAMES = ["📈  Birth rate (TFR)", "💍  Marriage", "🎓  Education", "🏠  Income and housing",
              "👩‍💼  Female labour force", "🔗  Links to marriage", "✅  Findings"]
with st.sidebar:
    html("""<div class="brand"><div class="logo">🇸🇬</div><div><div class="bt">Singapore<br>Birth Rate</div>
         <div class="bs">AN6100 · Group 7</div></div></div>""")
    page = st.radio("Menu", PAGE_NAMES, label_visibility="collapsed", key="nav")
    st.divider()
    Y0, Y1 = st.slider("Years shown", int(DF.index.min()), int(DF.index.max()),
                       (int(DF.index.min()), int(DF.index.max())))
    html("<div class='sbnote'>Filters every chart and correlation in the app.</div>")
    st.divider()
    st.markdown("<div class='sbnote' style='margin:0 0 6px'>Click to see those findings</div>", unsafe_allow_html=True)

    def _go(kind):
        st.session_state["nav"] = PAGE_NAMES[-1]
        st.session_state["finding_kind"] = kind

    for _kind, _lab in (("yes", "🟢  Correlated"), ("no", "🟣  No correlation"), ("ctx", "🔵  Context")):
        stretch(st.button, _lab, key=f"key_{_kind}", on_click=_go, args=(_kind,))
    html("""<div class='sbnote' style='margin-top:10px'>Correlated means the link survives after the shared
         time trend is removed.</div>""")
if Y1 - Y0 < 7:
    st.warning("Pick at least 8 years so the correlations mean something.")
    st.stop()

D = DF.loc[Y0:Y1]
C = CHG.loc[(CHG.index > Y0) & (CHG.index <= Y1)]


# =====================================================================
# One set of rules for every verdict in the app
# =====================================================================
def crit(n):
    """Smallest |r| that is significant at 5% for n points."""
    if tdist is None or n < 4:
        return 0.40
    t = tdist.ppf(0.975, n - 2)
    return float(t / np.sqrt(t * t + n - 2))


def pair(x, y, mode):
    src = D if mode == "levels" else C
    return src[x], src[y]


def rstat(x, y="TFR", mode="change"):
    a, b = pair(x, y, mode)
    r = a.corr(b)
    return r, len(a), abs(r) >= crit(len(a))


def final_ok(x, y="TFR"):
    return rstat(x, y, "change")[2]


def raw_ok(x, y="TFR"):
    return rstat(x, y, "levels")[2]


def verdict(ok):
    return "Correlated" if ok else "No correlation"


def borderline(r, n):
    return abs(abs(r) - crit(n)) < 0.03


# =====================================================================
# UI building blocks
# =====================================================================
def hero(title, sub, chips):
    cs = "".join(f"<div class='gchip'><div class='l'>{l}</div><div class='v'>{v}</div><div class='d'>{d}&nbsp;</div></div>"
                 for l, v, d in chips)
    html(f"<div class='hero'><h1>{title}</h1><div class='sub'>{sub}</div><div class='hgrid'>{cs}</div></div>")


def sec(title, sub=""):
    html(f"<div class='sec'><div class='bar'></div><div><div class='st'>{title}</div>"
         f"<div class='ss'>{sub}</div></div></div>")


def pill(text, kind="yes"):
    col = {"yes": YES, "no": NOC, "ctx": CTX}[kind]
    mark = {"yes": "✓ ", "no": "", "ctx": ""}[kind]
    return f"<span class='pill' style='background:{rgba(col, .14)};color:{col}'>{mark}{text}</span>"


def callout(text, kind="ctx"):
    col = {"yes": YES, "no": NOC, "ctx": CTX}[kind]
    html(f"<div class='callout' style='--c:{col};--bg:{rgba(col, .10)}'>{text}</div>")


def kcard(icon, title, big, sub="", color=C_TFR, sub_color=None, meter=None):
    m = ""
    if meter is not None:
        r, thr = meter
        w = min(abs(r) / 0.8, 1) * 100
        m = (f"<div class='meter'><i style='width:{w:.0f}%;background:{color}'></i>"
             f"<b style='left:{min(thr / 0.8, 1) * 100:.0f}%'></b></div>")
    html(f"""<div class='kc' style='--bg:{rgba(color, .13)};--ic:{rgba(color, .16)}'><div class='ic'>{icon}</div>
         <div style='flex:1;min-width:0'><div class='t'>{title}</div><div class='v'>{big}</div>
         <div class='s' style='color:{sub_color or color}'>{sub}&nbsp;</div>{m}</div></div>""")


# =====================================================================
# Chart helpers (plotly, always light)
# =====================================================================
def style(fig, h=380, title=None, legend=True):
    fig.update_layout(
        template="plotly_white", height=h, font=dict(family=FONT, size=12, color=INK),
        paper_bgcolor="white", plot_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font=dict(family=FONT, size=12), bordercolor="#d5dbe5"),
        margin=dict(l=10, r=14, t=88 if (title and legend) else (58 if title else 18), b=10),
        title=dict(text=title, x=0, y=0.97, yanchor="top", font=dict(size=15, color=INK)) if title else None,
        showlegend=legend, legend=dict(orientation="h", y=1.0, x=0, yanchor="bottom", font=dict(size=12)))
    fig.update_xaxes(gridcolor="#e9edf5", zerolinecolor="#cfd6e4", linecolor="#cfd6e4",
                     tickfont=dict(color=MUTED), title_font=dict(color="#334155", size=12))
    fig.update_yaxes(gridcolor="#e9edf5", zerolinecolor="#cfd6e4", linecolor="#cfd6e4",
                     tickfont=dict(color=MUTED), title_font=dict(color="#334155", size=12))
    try:
        fig.update_traces(marker_cornerradius=6, selector=dict(type="bar"))
    except Exception:
        pass
    return fig


def show(fig, key):
    with st.container(border=True):
        st.plotly_chart(fig, theme=None, key=key, config={"displaylogo": False})


def ts_fig(x, y, mode, h=380):
    src = D if mode == "levels" else C
    base = src[[x, y]]
    if mode == "levels":
        z = base / base.iloc[0] * 100
        ytitle, ttl = f"Index ({base.index[0]} = 100)", "Both series over time"
    else:
        z = (base - base.mean()) / base.std(ddof=0)
        ytitle, ttl = "Annual change (standardized)", "Year-to-year changes"
    fig = go.Figure()
    for col in (y, x):
        fig.add_trace(go.Scatter(
            x=z.index, y=z[col], name=NAME.get(col, col), mode="lines+markers",
            line=dict(color=COLOR.get(col, C_TFR), width=3), marker=dict(size=5),
            customdata=base[col], hovertemplate="%{y:.1f} (raw %{customdata:,.2f})"))
    fig.update_layout(hovermode="x unified", yaxis_title=ytitle, xaxis_title="Year")
    fig.add_hline(y=0 if mode == "change" else 100, line_color="#cfd6e4", line_width=1)
    return style(fig, h, ttl)


def scatter_fig(x, y, mode, h=380):
    a, b = pair(x, y, mode)
    r = a.corr(b)
    k, c0 = np.polyfit(a, b, 1)
    xs = np.linspace(a.min(), a.max(), 50)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=a, y=b, mode="markers", showlegend=False,
        marker=dict(size=11, color=a.index, colorscale=[[0, BLUE_RAMP[0]], [1, BLUE_RAMP[-1]]],
                    showscale=True, colorbar=dict(title="Year", thickness=11, len=0.8),
                    line=dict(width=2, color="white")),
        customdata=a.index, hovertemplate="Year %{customdata}<br>x: %{x:,.2f}<br>y: %{y:,.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=k * xs + c0, mode="lines", hoverinfo="skip", showlegend=False,
                             line=dict(color=COLOR.get(x, C_TFR) if abs(r) >= crit(len(a)) else "#9aa5ba",
                                       width=3)))
    if mode == "change":
        for yr in (2020, 2021):
            if yr in a.index:
                fig.add_annotation(x=a[yr], y=b[yr], text=str(yr), showarrow=False, yshift=14,
                                   font=dict(size=11, color=MUTED))
    fig.add_annotation(xref="paper", yref="paper", x=0.02, y=0.98, showarrow=False, align="left",
                       text=f"<b>r = {r:+.2f}</b><br>n = {len(a)}", bgcolor="rgba(255,255,255,0.92)",
                       bordercolor="#d5dbe5", borderpad=4, font=dict(color=INK))
    sfx = "" if mode == "levels" else " (annual change, %)"
    fig.update_layout(xaxis_title=NAME.get(x, x) + sfx, yaxis_title=NAME.get(y, y) + sfx)
    return style(fig, h, "Each dot is a year", legend=False)


def pair_bars(labels, colors, raw, trend, h=380, title=None, trend_name="Trend removed"):
    """Light bar = raw levels, solid bar = trend removed. Each bar keeps its entity colour."""
    t = crit(len(C))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=raw, marker_color=[rgba(c_, .35) for c_ in colors], showlegend=False,
                         text=[f"{v:+.2f}" for v in raw], textposition="outside",
                         hovertemplate="%{x}, raw: %{y:+.2f}<extra></extra>"))
    fig.add_trace(go.Bar(x=labels, y=trend, marker_color=colors, showlegend=False,
                         text=[f"{v:+.2f}{' ✓' if abs(v) >= t else ''}" for v in trend],
                         textposition="outside", hovertemplate="%{x}, " + trend_name.lower() + ": %{y:+.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="Raw levels (light)",
                             marker=dict(symbol="square", size=11, color="#c5cde2")))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=trend_name + " (solid)",
                             marker=dict(symbol="square", size=11, color="#475569")))
    fig.add_hrect(y0=-t, y1=t, fillcolor=BAND, line_width=0)
    fig.update_yaxes(range=[-1.12, 1.12], title="Correlation")
    fig.update_traces(textfont=dict(size=11, color=INK), selector=dict(type="bar"))
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05)
    return style(fig, h, title)


# =====================================================================
# Reusable chart builders
# =====================================================================
def fig_scoreboard(h=400):
    vals = [rstat(f)[0] for f in FACTORS]
    order = np.argsort(vals)
    fs = [FACTORS[i] for i in order]
    v = [vals[i] for i in order]
    t = crit(len(C))
    fig = go.Figure(go.Bar(
        y=[SHORT[f] for f in fs], x=v, orientation="h", marker_color=[COLOR[f] for f in fs],
        text=[f"{a:+.2f}{'  ✓ correlated' if abs(a) >= t else ''}" for a in v], textposition="outside",
        textfont=dict(size=13, color=INK), hovertemplate="%{y}: %{x:+.2f}<extra></extra>"))
    fig.add_vrect(x0=-t, x1=t, fillcolor=BAND, line_width=0)
    fig.update_xaxes(range=[-0.9, 1.0], title="Correlation with TFR after removing the time trend")
    fig.update_layout(bargap=0.3)
    return style(fig, h, "Which factors are correlated with TFR? (shaded = no clear link)", legend=False)


def fig_levels_vs_change(cols, h=380, title="Raw correlation vs trend removed"):
    return pair_bars([SHORT[c_] for c_ in cols], [COLOR[c_] for c_ in cols],
                     [rstat(c_, mode="levels")[0] for c_ in cols],
                     [rstat(c_, mode="change")[0] for c_ in cols], h, title)


DRAGON = [2000, 2012, 2024]
AGE_COL = {"15_19": "#e34948", "20_24": "#6250d6", "25_29": "#2a78d6", "30_34": "#eb6834",
           "35_39": "#1baf7a", "40_44": "#eda100", "45_49": "#d55181"}


def fig_overview(kind, ages=("25_29", "30_34", "35_39"), index100=False, h=400):
    fig = go.Figure()
    if kind in ("TFR trend", "Live births"):
        col, nm, colr = ("TFR", "TFR", C_TFR) if kind == "TFR trend" else ("births", "Resident live births", C_RAT)
        y = D[col] / D[col].iloc[0] * 100 if index100 else D[col]
        fig.add_trace(go.Scatter(x=D.index, y=y, mode="lines+markers", name=nm, fill="tozeroy",
                                 fillcolor=rgba(colr, .10), line=dict(color=colr, width=3.5),
                                 marker=dict(size=5),
                                 hovertemplate="%{x}: %{y:,.2f}<extra></extra>"))
        dr = [yr for yr in DRAGON if yr in D.index]
        fig.add_trace(go.Scatter(x=dr, y=[y[yr] for yr in dr], mode="markers", name="Dragon year",
                                 marker=dict(size=17, color="rgba(0,0,0,0)", line=dict(color=C_MAR, width=3)),
                                 hovertemplate="Dragon year %{x}<extra></extra>"))
        fig.update_yaxes(title="Index" if index100 else ("Births per woman" if col == "TFR" else "Live births"),
                         rangemode="tozero")
        return style(fig, h, "Total fertility rate" if col == "TFR" else "Resident live births")
    if kind == "Age-specific fertility":
        for a in ages:
            y = D["asfr_" + a] / D["asfr_" + a].iloc[0] * 100 if index100 else D["asfr_" + a]
            fig.add_trace(go.Scatter(x=D.index, y=y, mode="lines", name="Age " + a.replace("_", "-"),
                                     line=dict(color=AGE_COL[a], width=3)))
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(title="Index" if index100 else "Births per 1,000 women")
        return style(fig, h, "Age-specific fertility rates")
    parts = DF[["asfr_" + a for a in AGES]] * 5 / 1000
    ch1, ch2 = parts.loc[2021] - parts.loc[2000], parts.loc[2025] - parts.loc[2021]
    labs = [a.replace("_", "-") for a in AGES]
    fig.add_trace(go.Bar(x=labs, y=ch1.values, name="2000 to 2021", marker_color=C_INC))
    fig.add_trace(go.Bar(x=labs, y=ch2.values, name="2021 to 2025", marker_color=C_MAR))
    fig.update_layout(barmode="group", bargap=0.3, xaxis_title="Age group of mother", yaxis_title="Change in TFR")
    fig.add_hline(y=0, line_color="#94a3b8", line_width=1)
    return style(fig, h, "Where the fall came from (ignores the year filter)")


def fig_pair_scatter(x, h=380):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Raw levels", "Annual change (trend removed)"))
    for i, mode in enumerate(("levels", "change"), 1):
        a, b = pair(x, "TFR", mode)
        k, c0 = np.polyfit(a, b, 1)
        xs = np.linspace(a.min(), a.max(), 30)
        fig.add_trace(go.Scatter(x=a, y=b, mode="markers", customdata=a.index, showlegend=False,
                                 marker=dict(size=10, color=COLOR[x], line=dict(width=2, color="white")),
                                 hovertemplate="Year %{customdata}<br>%{x:,.2f}, %{y:,.2f}<extra></extra>"),
                      row=1, col=i)
        fig.add_trace(go.Scatter(x=xs, y=k * xs + c0, mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color=C_TFR, width=2.5)), row=1, col=i)
        fig.add_annotation(xref="x domain" if i == 1 else f"x{i} domain",
                           yref="y domain" if i == 1 else f"y{i} domain",
                           x=0.03, y=0.97, text=f"<b>r = {a.corr(b):+.2f}</b>", showarrow=False)
        fig.update_xaxes(title_text=NAME[x] if i == 1 else "Change (%)", row=1, col=i)
        fig.update_yaxes(title_text="TFR" if i == 1 else "TFR change (%)", row=1, col=i)
    return style(fig, h, legend=False)


def fig_ratio(h=380):
    ratio = DF["price_income_ratio"]
    fig = go.Figure()
    for s, e in ((2007, 2013), (2019, 2025)):
        fig.add_vrect(x0=s, x1=e, fillcolor=BAND, line_width=0,
                      annotation_text="affordability worsened", annotation_position="top left",
                      annotation_font=dict(size=11, color=MUTED))
    fig.add_trace(go.Scatter(x=ratio.index, y=ratio, mode="lines+markers", name="Price-to-income ratio",
                             line=dict(color=C_RAT, width=3.5), fill="tozeroy", fillcolor=rgba(C_RAT, .08),
                             marker=dict(size=5),
                             hovertemplate="%{x}: %{y:.2f} years of income<extra></extra>"))
    fig.add_hline(y=ratio.mean(), line_color="#94a3b8", line_width=1,
                  annotation_text=f"average {ratio.mean():.2f}", annotation_font=dict(size=11, color=MUTED))
    fig.update_yaxes(title="Years of income for a 4-room flat", range=[3.6, 6.0])
    return style(fig, h, "A flat costs 4 to 5.5 years of income, with no upward trend", legend=False)


LFPR_PAIRS = [("female_lfpr", "TFR", "Overall"), ("LFPR_25_29", "asfr_25_29", "Age 25-29"),
              ("LFPR_30_34", "asfr_30_34", "Age 30-34"), ("LFPR_35_39", "asfr_35_39", "Age 35-39")]


def fig_lfpr_age(h=380):
    return pair_bars([p[2] for p in LFPR_PAIRS], [C_LFP] * 4,
                     [rstat(x, y, "levels")[0] for x, y, _ in LFPR_PAIRS],
                     [rstat(x, y, "change")[0] for x, y, _ in LFPR_PAIRS], h,
                     "Female LFPR vs fertility, by age group")


MAR_AGE = {2000: (133.0, 69.8), 2021: (100.9, 106.4), 2025: (80.9, 94.9)}  # from the integration notebook


def fig_timing(h=380):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Marriage rate (per 1,000 unmarried women)",
                                                        "Fertility rate (births per 1,000 women)"))
    yrs = list(MAR_AGE)
    fig.add_trace(go.Scatter(x=yrs, y=[MAR_AGE[y][0] for y in yrs], name="Women 25-29", mode="lines+markers",
                             line=dict(color=AGE_COL["25_29"], width=3.5), marker=dict(size=9)), row=1, col=1)
    fig.add_trace(go.Scatter(x=yrs, y=[MAR_AGE[y][1] for y in yrs], name="Women 30-34", mode="lines+markers",
                             line=dict(color=AGE_COL["30_34"], width=3.5), marker=dict(size=9)), row=1, col=1)
    fig.add_trace(go.Scatter(x=DF.index, y=DF["asfr_25_29"], name="Women 25-29", showlegend=False,
                             line=dict(color=AGE_COL["25_29"], width=3.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=DF.index, y=DF["asfr_30_34"], name="Women 30-34", showlegend=False,
                             line=dict(color=AGE_COL["30_34"], width=3.5)), row=1, col=2)
    fig.update_yaxes(range=[0, 140])
    fig.update_annotations(font=dict(size=13, color=INK))
    style(fig, h + 40, "Marriage moved to the early thirties, but births did not follow")
    fig.update_layout(margin=dict(l=10, r=14, t=140, b=10),
                      legend=dict(orientation="h", x=0, y=1.2, yanchor="bottom", font=dict(size=12)))
    return fig


def fig_marriage_links(cols, mode, h=380):
    t = crit(len(C))
    r = [rstat(c_, "marriage", mode)[0] for c_ in cols]
    fig = go.Figure(go.Bar(
        y=[SHORT[c_] for c_ in cols], x=r, orientation="h", marker_color=[COLOR[c_] for c_ in cols],
        text=[f"{v:+.2f}{'  ✓ correlated' if abs(v) >= t else ''}" for v in r],
        textposition="outside", textfont=dict(size=13, color=INK),
        hovertemplate="%{y}: %{x:+.2f}<extra></extra>"))
    fig.add_vrect(x0=-t, x1=t, fillcolor=BAND, line_width=0)
    fig.update_xaxes(range=[-1.05, 1.15], title="Correlation with the marriage rate")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(bargap=0.3)
    return style(fig, h, "Which factors move with marriage? (shaded = no clear link)", legend=False)


LAG_ORDER = ["income", "hdb_price", "university", "female_lfpr"]


def fig_lag_lines(cols, maxlag, h=380):
    labs = ["Same year"] + [f"{k} yr earlier" for k in range(1, maxlag + 1)]
    t = crit(len(C))
    fig = go.Figure()
    fig.add_hrect(y0=-t, y1=t, fillcolor=BAND, line_width=0,
                  annotation_text="no clear link", annotation_position="bottom left",
                  annotation_font=dict(size=11, color=MUTED))
    for f in [c_ for c_ in LAG_ORDER if c_ in cols]:
        vals = [C[f].shift(k).corr(C["marriage"]) for k in range(maxlag + 1)]
        fig.add_trace(go.Scatter(x=labs, y=vals, mode="lines+markers", name=SHORT[f],
                                 line=dict(color=COLOR[f], width=3.5),
                                 marker=dict(size=11, line=dict(width=2, color="white")),
                                 hovertemplate="%{x}: %{y:+.2f}<extra>" + SHORT[f] + "</extra>"))
    fig.add_hline(y=0, line_color="#cfd6e4", line_width=1)
    fig.update_yaxes(range=[-1, 1], title="Correlation with marriage change")
    return style(fig, h, "Do earlier changes in a factor move marriage?")


EDU_ORDER = ["q_none", "q_primary", "q_secondary", "q_high", "q_diploma", "university"]


def edu_level_corr(lag):
    rows = []
    for q in QUAL:
        raw = D["TFR"].corr(D[q])
        ch = C["TFR"].corr(C[q].shift(lag))
        rows.append((QSHORT[q], raw, ch, len(C) - lag))
    return rows


def fig_edu_levels(lag=0, h=400):
    rows = edu_level_corr(lag)
    lab = {0: "Trend removed, same year", 1: "Trend removed, 1 yr earlier", 2: "Trend removed, 2 yrs earlier"}[lag]
    return pair_bars([r[0] for r in rows], [C_EDU] * len(rows), [r[1] for r in rows], [r[2] for r in rows], h,
                     "Which qualification level tracks TFR?", trend_name=lab)


def fig_edu_year(yr, h=400):
    """Share of residents by highest qualification in the chosen year."""
    cats = [QSHORT[q] for q in EDU_ORDER][::-1]
    vals = [D.loc[yr, q] for q in EDU_ORDER][::-1]
    cols = BLUE_RAMP[::-1]
    fig = go.Figure(go.Bar(y=cats, x=vals, orientation="h", marker_color=cols,
                           text=[f"{v:.0f}%" for v in vals], textposition="outside",
                           hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    fig.update_xaxes(range=[0, max(vals) * 1.25], title="% of residents aged 25+")
    fig.update_layout(bargap=0.35)
    return style(fig, h, f"Highest qualification of residents in {yr}", legend=False)


def fig_edu_shift(yr, h=400):
    """Dumbbell: first year of the range vs the chosen year, per qualification."""
    y0 = D.index[0]
    cats = [QSHORT[q] for q in EDU_ORDER][::-1]
    a = [D.loc[y0, q] for q in EDU_ORDER][::-1]
    b = [D.loc[yr, q] for q in EDU_ORDER][::-1]
    fig = go.Figure()
    for c_, u, v in zip(cats, a, b):
        fig.add_trace(go.Scatter(x=[u, v], y=[c_, c_], mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color="#c9cfe3", width=4)))
    fig.add_trace(go.Scatter(x=a, y=cats, mode="markers", name=str(y0),
                             marker=dict(size=15, color="#b9c4ec", line=dict(width=2, color="white")),
                             hovertemplate="%{y}: %{x:.1f}%<extra>" + str(y0) + "</extra>"))
    fig.add_trace(go.Scatter(x=b, y=cats, mode="markers", name=str(yr),
                             marker=dict(size=15, color=C_EDU, line=dict(width=2, color="white")),
                             hovertemplate="%{y}: %{x:.1f}%<extra>" + str(yr) + "</extra>"))
    fig.add_trace(go.Scatter(x=[max(u, v) for u, v in zip(a, b)], y=cats, mode="text", showlegend=False,
                             hoverinfo="skip", text=[f"  {v - u:+.0f} pts" for u, v in zip(a, b)],
                             textposition="middle right", textfont=dict(size=12, color=INK)))
    fig.update_xaxes(range=[0, max(a + b) * 1.25], title="% of residents aged 25+")
    return style(fig, h, f"How education shifted: {y0} vs {yr}", legend=True)


def edu_heat_note():
    n_sig, n_all = 0, 0
    for lag in (0, 1, 2):
        for q in QUAL:
            n = len(C) - lag
            n_all += 1
            n_sig += abs(C["TFR"].corr(C[q].shift(lag))) >= crit(n)
    return (f"Every qualification level looks linked to TFR in raw levels because they all drift over time. "
            f"After removing the trend only {n_sig} of {n_all} checks (6 levels, 3 timings) are significant and "
            f"they point in no consistent direction (about {0.05 * n_all:.0f} would appear by chance), "
            f"so there is no consistent education effect.")


# =====================================================================
# Page: main (TFR)
# =====================================================================
def page_main():
    t0, t1 = D["TFR"].iloc[0], D["TFR"].iloc[-1]
    hero("Singapore's birth rate", "Total fertility rate (TFR): average births per woman. "
         "We tested what moves it, using data from SingStat.",
         [(f"TFR in {Y0}", f"{t0:.2f}", "births per woman"),
          (f"TFR in {Y1}", f"{t1:.2f}", f"{t1 - t0:+.2f} ({(t1 / t0 - 1) * 100:+.0f}%)"),
          (f"Resident births in {Y1}", f"{D['births'].iloc[-1]:,.0f}",
           f"{(D['births'].iloc[-1] / D['births'].iloc[0] - 1) * 100:+.0f}% vs {Y0}"),
          ("Lowest TFR", f"{D['TFR'].min():.2f}", f"in {int(D['TFR'].idxmin())}")])

    sig = [f for f in FACTORS if final_ok(f)]
    trap = [f for f in FACTORS if raw_ok(f) and not final_ok(f)]
    mk = [f for f in ("university", "income", "hdb_price", "female_lfpr") if final_ok(f, "marriage")]

    sec("The story in four takeaways", "Pick one to see the number and the chart behind it")
    tabs = {"📉  The fall": 0, "🎯  What matters": 1, "🪞  Look-alikes": 2, "🔗  Marriage links": 3}
    pick = tabs[st.radio("Takeaway", list(tabs), horizontal=True, label_visibility="collapsed", key="take")]
    left, right = st.columns([1, 1.45])
    chips = ""
    if pick == 0:
        g = "linear-gradient(135deg,#0b2a55,#1c4fa0 60%,#0e9aa7)"
        big, cap = f"{(t1 / t0 - 1) * 100:+.0f}%", f"TFR went from {t0:.2f} to {t1:.2f} between {Y0} and {Y1}"
        chips = f"<span class='chip'>Below 1 child per woman: {'yes' if t1 < 1 else 'no'}</span>" \
                f"<span class='chip'>Lowest: {D['TFR'].min():.2f} in {int(D['TFR'].idxmin())}</span>"
        fig = fig_overview("TFR trend", h=330)
    elif pick == 1:
        g = "linear-gradient(135deg,#0f6b4a,#1baf7a 70%,#7be0b4)"
        big, cap = f"{len(sig)} of {len(FACTORS)}", "factors are correlated with TFR once the time trend is removed"
        chips = "".join(f"<span class='chip'>✓ {SHORT[f]} {rstat(f)[0]:+.2f}</span>" for f in sig) or \
                "<span class='chip'>none</span>"
        fig = fig_scoreboard(330)
    elif pick == 2:
        g = "linear-gradient(135deg,#4a2fa3,#6250d6 60%,#d55181)"
        big, cap = f"{len(trap)} of {len(FACTORS)}", "look strongly linked in raw data, but only because they all trend over time"
        chips = "".join(f"<span class='chip'>{SHORT[f]} raw {rstat(f, mode='levels')[0]:+.2f}</span>" for f in trap) or \
                "<span class='chip'>none</span>"
        fig = fig_levels_vs_change(FACTORS, 330, "Raw (light) vs trend removed (solid)")
    else:
        g = "linear-gradient(135deg,#a1360d,#eb6834 65%,#ffb347)"
        big, cap = f"{len(mk)} of 4", "other factors move with the marriage rate"
        chips = "".join(f"<span class='chip'>✓ {SHORT[f]} {rstat(f, 'marriage')[0]:+.2f}"
                        f"{' (borderline)' if borderline(*rstat(f, 'marriage')[:2]) else ''}</span>" for f in mk) or \
                "<span class='chip'>none</span>"
        fig = fig_marriage_links(["university", "income", "hdb_price", "female_lfpr"], "change", 330)
    with left:
        html(f"<div class='tk' style='--g:{g}'><div class='cap' style='margin:0'>&nbsp;</div>"
             f"<div class='big'>{big}</div><div class='cap'>{cap}</div>{chips}</div>")
    with right:
        show(fig, f"take_{pick}")

    sec("Factor scorecard", "Correlation with TFR after removing the shared time trend. The black tick is the "
        f"line a result must pass (|r| = {crit(len(C)):.2f})")
    lens = st.radio("Show", ["All six", "Correlated", "No correlation"], horizontal=True, key="lens")
    show_f = [f for f in FACTORS if lens == "All six" or (lens == "Correlated") == final_ok(f)]
    if not show_f:
        st.info("Nothing in this group for the selected years.")
    for i in range(0, len(show_f), 3):
        cols = st.columns(3)
        for c_, f in zip(cols, show_f[i:i + 3]):
            r, n, ok = rstat(f)
            rr = rstat(f, mode="levels")[0]
            sub = verdict(ok) + (f"  |  raw r = {rr:+.2f}, shared trend" if raw_ok(f) and not ok else "")
            with c_:
                kcard(ICON[f], SHORT[f], f"r = {r:+.2f}", sub, COLOR[f], YES if ok else NOC, meter=(r, crit(n)))

    sec("Explore the graphs", "Choose a chart, then filter it")
    f1, f2, f3 = st.columns([1.4, 1.8, 1])
    kind = f1.selectbox("Chart", ["TFR trend", "Live births", "Age-specific fertility",
                                  "Where the fall came from", "Factor scoreboard"])
    ages = f2.multiselect("Age groups", AGES, default=["25_29", "30_34", "35_39"],
                          format_func=lambda a: a.replace("_", "-"),
                          disabled=kind != "Age-specific fertility")
    idx = f3.toggle("Index to 100", value=False,
                    disabled=kind in ("Where the fall came from", "Factor scoreboard"),
                    help="Sets the first year to 100 so you can compare growth rates.")
    if kind == "Factor scoreboard":
        show(fig_scoreboard(), "ov_score")
    elif kind == "Age-specific fertility" and not ages:
        st.info("Pick at least one age group.")
    else:
        show(fig_overview(kind, tuple(ages), idx), "ov_main")
    if kind in ("TFR trend", "Live births"):
        callout("Orange rings mark <b>Dragon years</b> (2000, 2012, 2024). Many Chinese families plan births for "
                "the Dragon year, so births jump briefly. Treat them as one-off bumps, not changes in the trend.", "ctx")


# =====================================================================
# Page: one variable
# =====================================================================
def var_page(title, factor, options, blurb):
    x, y = factor, "TFR"
    if len(options) > 1:
        pick = st.session_state.get(f"opt_{factor}", list(options)[0])
        x, y = options[pick if pick in options else list(options)[0]]
    r_raw, f_raw = raw_ok(x, y), final_ok(x, y)
    rr, rf = rstat(x, y, "levels")[0], rstat(x, y, "change")[0]
    n = rstat(x, y, "change")[1]
    hero(title, blurb,
         [("Final verdict", verdict(f_raw), "after removing the trend"),
          ("Raw correlation", f"{rr:+.2f}", "looks strong" if r_raw else "weak"),
          ("Trend-removed correlation", f"{rf:+.2f}", "the fair test"),
          ("Needed to be significant", f"|r| ≥ {crit(n):.2f}", f"{n} annual changes")])
    left, right = st.columns([1.5, 1])
    if len(options) > 1:
        with right:
            st.radio("Compare with", list(options), horizontal=True, key=f"opt_{factor}")
        x, y = options[st.session_state[f"opt_{factor}"]]
        r_raw, f_raw = raw_ok(x, y), final_ok(x, y)
    with left:
        mode_key = st.radio(
            "Show", ["raw", "final"], horizontal=True, key=f"mode_{factor}",
            format_func=lambda m: (f"Raw levels ({'looks correlated' if r_raw else 'no correlation'})"
                                   if m == "raw" else f"Trend removed ({'correlated' if f_raw else 'no correlation'})"))
    mode = "levels" if mode_key == "raw" else "change"
    if mode == "levels" and r_raw and f_raw:
        callout("Correlated here, and the link also holds after removing the time trend.", "yes")
    elif mode == "levels" and r_raw:
        callout("Both series trend over time, which creates a strong raw correlation. Switch to <b>Trend removed</b> "
                "for the fair test: the final verdict is <b>no correlation</b>.", "ctx")
    elif mode == "levels":
        callout("No correlation in the raw levels, and none after removing the trend.", "no")
    elif f_raw:
        callout("The link survives after removing the time trend, so it is a real year-to-year link.", "yes")
    else:
        callout("Once the time trend is removed there is <b>no correlation</b>. This is the final verdict.", "no")
    c1, c2 = st.columns(2)
    with c1:
        show(ts_fig(x, y, mode), f"ts_{x}_{y}_{mode}")
    with c2:
        show(scatter_fig(x, y, mode), f"sc_{x}_{y}_{mode}")
    with st.expander("View the data table"):
        src = D if mode == "levels" else C
        stretch(st.dataframe, src[[y, x]].rename(columns=NAME).round(3))


def page_marriage():
    var_page("Marriage", "marriage", {"TFR": ("marriage", "TFR")},
             "Crude marriage rate (per 1,000 residents) against TFR.")
    sec("Go deeper")
    with st.expander("Lead and lag: does marriage come first?"):
        lags = [0, 1, 2, 3]
        vals = [C["TFR"].corr(C["marriage"].shift(k)) for k in lags]
        t = crit(len(C))
        fig = go.Figure(go.Bar(x=["Same year", "1 year earlier", "2 years earlier", "3 years earlier"], y=vals,
                               marker_color=C_MAR, text=[f"{v:+.2f}{' ✓' if abs(v) >= t else ''}" for v in vals],
                               textposition="outside"))
        fig.add_hrect(y0=-t, y1=t, fillcolor=BAND, line_width=0)
        fig.update_yaxes(range=[-0.8, 0.8], title="Correlation with TFR change")
        fig.update_layout(bargap=0.4)
        show(style(fig, 340, "Marriage vs TFR at different lags", legend=False), "mar_lag")
    with st.expander("Marriage moved later, births did not follow"):
        show(fig_timing(), "mar_timing")


def kcard_simple(label, value, sub, colr, icon="🎓"):
    kcard(icon, label, value, sub, colr, colr)


def page_education():
    var_page("Education", "university", {"TFR": ("university", "TFR")},
             "Share of residents aged 25+ with a university qualification against TFR.")
    sec("Education in detail", "Pick a year to see how educated residents were and how far that moved since the start")
    yrs = [int(y) for y in D.index]
    yr = st.selectbox("Year", yrs, index=len(yrs) - 1, key="eduyear")
    k1, k2, k3 = st.columns(3)
    with k1:
        kcard_simple("TFR in " + str(yr), f"{D.loc[yr, 'TFR']:.2f}", "births per woman", C_TFR, "📈")
    with k2:
        kcard_simple("University share", f"{D.loc[yr, 'university']:.0f}%", f"{D.loc[yr, 'university'] - D['university'].iloc[0]:+.0f} pts since {D.index[0]}", C_EDU)
    with k3:
        kcard_simple("No qualification", f"{D.loc[yr, 'q_none']:.0f}%", f"{D.loc[yr, 'q_none'] - D['q_none'].iloc[0]:+.0f} pts since {D.index[0]}", C_MAR, "📚")
    c1, c2 = st.columns(2)
    with c1:
        show(fig_edu_year(yr), f"edu_yr_{yr}")
    with c2:
        show(fig_edu_shift(yr), f"edu_shift_{yr}")
    callout(edu_heat_note(), "no")


def page_income():
    var_page("Income and housing", "income",
             {"Income": ("income", "TFR"), "HDB price": ("hdb_price", "TFR"),
              "Price-to-income": ("price_income_ratio", "TFR")},
             "Median household income, 4-room HDB resale price and the price-to-income ratio against TFR.")
    with st.expander("Affordability over time"):
        show(fig_ratio(), "inc_ratio")


def page_lfpr():
    var_page("Female labour force", "female_lfpr",
             {"Overall": ("female_lfpr", "TFR"), "Age 25-29": ("LFPR_25_29", "asfr_25_29"),
              "Age 30-34": ("LFPR_30_34", "asfr_30_34"), "Age 35-39": ("LFPR_35_39", "asfr_35_39")},
             "Female labour force participation against fertility, overall and by age group.")
    with st.expander("All age groups at a glance"):
        show(fig_lfpr_age(), "lfpr_age")


# =====================================================================
# Page: links to marriage
# =====================================================================
def page_links():
    MF = ["university", "income", "hdb_price", "female_lfpr"]
    rm = rstat("marriage", "TFR", "change")
    mk = [f for f in MF if final_ok(f, "marriage")]
    hero("Links to marriage", "We also tested whether each factor moves with the marriage rate.",
         [("Marriage vs TFR", f"{rm[0]:+.2f}", verdict(rm[2])),
          ("Factors linked to marriage", f"{len(mk)} of {len(MF)}", ", ".join(SHORT[f] for f in mk) or "none"),
          ("Needed to be significant", f"|r| ≥ {crit(len(C)):.2f}", f"{len(C)} annual changes")])
    a, b, b2 = st.columns([1.2, 1.7, 1])
    mode_lab = a.radio("Show", ["Annual change", "Raw levels"], horizontal=True, key="mlinks")
    mode = "levels" if mode_lab == "Raw levels" else "change"
    chosen = b.multiselect("Factors", MF, default=MF, format_func=lambda f: SHORT[f])
    maxlag = b2.slider("Years of lag to test", 1, 3, 2)
    if not chosen:
        st.info("Pick at least one factor.")
        return
    cols = st.columns(len(chosen))
    for c_, f in zip(cols, chosen):
        r, n, ok = rstat(f, "marriage", mode)
        with c_:
            kcard(ICON[f], SHORT[f] + " vs marriage", f"r = {r:+.2f}",
                  verdict(ok) + (" (borderline)" if borderline(r, n) else ""), COLOR[f], YES if ok else NOC,
                  meter=(r, crit(n)))

    c1, c2 = st.columns(2)
    with c1:
        show(fig_marriage_links(chosen, mode), "ml_bar")
    with c2:
        show(fig_lag_lines(chosen, maxlag), "ml_lag")

    sec("Look closer")
    pick = st.selectbox("Factor", chosen, format_func=lambda f: NAME[f])
    d1, d2 = st.columns(2)
    with d1:
        show(ts_fig("marriage", pick, mode), f"ml_ts_{pick}_{mode}")
    with d2:
        show(scatter_fig(pick, "marriage", mode), f"ml_sc_{pick}_{mode}")


# =====================================================================
# Page: findings (clickable panel on the right)
# =====================================================================
def findings():
    sig_f = [f for f in FACTORS if final_ok(f)]
    mk = [f for f in ("university", "income", "hdb_price", "female_lfpr") if final_ok(f, "marriage")]
    raws = [rstat(x, y, "levels")[0] for x, y, _ in LFPR_PAIRS]
    inc_sig = any(final_ok(f) for f in ("income", "hdb_price"))
    return [
        dict(label="Only marriage is correlated with TFR", st="yes" if "marriage" in sig_f else "no",
             text=f"After removing the time trend, correlated: {', '.join(SHORT[f] for f in sig_f) or 'none'}. "
                  f"Marriage r = {rstat('marriage')[0]:+.2f}.",
             fig=lambda: fig_scoreboard(420), key="f_score"),
        dict(label="Education: no correlation once the trend is removed", st="yes" if final_ok("university") else "no",
             text=f"University share rose as TFR fell (raw r = {rstat('university', mode='levels')[0]:+.2f}), "
                  f"but the annual-change correlation is only {rstat('university')[0]:+.2f}.",
             fig=lambda: fig_pair_scatter("university"), key="f_edu"),
        dict(label="Education levels: strong raw links, few after detrending", st="no",
             text=edu_heat_note(), fig=lambda: fig_edu_levels(0), key="f_eduheat"),
        dict(label="Income and HDB price: the raw link vanishes", st="yes" if inc_sig else "no",
             text="Both look strongly correlated in raw levels, then drop once the trend is removed.",
             fig=lambda: fig_levels_vs_change(["income", "hdb_price", "price_income_ratio"]), key="f_inc"),
        dict(label="Affordability has no trend and no correlation", st="yes" if final_ok("price_income_ratio") else "no",
             text=f"Price-to-income has no upward drift (r with TFR = {rstat('price_income_ratio')[0]:+.2f}).",
             fig=fig_ratio, key="f_ratio"),
        dict(label="Female LFPR: strong raw link, none after detrending", st="yes" if final_ok("female_lfpr") else "no",
             text=f"Raw correlation is strongly negative at every age ({min(raws):+.2f} to {max(raws):+.2f}), "
                  "but it disappears once the trend is removed.",
             fig=fig_lfpr_age, key="f_lfpr"),
        dict(label="Marriage moved later, births did not follow", st="ctx",
             text="Marriage shifted from the late twenties to the early thirties, yet fertility fell at both ages.",
             fig=fig_timing, key="f_timing"),
        dict(label="Since 2021 births fell at every age", st="ctx",
             text="Before 2021 births were postponed to older ages. After 2021 they fell in every age group.",
             fig=lambda: fig_overview("Where the fall came from"), key="f_contrib"),
        dict(label="Which factors move with marriage?", st="yes" if mk else "no",
             text=f"Moving with marriage after removing the trend: {', '.join(SHORT[f] for f in mk) or 'none'}.",
             fig=lambda: fig_marriage_links(["university", "income", "hdb_price", "female_lfpr"], "change"),
             key="f_mlinks"),
    ]


def page_findings():
    items = findings()
    n_y = sum(i["st"] == "yes" for i in items)
    n_n = sum(i["st"] == "no" for i in items)
    n_c = sum(i["st"] == "ctx" for i in items)
    hero("Our findings", "Click a finding on the right to see the evidence behind it.",
         [("Findings", f"{len(items)}", "in total"), ("Correlated", f"{n_y}", "link survives the trend test"),
          ("No correlation", f"{n_n}", "shared trend only"), ("Context", f"{n_c}", "background")])
    st.session_state.setdefault("finding", 0)
    kind_pick = st.session_state.pop("finding_kind", None)
    if kind_pick:
        st.session_state["finding"] = next((i for i, it in enumerate(items) if it["st"] == kind_pick), 0)
    left, right = st.columns([2, 1.1])
    with right:
        html("<div class='fpanel'><div class='fhead'>Key findings<small>Click one to open it</small></div></div>")
        for kind, title, col in (("yes", "Correlated", YES), ("no", "No correlation", NOC), ("ctx", "Context", CTX)):
            idxs = [i for i, it in enumerate(items) if it["st"] == kind]
            if not idxs:
                continue
            html(f"<div class='fgroup'><i style='background:{col}'></i>{title}</div>")
            for i in idxs:
                if stretch(st.button, items[i]["label"], key=f"fb{i}",
                           type="primary" if i == st.session_state["finding"] else "secondary"):
                    st.session_state["finding"] = i
                    st.rerun()
    cur = items[min(st.session_state["finding"], len(items) - 1)]
    col = {"yes": YES, "no": NOC, "ctx": CTX}[cur["st"]]
    nm = {"yes": "Correlated", "no": "No correlation", "ctx": "Context"}[cur["st"]]
    with left:
        html(f"<div class='fdetail' style='--c:{col}'>{pill(nm, cur['st'])}<h3>{cur['label']}</h3>"
             f"<p>{cur['text']}</p></div>")
        show(cur["fig"](), cur["key"])
        st.caption(f"Years {Y0} to {Y1}. Associations only, not proof of cause and effect.")


PAGES = {PAGE_NAMES[0]: page_main, PAGE_NAMES[1]: page_marriage, PAGE_NAMES[2]: page_education,
         PAGE_NAMES[3]: page_income, PAGE_NAMES[4]: page_lfpr, PAGE_NAMES[5]: page_links,
         PAGE_NAMES[6]: page_findings}
PAGES[page]()