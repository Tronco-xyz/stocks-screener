import streamlit as st
import yfinance as yf
import pandas as pd

# Cargar la lista de 500 acciones del S&P 500
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    return tables[0]["Symbol"].tolist()

# Parámetros iniciales
def get_rs_data(timeframes):
    tickers = get_sp500_tickers()
    tickers = [t.replace(".", "-") for t in tickers]  # Yahoo usa '-' en lugar de '.'
    tickers.append("^GSPC")  # Agregar el S&P 500

    # Descargar datos históricos
    try:
        data = yf.download(tickers, period="6mo")['Close']
    except Exception as e:
        st.error(f"Error al descargar datos: {e}")
        return pd.DataFrame()
    
    if "^GSPC" not in data.columns:
        st.error("No se pudo obtener datos del S&P 500.")
        return pd.DataFrame()

    sp500_prices = data["^GSPC"].fillna(method='ffill')  # Rellenar valores faltantes
    data = data.drop(columns=["^GSPC"], errors='ignore').fillna(method='ffill')

    # Calcular RS
    rs_data = {}
    for label, days in timeframes.items():
        if len(data) < days:
            st.warning(f"No hay suficientes datos para el timeframe {label}")
            continue
        rs = data.iloc[-days:] / sp500_prices.iloc[-days:]  # RS = Precio stock / Precio S&P 500
        rs_data[label] = rs.mean()
    
    return pd.DataFrame(rs_data).dropna()

# Interfaz en Streamlit
st.title("Stock Screener - Relative Strength")
st.write("Este screener calcula la fuerza relativa de acciones en base a 3 timeframes editables.")

# Configuración de timeframes
timeframes = {
    "6m": st.slider("Días para 6 meses", min_value=60, max_value=150, value=126),
    "3m": st.slider("Días para 3 meses", min_value=30, max_value=90, value=63),
    "10d": st.slider("Días para 10 días", min_value=5, max_value=20, value=10)
}

if st.button("Ejecutar Screener"):
    st.write("Obteniendo datos... Esto puede tardar unos segundos.")
    rs_data = get_rs_data(timeframes)
    
    if not rs_data.empty:
        # Ordenar por promedio ponderado (3m y 6m con doble peso)
        rs_data["Weighted RS"] = (rs_data.get("6m", 0) * 2 + rs_data.get("3m", 0) * 2 + rs_data.get("10d", 0)) / 5
        rs_data = rs_data.sort_values(by="Weighted RS", ascending=False)
        st.dataframe(rs_data)
    else:
        st.error("No se encontraron datos válidos.")
