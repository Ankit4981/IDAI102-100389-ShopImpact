import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import turtle

# =============================================================================
# CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="ShopImpact Dashboard",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# GLOBAL STYLING (FULLY FIXED VISIBILITY + COLORS)
# =============================================================================
st.markdown("""
<style>

/* ---------- MAIN BACKGROUND ---------- */
.main {
    background-color: #f5f7fa;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* ---------- HEADINGS ---------- */
h1, h2, h3 {
    color: #065f46;
    font-weight: 600;
}

/* ---------- LABELS (FIXED INVISIBLE ISSUE) ---------- */
label {
    color: #0f172a !important;
    font-weight: 500;
    font-size: 0.9rem;
}

/* ---------- INPUT PLACEHOLDERS ---------- */
::placeholder {
    color: #6b7280 !important;
}

/* ---------- CAPTIONS & SMALL TEXT ---------- */
small,
.stCaption,
[data-testid="stCaptionContainer"] {
    color: #374151 !important;
    font-weight: 500;
}

/* ---------- PARAGRAPH TEXT ---------- */
p {
    color: #111827;
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    background-color: #16a34a;
    color: white;
    border-radius: 10px;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #15803d;
}

/* ---------- CARDS ---------- */
.card {
    background-color: #ffffff;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* ---------- METRIC CARDS ---------- */
.metric-card {
    background: linear-gradient(135deg, #ecfeff, #ffffff);
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #d1fae5;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* ---------- PLOTLY TEXT ---------- */
.plotly text {
    fill: #111827 !important;
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
    "Electronic Goods": "Buy refurbished or repair existing gadgets.",
    "Cheap Clothing": "Try thrift stores or sustainable brands.",
    "Imported Items": "Look for locally manufactured alternatives."
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

def run_turtle_animation():
    try:
        wn = turtle.Screen()
        wn.setup(300, 300)
        t = turtle.Turtle()
        t.color("green")
        t.begin_fill()
        t.circle(40)
        t.end_fill()
        t.hideturtle()
        t.clear()
    except:
        pass

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

    df_temp = pd.DataFrame(st.session_state["purchases"])
    if not df_temp.empty:
        if len(df_temp) >= 1:
            st.caption("🏁 First Step")
        if score > 90:
            st.caption("🌍 Earth Guardian")
    else:
        st.caption("Log items to earn badges!")

# =============================================================================
# MAIN DASHBOARD
# =============================================================================
st.title("Conscious Shopping Dashboard")
st.caption("Track your spending and environmental impact")

# ---------- LOG PURCHASE ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("➕ Log a Purchase")

with st.form("purchase_form", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])

    product = c1.text_input("Product Name", placeholder="e.g. Organic Vegetables")
    brand = c2.text_input("Brand", placeholder="e.g. Local Farm")
    category = c3.selectbox("Category", list(CO2_FACTORS.keys()))
    price = c4.number_input("Price (₹)", min_value=0.0, step=100.0)
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
            st.balloons()
            run_turtle_animation()
        else:
            st.info(ALTERNATIVES.get(category, ""))

        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# METRICS + CHARTS
# =============================================================================
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

    st.markdown("## 📊 Visual Insights")
    st.markdown("<p>Where your money and emissions go</p>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    fig_pie = px.pie(
        df,
        values="Price",
        names="Category",
        hole=0.45,
        color_discrete_sequence=["#22c55e", "#86efac", "#4ade80", "#16a34a"]
    )
    fig_pie.update_layout(paper_bgcolor="white", plot_bgcolor="white")

    cat_group = df.groupby("Category")["CO2"].sum().reset_index()
    fig_bar = px.bar(
        cat_group,
        x="Category",
        y="CO2",
        color="CO2",
        color_continuous_scale="Greens"
    )
    fig_bar.update_layout(paper_bgcolor="white", plot_bgcolor="white")

    c1.markdown('<div class="card">', unsafe_allow_html=True)
    c1.plotly_chart(fig_pie, use_container_width=True)
    c1.markdown('</div>', unsafe_allow_html=True)

    c2.markdown('<div class="card">', unsafe_allow_html=True)
    c2.plotly_chart(fig_bar, use_container_width=True)
    c2.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 📅 Monthly Impact Summary")
    df["Month"] = pd.to_datetime(df["Date"]).dt.strftime("%B %Y")
    summary = df.groupby("Month")[["Price", "CO2"]].sum().reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

    with st.expander("View Purchase History"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Start by logging your first purchase to see insights")
