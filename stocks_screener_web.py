import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import rankdata

# Stock ticker list
stock_symbols = [
    "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A", "APD", "ABNB", "AKAM",
    "ALB", "ARE", "ALGN", "ALLE", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AEP",
    "AXP", "AIG", "AMT", "AWK", "AMP", "AME", "AMGN", "APH", "ADI", "ANSS", "AON", "APA", "APO",
    "AAPL", "AMAT", "APTV", "ACGL", "ADM", "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO",
    "AVB", "AVY", "AXON", "BKR", "BALL", "BAC", "BAX", "BDX", "BRK.B", "BBY", "TECH", "BIIB", "BLK",
    "BX", "BK", "BA", "BKNG", "BWA", "BSX", "BMY", "AVGO", "BR", "BRO", "BF.B", "BLDR", "BG", "BXP",
    "CHRW", "CDNS", "CZR", "CPT", "CPB", "COF", "CAH", "KMX", "CCL", "CARR", "CAT", "CBOE", "CBRE",
    "CDW", "CE", "COR", "CNC", "CNP", "CF", "CRL", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI",
    "CINF", "CTAS", "CSCO", "C", "CFG", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CAG", "COP",
    "ED", "STZ", "CEG", "COO", "CPRT", "GLW", "CPAY", "CTVA", "CSGP", "COST", "CTRA", "CRWD", "CCI",
    "CSX", "CMI", "CVS", "DHR", "DRI", "DVA", "DAY", "DECK", "DE", "DELL", "DAL", "DVN", "DXCM",
    "FANG", "DLR", "DFS", "DG", "DLTR", "D", "DPZ", "DOV", "DOW", "DHI", "DTE", "DUK", "DD", "EMN",
    "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "ELV", "EMR", "ENPH", "ETR", "EOG", "EPAM", "EQT",
    "EFX", "EQIX", "EQR", "ERIE", "ESS", "EL", "EG", "EVRG", "ES", "EXC", "EXPE", "EXPD", "EXR",
    "XOM", "FFIV", "FDS", "FICO", "FAST", "FRT", "FDX", "FIS", "FITB", "FSLR", "FE", "FI", "FMC",
    "F", "FTNT", "FTV", "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT", "GE", "GEHC", "GEV", "GEN",
    "GNRC", "GD", "GIS", "GM", "GPC", "GILD", "GPN", "GL", "GDDY", "GS", "HAL", "HIG", "HAS",
    "HCA", "DOC", "HSIC", "HSY", "HES", "HPE", "HLT", "HOLX", "HD", "HON", "HRL", "HST", "HWM",
    "HPQ", "HUBB", "HUM", "HBAN", "HII", "IBM", "IEX", "IDXX", "ITW", "INCY", "IR", "PODD",
    "INTC", "ICE", "IFF", "IP", "IPG", "INTU", "ISRG", "IVZ", "INVH", "IQV", "IRM", "JBHT",
    "JBL", "JKHY", "J", "JNJ", "JCI", "JPM", "JNPR", "K", "KVUE", "KDP", "KEY", "KEYS", "KMB",
    "KIM", "KMI", "KKR", "KLAC", "KHC", "KR", "LHX", "LH", "LRCX", "LW", "LVS", "LDOS", "LEN",
    "LII", "LLY", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LULU", "LYB", "MTB", "MPC", "MKTX",
    "MAR", "MMC", "MLM", "MAS", "MA", "MTCH", "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET",
    "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MRNA", "MHK", "MOH", "TAP", "MDLZ", "MPWR",
    "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP", "NFLX", "NEM", "NWSA", "NWS",
    "NEE", "NKE", "NI", "NDSN", "NSC", "NTRS", "NOC", "NCLH", "NRG", "NUE", "NVDA", "NVR",
    "NXPI", "ORLY", "OXY", "ODFL", "OMC", "ON", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PLTR",
    "PANW", "PARA", "PH", "PAYX", "PAYC", "PYPL", "PNR", "PEP", "PFE", "PCG", "PM", "PSX",
    "PNW", "PNC", "POOL", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PTC", "PSA",
    "PHM", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD",
    "RVTY", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SRE",
    "NOW", "SHW", "SPG", "SWKS", "SJM", "SW", "SNA", "SOLV", "SO", "LUV", "SWK", "SBUX",
    "STT", "STLD", "STE", "SYK", "SMCI", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO",
    "TPR", "TRGP", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA", "TXN", "TPL", "TXT", "TMO",
    "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC", "TYL", "TSN", "USB", "UBER", "UDR",
    "ULTA", "UNP", "UAL", "UPS", "URI", "UNH", "UHS", "VLO", "VTR", "VRSN", "VRSK", "VZ",
    "VRTX", "VICI", "V", "VST", "VMC", "WRB", "GWW", "WAB", "WBA", "WMT", "DIS", "WBD",
    "WM", "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WY", "WMB", "WTW", "WDAY", "WYNN",
    "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZTS"
]

