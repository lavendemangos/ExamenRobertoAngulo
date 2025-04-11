import streamlit as st
import yfinance as yf
import altair as alt
import pandas as pd
import google.generativeai as genai
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pandas.tseries.offsets import DateOffset
import re

st.set_page_config(page_title="Buscador de Empresas", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #1e1e2f;
        color: #ddddff;
    }
    .stButton>button {
        background-color: #6A0DAD;
        color: white;
    }
    .stSelectbox>div>div>div {
        color: black;
    }
    .big-text {
        font-size: 1.5em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def obtener_datos(symbol, intervalo):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=intervalo).reset_index()
    hist["Date"] = pd.to_datetime(hist["Date"]).dt.tz_localize(None)
    info = ticker.get_info()
    return hist, info

def traducir_texto(info):
    descripcion = info.get("longBusinessSummary", "NA")
    sector = info.get("sector", "NA")
    industria = info.get("industry", "NA")
    pais = info.get("country", "NA")

    texto_para_traducir = (
        f"Descripción:\n{descripcion}\n\nSector: {sector}\nIndustria: {industria}\nPaís: {pais}"
    )
    prompt_completo = (
        "Traduce al español de forma clara, profesional y sin encabezados el siguiente texto técnico sobre una empresa. "
        "Incluye la descripción y un resumen, muestra el sector, la industria y el país: en un texto a parte\n\n"
        + texto_para_traducir
    )
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        genai.configure(api_key="AIzaSyAt3B4Xa7FRqbreSwXrEWnbHtMWW-O4EqI")
        respuesta_completa = model.generate_content(prompt_completo)
        return respuesta_completa.text
    except Exception:
        return (
            "⚠️ No se pudo traducir la información debido a un límite de uso en la API de Gemini.\n\n"
            "Por favor, intente más tarde o revise su cuota de uso en: https://ai.google.dev/gemini-api/docs/rate-limits"
        )

def calcular_cagr(precio_inicio, precio_final, anios):
    if precio_inicio > 0 and anios > 0:
        return (precio_final / precio_inicio) ** (1 / anios) - 1
    return None

# ====== Sidebar - Inputs ======
with st.sidebar:
    symbol = st.text_input("Símbolo de la acción (ej. AAPL)", placeholder="Buscar...")
    intervalo = st.selectbox("Intervalo de precios:", ["6mo", "1y", "5y", "max"])
    usar_velas = st.checkbox("Mostrar gráfico de velas")
    buscar = st.button("Buscar")

# ====== Título principal ======
st.markdown("<h1 style='text-align:center; color:#6A0DAD;'>Buscador de Acciones del Mercado</h1>", unsafe_allow_html=True)
st.divider()

