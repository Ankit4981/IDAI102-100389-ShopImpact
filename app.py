"""
ShopImpact - Conscious Shopping Dashboard (Modern Purple-Blue Edition)
A beautiful, welcoming Streamlit app for tracking shopping and environmental impact
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime
import streamlit.components.v1 as components

# Try to import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ============================================================================
# MODERN PURPLE-BLUE COLOR PALETTE
# ============================================================================

COLORS = {
    # Primary purples
    "deep_purple": "#6B46C1",
    "royal_purple": "#805AD5",
    "light_purple": "#B794F6",
    "lavender": "#D6BCFA",
    
    # Blues
    "navy_blue": "#2C5282",
    "ocean_blue": "#3182CE",
    "sky_blue": "#63B3ED",
    "light_blue": "#90CDF4",
    
    # Teals & Cyans
    "teal": "#319795",
    "cyan": "#38B2AC",
    "mint": "#81E6D9",
    "aqua": "#B2F5EA",
    
    # Accents
    "pink": "#ED64A6",
    "coral": "#F687B3",
    "orange": "#F6AD55",
    "yellow": "#F6E05E",
    
    # Neutrals
    "off_white": "#F7FAFC",
    "light_gray": "#E2E8F0",
    "medium_gray": "#A0AEC0",
    "dark_gray": "#2D3748",
    "charcoal": "#1A202C"
}

# Impact multipliers
IMPACT_MULTIPLIERS = {
    "Electronics": 0.01,
    "Clothes": 0.003,
    "Groceries": 0.0018,
    "Home & Furniture": 0.005,
    "Beauty & Personal Care": 0.004,
    "Books & Stationery": 0.002,
    "Toys & Games": 0.0035,
    "Sports & Outdoor": 0.0038,
    "Second-hand": 0.00024,
    "Other": 0.003
}

# Category colors
CATEGORY_COLORS = {
    "Electronics": COLORS["ocean_blue"],
    "Clothes": COLORS["pink"],
    "Groceries": COLORS["teal"],
    "Home & Furniture": COLORS["orange"],
    "Beauty & Personal Care": COLORS["coral"],
    "Books & Stationery": COLORS["light_purple"],
    "Toys & Games": COLORS["yellow"],
    "Sports & Outdoor": COLORS["cyan"],
    "Second-hand": COLORS["mint"],
    "Other": COLORS["medium_gray"]
}

ECO_ALTERNATIVES = {
    "Electronics": "🔌 Try refurbished devices, energy-efficient models, or repair instead of replace",
    "Clothes": "👕 Shop thrift stores, swap with friends, or choose organic cotton",
    "Groceries": "🥬 Buy local farmers market, choose organic, eat seasonal",
    "Home & Furniture": "🏡 Upcycle, buy vintage, or choose sustainable materials",
    "Beauty & Personal Care": "✨ Go plastic-free, choose natural ingredients, support cruelty-free",
    "Books & Stationery": "📚 Visit libraries, buy used books, or go digital",
    "Toys & Games": "🎨 Choose wooden toys, educational items, or rent from toy libraries",
    "Sports & Outdoor": "⚽ Buy quality gear that lasts, rent equipment, shop second-hand",
    "Second-hand": "🌟 You're amazing! Keep championing reuse and circular economy!",
    "Other": "🌍 Always ask: Do I need it? Can I borrow it? Can I buy it used?"
}

ECO_TIPS = [
    "🌱 Small daily choices create massive environmental impact!",
    "♻️ The greenest product is the one you already own",
    "🌳 Quality over quantity = less waste, more savings",
    "💚 Your wallet AND the planet thank you for conscious choices",
    "🌸 Second-hand first, new only when necessary",
    "🦋 Every eco-choice inspires others to do the same",
    "🌊 Reducing plastic use is one of the kindest acts for oceans",
    "☀️ Sustainable living is a journey, not perfection",
    "🌿 Local & seasonal = fresher, healthier, greener",
    "🌈 Colorful planet needs colorful solutions - you're part of it!"
]

# ============================================================================
# SESSION STATE
# ============================================================================

if "purchases" not in st.session_state:
    st.session_state.purchases = []
if "latest_tip" not in st.session_state:
    st.session_state.latest_tip = None
if "reward_type" not in st.session_state:
    st.session_state.reward_type = None
if "show_celebration" not in st.session_state:
    st.session_state.show_celebration = False
if "ai_enabled" not in st.session_state:
    st.session_state.ai_enabled = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "demo_user": {"password": "demo123", "name": "Demo User", "email": "demo@shopimpact.com"},
        "eco_warrior": {"password": "green123", "name": "Eco Warrior", "email": "eco@shopimpact.com"}
    }

# ============================================================================
# GEMINI AI FUNCTIONS
# ============================================================================

def initialize_gemini():
    """Initialize Gemini AI if API key is available"""
    if not GEMINI_AVAILABLE:
        return False
    if "API_KEY" in os.environ:
        try:
            genai.configure(api_key=os.environ["API_KEY"])
            st.session_state.ai_enabled = True
            return True
        except:
            return False
    return False

def get_ai_validation_and_tip(category, brand, price):
    if not st.session_state.ai_enabled or not GEMINI_AVAILABLE:
        return get_fallback_validation(category, brand, price)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Analyze: Category: {category}, Brand: {brand}, Price: ₹{price}
Return JSON: {{"isValid": true/false, "rejectionReason": "reason", "insight": "impact insight", "alternative": "green tip"}}"""
        
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        ai_data = json.loads(text)
        
        if "isValid" not in ai_data:
            ai_data["isValid"] = True
        if "insight" not in ai_data:
            ai_data["insight"] = f"Standard impact for {category}."
        if "alternative" not in ai_data:
            ai_data["alternative"] = ECO_ALTERNATIVES.get(category, "Choose sustainably!")
        
        return ai_data
    except:
        return get_fallback_validation(category, brand, price)

