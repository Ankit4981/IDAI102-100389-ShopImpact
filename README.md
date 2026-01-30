# 🌍 ShopImpact - Conscious Shopping Dashboard

## Overview
ShopImpact is a Python Streamlit web application designed to help users track their shopping habits and understand the environmental impact of their purchases. By logging purchases and calculating CO₂ emissions, users can make more conscious shopping decisions and work towards a greener lifestyle.

## ✨ Features

### 1. **Purchase Logging**
- Log product type, brand, price, and purchase date
- Support for 9 different product categories
- Easy-to-use sidebar form interface

### 2. **Environmental Impact Tracking**
- Automatic CO₂ emission calculation based on product type
- Real-time impact dashboard
- Category-specific emission multipliers

### 3. **Live Dashboard**
- Total spending tracker
- Total CO₂ impact display
- Current eco-badge status
- Large, readable metrics with eco-friendly color theme

### 4. **Visual Analytics**
- Bar charts showing spending by category
- CO₂ impact visualization by category
- Monthly summary with trend lines
- Interactive data tables

### 5. **Eco Badges System**
- 5 achievement levels based on CO₂ savings
- Progress tracking towards next badge
- Motivational badge requirements display

### 6. **Greener Alternatives**
- Category-specific sustainable shopping suggestions
- Eco-tips rotation based on user activity
- Comprehensive alternatives guide

### 7. **Data Storage**
- In-memory storage using Python lists and dictionaries
- Session-based persistence during app runtime
- Easy data clearing option

### 8. **Eco-Friendly Design**
- Green color scheme (#2ecc71, #27ae60)
- Large, accessible text (24px+)
- Clean, professional interface
- Responsive layout

## 📊 CO₂ Emission Multipliers

| Product Category | CO₂ per Dollar |
|-----------------|----------------|
| Electronics | 0.8 kg |
| Clothing | 0.6 kg |
| Food & Groceries | 0.3 kg |
| Home & Furniture | 0.5 kg |
| Beauty & Personal Care | 0.4 kg |
| Books & Stationery | 0.2 kg |
| Toys & Games | 0.5 kg |
| Sports & Outdoor | 0.4 kg |
| Other | 0.3 kg |

## 🏆 Badge System

- 🌟 **Eco Warrior**: Save 50+ kg CO₂
- 🌿 **Green Champion**: Save 30+ kg CO₂
- 🌱 **Eco Conscious**: Save 15+ kg CO₂
- 💚 **Planet Protector**: Save 5+ kg CO₂
- 🌍 **Earth Friend**: Starting level

*CO₂ saved is calculated against a 100kg/month baseline*

## 🚀 Local Installation & Running

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Download the files**
   - Save `app.py`, `requirements.txt`, and `README.md` in the same folder

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   - Open your browser to `http://localhost:8501`
   - The app will automatically open in your default browser

## ☁️ Deploying to Streamlit Cloud

### Step 1: Prepare Your Repository
1. Create a GitHub account (if you don't have one)
2. Create a new repository (e.g., `shopimpact-dashboard`)
3. Upload these files to your repository:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch (usually `main`), and `app.py`
5. Click "Deploy"

### Step 3: Access Your App
- Your app will be available at: `https://[your-app-name].streamlit.app`
- Share this URL with others to let them use your dashboard

### Deployment Notes
- **Free tier limits**: Streamlit Cloud free tier has resource limits
- **Public apps**: Free apps are public by default
- **Updates**: Push changes to GitHub to automatically update your app
- **Sleep mode**: Free apps sleep after inactivity but wake up quickly

## 💡 How to Use

### Adding a Purchase
1. Use the sidebar form on the left
2. Select a product category
3. Enter the brand name
4. Input the price
5. Select the purchase date
6. Click "Add Purchase"

### Viewing Your Impact
- Check the main dashboard for total spend and CO₂ impact
- View your current eco-badge
- Read the rotating eco-tips
- Explore charts and monthly summaries

### Earning Badges
- Keep your CO₂ impact low by choosing sustainable products
- The lower your total CO₂, the higher your badge level
- Check badge requirements in the expandable section

### Finding Alternatives
- View greener alternatives for your most-purchased categories
- Expand "View all eco-friendly alternatives" for full list
- Apply suggestions to your next shopping trip

## 🎓 Educational Value

This project demonstrates:
- **Python Programming**: Functions, dictionaries, lists, conditionals
- **Data Structures**: Using lists and dicts for data storage
- **Streamlit Framework**: Web app development with Python
- **Data Visualization**: Charts and metrics display
- **User Interface Design**: Forms, buttons, layouts
- **Environmental Awareness**: Sustainability calculations
- **Session Management**: Streamlit session state

## 🛠️ Technical Architecture

### Data Storage
```python
# Purchase structure
{
    'product_type': str,
    'brand': str,
    'price': float,
    'date': datetime,
    'co2_impact': float
}

# Stored in session state
st.session_state.purchases = [purchase1, purchase2, ...]
```

### Key Functions
- `calculate_co2_impact()`: Computes emissions based on product and price
- `get_badge()`: Determines badge level from total CO₂
- `get_monthly_summary()`: Aggregates data by month

## 📝 Customization Ideas

1. **Add more product categories**
2. **Modify CO₂ multipliers** based on research
3. **Create custom badge levels**
4. **Add export functionality** (CSV download)
5. **Implement user authentication**
6. **Add comparison with friends**
7. **Include water footprint tracking**

## 🐛 Troubleshooting

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

### Turtle graphics not showing
- Turtle graphics are included in code but may have limited support in Streamlit Cloud
- The app works fully without turtle visualization

### Data disappears on refresh
- This is expected behavior - data is stored in session state
- For persistent storage, consider adding database integration

## 📚 Assessment Criteria Coverage

✅ **Data Structures**: Lists and dictionaries for storage  
✅ **Functions**: Multiple helper functions with clear purposes  
✅ **User Input**: Forms and interactive elements  
✅ **Calculations**: CO₂ impact computation  
✅ **Conditional Logic**: Badge assignment, data validation  
✅ **Data Visualization**: Charts and metrics  
✅ **User Experience**: Clean interface, feedback messages  
✅ **Documentation**: Comprehensive comments  
✅ **Real-world Application**: Environmental awareness  

## 📄 License

This project is created for educational purposes. Feel free to modify and extend it for your learning journey!

## 🌟 Credits

Developed as a Python programming assessment project demonstrating:
- Streamlit web development
- Environmental impact awareness
- Data-driven decision making
- Sustainable technology education

---

**Made with 💚 for a greener planet**

*Every conscious choice counts towards a sustainable future!*
