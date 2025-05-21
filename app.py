import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz

# Configuração do fuso horário de Goiânia (UTC-3)
GOIANIA_TZ = pytz.timezone('America/Sao_Paulo')

# Configuração da NASA API
NASA_API_KEY = "snngNMZnw1hqXpKEndt1Ggodg7Ld3FgthI9XlwpJ"  # Substitua por sua chave da NASA API

# Configuração do Streamlit
st.set_page_config(page_title="Dashboard Astronômico", layout="wide")
st.title("Dashboard Astronômico em Tempo Real")

# Função para buscar dados (NASA APOD + simulados)
@st.cache_data(ttl=60)
def fetch_astronomy_data():
    try:
        # Buscar dados da NASA APOD
        response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}")
        response.raise_for_status()  # Levanta erro para status != 200
        apod = response.json()

        # Usar horário de Goiânia
        now = datetime.now(GOIANIA_TZ)
        
        # Dados simulados para atividade solar
        solar_data = [
            {"time": (now - timedelta(hours=23-i)).strftime("%H:%M"), "xray_flux": 0.0001 * (i % 5 + 1 + (0.1 * i))}
            for i in range(24)
        ]
        
        return {
            "hubble": {
                "target": apod.get("title", "NGC 1234 (Galáxia Espiral)"),  # Título da imagem do dia
                "time": apod.get("date", now.strftime("%Y-%m-%d")) + " " + now.strftime("%H:%M:%S %Z")
            },
            "webb": {"target": "Cosmos Redshift 7", "time": now.strftime("%Y-%m-%d %H:%M:%S %Z")},
            "solar_activity": solar_data
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados da NASA API: {e}")
        # Dados de fallback
        now = datetime.now(GOIANIA_TZ)
        solar_data = [
            {"time": (now - timedelta(hours=23-i)).strftime("%H:%M"), "xray_flux": 0.0001 * (i % 5 + 1 + (0.1 * i))}
            for i in range(24)
        ]
        return {
            "hubble": {"target": "NGC 1234 (Galáxia Espiral)", "time": now.strftime("%Y-%m-%d %H:%M:%S %Z")},
            "webb": {"target": "Cosmos Redshift 7", "time": now.strftime("%Y-%m-%d %H:%M:%S %Z")},
            "solar_activity": solar_data
        }

# Função para criar o gráfico de atividade solar
def plot_solar_activity(solar_data):
    df = pd.DataFrame(solar_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["xray_flux"],
        mode="lines+markers",
        name="Fluxo de Raios X (W/m²)",
        line=dict(color="#38bdf8")
    ))
    fig.update_layout(
        title="Atividade Solar (Últimas 24 Horas)",
        xaxis_title="Hora (Goiânia, UTC-3)",
        yaxis_title="Fluxo de Raios X (W/m²)",
        template="plotly_dark",
        height=400
    )
    return fig

# Interface do dashboard
st.write("Carregando dashboard... Clique em 'Atualizar Dados' para exibir as informações.")
if st.button("Atualizar Dados"):
    data = fetch_astronomy_data()
    if data:
        st.subheader("Observações Atuais dos Telescópios")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Hubble - Alvo:** {data['hubble']['target']}")
            st.markdown(f"**Hora:** {data['hubble']['time']}")
        with col2:
            st.markdown(f"**Webb - Alvo:** {data['webb']['target']}")
            st.markdown(f"**Hora:** {data['webb']['time']}")
        
        fig = plot_solar_activity(data["solar_activity"])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"**Última atualização:** {datetime.now(GOIANIA_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        st.error("Falha ao carregar dados. Tente novamente.")
else:
    st.info("Clique em 'Atualizar Dados' para carregar o dashboard.")