def get_fallback_validation(category, brand, price):
    brand = brand.strip()
    
    if len(brand) < 2:
        return {"isValid": False, "rejectionReason": "Brand name too short", "insight": "", "alternative": ""}
    
    if not any(c.isalpha() for c in brand):
        return {"isValid": False, "rejectionReason": "Invalid brand name", "insight": "", "alternative": ""}
    
    impact = price * IMPACT_MULTIPLIERS.get(category, 0.003)
    
    if category == "Second-hand":
        insight = f"🌟 Amazing! Second-hand saves {impact*10:.1f}kg CO₂ vs new!"
    elif impact > 50:
        insight = f"⚠️ High impact: {impact:.2f}kg CO₂. Consider eco alternatives!"
    elif impact > 20:
        insight = f"💛 Moderate impact: {impact:.2f}kg CO₂. Look for eco-certified options!"
    else:
        insight = f"💚 Great choice! Only {impact:.2f}kg CO₂. Keep it up!"
    
    return {
        "isValid": True,
        "rejectionReason": None,
        "insight": insight,
        "alternative": ECO_ALTERNATIVES.get(category, "Choose sustainable options!")
    }

# ============================================================================
# LOGIN PAGE FUNCTION
# ============================================================================

def show_login_page():
    """Display beautiful login page with same UI theme"""
    
    # Create centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Animated header
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 40px;'>
                <div style='font-size: 8rem; margin-bottom: 20px; 
                            animation: bounce 2s ease-in-out infinite;'>
                    🌍🌿
                </div>
                <h1 style='font-family: "Poppins", sans-serif; font-size: 4rem; font-weight: 800;
                           background: linear-gradient(135deg, {COLORS['deep_purple']}, {COLORS['ocean_blue']}, {COLORS['teal']});
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                           margin: 0; line-height: 1.2;'>
                    ShopImpact
                </h1>
                <p style='font-size: 1.5rem; color: {COLORS['medium_gray']}; margin-top: 10px; font-weight: 600;'>
                    Conscious Shopping Journey
                </p>
            </div>
            
            <style>
                @keyframes bounce {{
                    0%, 100% {{ transform: translateY(0); }}
                    50% {{ transform: translateY(-20px); }}
                }}
            </style>
        """, unsafe_allow_html=True)
        
        # Login card
        st.markdown(f"""
            <div style='background: white; padding: 50px 40px; border-radius: 35px; 
                        box-shadow: 0 20px 60px rgba(107, 70, 193, 0.2); 
                        border: 6px solid {COLORS['light_purple']};'>
        """, unsafe_allow_html=True)
        
        # Toggle between login and signup
        if 'show_signup' not in st.session_state:
            st.session_state.show_signup = False
        
        if not st.session_state.show_signup:
            # LOGIN FORM
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 30px;'>
                    <h2 style='color: {COLORS['deep_purple']}; font-family: "Poppins", sans-serif; 
                               font-size: 2.5rem; margin: 0; font-weight: 700;'>
                        Welcome Back! 👋
                    </h2>
                    <p style='color: {COLORS['medium_gray']}; font-size: 1.1rem; margin-top: 10px;'>
                        Sign in to continue your eco journey
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "👤 Username",
                    placeholder="Enter your username",
                    key="login_username"
                )
                
                password = st.text_input(
                    "🔒 Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    login_button = st.form_submit_button("🚀 Sign In", use_container_width=True)
                
                with col_btn2:
                    if st.form_submit_button("📝 Sign Up", use_container_width=True):
                        st.session_state.show_signup = True
                        st.rerun()
                
                if login_button:
                    if username in st.session_state.user_data:
                        if st.session_state.user_data[username]["password"] == password:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success(f"✅ Welcome back, {st.session_state.user_data[username]['name']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Incorrect password!")
                    else:
                        st.error("❌ Username not found!")
            
            # Demo credentials info
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {COLORS['light_blue']}30, {COLORS['aqua']}20); 
                            padding: 20px; border-radius: 15px; margin-top: 25px; 
                            border: 2px dashed {COLORS['ocean_blue']};'>
                    <p style='margin: 0; font-size: 0.95rem; color: {COLORS['ocean_blue']}; font-weight: 600; text-align: center;'>
                        🎯 <strong>Demo Credentials:</strong><br>
                        Username: <code>demo_user</code> | Password: <code>demo123</code><br>
                        Username: <code>eco_warrior</code> | Password: <code>green123</code>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            # SIGNUP FORM
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 30px;'>
                    <h2 style='color: {COLORS['deep_purple']}; font-family: "Poppins", sans-serif; 
                               font-size: 2.5rem; margin: 0; font-weight: 700;'>
                        Join ShopImpact! 🌱
                    </h2>
                    <p style='color: {COLORS['medium_gray']}; font-size: 1.1rem; margin-top: 10px;'>
                        Start your sustainable shopping journey today
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("signup_form", clear_on_submit=False):
                new_name = st.text_input(
                    "✨ Full Name",
                    placeholder="Enter your full name",
                    key="signup_name"
                )
                
                new_email = st.text_input(
                    "📧 Email",
                    placeholder="your.email@example.com",
                    key="signup_email"
                )
                
                new_username = st.text_input(
                    "👤 Username",
                    placeholder="Choose a username",
                    key="signup_username"
                )
                
                new_password = st.text_input(
                    "🔒 Password",
                    type="password",
                    placeholder="Create a strong password",
                    key="signup_password"
                )
                
                confirm_password = st.text_input(
                    "🔐 Confirm Password",
                    type="password",
                    placeholder="Confirm your password",
                    key="signup_confirm"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    signup_button = st.form_submit_button("🌟 Create Account", use_container_width=True)
                
                with col_btn2:
                    if st.form_submit_button("← Back to Login", use_container_width=True):
                        st.session_state.show_signup = False
                        st.rerun()
                
                if signup_button:
                    if not new_name or not new_email or not new_username or not new_password:
                        st.error("❌ Please fill in all fields!")
                    elif new_username in st.session_state.user_data:
                        st.error("❌ Username already exists!")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        # Create new user
                        st.session_state.user_data[new_username] = {
                            "password": new_password,
                            "name": new_name,
                            "email": new_email
                        }
                        st.session_state.logged_in = True
                        st.session_state.username = new_username
                        st.success(f"✅ Account created! Welcome, {new_name}! 🎉")
                        st.balloons()
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer on login page
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='text-align: center; padding: 30px; 
                        background: linear-gradient(135deg, {COLORS['lavender']}, {COLORS['aqua']});
                        border-radius: 25px; margin-top: 40px;'>
                <p style='color: {COLORS['deep_purple']}; font-size: 1.1rem; margin: 0; font-weight: 600;'>
                    🌍 Join thousands of eco-conscious shoppers
                </p>
                <p style='color: {COLORS['dark_gray']}; font-size: 0.95rem; margin-top: 10px;'>
                    Track purchases • Reduce impact • Earn rewards
                </p>
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# COLORFUL ANIMATED REWARDS
# ============================================================================

def create_colorful_reward(reward_type):
    if not reward_type:
        return
    
    configs = {
        "leaf": {
            "color": COLORS["teal"],
            "bg": COLORS["mint"],
            "icon": "🌿",
            "title": "Eco Champion!",
            "message": "Green choice unlocked!"
        },
        "trophy": {
            "color": COLORS["orange"],
            "bg": COLORS["yellow"],
            "icon": "🏆",
            "title": "Low Impact Hero!",
            "message": "Under 1kg CO₂!"
        },
        "footprint": {
            "color": COLORS["ocean_blue"],
            "bg": COLORS["light_blue"],
            "icon": "👣",
            "title": "Impact Tracker!",
            "message": "Monitoring your footprint!"
        },
        "recycle": {
            "color": COLORS["cyan"],
            "bg": COLORS["aqua"],
            "icon": "♻️",
            "title": "Recycler Hero!",
            "message": "Second-hand superstar!"
        }
    }
    
    cfg = configs.get(reward_type, configs["leaf"])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 15px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: transparent;
                font-family: 'Poppins', sans-serif;
            }}
            .reward-box {{
                background: linear-gradient(135deg, {cfg['bg']}40, {cfg['color']}20);
                border: 4px solid {cfg['color']};
                border-radius: 30px;
                padding: 35px;
                text-align: center;
                box-shadow: 0 20px 50px rgba(0,0,0,0.15), 0 0 0 8px {cfg['bg']}30;
                animation: bounceIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }}
            .icon-big {{
                font-size: 90px;
                margin-bottom: 15px;
                animation: rotate 2s ease-in-out infinite;
                display: inline-block;
            }}
            canvas {{
                background: white;
                border-radius: 20px;
                margin: 15px 0;
                box-shadow: inset 0 4px 8px rgba(0,0,0,0.08);
            }}
            .title {{
                color: {cfg['color']};
                font-size: 28px;
                font-weight: 900;
                margin: 15px 0 8px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }}
            .message {{
                color: {COLORS['charcoal']};
                font-size: 16px;
                font-weight: 600;
                margin: 8px 0;
            }}
            .label {{
                color: {COLORS['medium_gray']};
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-top: 15px;
                font-weight: 700;
            }}
            @keyframes bounceIn {{
                0% {{ transform: scale(0) rotate(-180deg); opacity: 0; }}
                50% {{ transform: scale(1.1) rotate(5deg); }}
                100% {{ transform: scale(1) rotate(0); opacity: 1; }}
            }}
            @keyframes rotate {{
                0%, 100% {{ transform: rotate(-5deg) scale(1); }}
                50% {{ transform: rotate(5deg) scale(1.1); }}
            }}
        </style>
    </head>
    <body>
        <div class="reward-box">
            <div class="icon-big">{cfg['icon']}</div>
            <canvas id="canvas" width="180" height="180"></canvas>
            <div class="title">{cfg['title']}</div>
            <div class="message">{cfg['message']}</div>
            <div class="label">🎨 Digital Reward</div>
        </div>
        
        <script>
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            const cx = 90, cy = 90;
            
            ctx.strokeStyle = '{cfg['color']}';
            ctx.fillStyle = '{cfg['color']}30';
            ctx.lineWidth = 4;
            ctx.lineCap = 'round';
            
            let frame = 0;
            const maxFrames = 50;
            
            function draw() {{
                ctx.clearRect(0, 0, 180, 180);
                const t = Math.min(frame / maxFrames, 1);
                
                if ('{reward_type}' === 'leaf') {{
                    ctx.beginPath();
                    ctx.moveTo(cx, cy + 35);
                    ctx.bezierCurveTo(cx - 45*t, cy - 15*t, cx - 15*t, cy - 60*t, cx, cy - 35*t);
                    ctx.bezierCurveTo(cx + 15*t, cy - 60*t, cx + 45*t, cy - 15*t, cx, cy + 35);
                    ctx.fill();
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(cx, cy + 35);
                    ctx.lineTo(cx, cy - 35*t);
                    ctx.stroke();
                }} else if ('{reward_type}' === 'trophy') {{
                    ctx.beginPath();
                    ctx.moveTo(cx - 35*t, cy - 25*t);
                    ctx.lineTo(cx - 20*t, cy + 25*t);
                    ctx.lineTo(cx + 20*t, cy + 25*t);
                    ctx.lineTo(cx + 35*t, cy - 25*t);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                    ctx.fillRect(cx - 25*t, cy + 25*t, 50*t, 12*t);
                    ctx.strokeRect(cx - 25*t, cy + 25*t, 50*t, 12*t);
                    ctx.beginPath();
                    ctx.arc(cx - 35*t, cy, 10*t, 0.5*Math.PI, 1.5*Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(cx + 35*t, cy, 10*t, -0.5*Math.PI, 0.5*Math.PI);
                    ctx.stroke();
                }} else if ('{reward_type}' === 'footprint') {{
                    ctx.beginPath();
                    ctx.ellipse(cx, cy, 22*t, 32*t, 0, 0, 2*Math.PI);
                    ctx.fill();
                    ctx.stroke();
                    for (let i = 0; i < 4; i++) {{
                        ctx.beginPath();
                        ctx.arc(cx - 20*t + i*13*t, cy - 40*t, 6*t, 0, 2*Math.PI);
                        ctx.fill();
                    }}
                }} else if ('{reward_type}' === 'recycle') {{
                    for (let i = 0; i < 3; i++) {{
                        ctx.save();
                        ctx.translate(cx, cy);
                        ctx.rotate(i * 2*Math.PI/3);
                        ctx.beginPath();
                        ctx.moveTo(0, -30*t);
                        ctx.lineTo(20*t, 20*t);
                        ctx.lineTo(-20*t, 20*t);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(20*t, 20*t);
                        ctx.lineTo(15*t, 28*t);
                        ctx.moveTo(20*t, 20*t);
                        ctx.lineTo(28*t, 22*t);
                        ctx.stroke();
                        ctx.restore();
                    }}
                }}
                
                if (frame < maxFrames) {{
                    frame++;
                    requestAnimationFrame(draw);
                }}
            }}
            
            draw();
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=420)

# ============================================================================
# ANALYTICS
# ============================================================================

def calculate_eco_score(total_impact, num_purchases):
    if num_purchases == 0:
        return 100
    avg_impact = total_impact / num_purchases
    base_score = max(0, 100 - (avg_impact * 10))
    second_hand = sum(1 for p in st.session_state.purchases if p.get("Category") == "Second-hand")
    bonus = min(20, second_hand * 4)
    return min(100, int(base_score + bonus))

def check_badges():
    badges = {
        "beginner": {"earned": False, "icon": "🌱", "color": COLORS["mint"], "title": "Beginner", "desc": "First purchase!"},
        "eco_saver": {"earned": False, "icon": "🌊", "color": COLORS["light_blue"], "title": "Eco Saver", "desc": "Under 20kg CO₂"},
        "recycler": {"earned": False, "icon": "♻️", "color": COLORS["teal"], "title": "Recycler", "desc": "Bought second-hand"},
        "savvy": {"earned": False, "icon": "💎", "color": COLORS["cyan"], "title": "Savvy", "desc": "5+ purchases"},
        "champion": {"earned": False, "icon": "🏆", "color": COLORS["orange"], "title": "Champion", "desc": "10+ purchases"},
        "warrior": {"earned": False, "icon": "🌟", "color": COLORS["pink"], "title": "Warrior", "desc": "Under 10kg total"}
    }
    
    if not st.session_state.purchases:
        return badges
    
    df = pd.DataFrame(st.session_state.purchases)
    total_impact = df["Impact"].sum()
    count = len(st.session_state.purchases)
    
    if count >= 1: badges["beginner"]["earned"] = True
    if total_impact < 20: badges["eco_saver"]["earned"] = True
    if total_impact < 10 and count >= 3: badges["warrior"]["earned"] = True
    if any(p["Category"] == "Second-hand" for p in st.session_state.purchases): badges["recycler"]["earned"] = True
    if count >= 5: badges["savvy"]["earned"] = True
    if count >= 10: badges["champion"]["earned"] = True
    
    return badges

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🌍 ShopImpact - Conscious Shopping",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

initialize_gemini()

# ============================================================================
# MAIN APP LOGIC - CHECK LOGIN STATUS
# ============================================================================

# Check if user is logged in
if not st.session_state.logged_in:
    show_login_page()
    st.stop()  # Stop execution here if not logged in

# ============================================================================
# MODERN CUSTOM STYLING
# ============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap');
    
    /* Global styling */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['off_white']} 0%, {COLORS['light_gray']} 50%, {COLORS['lavender']}10 100%);
        font-family: 'Poppins', sans-serif;
    }}
    
    /* Headers */
    .mega-header {{
        font-family: 'Poppins', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, {COLORS['deep_purple']}, {COLORS['ocean_blue']}, {COLORS['teal']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 30px 0 10px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.1);
        line-height: 1.2;
    }}
    
    .subtitle {{
        text-align: center;
        font-size: 1.5rem;
        color: {COLORS['medium_gray']};
        font-weight: 600;
        margin-bottom: 40px;
    }}
    
    /* Colorful metric cards */
    .metric-card {{
        background: white;
        padding: 35px 25px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(107, 70, 193, 0.15);
        border: 5px solid;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-12px) scale(1.03);
        box-shadow: 0 25px 50px rgba(107, 70, 193, 0.25);
    }}
    
    .metric-card:hover::before {{
        opacity: 1;
    }}
    
    .metric-icon {{
        font-size: 3.5rem;
        margin-bottom: 15px;
        display: block;
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 700;
        margin-bottom: 12px;
        opacity: 0.7;
    }}
    
    .metric-value {{
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        margin: 15px 0;
    }}
    
    .metric-unit {{
        font-size: 1.1rem;
        opacity: 0.6;
        font-weight: 600;
    }}
    
    /* Section headers */
    .section-header {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 50px 0 30px 0;
        padding: 20px 30px;
        background: linear-gradient(135deg, {COLORS['lavender']}, {COLORS['light_blue']});
        border-left: 8px solid {COLORS['royal_purple']};
        border-radius: 20px;
        color: {COLORS['deep_purple']};
    }}
    
    /* Colorful cards */
    .color-card {{
        background: white;
        padding: 35px;
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(107, 70, 193, 0.12);
        margin: 20px 0;
        border-top: 6px solid;
        transition: all 0.3s ease;
    }}
    
    .color-card:hover {{
        box-shadow: 0 15px 40px rgba(107, 70, 193, 0.2);
        transform: translateY(-5px);
    }}
    
    /* Badge styling */
    .badge-container {{
        background: white;
        padding: 30px 20px;
        border-radius: 25px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 4px solid;
        position: relative;
        overflow: hidden;
    }}
    
    .badge-unlocked {{
        box-shadow: 0 15px 40px rgba(107, 70, 193, 0.25);
        animation: badgePulse 2s ease-in-out infinite;
    }}
    
    .badge-locked {{
        opacity: 0.35;
        filter: grayscale(100%);
        border-color: {COLORS['medium_gray']}40;
    }}
    
    @keyframes badgePulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    .badge-icon {{
        font-size: 4rem;
        margin-bottom: 15px;
        display: block;
    }}
    
    .badge-title {{
        font-size: 1.2rem;
        font-weight: 800;
        margin: 10px 0 5px 0;
    }}
    
    .badge-desc {{
        font-size: 0.9rem;
        opacity: 0.7;
        font-weight: 600;
    }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {COLORS['deep_purple']}, {COLORS['royal_purple']});
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 18px 35px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 8px 20px rgba(107, 70, 193, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {COLORS['royal_purple']}, {COLORS['ocean_blue']});
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(107, 70, 193, 0.4);
    }}
    
    /* Form inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox, .stDateInput input {{
        border-radius: 15px;
        border: 3px solid {COLORS['lavender']};
        padding: 15px;
        font-size: 1.05rem;
        transition: all 0.3s;
    }}
    
    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: {COLORS['royal_purple']};
        box-shadow: 0 0 0 4px {COLORS['lavender']}40;
    }}
    
    /* Info boxes */
    .insight-box {{
        padding: 25px;
        border-radius: 20px;
        margin: 15px 0;
        border-left: 6px solid;
        font-size: 1.1rem;
        line-height: 1.7;
        font-weight: 500;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 12px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS['light_gray']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {COLORS['royal_purple']}, {COLORS['teal']});
        border-radius: 10px;
    }}
    
    /* Welcome card */
    .welcome-card {{
        background: linear-gradient(135deg, white, {COLORS['off_white']});
        padding: 60px 40px;
        border-radius: 35px;
        box-shadow: 0 20px 60px rgba(107, 70, 193, 0.15);
        text-align: center;
        border: 6px solid {COLORS['light_purple']};
    }}
    
    .feature-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 30px;
        margin-top: 40px;
    }}
    
    .feature-item {{
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(107, 70, 193, 0.1);
        transition: all 0.3s ease;
        border-top: 5px solid;
    }}
    
    .feature-item:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(107, 70, 193, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# COLORFUL SIDEBAR
# ============================================================================

with st.sidebar:
    # User profile section
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {COLORS['deep_purple']}, {COLORS['ocean_blue']}); 
                    padding: 25px 20px; border-radius: 25px; margin-bottom: 20px; text-align: center;'>
            <div style='font-size: 3.5rem; margin-bottom: 10px;'>👤</div>
            <h3 style='color: white; margin: 0; font-size: 1.3rem; font-weight: 700;'>
                {st.session_state.user_data[st.session_state.username]['name']}
            </h3>
            <p style='color: white; opacity: 0.85; margin: 5px 0 0 0; font-size: 0.85rem;'>
                @{st.session_state.username}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.purchases = []
        st.session_state.latest_tip = None
        st.session_state.reward_type = None
        st.session_state.show_celebration = False
        st.rerun()
    
    st.markdown("---")
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {COLORS['royal_purple']}, {COLORS['teal']}); 
                    padding: 30px 20px; border-radius: 25px; margin-bottom: 25px; text-align: center;'>
            <div style='font-size: 3.5rem; margin-bottom: 10px;'>🌿</div>
            <h2 style='color: white; margin: 0; font-family: "Poppins", sans-serif; font-size: 2rem; font-weight: 800;'>
                Log Purchase
            </h2>
            <p style='color: white; opacity: 0.9; margin: 8px 0 0 0; font-size: 0.95rem;'>
                Track your shopping impact
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.ai_enabled:
        st.success("✨ AI Insights Active")
    else:
        st.info("💡 Standard Mode Active")
    
    with st.form("add_purchase_form", clear_on_submit=True):
        category = st.selectbox(
            "📦 Product Category",
            list(IMPACT_MULTIPLIERS.keys()),
            help="Choose the category that fits your purchase"
        )
        
        brand = st.text_input(
            "🏷️ Brand or Product Name",
            placeholder="e.g., Samsung, Zara, Local Market"
        )
        
        price = st.number_input(
            "💰 Amount (₹)",
            min_value=0.0,
            step=50.0,
            help="Enter purchase amount in Indian Rupees"
        )
        
        purchase_date = st.date_input(
            "📅 Purchase Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
        
        submit = st.form_submit_button("🔍 Analyze & Log Purchase", use_container_width=True)
        
        if submit:
            if not brand or not brand.strip():
                st.error("❌ Please enter a brand name!")
            elif price <= 0:
                st.error("❌ Please enter a valid price!")
            else:
                with st.spinner("🤖 AI analyzing..."):
                    ai_data = get_ai_validation_and_tip(category, brand, price)
                    
                    if not ai_data.get("isValid", True):
                        st.error(f"❌ {ai_data.get('rejectionReason', 'Invalid entry')}")
                    else:
                        impact = price * IMPACT_MULTIPLIERS.get(category, 0.003)
                        new_purchase = {
                            "id": datetime.now().timestamp(),
                            "Category": category,
                            "Brand": brand.strip(),
                            "Price": round(price, 2),
                            "Impact": round(impact, 4),
                            "Date": purchase_date.strftime("%Y-%m-%d")
                        }
                        
                        st.session_state.purchases.append(new_purchase)
                        st.session_state.latest_tip = ai_data
                        st.session_state.show_celebration = True
                        
                        if category == "Second-hand":
                            st.session_state.reward_type = "recycle"
                            st.balloons()
                        elif impact < 1.0:
                            st.session_state.reward_type = "trophy"
                        elif len(st.session_state.purchases) % 5 == 0:
                            st.session_state.reward_type = "leaf"
                        else:
                            st.session_state.reward_type = "footprint"
                        
                        st.success(f"✅ Logged: {brand} - ₹{price:.2f} ({impact:.2f} kg CO₂)")
                        st.rerun()
    
    # Animated reward display
    if st.session_state.reward_type and st.session_state.show_celebration:
        st.markdown("---")
        create_colorful_reward(st.session_state.reward_type)
        if st.button("✨ Continue", use_container_width=True):
            st.session_state.reward_type = None
            st.session_state.show_celebration = False
            st.rerun()
    
    # Colorful quick stats
    if st.session_state.purchases:
        st.markdown("---")
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {COLORS['light_blue']}50, {COLORS['aqua']}40); 
                        padding: 20px; border-radius: 20px; border: 3px solid {COLORS['cyan']};'>
                <h3 style='color: {COLORS['ocean_blue']}; margin: 0 0 15px 0; font-size: 1.3rem;'>
                    📊 Quick Stats
                </h3>
        """, unsafe_allow_html=True)
        
        df = pd.DataFrame(st.session_state.purchases)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🛍️ Items", len(st.session_state.purchases), delta=None)
        with col2:
            st.metric("🌡️ CO₂", f"{df['Impact'].sum():.1f}kg", delta=None, delta_color="inverse")
        
        top_cat = df["Category"].mode()[0] if not df.empty else "None"
        st.metric("⭐ Top Category", top_cat)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# MAIN DASHBOARD HEADER
