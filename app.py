from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
import calendar
import html
import re

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "palpites.csv"
PHOTOS_DIR = BASE_DIR / "fotos_jose"

st.set_page_config(page_title="Bolão de José Benjamin", page_icon="🍼", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp { background: #fbf7f2; color: #3e322d; } h1,h2,h3 { font-family:'Playfair Display',Georgia,serif!important;color:#68483c; }
.hero { padding:2rem 0 .6rem; }.hero h1{font-size:clamp(2.35rem,5vw,4.5rem);margin-bottom:.2rem}.eyebrow{color:#b77a5c;letter-spacing:.13em;font-weight:700;font-size:.76rem;text-transform:uppercase}
.intro-card{background:#fffdf9;border:1px solid #ecdcd0;border-radius:20px;padding:1.45rem 1.6rem;box-shadow:0 8px 25px rgba(104,72,60,.06)}.intro-card p{font-size:1.07rem;line-height:1.65;margin:0}
.stat{background:#f2e3d7;border-radius:16px;padding:1rem;text-align:center}.stat b{display:block;font:700 1.75rem 'Playfair Display',Georgia,serif;color:#9d6048}
div[data-testid="stForm"]{border:1px solid #ecdcd0;border-radius:20px;background:#fffdf9;padding:1.4rem}.stButton>button,.stFormSubmitButton>button{background:#9d6048!important;color:white!important;border:0!important;border-radius:10px!important;font-weight:700!important;padding:.55rem 1.2rem!important}.stTabs [data-baseweb="tab-list"]{gap:1.5rem}.stTabs [data-baseweb="tab"]{font-weight:700;color:#795a4d}
.viz-note{color:#8a6b5d;font-size:.9rem;margin:.3rem 0 1rem}.month-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin-top:.6rem}.month-wrap{background:#fffdf9;border:1px solid #ecdcd0;border-radius:18px;padding:1rem;margin:0 0 1rem}.month-title{font:700 1.25rem 'Playfair Display',Georgia,serif;color:#68483c;text-transform:capitalize}.weekday{text-align:center;font-size:.68rem;font-weight:700;color:#b49281;padding:.15rem}.day{position:relative;min-height:48px;border-radius:10px;background:#f9f1eb;padding:5px;font-size:.78rem;color:#795a4d}.day.empty{background:transparent}.day.has-bets{background:#f0cdb9;color:#603d30;font-weight:700}.day.top-day{background:#b77a5c;color:white;box-shadow:0 4px 10px rgba(157,96,72,.25)}.day.today{outline:2px solid #c94d4d;outline-offset:1px;box-shadow:0 0 0 3px rgba(201,77,77,.14)}.day.past-day::after{content:'×';position:absolute;right:5px;top:0px;color:#bd6660;font-size:1.25rem;line-height:1;font-weight:400;opacity:.72}.day.past-day.top-day::after{color:#fff4ec}.count-dot{display:block;font-size:.66rem;margin-top:3px}.winner-card{background:linear-gradient(135deg,#fff6dd,#f2d9ba);border:1px solid #e6b87e;border-radius:20px;padding:1.25rem;margin-bottom:1rem;color:#68483c}.winner-card b{font:700 1.45rem 'Playfair Display',Georgia,serif}.legend-dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin:0 5px 0 12px;background:#f0cdb9}.legend-dot.first{margin-left:0;background:#b77a5c}
.bet-card{background:#fffdf9;border:1px solid #ecdcd0;border-radius:14px;padding:.9rem 1rem;margin:.55rem 0;color:#68483c}.bet-card-header{display:flex;align-items:center;justify-content:space-between;gap:1rem}.bet-date{font-weight:700;font-size:1.02rem}.bet-people{margin:.7rem 0 0;padding-left:1.25rem;color:#795a4d}.bet-people li{margin:.22rem 0}.bet-count{flex-shrink:0;background:#f2e3d7;border-radius:999px;padding:.35rem .65rem;color:#795a4d;font-size:.77rem;font-weight:700;text-align:center}
@media (max-width: 600px){.bet-card-header{align-items:flex-start;flex-direction:column;gap:.55rem}.bet-count{align-self:flex-start}}
</style>""", unsafe_allow_html=True)

# As abas do Streamlit herdam cores diferentes no modo escuro. Estas regras
# mantêm contraste no tema visual claro e fixo deste bolão.
st.markdown("""<style>
.stTabs [role="tab"], .stTabs [data-baseweb="tab"] {
    color: #68483c !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}
.stTabs [role="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #9d6048 !important;
}
.stTabs [role="tab"]:hover, .stTabs [data-baseweb="tab"]:hover {
    color: #7c4634 !important;
    background: #f2e3d7 !important;
}
.stTabs [data-baseweb="tab-highlight"] { background-color: #b77a5c !important; }
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child {
    background: #ead5c7 !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child > div {
    background: #b77a5c !important;
}
div[data-testid="stSliderThumbValue"] [role="slider"] {
    background: #9d6048 !important;
    border: 2px solid #fffdf9 !important;
    box-shadow: 0 1px 5px rgba(104, 72, 60, .28) !important;
}
div[data-testid="stSlider"] [role="slider"]:focus-visible {
    outline: 3px solid rgba(183, 122, 92, .42) !important;
}
</style>""", unsafe_allow_html=True)

def load_bets() -> pd.DataFrame:
    columns = ["nome", "data_palpite", "peso_palpite_kg", "enviado_em"]
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=columns)
    try:
        bets = pd.read_csv(DATA_FILE)
        # Arquivos criados antes do palpite de peso continuam funcionando.
        if "peso_palpite_kg" not in bets.columns:
            bets["peso_palpite_kg"] = pd.NA
        if set(columns).issubset(bets.columns):
            bets["data_palpite"] = pd.to_datetime(bets["data_palpite"], errors="coerce")
            bets["peso_palpite_kg"] = pd.to_numeric(bets["peso_palpite_kg"], errors="coerce")
            return bets.dropna(subset=["data_palpite"])
    except (OSError, pd.errors.ParserError):
        pass
    return pd.DataFrame(columns=columns)

def save_bet(name: str, guess: date, weight: float) -> None:
    bets = load_bets()
    entry = pd.DataFrame([{"nome": name, "data_palpite": pd.Timestamp(guess), "peso_palpite_kg": weight, "enviado_em": datetime.now().isoformat(timespec="seconds")}])
    pd.concat([bets, entry], ignore_index=True).to_csv(DATA_FILE, index=False)

def clean_name(name: str) -> str:
    return " ".join(name.strip().split())

MONTHS_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

def calendar_view(counts: dict[date, int], highlight: bool = False, intensity: bool = False) -> None:
    """Renderiza os meses com destaque do líder ou cor proporcional aos palpites."""
    dates = sorted(counts)
    start, end = dates[0], dates[-1]
    year, month = start.year, start.month
    max_count = max(counts.values())
    while (year, month) <= (end.year, end.month):
        weeks = calendar.monthcalendar(year, month)
        cells = "".join('<div class="weekday">' + day + '</div>' for day in ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"])
        for week in weeks:
            for day_number in week:
                if not day_number:
                    cells += '<div class="day empty"></div>'
                    continue
                current = date(year, month, day_number)
                total = counts.get(current, 0)
                classes = "day"
                if current == date.today():
                    classes += " today"
                elif current < date.today():
                    classes += " past-day"
                if total:
                    classes += " has-bets"
                style = ""
                if highlight and total == max_count and total:
                    classes += " top-day"
                elif intensity and total:
                    # Do creme ao terracota: a cor máxima é a do dia líder original.
                    fraction = total / max_count
                    light, dark = (242, 227, 215), (183, 122, 92)
                    red, green, blue = [round(a + (b - a) * fraction) for a, b in zip(light, dark)]
                    text_color = "#ffffff" if fraction >= 0.62 else "#603d30"
                    style = f' style="background:rgb({red},{green},{blue});color:{text_color};font-weight:700"'
                label = f'<span>{day_number}</span>' + (f'<span class="count-dot">🍼 {total}</span>' if total else "")
                cells += f'<div class="{classes}"{style}>{label}</div>'
        st.markdown(f'<div class="month-wrap"><div class="month-title">{MONTHS_PT[month - 1]} de {year}</div><div class="month-grid">{cells}</div></div>', unsafe_allow_html=True)
        month += 1
        if month == 13:
            year, month = year + 1, 1

def bet_cards(records: pd.DataFrame) -> None:
    """Exibe um cartão por data, dos dias mais disputados aos menos disputados."""
    grouped = records.groupby("data_palpite", sort=False)
    for bet_day, group in grouped:
        total = len(group)
        bet_date = bet_day.strftime("%d/%m/%Y")
        label = "palpite" if total == 1 else "palpites"
        people = "".join(f"<li>{html.escape(str(name))}</li>" for name in sorted(group["nome"], key=str.casefold))
        st.markdown(
            f'<div class="bet-card"><div class="bet-card-header"><div class="bet-date">📅 {bet_date}</div>'
            f'<div class="bet-count">🍼 {total} {label}</div></div><ul class="bet-people">{people}</ul></div>',
            unsafe_allow_html=True,
        )

def weight_cards(records: pd.DataFrame) -> None:
    """Exibe um cartão por peso, com a lista de quem apostou nele."""
    for weight, group in records.groupby("peso_palpite_kg", sort=False):
        total = len(group)
        label = "palpite" if total == 1 else "palpites"
        people = "".join(f"<li>{html.escape(str(name))}</li>" for name in sorted(group["nome"], key=str.casefold))
        weight_label = f"{weight:.3f}".replace(".", ",") + " kg"
        st.markdown(
            f'<div class="bet-card"><div class="bet-card-header"><div class="bet-date">⚖️ {weight_label}</div>'
            f'<div class="bet-count">🍼 {total} {label}</div></div><ul class="bet-people">{people}</ul></div>',
            unsafe_allow_html=True,
        )

bets = load_bets()
photos = sorted([*PHOTOS_DIR.glob("*.jpg"), *PHOTOS_DIR.glob("*.jpeg"), *PHOTOS_DIR.glob("*.png")])
left, right = st.columns([1.25, .75], vertical_alignment="center")
with left:
    st.markdown('<section class="hero"><div class="eyebrow">Uma brincadeira para celebrar</div><h1>Bolão de José Benjamin</h1></section>', unsafe_allow_html=True)
    st.markdown('<div class="intro-card"><p>Oi, pessoal! Eu sou o José Benjamin e estou quase chegando. Antes de me conhecerem, que tal tentarem adivinhar o dia e peso da minha estreia? Escolham uma data e um peso, deixem o nome de vocês e acompanhem os palpites por aqui. 🤎</p></div>', unsafe_allow_html=True)
with right:
    if photos:
        st.image(photos[0], width="stretch")

st.write("")
today = date.today()
active = bets[bets["data_palpite"].dt.date >= today] if not bets.empty else bets
stats = st.columns(3)
for slot, value, label in zip(stats, [len(bets), len(active), bets["nome"].nunique() if not bets.empty else 0], ["palpite(s)", "ainda na torcida", "participante(s)"]):
    with slot: st.markdown(f'<div class="stat"><b>{value}</b>{label}</div>', unsafe_allow_html=True)

st.write("")
tab_bet, tab_panel, tab_weight = st.tabs(["✦ Fazer meu palpite", "📅 Palpites de data", "⚖️ Resultados de peso"])
with tab_bet:
    st.subheader("Quando você acha que eu chego?")
    st.caption("Cada pessoa pode participar uma vez. O palpite fica público no painel.")
    with st.form("bet_form", clear_on_submit=True):
        name = st.text_input("Seu nome", placeholder="Ex.: Tia Marina")
        guess = st.date_input("Minha aposta é para", value=today + timedelta(days=7), min_value=today, max_value=today + timedelta(days=90), format="DD/MM/YYYY")
        weight = st.slider("E com qual peso eu vou nascer? (em kg)", min_value=2.400, max_value=4.000, value=2.800, step=0.010, format="%.3f")
        
        submitted = st.form_submit_button("Registrar meu palpite 🍼")
    if submitted:
        name = clean_name(name)
        if len(name) < 2 or not re.search(r"[A-Za-zÀ-ÿ]", name): st.error("Conte para a gente seu nome, por favor.")
        # elif not bets.empty and bets["nome"].str.casefold().eq(name.casefold()).any(): st.warning("Já temos um palpite registrado com esse nome. 😊")
        else:
            save_bet(name, guess, weight)
            st.success(f"Pronto, {name}! Seu palpite é {guess.strftime('%d/%m/%Y')} e {weight:.3f} kg.")
            st.balloons()
            # st.rerun()

with tab_panel:
    st.subheader("A torcida está assim")
    if bets.empty:
        st.info("Os primeiros palpites vão aparecer aqui. Quem será que acerta?")
    else:
        display = bets.copy()
        display["data"] = display["data_palpite"].dt.strftime("%d/%m/%Y")
        display["situação"] = display["data_palpite"].dt.date.map(lambda d: "Ainda na torcida" if d >= today else "Não foi dessa vez")
        counts = display.groupby(display["data_palpite"].dt.date).size().to_dict()
        top_count = max(counts.values())
        top_dates = [day for day, total in counts.items() if total == top_count]

        st.markdown("#### Calendário da torcida")
        leaders = " e ".join(day.strftime("%d/%m") for day in top_dates)
        plural = "são os dias mais cotados" if len(top_dates) > 1 else "é o dia mais cotado"
        st.markdown(f'<div class="winner-card">⭐ <b>{leaders}</b> {plural}, com <b>{top_count}</b> palpite(s)!</div><span class="legend-dot first"></span>mais cotado <span class="legend-dot"></span>com palpite', unsafe_allow_html=True)
        st.markdown('<p class="viz-note">Quanto mais escuro o dia, mais palpites ele recebeu. O tom mais intenso é o do dia mais cotado.</p>', unsafe_allow_html=True) 
        calendar_view(counts, intensity=True)

        st.markdown("#### Quem apostou em quê")
        active_tab, missed_tab = st.tabs(["🤎 Palpites que ainda valem", "☁️ Palpites que já perderam"])
        display["total_na_data"] = display["data_palpite"].dt.date.map(counts)
        order = ["total_na_data", "data_palpite", "nome"]

        with active_tab:
            active_display = display[display["situação"] == "Ainda na torcida"].sort_values(order, ascending=[False, True, True])
            if active_display.empty:
                st.info("Ainda não há palpites em datas futuras.")
            else:
                bet_cards(active_display)

        with missed_tab:
            missed = display[display["situação"] == "Não foi dessa vez"].sort_values(order, ascending=[False, True, True])
            if missed.empty:
                st.caption("Ainda nenhum palpite ficou para trás. ✨")
            else:
                bet_cards(missed)

with tab_weight:
    st.subheader("Quanto o José Benjamin vai pesar?")
    weight_bets = bets.dropna(subset=["peso_palpite_kg"]).copy()
    if weight_bets.empty:
        st.info("Os palpites de peso vão aparecer aqui assim que a primeira pessoa participar.")
    else:
        weight_counts = weight_bets.groupby("peso_palpite_kg").size().to_dict()
        average_weight = weight_bets["peso_palpite_kg"].mean()
        max_weight = weight_bets["peso_palpite_kg"].max()
        min_weight = weight_bets["peso_palpite_kg"].min()
        weight_stats = st.columns(4)
        with weight_stats[0]:
            st.markdown(f'<div class="stat"><b>{len(weight_bets)}</b>palpite(s) de peso</div>', unsafe_allow_html=True)
        with weight_stats[1]:
            st.markdown(f'<div class="stat"><b>{average_weight:.3f} kg</b>média dos palpites</div>', unsafe_allow_html=True)
        with weight_stats[2]:
            st.markdown(f'<div class="stat"><b>{max_weight:.3f} kg</b>peso máximo dos palpites</div>', unsafe_allow_html=True)
        with weight_stats[3]:
            st.markdown(f'<div class="stat"><b>{min_weight:.3f} kg</b>peso mínimo dos palpites</div>', unsafe_allow_html=True)

        st.write("")
        st.caption("Os pesos mais escolhidos aparecem primeiro.")
        weight_bets["total_no_peso"] = weight_bets["peso_palpite_kg"].map(weight_counts)
        weight_bets = weight_bets.sort_values(["total_no_peso", "peso_palpite_kg", "nome"], ascending=[False, False, True])
        weight_cards(weight_bets)

st.divider()
st.caption("Feito com carinho para celebrar a chegada de José Benjamin.")
