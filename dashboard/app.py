"""Premium Streamlit dashboard for Bank Marketing campaign analysis."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Bank Marketing | Insights", page_icon=":material/insights:", layout="wide", initial_sidebar_state="expanded")
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
FEATURES = ["age", "job", "marital", "education", "default", "balance", "housing", "loan", "contact", "day", "month", "campaign", "pdays", "previous", "poutcome"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MONTH_LABEL = dict(zip(MONTHS, ["Janvier", "F\u00e9vrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Ao\u00fbt", "Septembre", "Octobre", "Novembre", "D\u00e9cembre"]))
JOB_LABEL = {"admin.": "Administration", "blue-collar": "Ouvriers", "entrepreneur": "Entrepreneurs", "housemaid": "Employ\u00e9s de maison", "management": "Management", "retired": "Retrait\u00e9s", "self-employed": "Ind\u00e9pendants", "services": "Services", "student": "\u00c9tudiants", "technician": "Techniciens", "unemployed": "Sans emploi", "unknown": "Non renseign\u00e9"}

st.markdown("""<style>
:root{--ink:#142a2b;--muted:#738180;--paper:#f4f6f3;--line:#e4e9e4;--green:#087a64;--green2:#0d9a79;--soft:#e7f4ee;--gold:#d7a65c}
html,body,[class*="css"]{font-family:'Segoe UI',Arial,sans-serif;color:var(--ink)}
.stApp{background:radial-gradient(ellipse at 70% -20%,#e7f3ed 0,transparent 38%),var(--paper)}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding:1.8rem 2.7rem 3rem}
h1,h2,h3{font-family:'Segoe UI',Arial,sans-serif;letter-spacing:-.045em;color:var(--ink)}
h2{font-size:1.35rem!important;font-weight:700!important}h3{font-size:1.06rem!important;font-weight:700!important}
[data-testid="stSidebar"]{background:#112c2c;border-right:1px solid #254342}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#d1dfda}
[data-testid="stSidebar"] [data-baseweb="select"] *{color:#142a2b}
[data-testid="stSidebar"] [data-testid="stRadio"] label{color:#edf5f1}
[data-testid="stSidebar"] hr{border-color:#31504d}
.brand{font-size:1.03rem;font-weight:800;letter-spacing:.08em;color:#f4faf6}.brand-mark{color:#51c6a3;font-size:1.4rem;vertical-align:-.12em;margin-right:.35rem}
.sidebar-caption{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#91aaa2!important}
.hero{position:relative;overflow:hidden;background:linear-gradient(115deg,#153d39 0%,#087a64 70%,#11977a 100%);padding:1.8rem 2rem;border-radius:22px;color:white;margin:.3rem 0 1.25rem;box-shadow:0 18px 40px #124b3520}
.hero:after{content:'';position:absolute;width:300px;height:300px;border:1px solid #ffffff20;border-radius:50%;right:-65px;top:-170px;box-shadow:0 0 0 35px #ffffff09,0 0 0 75px #ffffff07}
.hero h1{color:white;font-size:2.15rem;line-height:1.1;margin:.35rem 0}.hero p{color:#d4ebe2;margin:0;font-size:.98rem;max-width:780px}
.eyebrow{font-size:.68rem;text-transform:uppercase;letter-spacing:.18em;font-weight:700;color:#a8dec9}
.hero-meta{margin-top:1rem;color:#d7eee5;font-size:.77rem;letter-spacing:.02em}
.kpi-card{position:relative;overflow:hidden;background:#fff;border:1px solid var(--line);border-radius:16px;padding:1.05rem 1.1rem 1rem;min-height:132px;box-shadow:0 4px 16px #203c2c08}
.kpi-card:before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--green2)}
.kpi-top{display:flex;align-items:center;justify-content:space-between}.kpi-label{font-size:.76rem;letter-spacing:.03em;color:var(--muted);font-weight:650}.kpi-icon{width:28px;height:28px;border-radius:9px;background:var(--soft);color:var(--green);display:grid;place-items:center;font-size:.85rem}
.kpi-value{font-size:1.85rem;line-height:1.2;font-weight:750;letter-spacing:-.055em;margin:.65rem 0 .22rem;color:var(--ink)}.kpi-note{font-size:.74rem;color:var(--muted)}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 4px 18px #203c2c07}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]{gap:.65rem}
.insight{background:#f5faf7;border:1px solid #dfebe3;border-left:3px solid var(--green2);border-radius:11px;padding:.85rem 1rem;margin:.2rem 0;color:#284442;font-size:.88rem;line-height:1.5}
.insight strong{color:#116b58}.section-kicker{font-size:.7rem;text-transform:uppercase;letter-spacing:.13em;color:var(--green);font-weight:750}
.stButton>button,.stDownloadButton>button{border-radius:9px;font-weight:650;border-color:#dce5df}
.stButton>button[kind="primary"]{background:#087a64;border-color:#087a64}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}
[data-testid="stMetric"]{background:#fff;padding:.9rem 1rem;border:1px solid var(--line);border-radius:12px}
[data-testid="stCaptionContainer"]{color:var(--muted)}
footer{visibility:hidden}
@media(max-width:800px){.block-container{padding:1rem}.hero{padding:1.4rem}.hero h1{font-size:1.7rem}}
</style>""", unsafe_allow_html=True)


def find_data_file() -> Path:
    configured = os.getenv("BANK_DATA_PATH")
    candidates = ([Path(configured)] if configured else []) + [Path("/app/bank/bank-full.csv"), Path(__file__).resolve().parents[1] / "bank" / "bank-full.csv"]
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[-1])


@st.cache_data(show_spinner="Chargement des campagnes...")
def load_data(path_text: str) -> pd.DataFrame:
    df = pd.read_csv(path_text, sep=";")
    df["converted"] = df["y"].eq("yes")
    return df


def render_header(title: str, subtitle: str, count: int) -> None:
    st.markdown(f'<section class="hero"><div class="eyebrow">BANK MARKETING &nbsp; / &nbsp; CAMPAIGN INTELLIGENCE</div><h1>{title}</h1><p>{subtitle}</p><div class="hero-meta">{count:,} contacts dans la s\u00e9lection &nbsp; ? &nbsp; Donn\u00e9es historiques</div></section>'.replace(",", " "), unsafe_allow_html=True)


def render_kpi(label: str, value: str, note: str, icon: str) -> None:
    st.markdown(f'<div class="kpi-card"><div class="kpi-top"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)


def render_insight(title: str, detail: str) -> None:
    st.markdown(f'<div class="insight"><strong>{title}</strong> &nbsp; {detail}</div>', unsafe_allow_html=True)


DATA_PATH = find_data_file()
with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">&#9672;</span>BANK / INSIGHTS</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-caption">Campaign intelligence</p>', unsafe_allow_html=True)
    st.divider()
    page = st.radio("ESPACE", ["Vue d'ensemble", "Segments", "Scoring fichier"], label_visibility="visible")
    st.divider()
    if DATA_PATH.is_file():
        st.success("Source connect\u00e9e")
        st.caption(DATA_PATH.name)
    else:
        st.error("Source introuvable")

if not DATA_PATH.is_file():
    st.error(f"CSV introuvable : {DATA_PATH}. Placez bank-full.csv dans bank/ ou d\u00e9finissez BANK_DATA_PATH.")
    st.stop()

raw = load_data(str(DATA_PATH))
with st.sidebar:
    st.markdown("#### FILTRES")
    picked_months = st.multiselect("Mois de campagne", MONTHS, default=MONTHS, format_func=lambda m: MONTH_LABEL[m])
    all_jobs = sorted(raw.job.dropna().unique())
    picked_jobs = st.multiselect("Profession", all_jobs, default=all_jobs, format_func=lambda j: JOB_LABEL.get(j, j))
    st.divider()
    st.caption(f"Base compl\u00e8te : {len(raw):,} contacts".replace(",", " "))

filtered = raw[raw.month.isin(picked_months) & raw.job.isin(picked_jobs)].copy()
if filtered.empty:
    st.warning("Aucun contact ne correspond aux filtres. Modifiez la s\u00e9lection dans le menu lat\u00e9ral.")
    st.stop()

if page == "Vue d'ensemble":
    render_header("Pilotez vos campagnes", "Une lecture claire des performances pour orienter la prochaine action commerciale.", len(filtered))
    total = len(filtered)
    subscriptions = int(filtered.converted.sum())
    rate = float(filtered.converted.mean())
    calls = float(filtered.campaign.mean())
    avg_balance = float(filtered.balance.median())
    cols = st.columns(4, gap="medium")
    with cols[0]: render_kpi("Contacts analys\u00e9s", f"{total:,}".replace(",", " "), "P\u00e9rim\u00e8tre filtr\u00e9", "01")
    with cols[1]: render_kpi("Souscriptions", f"{subscriptions:,}".replace(",", " "), "R\u00e9sultats confirm\u00e9s", "02")
    with cols[2]: render_kpi("Taux de souscription", f"{rate:.1%}".replace(".", ","), "Conversion historique", "03")
    with cols[3]: render_kpi("Relances moyennes", f"{calls:.1f}".replace(".", ","), f"Solde m\u00e9dian : {avg_balance:,.0f} \u20ac".replace(",", " "), "04")

    st.write("")
    left, right = st.columns([1.25, 1], gap="medium")
    with left, st.container(border=True):
        st.markdown('<div class="section-kicker">TENDANCE</div>', unsafe_allow_html=True)
        st.subheader("Performance mensuelle")
        st.caption("Part des contacts ayant souscrit, selon le mois de campagne")
        monthly = filtered.groupby("month").converted.agg(taux="mean", contacts="size").reindex(MONTHS).dropna()
        monthly.index = [MONTH_LABEL[m] for m in monthly.index]
        st.bar_chart(monthly["taux"], color="#0d9a79", height=270)
        st.caption("Les volumes mensuels peuvent varier ; consultez le d?tail dans Segments.")
    with right, st.container(border=True):
        st.markdown('<div class="section-kicker">ACTIVATION</div>', unsafe_allow_html=True)
        st.subheader("Performance par canal")
        channel = filtered.groupby("contact").converted.agg(taux="mean", volume="size").sort_values("taux", ascending=False)
        channel.index = channel.index.map({"cellular": "Mobile", "telephone": "T\u00e9l\u00e9phone fixe", "unknown": "Non renseign\u00e9"})
        st.bar_chart(channel["taux"], color="#d7a65c", height=270)
        st.caption("Taux observ\u00e9 par canal, sur le p\u00e9rim\u00e8tre filtr\u00e9.")

    segment = filtered.groupby("job").converted.agg(taux="mean", contacts="size", souscriptions="sum")
    segment = segment[segment.contacts >= 100].sort_values("taux", ascending=False)
    channel_rates = filtered.groupby("contact").converted.mean()
    st.write("")
    insight_col, reco_col = st.columns([1, 1], gap="medium")
    with insight_col, st.container(border=True):
        st.markdown('<div class="section-kicker">LECTURE DES R\u00c9SULTATS</div>', unsafe_allow_html=True)
        st.subheader("Signaux \u00e0 retenir")
        if not segment.empty:
            job = segment.index[0]
            row = segment.iloc[0]
            render_insight("Segment le plus r\u00e9ceptif", f"{JOB_LABEL.get(job, job)} : {row.taux:.1%} sur {row.contacts:,.0f} contacts (minimum 100).".replace(",", " "))
        if "cellular" in channel_rates and "unknown" in channel_rates:
            render_insight("Qualit\u00e9 du canal", f"Mobile : {channel_rates['cellular']:.1%} ; canal non renseign\u00e9 : {channel_rates['unknown']:.1%}.")
        render_insight("Intensit\u00e9 commerciale", f"{calls:.1f} relances par dossier en moyenne.")
    with reco_col, st.container(border=True):
        st.markdown('<div class="section-kicker">PROCHAINE ACTION</div>', unsafe_allow_html=True)
        st.subheader("Recommandations")
        if not segment.empty:
            job = segment.index[0]
            render_insight("01 ? Piloter", f"Tester le segment {JOB_LABEL.get(job, job)} sur une campagne limit\u00e9e, puis comparer au taux global de {rate:.1%}.")
        render_insight("02 ? Ma\u00eetriser", "Tester un plafond de relances et mesurer les conversions marginales avant d'augmenter la pression commerciale.")
        render_insight("03 ? Mesurer", "Conserver un groupe t\u00e9moin pour distinguer l'effet de la campagne des variations naturelles.")
    st.caption("Lecture descriptive des campagnes historiques. Les associations observ\u00e9es ne prouvent pas une causalit\u00e9 et ne garantissent pas les r\u00e9sultats futurs.")

elif page == "Segments":
    render_header("Explorez les segments", "Comparez les taux et les volumes avant d'allouer votre budget de campagne.", len(filtered))
    by_job = filtered.groupby("job").converted.agg(taux="mean", contacts="size", souscriptions="sum").sort_values("taux", ascending=False)
    by_job.index = by_job.index.map(lambda x: JOB_LABEL.get(x, x))
    left, right = st.columns([1.1, 1], gap="medium")
    with left, st.container(border=True):
        st.markdown('<div class="section-kicker">COMPARAISON</div>', unsafe_allow_html=True)
        st.subheader("Taux de souscription par profession")
        st.bar_chart(by_job["taux"], color="#0d9a79", height=380)
    with right, st.container(border=True):
        st.markdown('<div class="section-kicker">VOLUME & CONVERSION</div>', unsafe_allow_html=True)
        st.subheader("D\u00e9tail des r\u00e9sultats")
        st.dataframe(by_job, use_container_width=True, column_config={"taux": st.column_config.ProgressColumn("Taux", min_value=0, max_value=1, format="percent"), "contacts": st.column_config.NumberColumn("Contacts", format="%d"), "souscriptions": st.column_config.NumberColumn("Souscriptions", format="%d")})
        st.download_button("Exporter les segments CSV", by_job.to_csv().encode("utf-8-sig"), "segments_campagne.csv", "text/csv", use_container_width=True)
    with st.container(border=True):
        st.markdown('<div class="section-kicker">FR\u00c9QUENCE DE CONTACT</div>', unsafe_allow_html=True)
        st.subheader("Relances et taux de souscription")
        attempts = filtered.assign(groupe=pd.cut(filtered.campaign, [0, 1, 2, 3, 5, 10, 100], labels=["1", "2", "3", "4\u20135", "6\u201310", "11+"])).groupby("groupe", observed=True).converted.agg(taux="mean", contacts="size")
        st.line_chart(attempts["taux"], color="#d7a65c", height=250)
        st.caption("Une association entre nombre de relances et conversion ne mesure pas l'effet causal des appels.")

else:
    render_header("Scoring de votre portefeuille", "Importez une liste de profils pour obtenir une priorisation via le service de pr\u00e9diction.", len(filtered))
    st.info("Cette fonction n\u00e9cessite l'API FastAPI et les 15 champs du mod\u00e8le.")
    try:
        api_ok = requests.get(f"{API_URL}/health", timeout=2).ok
    except requests.RequestException:
        api_ok = False
    api_status = "connect\u00e9" if api_ok else "indisponible"
    st.caption(f"Service de scoring : {api_status} | {API_URL}")
    file = st.file_uploader("S\u00e9lectionner un fichier CSV", type=["csv"])
    if file:
        try:
            incoming = pd.read_csv(file, sep=None, engine="python")
            missing = [column for column in FEATURES if column not in incoming.columns]
            st.dataframe(incoming.head(8), use_container_width=True, hide_index=True)
            if missing:
                st.error("Champs manquants : " + ", ".join(missing))
            elif st.button("Calculer les scores", type="primary", disabled=not api_ok):
                response = requests.post(f"{API_URL}/predict/batch", json={"customers": incoming[FEATURES].to_dict(orient="records")}, timeout=90)
                response.raise_for_status()
                predictions = response.json()["predictions"]
                incoming["probabilite"] = [prediction["probability"] for prediction in predictions]
                incoming["priorite"] = ["A contacter" if prediction["prediction"] else "A relancer plus tard" for prediction in predictions]
                st.metric("Profils prioritaires", sum(prediction["prediction"] for prediction in predictions))
                st.dataframe(incoming.sort_values("probabilite", ascending=False), use_container_width=True, hide_index=True)
                st.download_button("T\u00e9l\u00e9charger les r\u00e9sultats", incoming.to_csv(index=False).encode("utf-8-sig"), "scoring_clients.csv", "text/csv")
        except Exception as exc:
            st.error(f"Impossible de lire ou scorer ce fichier : {exc}")

st.divider()
st.caption(f"BANK / INSIGHTS  ?  Source {DATA_PATH.name}  ?  {len(filtered):,} contacts affich\u00e9s".replace(",", " "))