# ============================================================================

# Welcome message with username
st.markdown(f"""
    <div style='background: linear-gradient(135deg, {COLORS['lavender']}, {COLORS['light_blue']}30); 
                padding: 20px 30px; border-radius: 20px; margin-bottom: 30px; 
                border-left: 6px solid {COLORS['deep_purple']};'>
        <p style='margin: 0; font-size: 1.2rem; color: {COLORS['deep_purple']}; font-weight: 600;'>
            Welcome back, <strong>{st.session_state.user_data[st.session_state.username]['name']}</strong>! 👋
        </p>
        <p style='margin: 5px 0 0 0; font-size: 1rem; color: {COLORS['dark_gray']};'>
            Keep making sustainable choices for a better tomorrow 🌍
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 class='mega-header'>🌍 ShopImpact</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>✨ Your Conscious Shopping Journey ✨</p>", unsafe_allow_html=True)

# Calculate metrics
if st.session_state.purchases:
    df = pd.DataFrame(st.session_state.purchases)
    total_impact = df["Impact"].sum()
    total_spend = df["Price"].sum()
    num_purchases = len(st.session_state.purchases)
    eco_score = calculate_eco_score(total_impact, num_purchases)
    avg_impact = total_impact / num_purchases
else:
    total_impact = total_spend = num_purchases = avg_impact = 0.0
    eco_score = 100

# ============================================================================
# COLORFUL METRIC CARDS
# ============================================================================

col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown(f"""
        <div class='metric-card' style='border-color: {COLORS['pink']};'>
            <span class='metric-icon'>🌡️</span>
            <div class='metric-label' style='color: {COLORS['pink']};'>Carbon Footprint</div>
            <div class='metric-value' style='color: {COLORS['pink']};'>{total_impact:.1f}</div>
            <div class='metric-unit'>kg CO₂</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card' style='border-color: {COLORS['orange']};'>
            <span class='metric-icon'>💰</span>
            <div class='metric-label' style='color: {COLORS['orange']};'>Total Spending</div>
            <div class='metric-value' style='color: {COLORS['orange']};'>₹{total_spend:,.0f}</div>
            <div class='metric-unit'>Indian Rupees</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    score_color = COLORS['teal'] if eco_score >= 70 else (COLORS['orange'] if eco_score >= 40 else COLORS['pink'])
    st.markdown(f"""
        <div class='metric-card' style='border-color: {score_color};'>
            <span class='metric-icon'>⭐</span>
            <div class='metric-label' style='color: {score_color};'>Eco Score</div>
            <div class='metric-value' style='color: {score_color};'>{eco_score}</div>
            <div class='metric-unit'>out of 100</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='metric-card' style='border-color: {COLORS['ocean_blue']};'>
            <span class='metric-icon'>📊</span>
            <div class='metric-label' style='color: {COLORS['ocean_blue']};'>Avg Impact</div>
            <div class='metric-value' style='color: {COLORS['ocean_blue']};'>{avg_impact:.2f}</div>
            <div class='metric-unit'>kg/purchase</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# CONTENT SECTIONS
# ============================================================================

if not st.session_state.purchases:
    # Beautiful welcome screen
    st.markdown(f"""
    <div class='welcome-card'>
        <div style='font-size: 6rem; margin-bottom: 25px;'>🌿✨</div>
        <h2 style='font-family: "Poppins", sans-serif; font-size: 3rem; font-weight: 800;
                   color: {COLORS['deep_purple']}; margin-bottom: 20px;'>
            Welcome to Your Eco Journey!
        </h2>
        <p style='font-size: 1.4rem; color: {COLORS['medium_gray']}; 
                  margin-bottom: 50px; max-width: 700px; margin-left: auto; margin-right: auto;'>
            Every purchase tells a story. Let's make yours a green one! 🌍💚
        </p>
        
        <div class='feature-grid'>
            <div class='feature-item' style='border-color: {COLORS['teal']};'>
                <div style='font-size: 4rem; margin-bottom: 20px;'>📊</div>
                <h4 style='color: {COLORS['teal']}; font-size: 1.3rem; margin: 15px 0;'>
                    Track Everything
                </h4>
                <p style='color: {COLORS['medium_gray']}; font-size: 1rem; line-height: 1.6;'>
                    Monitor spending, carbon footprint, and shopping patterns
                </p>
            </div>
            
            <div class='feature-item' style='border-color: {COLORS['ocean_blue']};'>
                <div style='font-size: 4rem; margin-bottom: 20px;'>🤖</div>
                <h4 style='color: {COLORS['ocean_blue']}; font-size: 1.3rem; margin: 15px 0;'>
                    AI Insights
                </h4>
                <p style='color: {COLORS['medium_gray']}; font-size: 1rem; line-height: 1.6;'>
                    Get personalized sustainability tips powered by AI
                </p>
            </div>
            
            <div class='feature-item' style='border-color: {COLORS['orange']};'>
                <div style='font-size: 4rem; margin-bottom: 20px;'>🏆</div>
                <h4 style='color: {COLORS['orange']}; font-size: 1.3rem; margin: 15px 0;'>
                    Earn Rewards
                </h4>
                <p style='color: {COLORS['medium_gray']}; font-size: 1rem; line-height: 1.6;'>
                    Unlock animated badges for eco-friendly achievements
                </p>
            </div>
            
            <div class='feature-item' style='border-color: {COLORS['cyan']};'>
                <div style='font-size: 4rem; margin-bottom: 20px;'>💡</div>
                <h4 style='color: {COLORS['cyan']}; font-size: 1.3rem; margin: 15px 0;'>
                    Go Greener
                </h4>
                <p style='color: {COLORS['medium_gray']}; font-size: 1rem; line-height: 1.6;'>
                    Discover sustainable alternatives for every purchase
                </p>
            </div>
        </div>
        
        <div style='margin-top: 50px; padding: 30px; 
                    background: linear-gradient(135deg, {COLORS['lavender']}, {COLORS['aqua']}); 
                    border-radius: 20px; border: 3px dashed {COLORS['royal_purple']};'>
            <p style='margin: 0; font-size: 1.4rem; color: {COLORS['deep_purple']}; font-weight: 700;'>
                👈 Start by logging your first purchase in the sidebar!
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ========================================================================
    # COLORFUL CHARTS SECTION
    # ========================================================================
    
    st.markdown(f"<h2 class='section-header'>📈 Visual Impact Analysis</h2>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2, gap="large")
    
    with chart_col1:
        st.markdown(f"<div class='color-card' style='border-color: {COLORS['ocean_blue']};'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: {COLORS['ocean_blue']}; font-size: 1.8rem; margin-bottom: 25px;'>📊 Impact by Category</h3>", 
                   unsafe_allow_html=True)
        
        cat_data = df.groupby("Category")["Impact"].sum().reset_index()
        
        fig = px.bar(
            cat_data, 
            x="Category", 
            y="Impact",
            color="Category",
            color_discrete_map=CATEGORY_COLORS,
            template="plotly_white"
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12, color=COLORS['charcoal'])
        )
        fig.update_traces(
            marker_line_color='white',
            marker_line_width=3,
            hovertemplate='<b>%{x}</b><br>Impact: %{y:.2f} kg CO₂<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown(f"<div class='color-card' style='border-color: {COLORS['royal_purple']};'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: {COLORS['deep_purple']}; font-size: 1.8rem; margin-bottom: 25px;'>🥧 Distribution Breakdown</h3>", 
                   unsafe_allow_html=True)
        
        fig2 = px.pie(
            df,
            values="Impact",
            names="Category",
            hole=0.5,
            color="Category",
            color_discrete_map=CATEGORY_COLORS
        )
        fig2.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12)
        )
        fig2.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=13,
            marker=dict(line=dict(color='white', width=4)),
            hovertemplate='<b>%{label}</b><br>%{value:.2f} kg CO₂<br>%{percent}<extra></extra>'
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # AI INSIGHTS & ECO TIPS
    # ========================================================================
    
    st.markdown(f"<h2 class='section-header'>✨ Sustainability Intelligence</h2>", unsafe_allow_html=True)
    
    insights_col, tips_col = st.columns([3, 2], gap="large")
    
    with insights_col:
        st.markdown(f"<div class='color-card' style='border-color: {COLORS['cyan']};'>", unsafe_allow_html=True)
        
        if st.session_state.latest_tip:
            tip = st.session_state.latest_tip
            
            st.markdown(f"""
                <div class='insight-box' style='background: linear-gradient(135deg, {COLORS['light_blue']}30, {COLORS['aqua']}20); 
                            border-color: {COLORS['ocean_blue']};'>
                    <div style='font-size: 2.5rem; margin-bottom: 15px;'>🔍</div>
                    <div style='font-weight: 700; color: {COLORS['ocean_blue']}; font-size: 1.1rem; 
                                text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px;'>
                        Impact Insight
                    </div>
                    <p style='margin: 0; font-size: 1.15rem; line-height: 1.7; color: {COLORS['charcoal']};'>
                        {tip['insight']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class='insight-box' style='background: linear-gradient(135deg, {COLORS['mint']}30, {COLORS['aqua']}20); 
                            border-color: {COLORS['teal']};'>
                    <div style='font-size: 2.5rem; margin-bottom: 15px;'>💡</div>
                    <div style='font-weight: 700; color: {COLORS['teal']}; font-size: 1.1rem; 
                                text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px;'>
                        Green Alternative
                    </div>
                    <p style='margin: 0; font-size: 1.15rem; line-height: 1.7; color: {COLORS['charcoal']};'>
                        {tip['alternative']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {COLORS['lavender']}, {COLORS['light_blue']}30); 
                            padding: 40px; border-radius: 20px; text-align: center; 
                            border: 4px dashed {COLORS['royal_purple']};'>
                    <div style='font-size: 4rem; margin-bottom: 15px;'>🤖</div>
                    <p style='font-size: 1.3rem; color: {COLORS['deep_purple']}; font-weight: 600;'>
                        Log a purchase to unlock AI-powered insights!
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tips_col:
        st.markdown(f"<div class='color-card' style='border-color: {COLORS['pink']};'>", unsafe_allow_html=True)
        
        # Rotating eco tip
        tip_idx = len(st.session_state.purchases) % len(ECO_TIPS)
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {COLORS['coral']}30, {COLORS['pink']}20); 
                        padding: 30px; border-radius: 20px; text-align: center;
                        border: 4px solid {COLORS['pink']};'>
                <div style='font-size: 3rem; margin-bottom: 15px;'>💚</div>
                <div style='font-weight: 700; color: {COLORS['pink']}; font-size: 1rem; 
                            text-transform: uppercase; letter-spacing: 2px; margin-bottom: 15px;'>
                    Eco Tip #{tip_idx + 1}
                </div>
                <p style='margin: 0; font-size: 1.1rem; line-height: 1.7; color: {COLORS['charcoal']};'>
                    {ECO_TIPS[tip_idx]}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # COLORFUL BADGES SECTION
    # ========================================================================
    
    st.markdown(f"<h2 class='section-header'>🏆 Your Achievement Collection</h2>", unsafe_allow_html=True)
    
    badges = check_badges()
    badge_cols = st.columns(3, gap="medium")
    
    badge_list = list(badges.items())
    for idx, (badge_id, badge) in enumerate(badge_list):
        with badge_cols[idx % 3]:
            status = "badge-unlocked" if badge["earned"] else "badge-locked"
            icon = badge["icon"] if badge["earned"] else "🔒"
            border_color = badge["color"] if badge["earned"] else COLORS['medium_gray']
            
            st.markdown(f"""
                <div class='badge-container {status}' style='border-color: {border_color};'>
                    <span class='badge-icon'>{icon}</span>
                    <div class='badge-title' style='color: {border_color};'>{badge["title"]}</div>
                    <div class='badge-desc'>{badge["desc"]}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # PURCHASE HISTORY TABLE
    # ========================================================================
    
    st.markdown(f"<h2 class='section-header'>📋 Shopping Log & Impact Audit</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='color-card' style='border-color: {COLORS['light_purple']};'>", unsafe_allow_html=True)
    
    # Display dataframe
    display_df = df.sort_values("Date", ascending=False).copy()
    
    styled_df = display_df.style.format({
        "Price": "₹{:.2f}",
        "Impact": "{:.4f} kg"
    })
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=350)
    
    # Action buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    
    with btn_col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Report",
            data=csv,
            file_name=f"shopimpact_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with btn_col2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    
    with btn_col3:
        if st.button("📊 View Stats", use_container_width=True):
            st.info(f"Total Items: {num_purchases} | Avg: ₹{total_spend/num_purchases:.2f}")
    
    with btn_col4:
        if st.button("🗑️ Clear All", use_container_width=True):
            if st.session_state.get('confirm_clear'):
                st.session_state.purchases = []
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # GREEN ALTERNATIVES SECTION
    # ========================================================================
    
    st.markdown(f"<h2 class='section-header'>🌿 Your Personalized Green Guide</h2>", unsafe_allow_html=True)
    
    # Get top 3 categories
    top_categories = df["Category"].value_counts().head(3)
    
    alt_cols = st.columns(len(top_categories), gap="large")
    
    for idx, (cat, count) in enumerate(top_categories.items()):
        with alt_cols[idx]:
            cat_color = CATEGORY_COLORS.get(cat, COLORS['medium_gray'])
            st.markdown(f"""
                <div class='color-card' style='border-color: {cat_color}; min-height: 280px;'>
                    <div style='font-size: 3.5rem; margin-bottom: 15px;'>
                        {['🎯', '⭐', '💫'][idx]}
                    </div>
                    <h4 style='color: {cat_color}; font-size: 1.4rem; margin-bottom: 15px; font-weight: 700;'>
                        {cat}
                    </h4>
                    <div style='background: {cat_color}20; padding: 8px 16px; border-radius: 50px; 
                                display: inline-block; margin-bottom: 20px;'>
                        <span style='font-weight: 700; color: {cat_color};'>{count} purchase{"s" if count > 1 else ""}</span>
                    </div>
                    <p style='font-size: 1.05rem; line-height: 1.7; color: {COLORS['charcoal']};'>
                        {ECO_ALTERNATIVES[cat]}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # MONTHLY TREND (if enough data)
    # ========================================================================
    
    if num_purchases >= 3:
        st.markdown(f"<h2 class='section-header'>📅 Your Shopping Journey</h2>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='color-card' style='border-color: {COLORS['coral']};'>", unsafe_allow_html=True)
        
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        monthly = df.groupby('Month').agg({'Price': 'sum', 'Impact': 'sum'}).reset_index()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=monthly['Month'],
            y=monthly['Impact'],
            mode='lines+markers',
            name='CO₂ Impact',
            line=dict(color=COLORS['pink'], width=4),
            marker=dict(size=12, color=COLORS['coral'], line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor=f"{COLORS['pink']}30"
        ))
        
        fig3.update_layout(
            title="Monthly Carbon Footprint Trend",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=13),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# COLORFUL FOOTER
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='background: linear-gradient(135deg, {COLORS['deep_purple']}, {COLORS['royal_purple']}, {COLORS['ocean_blue']}, {COLORS['teal']}); 
                padding: 50px 30px; border-radius: 30px; text-align: center; 
                box-shadow: 0 20px 50px rgba(107, 70, 193, 0.2);'>
        <div style='font-size: 4rem; margin-bottom: 20px;'>🌍💚🌿</div>
        <h3 style='color: white; font-size: 2rem; margin: 0 0 15px 0; font-family: "Poppins", sans-serif; font-weight: 800;'>
            Every Choice Matters
        </h3>
        <p style='color: white; font-size: 1.2rem; opacity: 0.95; margin: 0 0 10px 0;'>
            You're making a positive impact on our planet!
        </p>
        <p style='color: white; opacity: 0.8; font-size: 0.95rem; margin: 20px 0 0 0;'>
            ShopImpact Dashboard • Sustainable Shopping Tracker • 2025
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
