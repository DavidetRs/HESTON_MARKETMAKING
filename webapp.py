import streamlit as st
import requests

st.set_page_config(page_title="Options Pricing Tool", layout="wide")

#CSS part
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        color: #1F77B4;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #1F77B4;
        color: #fff;
        border-radius: 0.5rem;
        padding: 0.6rem 1.5rem;
        font-size: 1rem;
    }
    .block-container {
        padding: 2rem 3rem;
    }
    </style>
""", unsafe_allow_html=True)
# creation des 4 matruces avec info necessaire au pricing 
vol_matrices = {
    "NASDAQ 100 Index 2015": {
        "metadata": {"underlying": "NASDAQ 2015", "date": "09/06/2015", "dividend_rate": 1.32, "spot_price": 4427.61, "interest_rate": 1.50},
        "maturities": ["1M","2M","3M","6M","9M","1Y","18M","2Y","3Y","4Y","5Y","7Y","10Y"],
        "maturities_values": [1/12,2/12,3/12,0.5,0.75,1,1.5,2,3,4,5,7,10], #transformation en année pour correspondre a nos csv clean 
        "strikes_pct": ["80% - 3542.09","90% - 3984.85","95% - 4206.23","97.5% - 4316.92","100% - 4427.61","102.5% - 4538.30","105% - 4648.99","110% - 4870.37","120% - 5313.13"],
        "strikes_values": [0.8,0.9,0.95,0.975,1.0,1.025,1.05,1.1,1.2] # pourcentage du spot price
    },
   "NASDAQ 100 Index 2014": {
        "metadata": {
            "underlying":    "NASDAQ 2014",
            "date":          "09/06/2014",
            "dividend_rate": 1.50,
            "spot_price":    3795.74,
            "interest_rate": 1.40
        },
        "maturities":  ["1M","2M","3M","6M","9M","1Y","18M","2Y","3Y","4Y","5Y","7Y","10Y"],
        "maturities_values": [1/12, 2/12, 3/12, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7, 10],
        "strikes_pct": ["80% - 3036.59","90% - 3416.17","95% - 3605.95","97.5% - 3700.85","100% - 3795.74","102.5% - 3890.63","105% - 3985.53","110% - 4175.31","120% - 4554.89"],
        "strikes_values": [0.8, 0.9, 0.95, 0.975, 1.0, 1.025, 1.05, 1.1, 1.2]
    },
    "SPX Index 2015": {
        "metadata": {
            "underlying":    "SPX 2015",
            "date":          "09/06/2015",
            "dividend_rate": 2.15,
            "spot_price":    2079.94,
            "interest_rate": 1.5
        },
        "maturities":  ["1M","2M","3M","6M","9M","1Y","18M","2Y","3Y","4Y","5Y","7Y","10Y"],
        "maturities_values": [1/12, 2/12, 3/12, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7, 10],
        "strikes_pct": ["80% - 1663.95","90% - 1871.95","95% - 1975.94","97.5% - 2027.94","100% - 2079.94","102.5% - 2131.94","105% - 2183.94","110% - 2287.93","120% - 2495.93"],
        "strikes_values": [0.8, 0.9, 0.95, 0.975, 1.0, 1.025, 1.05, 1.1, 1.2]
    },"SPX Index 2014": {
        "metadata": {
            "underlying":    "SPX 2014",
            "date":          "09/06/2014",
            "dividend_rate": 2.26,
            "spot_price":    1951.16,
            "interest_rate": 1.40
        },
        "maturities":  ["1M","2M","3M","6M","9M","1Y","18M","2Y","3Y","4Y","5Y","7Y","10Y"],
        "maturities_values": [1/12, 2/12, 3/12, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7, 10],
        "strikes_pct": ["80% - 1560.93","90% - 1756.04","95% - 1853.60","97.5% - 1902.38","100% - 1951.16","102.5% - 1999.94","105% - 2048.72","110% - 2146.28","120% - 2341.39"],
        "strikes_values": [0.8, 0.9, 0.95, 0.975, 1.0, 1.025, 1.05, 1.1, 1.2]
    }
}

models = ["Heston", "Bates", "Double Heston"] # choix des modèles de pricing
# choix des produits dérivés
products = [
    "Cash-or-Nothing Call", "Cash-or-Nothing Put", "Asset-or-Nothing Call", "Asset-or-Nothing Put",
    "Gap Option Call", "Gap Option Put", "Super Share Option Call", "Super Share Option Put",
    "One-Touch Option", "No-Touch Option", "Double One-Touch Option", "Double No-Touch Option",
    "Ladder Option Call", "Ladder Option Put", "Range Binary Option", "Range Reverse Binary Option",
    "Up-and-In Binary", "Down-and-In Binary", "Classic Variance Swap", "Floating Strike Variance Swap",
    "Log Contract Variance Swap", "Volatility Swap", "Gamma Swap", "Conditional Variance Swap"
]

st.markdown('<div class="main-header">🔧 Options Pricing Tool</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🗂️ Parameters selection")
    matrix = st.selectbox("1) Underlying asset", list(vol_matrices.keys()))
    maturity = st.selectbox("2) Maturity (years)", vol_matrices[matrix]["maturities"])
    strike_pct = st.selectbox("3) Strike (% of spot) and strike price", vol_matrices[matrix]["strikes_pct"])
    model = st.selectbox("4) Pricing model", models)
    product = st.selectbox("5) Type of derivative product", products)
    do_price = st.button("Request a price quote")

data_meta = vol_matrices[matrix]["metadata"]
idx_mat = vol_matrices[matrix]["maturities"].index(maturity)
idx_str = vol_matrices[matrix]["strikes_pct"].index(strike_pct)
maturity_value = vol_matrices[matrix]["maturities_values"][idx_mat]
strike_price = data_meta["spot_price"] * vol_matrices[matrix]["strikes_values"][idx_str]

# data a envoyer a l'api
if do_price:
    payload = {
        "model": model,
        "product": product,
        "strike": strike_price,
        "maturity": maturity_value
    }
    api_url = "https://api-pricer.onrender.com/parameter" #API URL render
# test des erreurs et affichage 
    with st.spinner("🔄 Calibration & pricing in progress…"):
        try:
            resp = requests.post(api_url, json=payload, timeout=20)
            resp.raise_for_status()
            price = resp.json().get("price")
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur API : {e}")
            st.stop()
        if price is None:
            st.error("Pas de prix retourné par l'API.")
            st.stop()

    st.markdown("## 💰 Option Price quote Bid Ask")
    c1, _ = st.columns([1, 3])
    c1.markdown(
        f"<h1 style='color:#1F77B4; font-size:3rem; margin:0;'>{price:.4f}</h1>",
        unsafe_allow_html=True
    )

# recap des paramètres choisis et du prix
    st.markdown("### 📋 Parameters recap")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Underlying", data_meta["underlying"])
        st.metric("Date", data_meta["date"])
        st.metric("Dividend Rate %", f"{data_meta['dividend_rate']:.2f}%")
    with col2:
        st.metric("Spot Price", f"{data_meta['spot_price']:.2f}")
        st.metric("Interest Rate %", f"{data_meta['interest_rate']:.2f}%")
        st.metric("Maturity (years)", maturity_value)

    st.markdown("### ⚙️ Selected Product & Strike")
    c3, c4 = st.columns(2)
    with c3:
        st.metric("Model used", model)
        st.metric("Product", product)
    with c4:
        st.metric("Strike", f"{strike_price:.2f}")
        st.metric("Option Price", f"{price:.4f}")




# %%



