import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ShopImpact – Conscious Shopping Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# GLOBAL STYLING (CLOUD SAFE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
/* Main background */
.main {
    background-color: #f6f9fc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* Cards */
.card {
    background-color: #ffffff;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #ecfeff, #ffffff);
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #99f6e4;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}

/* Headings */
h1, h2, h3 {
    color: #065f46;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    background-color: #16a34a;
    color: white;
    border-radius: 10px;
    font-weight: 600;
}

/* Inputs */
input, select {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA SETUP
# -----------------------------------------------------------------------------
if "purchases" not in st.session_state:
    st.session_state["purchases"] = []

CO2_FACTORS = {
    "Local Food": 0.0001,
    "Eco-Friendly Fashion": 0.0002,
    "Public Transport": 0.0001,
    "Electronic Goods": 0.0005,
    "Fast Fashion": 0.0008,
    "Imported Goods": 0.0010
}

ALTERNATIVES = {
    "Electronic Goods": "Buy refurbished electronics or repair existing devices.",
    "Fast Fashion": "Try thrift stores or sustainable fashion brands.",
    "Imported Goods": "Choose locally made alternatives to reduce transport emissions."
}

def calculate_impact(price, category):
    return round(price * CO2_FACTORS.get(category, 0.0005), 2)

def eco_score(data):
    if not data:
        return 50
    spend = sum(d["Price"] for d in data)
    co2 = sum(d["CO2"] for d in data)
    if spend == 0:
        return 50
    ratio = (co2 / spend) * 1000
    return int(max(0, min(100, 100 - ratio * 50)))

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌱 ShopImpact")
    st.markdown("### Your Eco Habitat")

    score = eco_score(st.session_state["purchases"])

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

    if len(st.session_state["purchases"]) >= 1:
        st.caption("🏁 First Step")
    if score > 90:
        st.caption("🌍 Earth Guardian")
    if not st.session_state["purchases"]:
        st.caption("Log items to earn badges!")

# -----------------------------------------------------------------------------
# MAIN DASHBOARD
# -----------------------------------------------------------------------------
st.title("Conscious Shopping Dashboard")
st.caption("Track your spending and environmental impact clearly and responsibly")

# -----------------------------------------------------------------------------
# LOG PURCHASE
# -----------------------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("➕ Log a Purchase")

with st.form("purchase_form", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])

    product = c1.text_input("Product Name", placeholder="e.g. Organic Vegetables")
    brand = c2.text_input("Brand", placeholder="Optional")
    category = c3.selectbox("Category", list(CO2_FACTORS.keys()))
    price = c4.number_input("Price (₹ INR)", min_value=0.0, step=100.0)
    submit = c5.form_submit_button("Add")

    if submit and product and price > 0:
        entry = {
            "Product": product,
            "Brand": brand,
            "Category": category,
            "Price": price,
            "CO2": calculate_impact(price, category),
            "Date": datetime.date.today()
        }
        st.session_state["purchases"].append(entry)

        if category in ["Local Food", "Eco-Friendly Fashion", "Public Transport"]:
            st.success("Great eco-friendly choice! 🌿")
            st.balloons()
        else:
            st.info(ALTERNATIVES.get(category, "Consider greener alternatives next time."))

        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# METRICS
# -----------------------------------------------------------------------------
if st.session_state["purchases"]:
    df = pd.DataFrame(st.session_state["purchases"])

    total_items = len(df)
    total_spend = df["Price"].sum()
    total_co2 = df["CO2"].sum()

    m1, m2, m3 = st.columns(3)

    m1.markdown(f"""
    <div class="metric-card">
        <h4>Total Items</h4>
        <h2>{total_items}</h2>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="metric-card">
        <h4>Total Spend</h4>
        <h2>₹ {total_spend:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    m3.markdown(f"""
    <div class="metric-card">
        <h4>CO₂ Output</h4>
        <h2>{total_co2:.2f} kg</h2>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # VISUAL INSIGHTS
    # -----------------------------------------------------------------------------
    st.markdown("## 📊 Visual Insights")
    st.caption("Where your money and emissions go")

    c1, c2 = st.columns(2)

    pie = px.pie(
        df,
        values="Price",
        names="Category",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Greens
    )
    pie.update_layout(paper_bgcolor="white", plot_bgcolor="white")

    bar_df = df.groupby("Category")["CO2"].sum().reset_index()
    bar = px.bar(
        bar_df,
        x="Category",
        y="CO2",
        color="CO2",
        color_continuous_scale="Greens"
    )
    bar.update_layout(paper_bgcolor="white", plot_bgcolor="white")

    c1.markdown('<div class="card">', unsafe_allow_html=True)
    c1.plotly_chart(pie, use_container_width=True)
    c1.markdown('</div>', unsafe_allow_html=True)

    c2.markdown('<div class="card">', unsafe_allow_html=True)
    c2.plotly_chart(bar, use_container_width=True)
    c2.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # MONTHLY SUMMARY
    # -----------------------------------------------------------------------------
    st.markdown("## 📅 Monthly Impact Summary")
    df["Month"] = pd.to_datetime(df["Date"]).dt.strftime("%B %Y")
    summary = df.groupby("Month")[["Price", "CO2"]].sum().reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

    with st.expander("📜 View Purchase History"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Start by logging your first purchase to see insights")