# Replace ETF symbols with stock symbols
etf_symbols = stock_symbols


# Streamlit UI
st.title("SP500 Stocks Screener & RS Ranking")
st.write("Live Stocks ranking based on relative strength.")

# Fetch historical price data from Yahoo Finance
st.write("Fetching latest data...")
etf_data = yf.download(etf_symbols, period="1y", interval="1d")
if etf_data.empty:
    st.error("Yahoo Finance returned empty data. Check ETF symbols and API limits.")
    st.stop()

# Extract 'Close' prices
if isinstance(etf_data.columns, pd.MultiIndex):
    etf_data = etf_data['Close']

# Ensure ETFs have enough data
available_days = etf_data.count()
max_days = available_days.max()

# Adjust 12M lookback dynamically
lookback_periods = {"12M": min(252, max_days), "3M": 63, "1M": 21, "1W": 5}

valid_etfs = [etf for etf in etf_data.columns if available_days[etf] >= 63]
etf_data = etf_data[valid_etfs]

# Calculate performance over available periods
performance = {}
for period, days in lookback_periods.items():
    performance[period] = {
        etf: round(((etf_data[etf].iloc[-1] - etf_data[etf].iloc[-days]) / etf_data[etf].iloc[-days] * 100), 2)
        if available_days[etf] >= days else np.nan for etf in valid_etfs
    }

performance_df = pd.DataFrame(performance)

# Calculate moving averages
ma_200 = etf_data.rolling(window=200).mean()
ma_50 = etf_data.rolling(window=50).mean()
ema_5 = etf_data.ewm(span=5, adjust=False).mean()
ema_20 = etf_data.ewm(span=20, adjust=False).mean()

# Determine if price is above or below 200-day & 50-day MA
above_ma_200 = etf_data.iloc[-1] > ma_200.iloc[-1]
above_ma_50 = etf_data.iloc[-1] > ma_50.iloc[-1]
ema_trend = pd.Series(np.where(ema_5.iloc[-1] > ema_20.iloc[-1], "EMA 5 > EMA 20", "EMA 5 < EMA 20"), index=valid_etfs)

# Calculate RS Rankings (percentile-based scores from 1-99)
rs_ratings = {}
for period in lookback_periods.keys():
    valid_performance = performance_df[period].dropna()
    ranked = rankdata(valid_performance, method="average") / len(valid_performance) * 99
    rs_ratings[period] = dict(zip(valid_performance.index, np.round(ranked, 2)))

rs_ratings_df = pd.DataFrame(rs_ratings, index=performance_df.index).fillna(np.nan)

# Add filters
st.sidebar.header("Filters")
filter_rs_12m = st.sidebar.checkbox("RS 12M > 80")
filter_above_ma_200 = st.sidebar.checkbox("Above 200 MA")
filter_above_ma_50 = st.sidebar.checkbox("Above 50 MA")
filter_ema_trend = st.sidebar.checkbox("EMA 5 > EMA 20")

# Store results in a DataFrame
etf_ranking = pd.DataFrame({
    "ETF": performance_df.index,
    "RS Rating 12M": rs_ratings_df["12M"].tolist(),
    "RS Rating 3M": rs_ratings_df["3M"].tolist(),
    "RS Rating 1M": rs_ratings_df["1M"].tolist(),
    "RS Rating 1W": rs_ratings_df["1W"].tolist(),
    "Above 200 MA": above_ma_200.reindex(performance_df.index).fillna(False).tolist(),
    "Above 50 MA": above_ma_50.reindex(performance_df.index).fillna(False).tolist(),
    "EMA Trend": ema_trend.reindex(performance_df.index).fillna("Unknown").tolist()
})

# Apply filters
if filter_rs_12m:
    etf_ranking = etf_ranking[etf_ranking["RS Rating 12M"] > 80]
if filter_above_ma_200:
    etf_ranking = etf_ranking[etf_ranking["Above 200 MA"]]
if filter_above_ma_50:
    etf_ranking = etf_ranking[etf_ranking["Above 50 MA"]]
if filter_ema_trend:
    etf_ranking = etf_ranking[etf_ranking["EMA Trend"] == "EMA 5 > EMA 20"]

# Add performance metrics at the end
performance_columns = ["12M Performance (%)", "3M Performance (%)", "1M Performance (%)", "1W Performance (%)"]
for col in performance_columns:
 if col.replace(" Performance (%)", "") in performance_df.columns:
    etf_ranking[col] = performance_df[col.replace(" Performance (%)", "")].reindex(etf_ranking.index).tolist()


# Display ETF Rankings in Streamlit
st.dataframe(etf_ranking.sort_values(by="RS Rating 12M", ascending=False))

# Download Button
st.download_button(
    label="Download CSV",
    data=etf_ranking.to_csv(index=False),
    file_name="etf_ranking.csv",
    mime="text/csv"
)
