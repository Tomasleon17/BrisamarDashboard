# =========================================================
# BRISAMAR INVESTMENTS
# INSTITUTIONAL PORTFOLIO DASHBOARD
# VERSION 3.0
# =========================================================

# =========================================================
# LIBRERÍAS
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

from scipy.stats import norm
from datetime import datetime
import pytz

# =========================================================
# CONFIGURACIÓN STREAMLIT
# =========================================================

st.set_page_config(
    page_title="Brisamar Investments",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS INSTITUCIONAL
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

html, body, [class*="css"] {
    background-color: #0B0F19;
    color: white;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.metric-card {
    background-color: #151B28;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #2A3245;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.35);
}

.metric-title {
    color: #9CA3AF;
    font-size: 13px;
}

.metric-value {
    color: white;
    font-size: 34px;
    font-weight: bold;
}

.metric-positive {
    color: #22C55E;
    font-size: 14px;
    font-weight: bold;
}

.metric-negative {
    color: #EF4444;
    font-size: 14px;
    font-weight: bold;
}

.metric-warning {
    color: #EAB308;
    font-size: 14px;
    font-weight: bold;
}

.alert-green {
    background-color: rgba(34,197,94,0.15);
    padding: 16px;
    border-radius: 12px;
    border-left: 6px solid #22C55E;
    margin-bottom: 12px;
}

.alert-yellow {
    background-color: rgba(234,179,8,0.15);
    padding: 16px;
    border-radius: 12px;
    border-left: 6px solid #EAB308;
    margin-bottom: 12px;
}

.alert-red {
    background-color: rgba(239,68,68,0.15);
    padding: 16px;
    border-radius: 12px;
    border-left: 6px solid #EF4444;
    margin-bottom: 12px;
}

.title-main {
    font-size: 44px;
    font-weight: bold;
    color: white;
}

.subtitle-main {
    color: #9CA3AF;
    font-size: 18px;
}

hr {
    border: 1px solid #222B3A;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("BRISAMAR")
st.sidebar.caption("Monitoreo Cuantitativo de Portafolio")

pagina = st.sidebar.radio(
    "Navegación",
    [
        "Dashboard Ejecutivo",
        "Motor de Riesgo",
        "Asignación de Activos",
        "Monitoreo IPS"
    ]
)

st.sidebar.divider()

# =========================================================
# HORARIO CHILE
# =========================================================

chile_tz = pytz.timezone("America/Santiago")
now_chile = datetime.now(chile_tz)

market_open = now_chile.replace(
    hour=10,
    minute=30,
    second=0
)

market_close = now_chile.replace(
    hour=17,
    minute=0,
    second=0
)

market_is_open = (
    market_open <= now_chile <= market_close
)

if now_chile.weekday() >= 5:
    market_is_open = False

st.sidebar.markdown("## 🌎 Mercados Operativos")

st.sidebar.markdown("""
NYSE  
NASDAQ  
NYSE ARCA  
US ETF MARKET
""")

if market_is_open:
    st.sidebar.success("🟢 MERCADO ABIERTO")
else:
    st.sidebar.error("🔴 MERCADO CERRADO")

st.sidebar.markdown("""
**Horario Mercado Chile**  
10:30 → 17:00
""")

st.sidebar.markdown(f"""
**Hora Actual Chile**  
{now_chile.strftime("%H:%M:%S")}
""")

st.sidebar.divider()

# =========================================================
# PORTAFOLIO ACTUAL BRISAMAR
# =========================================================

positions = {

    # ====================================
    # EQUITY
    # ====================================

    "SPY": 181.8131,
    "CB": 54.3421,
    "NSC": 54.2301,
    "UNP": 62.5444,
    "VICI": 603.3692,
    "ADBE": 67.6656,

    # ====================================
    # ALTERNATIVOS
    # ====================================

    "GLD": 80.5246,

    # ====================================
    # FIXED INCOME ETF
    # ====================================

    "AGG": 1414.8007

}

benchmark = "SPY"

# =========================================================
# CASH REAL
# =========================================================

cash_balance = 831.49

# =========================================================
# COST BASIS
# =========================================================

cost_basis = {

    "SPY": 710.45,
    "CB": 324.69,
    "NSC": 318.00,
    "UNP": 272.00,
    "VICI": 28.02,
    "ADBE": 248.19,
    "GLD": 430.70,
    "AGG": 99.56
}

# =========================================================
# DESCARGA DATOS
# =========================================================

tickers = list(positions.keys())

data = yf.download(
    tickers,
    period="1y",
    interval="1d",
    auto_adjust=True,
    progress=False
)

prices = data["Close"].dropna()

latest_prices = prices.iloc[-1]

returns = prices.pct_change().dropna()

# =========================================================
# MARKET VALUES
# =========================================================

market_values = {}

for ticker in positions:

    market_values[ticker] = (
        positions[ticker] *
        latest_prices[ticker]
    )

# =========================================================
# TOTAL EQUITY
# =========================================================

portfolio_market_value = sum(market_values.values())

portfolio_value = (
    portfolio_market_value +
    cash_balance
)

# =========================================================
# WEIGHTS REALES
# =========================================================

weights = []

for ticker in positions:

    weight = (
        market_values[ticker] /
        portfolio_market_value
    )

    weights.append(weight)

weights = np.array(weights)

# =========================================================
# RETORNOS PORTAFOLIO
# =========================================================

returns = returns[tickers]

portfolio_returns = returns.dot(weights)

benchmark_returns = returns[benchmark]

active_returns = (
    portfolio_returns -
    benchmark_returns
)

# =========================================================
# MÉTRICAS IPS
# =========================================================

tracking_error = (
    np.std(active_returns) *
    np.sqrt(252)
)

information_ratio = (
    np.mean(active_returns) /
    np.std(active_returns)
) * np.sqrt(252)

portfolio_volatility = (
    np.std(portfolio_returns) *
    np.sqrt(252)
)

sharpe_ratio = (
    np.mean(portfolio_returns) /
    np.std(portfolio_returns)
) * np.sqrt(252)

beta = np.cov(
    portfolio_returns,
    benchmark_returns
)[0][1] / np.var(benchmark_returns)

alpha = (
    np.mean(portfolio_returns) -
    beta * np.mean(benchmark_returns)
) * 252

# =========================================================
# VAR 95
# =========================================================

confidence = 0.95

var_95 = (
    norm.ppf(1 - confidence) *
    np.std(portfolio_returns) *
    np.sqrt(252)
)

# =========================================================
# DRAWDOWN
# =========================================================

cumulative_returns = (
    1 + portfolio_returns
).cumprod()

rolling_max = cumulative_returns.cummax()

drawdown = (
    cumulative_returns -
    rolling_max
) / rolling_max

max_drawdown = drawdown.min()

# =========================================================
# ROLLING TRACKING ERROR
# =========================================================

rolling_te = (
    active_returns
    .rolling(30)
    .std()
) * np.sqrt(252)

# =========================================================
# DAILY RETURN
# =========================================================

daily_return = portfolio_returns.iloc[-1]

# =========================================================
# IPS LOGIC
# =========================================================

if tracking_error > 0.06:

    rebalance_signal = "🔴 REBALANCEO REQUERIDO"
    rebalance_class = "alert-red"

elif tracking_error < 0.02:

    rebalance_signal = "🟡 PORTAFOLIO DEMASIADO PASIVO"
    rebalance_class = "alert-yellow"

else:

    rebalance_signal = "🟢 IPS DENTRO DEL RANGO OBJETIVO"
    rebalance_class = "alert-green"

# =========================================================
# STATUS GENERAL
# =========================================================

if tracking_error <= 0.06 and abs(max_drawdown) < 0.10:

    portfolio_status = """
    <div class="alert-green">
    🟢 PORTAFOLIO STATUS — HEALTHY
    </div>
    """

else:

    portfolio_status = """
    <div class="alert-yellow">
    ⚠️ PORTAFOLIO STATUS — RISK ELEVATED
    </div>
    """

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="title-main">
📈 BRISAMAR INVESTMENTS
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle-main">
Generando alfa consistente mediante una gestión disciplinada y controlada del riesgo.
</div>
""", unsafe_allow_html=True)

st.write("")

st.markdown(
    portfolio_status,
    unsafe_allow_html=True
)

# =========================================================
# KPI ROW
# =========================================================

col1, col2, col3, col4, col5 = st.columns(5)

# =========================================================
# PORTFOLIO VALUE
# =========================================================

with col1:

    daily_color = (
        "metric-positive"
        if daily_return >= 0
        else "metric-negative"
    )

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-title">
        Valor Portafolio
        </div>

        <div class="metric-value">
        ${portfolio_value:,.0f}
        </div>

        <div class="{daily_color}">
        {daily_return:.2%}
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TRACKING ERROR
# =========================================================

with col2:

    te_color = (
        "metric-positive"
        if tracking_error <= 0.06
        else "metric-negative"
    )

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-title">
        Tracking Error
        </div>

        <div class="metric-value">
        {tracking_error:.2%}
        </div>

        <div class="{te_color}">
        Monitoreo IPS
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# INFORMATION RATIO
# =========================================================

with col3:

    ir_color = (
        "metric-positive"
        if information_ratio >= 0
        else "metric-negative"
    )

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-title">
        Information Ratio
        </div>

        <div class="metric-value">
        {information_ratio:.2f}
        </div>

        <div class="{ir_color}">
        Gestión Activa
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ALPHA
# =========================================================

with col4:

    alpha_color = (
        "metric-positive"
        if alpha >= 0
        else "metric-negative"
    )

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-title">
        Jensen Alpha
        </div>

        <div class="metric-value">
        {alpha:.2%}
        </div>

        <div class="{alpha_color}">
        Generación de Alfa
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# DRAWDOWN
# =========================================================

with col5:

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-title">
        Max Drawdown
        </div>

        <div class="metric-value">
        {max_drawdown:.2%}
        </div>

        <div class="metric-negative">
        Control de Riesgo
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ALERTAS
# =========================================================

st.write("")

st.markdown(f"""
<div class="{rebalance_class}">
{rebalance_signal}
</div>
""", unsafe_allow_html=True)

if portfolio_volatility > 0.20:

    st.markdown("""
    <div class="alert-red">
    ⚠️ La volatilidad del portafolio excede el objetivo estratégico.
    </div>
    """, unsafe_allow_html=True)

if abs(max_drawdown) > 0.10:

    st.markdown("""
    <div class="alert-yellow">
    ⚠️ El drawdown excede la tolerancia preferida.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="alert-green">
💰 Monitoreando oportunidades de captura de alfa.
</div>
""", unsafe_allow_html=True)

# =========================================================
# PERFORMANCE + ASSET ALLOCATION
# =========================================================

st.divider()

left, right = st.columns((2,1))

# =========================================================
# PERFORMANCE
# =========================================================

with left:

    perf_df = pd.DataFrame({

        "Portafolio": cumulative_returns,

        "Benchmark": (
            1 + benchmark_returns
        ).cumprod()

    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=perf_df.index,
        y=perf_df["Portafolio"],
        mode='lines',
        name='Portafolio',
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=perf_df.index,
        y=perf_df["Benchmark"],
        mode='lines',
        name='Benchmark',
        line=dict(width=2, dash='dash')
    ))

    fig.update_layout(
        title="Portafolio vs Benchmark",
        template="plotly_dark",
        height=500,
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# ASSET ALLOCATION
# =========================================================

with right:

    asset_classes = {

        "Renta Variable": 0.68,
        "Alternativos": 0.07,
        "Renta Fija": 0.25

    }

    allocation_df = pd.DataFrame({

        "Clase": asset_classes.keys(),
        "Peso": asset_classes.values()

    })

    fig2 = px.pie(
        allocation_df,
        values="Peso",
        names="Clase",
        hole=0.55
    )

    fig2.update_layout(
        title="Asignación de Activos",
        template="plotly_dark",
        height=500,
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# TRACKING ERROR
# =========================================================

st.divider()

fig_te = go.Figure()

fig_te.add_trace(go.Scatter(
    x=rolling_te.index,
    y=rolling_te,
    mode='lines',
    name='Rolling TE',
    line=dict(width=3)
))

fig_te.add_hrect(
    y0=0,
    y1=0.02,
    fillcolor="yellow",
    opacity=0.12,
    line_width=0
)

fig_te.add_hrect(
    y0=0.02,
    y1=0.06,
    fillcolor="green",
    opacity=0.12,
    line_width=0
)

fig_te.add_hrect(
    y0=0.06,
    y1=0.20,
    fillcolor="red",
    opacity=0.12,
    line_width=0
)

fig_te.update_layout(
    title="Rolling Tracking Error",
    template="plotly_dark",
    height=400,
    paper_bgcolor="#0B0F19",
    plot_bgcolor="#0B0F19"
)

st.plotly_chart(
    fig_te,
    use_container_width=True
)

# =========================================================
# DRAWDOWN
# =========================================================

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=drawdown.index,
    y=drawdown,
    fill='tozeroy',
    mode='lines',
    name='Drawdown',
    line=dict(color='red')
))

fig3.update_layout(
    title="Drawdown del Portafolio",
    template="plotly_dark",
    height=400,
    paper_bgcolor="#0B0F19",
    plot_bgcolor="#0B0F19"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================================
# TABLA HOLDINGS
# =========================================================

st.divider()

st.subheader("Holdings Actuales")

holdings_df = pd.DataFrame({

    "Ticker": positions.keys(),

    "Cantidad": [
        round(v,2)
        for v in positions.values()
    ],

    "Precio Actual": [
        round(latest_prices[t],2)
        for t in positions.keys()
    ],

    "Market Value": [
        round(market_values[t],2)
        for t in positions.keys()
    ],

    "Peso": [

        f"{(market_values[t]/portfolio_market_value):.2%}"

        for t in positions.keys()
    ]
})

st.dataframe(
    holdings_df,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# TABLA MÉTRICAS
# =========================================================

st.divider()

st.subheader("Monitoreo de Riesgo")

risk_df = pd.DataFrame({

    "Métrica": [

        "Tracking Error",
        "Information Ratio",
        "Sharpe Ratio",
        "Jensen Alpha",
        "Beta",
        "VaR 95%",
        "Max Drawdown"

    ],

    "Valor": [

        f"{tracking_error:.2%}",
        f"{information_ratio:.2f}",
        f"{sharpe_ratio:.2f}",
        f"{alpha:.2%}",
        f"{beta:.2f}",
        f"{var_95:.2%}",
        f"{max_drawdown:.2%}"

    ]
})

st.dataframe(
    risk_df,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption("""
BRISAMAR INVESTMENTS — Sistema Cuantitativo Institucional
""")