# ====== Lógica principal ======
if buscar and symbol.strip():
    symbol_upper = symbol.strip().upper()

    if not re.match("^[A-Z.]{1,5}$", symbol_upper):
        st.error("Símbolo no válido.")
    else:
        with st.spinner("🔄 Consultando y procesando datos..."):
            try:
                hist, info = obtener_datos(symbol_upper, intervalo)

                if not info or info.get("regularMarketPrice") is None:
                    st.error("❌ Ticker inválido. Por favor revise e intente de nuevo.")
                else:
                    nombre_largo = info.get("longName", "NA")
                    previous_close = info.get("previousClose", "NA")
                    open_price = info.get("open", "NA")
                    current_price = info.get("regularMarketPrice", "NA")
                    beta = info.get("beta", "NA")
                    texto_traducido = traducir_texto(info)

                    with st.container():
                        st.header("📋 Información General")
                        st.markdown(f"## {nombre_largo}")
                        st.markdown(f"**Información traducida:**\n\n{texto_traducido}")
                        st.subheader("📉 Datos clave")
                        st.markdown(f"<div class='big-text'>- <strong>Precio anterior de cierre:</strong> ${previous_close} USD</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='big-text'>- <strong>Precio de apertura:</strong> ${open_price} USD</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='big-text'>- <strong>Precio actual:</strong> ${current_price} USD</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='big-text'>- <strong>Beta (riesgo relativo):</strong> {beta}</div>", unsafe_allow_html=True)
                        st.divider()

                    with st.container():
                        st.header("📈 Historial de Precios")
                        hist["MA20"] = hist["Close"].rolling(window=20).mean()
                        hist["UpperBB"] = hist["MA20"] + 2 * hist["Close"].rolling(window=20).std()
                        hist["LowerBB"] = hist["MA20"] - 2 * hist["Close"].rolling(window=20).std()

                        hist_spy = yf.Ticker("SPY").history(start=hist["Date"].min(), end=hist["Date"].max()).reset_index()
                        hist_spy["Date"] = pd.to_datetime(hist_spy["Date"]).dt.tz_localize(None)
                        hist["NormClose"] = hist["Close"] / hist["Close"].iloc[0] * 100
                        hist_spy["NormClose"] = hist_spy["Close"] / hist_spy["Close"].iloc[0] * 100

                        if usar_velas:
                            fig = go.Figure(data=[go.Candlestick(
                                x=hist["Date"], open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"]
                            )])
                            fig.update_layout(height=400, xaxis_rangeslider_visible=False)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            linea_ticker = alt.Chart(hist).mark_line().encode(
                                x="Date:T",
                                y=alt.Y("NormClose:Q", title="Precio Normalizado"),
                                color=alt.value("#6A0DAD"),
                                tooltip=["Date:T", alt.Tooltip("NormClose:Q", title=symbol_upper)]
                            ).properties(title=f"{symbol_upper} (Línea morada)")

                            linea_spy = alt.Chart(hist_spy).mark_line(strokeDash=[5, 3], color="gray").encode(
                                x="Date:T",
                                y=alt.Y("NormClose:Q"),
                                tooltip=["Date:T", alt.Tooltip("NormClose:Q", title="SPY")]
                            ).properties(title="SPY (Línea gris punteada)")

                            barras = alt.Chart(hist).mark_bar(opacity=0.3).encode(
                                x="Date:T",
                                y=alt.Y("Volume:Q", title="Volumen"),
                                tooltip=["Date:T", "Volume:Q"]
                            ).properties(height=100)

                            chart = (linea_ticker + linea_spy).properties(
                                height=300, title="Comparación de Rendimiento Normalizado: Ticker vs SP500"
                            ) & barras

                            st.altair_chart(chart, use_container_width=True)

                        st.divider()

                    with st.container():
                        st.header("📊 Métricas de Desempeño")
                        hoy = hist["Date"].max()
                        rendimiento = {"Periodo": ["1 mes", "3 meses", "YTD", "1 año", "3 años", "5 años"], "Rendimiento": []}
                        fechas_inicio = {
                            "1 mes": hoy - pd.DateOffset(months=1),
                            "3 meses": hoy - pd.DateOffset(months=3),
                            "YTD": datetime(hoy.year, 1, 1),
                            "1 año": hoy - pd.DateOffset(years=1),
                            "3 años": hoy - pd.DateOffset(years=3),
                            "5 años": hoy - pd.DateOffset(years=5),
                        }
                        for periodo, inicio in fechas_inicio.items():
                            datos = hist[hist["Date"] >= inicio]
                            if not datos.empty:
                                ret = (datos["Close"].iloc[-1] - datos["Close"].iloc[0]) / datos["Close"].iloc[0] * 100
                                rendimiento["Rendimiento"].append(f"{ret:.2f}%")
                            else:
                                rendimiento["Rendimiento"].append("N/D")
                        st.subheader("📆 Rendimiento Histórico")
                        st.dataframe(pd.DataFrame(rendimiento), use_container_width=True)

                        st.markdown("""
#### ℹ️ ¿Qué es el **CAGR**?
El CAGR (*Compound Annual Growth Rate* o **Tasa de Crecimiento Anual Compuesto**) representa el crecimiento promedio anual de una inversión durante un periodo específico, como si hubiera crecido a una tasa constante cada año. Es útil para evaluar el rendimiento a largo plazo de una acción, eliminando fluctuaciones interanuales.
""", unsafe_allow_html=True)

                        st.subheader("📈 CAGR (Crecimiento Anual Compuesto)")
                        cagr_data = {"Periodo": [], "CAGR": []}
                        for anios in [1, 3, 5]:
                            inicio = hoy - pd.DateOffset(years=anios)
                            datos = hist[hist["Date"] >= inicio]
                            if not datos.empty:
                                cagr = calcular_cagr(datos["Close"].iloc[0], datos["Close"].iloc[-1], anios)
                                cagr_data["Periodo"].append(f"{anios} años")
                                cagr_data["CAGR"].append(f"{cagr * 100:.2f}%" if cagr else "N/D")
                            else:
                                cagr_data["Periodo"].append(f"{anios} años")
                                cagr_data["CAGR"].append("N/D")
                        st.dataframe(pd.DataFrame(cagr_data), use_container_width=True)

                        st.markdown("""
#### ℹ️ ¿Qué es la **Volatilidad Anualizada**?
La volatilidad anualizada mide cuánto varían los precios de una acción en promedio durante un año. Es una medida del **riesgo**: cuanto mayor es la volatilidad, más incierto es el comportamiento futuro del precio.
""", unsafe_allow_html=True)

                        st.subheader("📉 Volatilidad Anualizada")
                        rendimientos = hist["Close"].pct_change().dropna()
                        volatilidad = np.std(rendimientos) * np.sqrt(252)
                        st.metric("Volatilidad anual", f"{volatilidad * 100:.2f}%")

            except Exception as e:
                st.error(f"No se pudo obtener la información. Error: {str(e)}")
else:
    st.info("Ingresa un símbolo para comenzar la búsqueda.")