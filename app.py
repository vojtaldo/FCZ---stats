import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- POMOCNÁ FUNKCE PRO NAČTENÍ LOKÁLNÍHO OBRÁZKU DO CSS ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# --- 1. KONFIGURACE A DESIGN (Společné pro všechny stránky) ---
st.set_page_config(page_title="FC Zličín - Portál", layout="wide", page_icon="⚽")

grass_bg = get_base64_of_bin_file("grass.jpg")
bg_url = f"data:image/jpg;base64,{grass_bg}" if grass_bg else ""
MAIN_BLUE = "#0056b3"
BLUE_GRADIENT = ["#003366", "#004080", "#0056b3", "#3377cc", "#66a3ff"]
TOP_COLOR_DARKER = "#3377cc" 
PIE_COLORS = [TOP_COLOR_DARKER, "#205081", "#003366"]

st.markdown(f"""
<style>
    header[data-testid="stHeader"] {{ background-color: rgba(0,0,0,0) !important; }}
    .stApp {{ 
        background-color: #333333 !important; 
        background-image: url("{bg_url}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-blend-mode: luminosity !important;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.5); 
        backdrop-filter: grayscale(100%) brightness(0.4);
        z-index: 0;
    }}
    .stApp > div {{ position: relative; z-index: 1; }}
    .block-container {{ max-width: 95% !important; padding: 1rem 2rem !important; }}
    h1, h2, h3, p, label, .stMetric label, [data-testid="stMetricValue"] {{ 
        color: #FFFFFF !important; font-family: 'Arial', sans-serif !important; font-weight: bold;
    }}
    .table-container {{ display: flex; justify-content: center; width: 100%; margin-top: 20px; }}
    .rendered_html {{ width: 90% !important; }}
    .rendered_html table {{
        width: 100% !important; border-collapse: collapse; color: white !important;
        border: 2px solid {MAIN_BLUE} !important; background-color: rgba(0, 0, 0, 0.4) !important;
    }}
    .rendered_html th {{ background-color: {MAIN_BLUE} !important; color: white !important; padding: 12px !important; text-align: center !important; }}
    .rendered_html td {{ text-align: center !important; padding: 10px !important; border: 1px solid #555555 !important; }}
    
    [data-testid="stSidebar"] {{ background-color: rgba(20, 20, 20, 0.9) !important; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# --- 2. BOČNÍ MENU ---
with st.sidebar:
    if os.path.exists('logo_zlicin.png'):
        st.image('logo_zlicin.png', use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>Menu</h2>", unsafe_allow_html=True)
    page = st.radio("Přejít na:", ["📊 Analýza výsledků", "👥 Soupiska", "🖼️ Fotogalerie"])
    st.divider()
    st.info("FC Zličín | Sezóna 2025/26")

# --- 3. LOGIKA STRÁNEK ---

if page == "📊 Analýza výsledků":
    try:
        df = pd.read_csv('data.csv', sep=';', encoding='cp1250', skipinitialspace=True, dtype={'#': str})
        df.columns = [c.strip() for c in df.columns]
        if '#' in df.columns: df = df.rename(columns={'#': 'Pořadí'})
        df_num = df.copy()
        for col in ['Z', 'V', 'R', 'P', 'B', 'ŽK', 'ČK']:
            if col in df_num.columns: df_num[col] = pd.to_numeric(df_num[col], errors='coerce').fillna(0)

        c_logo_l, c_title, c_logo_r = st.columns([1, 8, 1])
        with c_logo_l:
            if os.path.exists('logo_zlicin.png'): st.image('logo_zlicin.png', width=100)
        with c_title:
            st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>FC Zličín - analýza</h1>", unsafe_allow_html=True)
            # DOPLNĚNO: Pražský přebor | Sezóna 2025/2026
            st.markdown("<p style='text-align: center; margin-top: 0;'>Pražský přebor | Sezóna 2025/2026</p>", unsafe_allow_html=True)
        with c_logo_r:
            if os.path.exists('logo_zlicin.png'): st.image('logo_zlicin.png', width=100)

        st.divider()

        z_mask = df['Klub'].str.contains("Zličín", case=False, na=False)
        if z_mask.any():
            z_n = df_num[z_mask].iloc[0]
            z_o = df[z_mask].iloc[0]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Pořadí", f"{z_o['Pořadí']}")
            m2.metric("Body", f"{int(z_n['B'])}")
            m3.metric("Skóre", f"{z_o['Skóre']}")
            m4.metric("Karty (ŽK)", f"{int(z_n['ŽK'])}")

        st.divider()
        col_bar, col_pie = st.columns([1.6, 1])
        CHART_HEIGHT = 500

        with col_bar:
            st.markdown("<h3 style='text-align: center;'>Ofenziva (G+)</h3>", unsafe_allow_html=True)
            if 'Skóre' in df.columns:
                df_num['G+'] = pd.to_numeric(df['Skóre'].str.split(':', expand=True)[0], errors='coerce')
            
            fig_bar = px.bar(df_num.sort_values("G+", ascending=True), x="G+", y="Klub", orientation='h', text="G+",
                             color="G+", color_continuous_scale=BLUE_GRADIENT)
            
            fig_bar.update_traces(
                textfont=dict(color="white", size=13),
                textposition='outside',
                textangle=0,
                cliponaxis=False
            )
            
            fig_bar.update_layout(
                font=dict(color="white"), 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False, 
                height=CHART_HEIGHT, 
                margin=dict(l=0, r=80, t=10, b=10),
                xaxis=dict(title=dict(text="Góly (G+)", font=dict(size=18)), tickfont=dict(size=14), gridcolor='#444444'),
                yaxis=dict(title=dict(text="Klub", font=dict(size=18)), tickfont=dict(size=14))
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_pie:
            st.markdown("<h3 style='text-align: center; margin-right: 80px; margin-bottom: -10px;'>Bilance výher</h3>", unsafe_allow_html=True)
            bilance = pd.DataFrame({'Výsledek': ['Výhry', 'Remízy', 'Prohry'], 'Počet': [z_n['V'], z_n['R'], z_n['P']]})
            fig_pie = px.pie(bilance, values='Počet', names='Výsledek', color_discrete_sequence=PIE_COLORS)
            fig_pie.update_traces(textinfo='percent', textposition='inside', insidetextorientation='horizontal',
                                  textfont=dict(color="white", size=18, weight='normal'))
            fig_pie.update_layout(height=CHART_HEIGHT, showlegend=True, paper_bgcolor='rgba(0,0,0,0)',
                                  legend=dict(font=dict(size=14, color="white"), orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
                                  margin=dict(l=10, r=100, t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()
        st.markdown("<h2 style='text-align: center;'>Aktuální celková tabulka</h2>", unsafe_allow_html=True)
        tab_df = df[['Pořadí', 'Klub', 'Z', 'V', 'R', 'P', 'Skóre', 'B', 'ŽK', 'ČK']].copy()
        html_table = tab_df.style.hide(axis='index').background_gradient(subset=['B'], cmap='RdYlGn').to_html()
        st.markdown(f'<div class="table-container"><div class="rendered_html">{html_table}</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Chyba při načítání dat: {e}")

elif page == "👥 Soupiska":
    st.markdown("<h1 style='text-align: center;'>Soupiska A-týmu</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sezóna 2025/2026</p>", unsafe_allow_html=True)
    st.divider()
    # Příklad soupisky
    soupiska_data = pd.DataFrame({
        "Číslo": [1, 5, 8, 10, 11],
        "Jméno": ["Petr Brankář", "Jan Obránce", "Marek Záložník", "Lukáš Útočník", "Tomáš Křídlo"],
        "Pozice": ["Brankář", "Obrana", "Záložník", "Útočník", "Útočník"],
        "Zápasy": [12, 12, 10, 12, 9],
        "Góly": [0, 1, 4, 15, 6]
    })
    html_soupiska = soupiska_data.style.hide(axis='index').to_html()
    st.markdown(f'<div class="table-container"><div class="rendered_html">{html_soupiska}</div></div>', unsafe_allow_html=True)

elif page == "🖼️ Fotogalerie":
    st.markdown("<h1 style='text-align: center;'>Fotogalerie ze zápasů</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sezóna 2025/2026</p>", unsafe_allow_html=True)
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1: st.image("https://via.placeholder.com/500x350/0056b3/FFFFFF?text=Zapas+1", caption="Vítězství nad Admirou")
    with col2: st.image("https://via.placeholder.com/500x350/0056b3/FFFFFF?text=Trenink", caption="Příprava v areálu")
    with col3: st.image("https://via.placeholder.com/500x350/0056b3/FFFFFF?text=Oslava", caption="Děkovačka s fanoušky")