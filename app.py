import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="ShopImpact – Conscious Shopping Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# GLOBAL DARK THEME + VISIBILITY FIX (CRITICAL)
# =============================================================================
st.markdown("""
<style>

/* -------- BACKGROUND -------- */
.main {
    background: linear-gradient(180deg, #020617, #020617);
}

/* -------- SIDEBAR -------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* -------- TEXT VISIBILITY FIX -------- */
body, p, span, div, label {
    color: #e5e7eb !important;
}

h1, h2, h3, h4 {
    color: #ecfeff !important;
}

/* Captions */
.stCaption {
    color: #cbd5f5 !important;
}

/* -------- INPUTS -------- */
input, textarea, select {
    background-color: #1f2937 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
}

/* -------- BUTTONS -------- */
.stButton > button {
    background-color: #16a34a;
    color: white;
    border-radius: 10px;
    font-weight: 600;
}

/* -------- METRIC CARDS -------- */
.metric-card {
    background: linear-gradient(135deg, #022c22, #064e3b);
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #065f46;
    text-align: center;
}

/* Metric text */
.metric-card h4 {
    color: #a7f3d0 !important;
}
.metric-card h2 {
    color: #ffffff !important;
}

/* -------- CARDS -------- */
.card {
    background-color: #020617;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #1e293b;
    margin-bottom: 20px;
}

/* -------- PLOTLY -------- */
svg text {
    fill: #e5e7eb !important;
}

/* -------- DATAFRAME -------- */
thead tr th, tbody tr td {
    color: #e5e7eb !important;
    background-color: #020617 !important;
}

/* -------- HR -------- */
hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOGIC
# =============================================================================
if "purchases" not in st.session_state:
    st.session_state["purchases"] = []

CO2_FACTORS = {
    "Local Food": 0.0001,
    "Eco-Friendly Fashion": 0.0002,
    "Public Transport": 0.0001,
    "Electronic Goods": 0.0005,
    "Cheap Clothing": 0.0008,
    "Imported Items": 0.0010
}

ALTERNATIVES = {
    "Electronic Goods": "Consider repairing or buying refurbished electronics.",
    "Cheap Clothing": "Try sustainable brands or thrift shopping.",
    "Imported Items": "Choose locally produced alternatives."
}

def calculate_impact(price, category):
    return round(price * CO2_FACTORS.get(category, 0.0005), 2)

def get_eco_score(data):
    if not data:
        return 50
    spend = sum(d["Price"] for d in data)
    co2 = sum(d["CO2"] for d in data)
    if spend == 0:
        return 50
    ratio = (co2 / spend) * 1000
    return int(max(0, min(100, 100 - ratio * 50)))

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.title("🌱 ShopImpact")
    st.markdown("### Your Eco Habitat")

    score = get_eco_score(st.session_state["purchases"])

    if score >= 80:
        st.success("Excellent progress 🌍")
    elif score >= 50:
        st.info("Good progress 🌿")
    else:
        st.warning("High footprint ⚠️")

    st.metric("Eco Score", f"{score}/100")
    st.progress(score / 100)

    st.markdown("---")
    st.subheader("Achievements")

    if st.session_state["purchases"]:
        st.caption("🏁 First Step")
        if score > 90:
            st.caption("🌍 Earth Guardian")
    else:
        st.caption("Log items to earn badges!")

# =============================================================================
# MAIN DASHBOARD
# =============================================================================
st.title("Conscious Shopping Dashboard")
st.caption("Track your spending and environmental impact clearly and responsibly")

# =============================================================================
# LOG PURCHASE
# =============================================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("➕ Log a Purchase")

with st.form("purchase_form", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])

    product = c1.text_input("Product Name", placeholder="e.g. Organic Vegetables")
    brand = c2.text_input("Brand (Optional)")
    category = c3.selectbox("Category", list(CO2_FACTORS.keys()))
    price = c4.number_input("Price (₹ INR)", min_value=0.0, step=100.0)
    submit = c5.form_submit_button("Add")

    if submit and product and price > 0:
        st.session_state["purchases"].append({
            "Product": product,
            "Brand": brand,
            "Category": category,
            "Price": price,
            "CO2": calculate_impact(price, category),
            "Date": datetime.date.today()
        })

        if category in ALTERNATIVES:
            st.info(f"💡 Greener Tip: {ALTERNATIVES[category]}")
        else:
            st.balloons()

        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# METRICS
# =============================================================================
if st.session_state["purchases"]:
    df = pd.DataFrame(st.session_state["purchases"])

    c1, c2, c3 = st.columns(3)

    c1.markdown(f"""
    <div class="metric-card">
        <h4>Total Items</h4>
        <h2>{len(df)}</h2>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="metric-card">
        <h4>Total Spend</h4>
        <h2>₹ {df["Price"].sum():,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="metric-card">
        <h4>CO₂ Output</h4>
        <h2>{df["CO2"].sum():.2f} kg</h2>
    </div>
    """, unsafe_allow_html=True)

    # =============================================================================
    # VISUAL INSIGHTS
    # =============================================================================
    st.markdown("## 📊 Visual Insights")
    st.caption("Where your money and emissions go")

    col1, col2 = st.columns(2)

    fig_pie = px.pie(
        df,
        values="Price",
        names="Category",
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.Greens
    )
    fig_pie.update_layout(paper_bgcolor="#020617", font_color="#e5e7eb")

    bar_data = df.groupby("Category")["CO2"].sum().reset_index()
    fig_bar = px.bar(
        bar_data,
        x="Category",
        y="CO2",
        color="CO2",
        color_continuous_scale="Greens"
    )
    fig_bar.update_layout(paper_bgcolor="#020617", font_color="#e5e7eb")

    col1.plotly_chart(fig_pie, use_container_width=True)
    col2.plotly_chart(fig_bar, use_container_width=True)

    # =============================================================================
    # MONTHLY SUMMARY
    # =============================================================================
    st.markdown("## 📅 Monthly Impact Summary")

    df["Month"] = pd.to_datetime(df["Date"]).dt.strftime("%B %Y")
    summary = df.groupby("Month")[["Price", "CO2"]].sum().reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

    with st.expander("View Purchase History"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Start by logging your first purchase above")
