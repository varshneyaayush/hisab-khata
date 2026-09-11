import streamlit as st
from datetime import date, datetime
from collections import defaultdict
import pandas as pd

from ai_assistant import ask_ai

from database import (
    create_database,
    create_user,
    login_user,
    get_user,
    get_wallet,
    set_wallet,
    add_money,
    subtract_money,
    add_expense,
    get_expenses,
    update_user_language,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Hisab Khata | AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_database()


# ============================================================
# HELPERS
# ============================================================

TRANSLATIONS = {

    "English": {
        "overview": "Overview",
        "expenses": "Expenses",
        "analytics": "Analytics",
        "ai_assistant": "AI Assistant",
        "settings": "Settings",
        "workspace": "WORKSPACE",
        "add_money": "Add money to wallet",
        "current_wallet": "Current wallet",
        "total_available": "TOTAL AVAILABLE",
        "total_spent": "TOTAL SPENT",
        "this_month": "THIS MONTH",
        "recent_transactions": "Recent transactions",
        "add_expense": "Add an expense",
        "spending_activity": "Spending activity",
        "financial_overview": "Here's your financial overview for today.",
        "personal_finance": "PERSONAL FINANCE",
        "ai_active": "✨ AI Assistant Active",
        "increase_wallet": "Increase the amount available for your expenses.",
        "available_balance": "Available balance",
        "total_available": "TOTAL AVAILABLE",
        "total_spent": "TOTAL SPENT",
        "this_month": "THIS MONTH",
        "monthly_expenses": "Your expenses this month",
        "latest_activity": "Latest activity from your ledger",
        "transaction_ledger": "TRANSACTION LEDGER",
        "user_expenses": "{username}'s expenses",
        "every_transaction": "Every transaction in one place.",
        "financial_analytics": "FINANCIAL ANALYTICS",
        "spending_analytics": "Spending analytics",
        "understand_spending": "Understand where your money goes.",
        "settings_title": "Settings",
        "settings_subtitle": "Manage your Hisab Khata preferences.",
        "language": "Language",
        "language_description": "Choose the language you want to use in Hisab Khata.",
        "choose_language": "Choose your language",
    },

    "हिंदी": {
        "overview": "ओवरव्यू",
        "expenses": "खर्चे",
        "analytics": "विश्लेषण",
        "ai_assistant": "AI सहायक",
        "settings": "सेटिंग्स",
        "workspace": "कार्यस्थल",
        "add_money": "पैसे जोड़ें",
        "current_wallet": "वर्तमान वॉलेट",
        "total_available": "कुल उपलब्ध",
        "total_spent": "कुल खर्च",
        "this_month": "इस महीने",
        "recent_transactions": "हाल के लेन-देन",
        "add_expense": "खर्च जोड़ें",
        "spending_activity": "खर्च की गतिविधि",
        "financial_overview": "आज आपके वित्तीय खर्च और बचत का पूरा विवरण यहाँ है।",
        "personal_finance": "व्यक्तिगत वित्त",
        "ai_active": "✨ AI Assistant सक्रिय है",
        "increase_wallet": "अपने खर्चों के लिए उपलब्ध राशि बढ़ाएँ।",
        "available_balance": "उपलब्ध शेष राशि",
        "total_available": "कुल उपलब्ध",
        "total_spent": "कुल खर्च",
        "this_month": "इस महीने",
        "monthly_expenses": "इस महीने के आपके खर्च",
        "latest_activity": "आपके हिसाब-किताब की हाल की गतिविधि",
        "transaction_ledger": "लेन-देन का हिसाब",
        "user_expenses": "{username} के खर्च",
        "every_transaction": "आपके सभी लेन-देन एक ही जगह।",
        "financial_analytics": "वित्तीय विश्लेषण",
        "spending_analytics": "खर्च का विश्लेषण",
        "understand_spending": "समझें कि आपका पैसा कहाँ खर्च हो रहा है।",
        "settings_title": "सेटिंग्स",
        "settings_subtitle": "अपने Hisab Khata की प्राथमिकताएँ बदलें।",
        "language": "भाषा",
        "language_description": "Hisab Khata में अपनी पसंदीदा भाषा चुनें।",
        "choose_language": "अपनी भाषा चुनें",
    },

    "Hinglish": {
        "overview": "Overview",
        "expenses": "Kharch",
        "analytics": "Spending Analysis",
        "ai_assistant": "AI Assistant",
        "settings": "Settings",
        "workspace": "WORKSPACE",
        "add_money": "Paise add karein",
        "current_wallet": "Current wallet",
        "total_available": "TOTAL AVAILABLE",
        "total_spent": "TOTAL SPENT",
        "this_month": "IS MONTH",
        "recent_transactions": "Recent transactions",
        "add_expense": "Expense add karein",
        "spending_activity": "Spending activity",
        "financial_overview": "Aaj aapke finances ka complete overview yahan hai.",
        "personal_finance": "PERSONAL FINANCE",
        "ai_active": "✨ AI Assistant Active",
        "increase_wallet": "Apne expenses ke liye available amount badhayein.",
        "available_balance": "Available balance",
        "total_available": "TOTAL AVAILABLE",
        "total_spent": "TOTAL SPENT",
        "this_month": "IS MONTH",
        "monthly_expenses": "Is month ke aapke expenses",
        "latest_activity": "Aapke hisaab-kitaab ki latest activity",
        "transaction_ledger": "TRANSACTION LEDGER",
        "user_expenses": "{username} ke expenses",
        "every_transaction": "Aapke saare transactions ek hi jagah.",
        "financial_analytics": "FINANCIAL ANALYTICS",
        "spending_analytics": "Spending analysis",
        "understand_spending": "Samjhein aapka paisa kahan ja raha hai.",
        "settings_title": "Settings",
        "settings_subtitle": "Apni Hisab Khata preferences manage karein.",
        "language": "Language",
        "language_description": "Hisab Khata mein apni preferred language choose karein.",
        "choose_language": "Apni language choose karein",
        
    }
}


def t(key):
    language = st.session_state.get(
        "language",
        "English"
    )

    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["English"]
    ).get(
        key,
        key
    )

def money(value):
    return f"₹{value:,.0f}"


def parse_date(value):
    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return None


def category_icon(category):
    icons = {
        "Food & Dining": "🍔",
        "Transport": "🚗",
        "Shopping": "🛍️",
        "Bills & Utilities": "⚡",
        "Entertainment": "🎮",
        "Health": "❤️",
        "Education": "🎓",
        "Other": "💳",
    }

    return icons.get(
        category or "Other",
        "💳"
    )


def html(content):
    st.html(content)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "language" not in st.session_state:
    st.session_state.language = "English"


# ============================================================
# THEME #8: WARM FINANCE UI SYSTEM
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap'
);

:root {
    --bg: #FFF8EE;
    --bg2: #F7EFE3;
    --card: #FFFCF7;
    --card2: #FAF2E6;
    --border: #E8D9C8;
    --border-hover: #D9C4AF;
    --text: #3B2A20;
    --text-secondary: #6B4F3A;
    --muted: #806F62;
    --primary: #E8892D;
    --primary-hover: #D9771C;
    --primary-light: #FDF2E7;
    --primary-border: #F6C89B;
    --green: #16845B;
    --green-bg: #EAF5F0;
    --green-border: #A3D9C3;
    --gold: #C46210;
    --shadow-sm: 0 4px 14px rgba(59, 42, 32, 0.04);
    --shadow-md: 0 10px 30px rgba(59, 42, 32, 0.07);
    --shadow-lg: 0 20px 45px rgba(59, 42, 32, 0.10);
}

html, body, [class*="css"] {
    font-family: "Plus Jakarta Sans", "Inter", -apple-system, sans-serif;
    color: var(--text);
}

.stApp {
    background: 
        radial-gradient(
            circle at 10% 0%,
            rgba(232, 137, 45, 0.06),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 15%,
            rgba(22, 132, 91, 0.05),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #FFF8EE 0%,
            #FAF2E6 100%
        );
    color: var(--text);
}

.block-container {
    max-width: 1450px;
    padding: 2rem 2.7rem 4rem;
}

#MainMenu, footer {
    visibility: hidden;
}

header {
    visibility: visible !important;
    background: transparent !important;
}

/* Base text color overrides */
p, span, label, h1, h2, h3, h4, h5, h6 {
    color: var(--text);
}

/* =========================================================
   LOGIN
========================================================= */

.login-page {
    min-height: 78vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-card {
    width: 100%;
    max-width: 470px;
    padding: 2.2rem;
    border-radius: 24px;
    background: var(--card);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-lg);
    animation: fadeUp 0.7s ease both;
}

.login-logo {
    width: 58px;
    height: 58px;
    display: grid;
    place-items: center;
    border-radius: 18px;
    background: linear-gradient(135deg, #E8892D, #D9771C);
    box-shadow: 0 10px 25px rgba(232, 137, 45, 0.28);
    font-size: 1.6rem;
    margin-bottom: 1.2rem;
}

.login-title {
    color: var(--text) !important;
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
}

.login-subtitle {
    color: var(--muted) !important;
    font-size: 0.88rem;
    margin-top: 0.45rem;
}

.login-divider {
    height: 1px;
    background: var(--border);
    margin: 1.4rem 0;
}

/* =========================================================
   SIDEBAR
========================================================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F7EFE3 0%, #F1E5D5 60%, #EFE1CE 100%);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
    padding: 1.4rem 1rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text);
    font-size: 1.4rem;
    font-weight: 800;
    padding: 0.4rem 0.5rem 1.8rem;
}

.brand-icon {
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    background: linear-gradient(135deg, #E8892D, #D9771C);
    box-shadow: 0 8px 20px rgba(232, 137, 45, 0.25);
    font-size: 1.2rem;
}

.sidebar-label {
    color: var(--muted);
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    margin: 1rem 0 0.5rem 0.6rem;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
}

section[data-testid="stSidebar"] label {
    border-radius: 14px;
    padding: 0.72rem 0.8rem;
    background: transparent;
    transition: all 0.22s ease;
    border: 1px solid transparent;
}

section[data-testid="stSidebar"] label:hover {
    background: rgba(232, 137, 45, 0.08);
    border-color: rgba(232, 137, 45, 0.2);
    transform: translateX(4px);
}

section[data-testid="stSidebar"] label[aria-checked="true"],
section[data-testid="stSidebar"] label:has(input:checked) {
    background: #FFFCF7 !important;
    border-color: var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}

section[data-testid="stSidebar"] label p {
    color: var(--text-secondary) !important;
    font-size: 0.84rem;
    font-weight: 700;
}

section[data-testid="stSidebar"] label[aria-checked="true"] p,
section[data-testid="stSidebar"] label:has(input:checked) p {
    color: var(--primary) !important;
    font-weight: 800;
}

.sidebar-user {
    margin-top: 2rem;
    padding: 1.1rem;
    border-radius: 16px;
    background: var(--card);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
}

.sidebar-user-name {
    color: var(--text);
    font-size: 0.85rem;
    font-weight: 800;
}

.sidebar-user-balance {
    color: var(--green);
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 4px;
}

/* =========================================================
   HERO
========================================================= */

.hero {
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 2.2rem;
    margin-bottom: 1.6rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #FDF7EE 0%, #F8EAD7 50%, #FAF0E4 100%);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-md);
    animation: fadeUp 0.65s ease both;
}

.hero::before {
    content: "";
    position: absolute;
    width: 350px;
    height: 350px;
    right: -100px;
    top: -180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(232, 137, 45, 0.15), transparent 70%);
}

.hero-content {
    position: relative;
    z-index: 2;
}

.eyebrow {
    color: var(--gold);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    margin-bottom: 0.45rem;
    text-transform: uppercase;
}

.hero-title {
    color: var(--text) !important;
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
}

.hero-subtitle {
    color: var(--text-secondary) !important;
    font-size: 0.9rem;
    margin: 0.45rem 0 0;
}

.ai-badge {
    position: relative;
    z-index: 3;
    padding: 0.65rem 1.1rem;
    border-radius: 999px;
    background: var(--primary-light);
    border: 1px solid var(--primary-border);
    color: var(--primary) !important;
    font-size: 0.76rem;
    font-weight: 800;
}

/* =========================================================
   CARDS & METRICS
========================================================= */

.metric-card {
    position: relative;
    overflow: hidden;
    min-height: 150px;
    padding: 1.4rem;
    border-radius: 20px;
    background: var(--card);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    animation: fadeUp 0.75s ease both;
}

.metric-card:hover {
    transform: translateY(-5px);
    border-color: var(--primary-border);
    box-shadow: var(--shadow-md);
}

.metric-label {
    color: var(--muted);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.metric-value {
    color: var(--text);
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-top: 0.5rem;
}

.metric-note {
    color: var(--green);
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 0.45rem;
}

.metric-note.neutral {
    color: var(--muted);
}

/* =========================================================
   PANELS
========================================================= */

.panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.4rem;
    box-shadow: var(--shadow-sm);
    animation: fadeUp 0.85s ease both;
}

.panel-title {
    color: var(--text) !important;
    font-size: 1.05rem;
    font-weight: 800;
    margin: 0;
}

.panel-caption {
    color: var(--muted) !important;
    font-size: 0.75rem;
    margin: 0.35rem 0 1rem;
}

/* =========================================================
   AI CARD
========================================================= */

.ai-card {
    position: relative;
    overflow: hidden;
    min-height: 215px;
    padding: 1.6rem;
    border-radius: 22px;
    background: linear-gradient(135deg, #FAF2E7 0%, #F5E5D3 100%);
    border: 1px solid var(--primary-border);
    box-shadow: var(--shadow-sm);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.ai-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}

.ai-label {
    color: var(--gold);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.13em;
}

.ai-title {
    color: var(--text);
    font-size: 1.15rem;
    font-weight: 800;
    margin: 0.7rem 0 0.55rem;
}

.ai-text {
    color: var(--text-secondary);
    font-size: 0.82rem;
    line-height: 1.65;
}

.ai-chip {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.45rem 0.75rem;
    border-radius: 10px;
    background: var(--primary-light);
    border: 1px solid var(--primary-border);
    color: var(--primary);
    font-size: 0.7rem;
    font-weight: 800;
}

/* =========================================================
   TRANSACTIONS
========================================================= */

.transaction {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 0.85rem 0;
    border-bottom: 1px solid var(--border);
    transition: transform 0.22s ease;
}

.transaction:last-child {
    border-bottom: none;
}

.transaction:hover {
    transform: translateX(4px);
}

.transaction-icon {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    background: var(--primary-light);
    border: 1px solid var(--primary-border);
    font-size: 1.1rem;
}

.transaction-copy {
    flex: 1;
}

.transaction-name {
    color: var(--text);
    font-size: 0.84rem;
    font-weight: 750;
}

.transaction-meta {
    color: var(--muted);
    font-size: 0.7rem;
    margin-top: 3px;
}

.transaction-value {
    color: var(--text);
    font-size: 0.88rem;
    font-weight: 800;
}

/* =========================================================
   BUDGET BAR
========================================================= */

.budget-bar {
    width: 100%;
    height: 8px;
    margin-top: 0.8rem;
    border-radius: 999px;
    background: var(--border);
    overflow: hidden;
}

.budget-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--green), var(--primary));
    transition: width 1s ease;
}

/* =========================================================
   FORM & INPUTS
========================================================= */

div[data-testid="stForm"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.4rem;
    box-shadow: var(--shadow-sm);
}

div[data-testid="stForm"] label,
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stDateInput label,
.stTextArea label {
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    font-weight: 750 !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: #FFFCF7 !important;
    color: var(--text) !important;
    font-weight: 600 !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(232, 137, 45, 0.15) !important;
}

div[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
    background: linear-gradient(135deg, #E8892D, #D9771C) !important;
    color: #FFFFFF !important;
    border: 0 !important;
    border-radius: 12px !important;
    min-height: 2.8rem !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 18px rgba(232, 137, 45, 0.22) !important;
    transition: all 0.22s ease !important;
}

div[data-testid="stFormSubmitButton"] button:hover,
button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(232, 137, 45, 0.32) !important;
    background: linear-gradient(135deg, #EF9236, #E07F22) !important;
}

/* =========================================================
   BUTTONS
========================================================= */

div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--card) !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    transition: all 0.22s ease !important;
}

div.stButton > button:hover {
    border-color: var(--primary-border) !important;
    background: var(--primary-light) !important;
    color: var(--primary) !important;
    transform: translateY(-2px) !important;
}

/* Secondary & Special Buttons */
button[kind="secondary"] {
    transition: all 0.25s ease !important;
}

div[data-testid="stHorizontalBlock"] button {
    border-radius: 999px !important;
}

div[data-testid="stHorizontalBlock"] button:hover {
    transform: translateY(-2px) !important;
    border-color: var(--primary-border) !important;
    background: var(--primary-light) !important;
    box-shadow: 0 8px 20px rgba(232, 137, 45, 0.15) !important;
}

/* Alert Styling */
.stAlert {
    border-radius: 14px !important;
    border: 1px solid var(--border) !important;
}

/* Radio button text contrast */
div[role="radiogroup"] label p {
    color: var(--text) !important;
}

/* =========================================================
   ANIMATIONS
========================================================= */

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 900px) {
    .block-container {
        padding: 1rem;
    }
    .hero {
        padding: 1.4rem;
    }
    .hero-title {
        font-size: 1.55rem;
    }
    .ai-badge {
        display: none;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN / SIGNUP SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        "<div style='height:8vh'></div>",
        unsafe_allow_html=True
    )

    login_left, login_center, login_right = st.columns(
        [1, 1.15, 1]
    )

    with login_center:

        html(
            """
            <div class="login-card">

                <div class="login-logo">
                    💰
                </div>

                <h1 class="login-title">
                    Hisab Khata
                </h1>

                <p class="login-subtitle">
                    Your intelligent personal finance assistant.
                </p>

            </div>
            """
        )

        login_mode = st.radio(
            "Account",
            ["Login", "Create account"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown(
            "<div class='login-divider'></div>",
            unsafe_allow_html=True
        )

        language = st.selectbox(
            "🌐 Choose your language",
            [
                "English",
                "हिंदी",
                "Hinglish"
                ],
                key="login_language"
        )

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )

        if login_mode == "Create account":

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Confirm your password",
            )

            if st.button(
                "Create account",
                use_container_width=True,
            ):

                if not username.strip():

                    st.error(
                        "Please enter a username."
                    )

                elif not password:

                    st.error(
                        "Please enter a password."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif len(password) < 4:

                    st.error(
                        "Password should contain at least 4 characters."
                    )

                else:

                    user_id = create_user(
                        username,
                        password,
                        language
                    )

                    if user_id:

                        st.success(
                            "Account created successfully! "
                            "You can now login."
                        )

                    else:

                        st.error(
                            "That username already exists."
                        )

        else:

            if st.button(
                "Login",
                use_container_width=True,
            ):

                user = login_user(
                    username,
                    password
                )

                if user:

                    st.session_state.logged_in = True

                    st.session_state.user_id = user[
                        "id"
                    ]

                    st.session_state.username = user[
                        "username"
                    ]
                    st.session_state.language = user[
                        "language"
                    ]

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

user_id = st.session_state.user_id

current_user = get_user(
    user_id
)

username = current_user["username"]

wallet_balance = get_wallet(
    user_id
)

expenses = get_expenses(
    user_id
)


# ============================================================
# CALCULATIONS
# ============================================================

total_spent = sum(
    float(expense["amount"])
    for expense in expenses
)

remaining_balance = max(
    wallet_balance,
    0
)

today = date.today()

month_expenses = []

for expense in expenses:

    expense_date = parse_date(
        expense["date"]
    )

    if (
        expense_date
        and expense_date.year == today.year
        and expense_date.month == today.month
    ):
        month_expenses.append(expense)


month_spent = sum(
    float(expense["amount"])
    for expense in month_expenses
)


categories = defaultdict(float)

daily_spend = defaultdict(float)

for expense in month_expenses:

    category = (
        expense["category"]
        or "Other"
    )

    amount = float(
        expense["amount"]
    )

    categories[category] += amount

    daily_spend[
        expense["date"]
    ] += amount


if categories:

    top_category = max(
        categories,
        key=categories.get
    )

    top_category_amount = categories[
        top_category
    ]

else:

    top_category = "No category yet"

    top_category_amount = 0


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html(
        """
        <div class="sidebar-brand">

            <div class="brand-icon">
                💰
            </div>

            Hisab Khata

        </div>
        """
    )

    html(
        """
        <div class="sidebar-label">
            WORKSPACE
        </div>
        """
    )

    navigation_options = {
    f"🏠  {t('overview')}": "Overview",
    f"💳  {t('expenses')}": "Expenses",
    f"📊  {t('analytics')}": "Analytics",
    f"🤖  {t('ai_assistant')}": "AI Assistant",
    f"⚙️  {t('settings')}": "Settings",
    }
    selected_navigation = st.radio(
        "Navigation",
        list(navigation_options.keys()),
        label_visibility="collapsed",
        )
    navigation = navigation_options[selected_navigation]
    
    if st.session_state.get("open_ai", False):
            navigation = "🤖  AI Assistant"
            st.session_state["open_ai"] = False
            
            html(
                f"""
                <div class="sidebar-user">
                
                <div class="sidebar-user-name">
                    ◉ {username}
                </div>

                <div class="sidebar-user-balance">
                    Balance · {money(remaining_balance)}
                </div>
                
                </div>
                """
                )

    st.markdown(
        "<div style='height:0.8rem'></div>",
        unsafe_allow_html=True
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""

        st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

if "Overview" in navigation:

    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good morning"

    elif hour < 18:
        greeting = "Good afternoon"

    else:
        greeting = "Good evening"

    html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="eyebrow">
                    {t("personal_finance")}
                </div>

                <h1 class="hero-title">
                    {greeting}, {username} 👋
                </h1>

                <p class="hero-subtitle">
                    {t("financial_overview")}
                </p>

            </div>

            

        </div>
        """
    )


    # --------------------------------------------------------
    # WALLET ACTIONS
    # --------------------------------------------------------

    wallet_col1, wallet_col2 = st.columns(
        [1.5, 1],
        gap="large"
    )

    with wallet_col1:

        html(
            f"""
            <div class="panel">

                <p class="panel-title">
                    💰 {t("add_money")}
                </p>

                <p class="panel-caption">
                    {t("increase_wallet")}
                </p>

            </div>
            """
        )

        add_amount = st.number_input(
            "Amount to add (₹)",
            min_value=0.0,
            step=500.0,
            key="wallet_add",
        )

        if st.button(
            "Add money",
            use_container_width=True,
        ):

            if add_amount <= 0:

                st.error(
                    "Enter an amount greater than zero."
                )

            else:

                add_money(
                    user_id,
                    add_amount
                )

                st.success(
                    f"{money(add_amount)} added to your wallet."
                )

                st.rerun()


    with wallet_col2:

        html(
            f"""
            <div class="panel">

                <p class="panel-title">
                    {t("current_wallet")}
                </p>

                <div
                    style="
                        color:#16845B;
                        font-size:2rem;
                        font-weight:800;
                        margin-top:0.6rem;
                    "
                >
                    {money(wallet_balance)}
                </div>

                <p class="panel-caption">
                    {t("available_balance")}
                </p>

            </div>
            """
        )


    st.markdown(
        "<div style='height:1.5rem'></div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(
        3,
        gap="large"
    )

    with col1:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    {t("total_available")}
                </div>

                <div class="metric-value">
                    {money(wallet_balance)}
                </div>

                <div class="metric-note neutral">
                    Current wallet balance
                </div>

            </div>
            """
        )


    with col2:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    {t("total_spent")}
                </div>

                <div class="metric-value">
                    {money(total_spent)}
                </div>

                <div class="metric-note">
                    {len(expenses)}
                    total transactions
                </div>

            </div>
            """
        )


    with col3:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    {t("this_month")}
                </div>

                <div class="metric-value">
                    {money(month_spent)}
                </div>

                <div class="metric-note neutral">
                    {len(month_expenses)}
                    transactions this month
                </div>

            </div>
            """
        )


    st.markdown(
        "<div style='height:1.5rem'></div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CHART + AI
    # --------------------------------------------------------

    left, right = st.columns(
        [1.65, 1],
        gap="large"
    )

    with left:

        html(
            f"""
            <div class="panel">

                <p class="panel-title">
                    {t("spending_activity")}
                </p>

                <p class="panel-caption">
                    {t("monthly_expenses")}
                </p>

            </div>
            """
        )

        if daily_spend:

            chart_data = pd.DataFrame(
                {
                    "Date": list(
                        daily_spend.keys()
                    ),
                    "Amount": list(
                        daily_spend.values()
                    ),
                }
            )

            chart_data["Date"] = pd.to_datetime(
                chart_data["Date"]
            )

            chart_data = (
                chart_data
                .sort_values("Date")
                .set_index("Date")
            )

            st.bar_chart(
                chart_data["Amount"],
                height=230
            )

        else:

            st.info(
                "Your spending trend will appear here after you add an expense.",
                icon="📊"
            )


    with right:

        if categories:

            insight_text = (
                f"{top_category} is your largest "
                f"expense category this month, "
                f"with {money(top_category_amount)} spent."
            )

            chip = (
                f"Top category · {top_category}"
            )

        else:

            insight_text = (
                "Add your first expense and "
                "Hisab Khata will start identifying "
                "your spending patterns."
            )

            chip = (
                "Waiting for your first expense"
            )

        html(
            f"""
            <div class="ai-card">

                <div class="ai-label">
                    🤖 SMART INSIGHT
                </div>

                <div class="ai-title">
                    Spend with intention
                </div>

                <div class="ai-text">
                    {insight_text}
                    You currently have
                    {money(wallet_balance)}
                    available in your wallet.
                </div>

                <div class="ai-chip">
                    {chip}
                </div>

            </div>
            """
        )


    st.markdown(
        "<div style='height:1.5rem'></div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # RECENT TRANSACTIONS + ADD EXPENSE
    # --------------------------------------------------------

    recent_col, add_col = st.columns(
        [1.45, 1],
        gap="large"
    )


    with recent_col:

        html(
            f"""
            <div class="panel">

                <p class="panel-title">
                    {t("recent_transactions")}
                </p>

                <p class="panel-caption">
                    {t("latest_activity")}
                </p>

            </div>
            """
        )

        if expenses:

            for expense in expenses[:6]:

                category = (
                    expense["category"]
                    or "Other"
                )

                html(
                    f"""
                    <div class="transaction">

                        <div class="transaction-icon">
                            {category_icon(category)}
                        </div>

                        <div class="transaction-copy">

                            <div class="transaction-name">
                                {expense["description"]}
                            </div>

                            <div class="transaction-meta">
                                {category}
                                ·
                                {expense["date"]}
                            </div>

                        </div>

                        <div class="transaction-value">
                            −{money(float(expense["amount"]))}
                        </div>

                    </div>
                    """
                )

        else:

            st.info(
                "No expenses yet. Add your first expense!",
                icon="💳"
            )


    with add_col:

        html(
            """
            <div
                style="
                    color:#3B2A20;
                    font-size:0.97rem;
                    font-weight:800;
                    margin-bottom:0.8rem;
                "
            >
                Add an expense
            </div>
            """
        )

        with st.form(
            "expense_form",
            clear_on_submit=True
        ):

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=10.0
            )

            description = st.text_input(
                "Description",
                placeholder="e.g. Swiggy dinner"
            )

            category = st.selectbox(
                "Category",
                [
                    "Food & Dining",
                    "Transport",
                    "Shopping",
                    "Bills & Utilities",
                    "Entertainment",
                    "Health",
                    "Education",
                    "Other"
                ]
            )

            expense_date = st.date_input(
                "Date",
                value=today,
                max_value=today
            )

            submitted = st.form_submit_button(
                "Save expense",
                use_container_width=True
            )

            if submitted:

                if amount <= 0:

                    st.error(
                        "Enter an amount greater than zero."
                    )

                elif amount > wallet_balance:

                    st.error(
                        f"Insufficient balance. "
                        f"You currently have "
                        f"{money(wallet_balance)}."
                    )

                elif not description.strip():

                    st.error(
                        "Please enter a description."
                    )

                else:

                    add_expense(
                        user_id,
                        amount,
                        description.strip(),
                        category,
                        expense_date.isoformat()
                    )

                    subtract_money(
                        user_id,
                        amount
                    )

                    st.success(
                        f"{money(amount)} expense saved!"
                    )

                    st.rerun()


# ============================================================
# EXPENSES PAGE
# ============================================================

elif "Expenses" in navigation:

    html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="eyebrow">
                    {t("transaction_ledger")}
                </div>

                <h1 class="hero-title">
                    {username} — {t("expenses")}
                </h1>

                <p class="hero-subtitle">
                    {t("every_transaction")}
                </p>

            </div>

        </div>
        """
    )
    ai_button_col = st.columns([4, 1])[1]

    with ai_button_col:
        if st.button(
            "✨ AI Assistant",
            key="hero_ai_button",
            use_container_width=True
        ):
            st.session_state["open_ai"] = True
            st.rerun()

    if expenses:

        for expense in expenses:

            category = (
                expense["category"]
                or "Other"
            )

            html(
                f"""
                <div class="panel"
                     style="margin-bottom:10px;">

                    <div class="transaction">

                        <div class="transaction-icon">
                            {category_icon(category)}
                        </div>

                        <div class="transaction-copy">

                            <div class="transaction-name">
                                {expense["description"]}
                            </div>

                            <div class="transaction-meta">
                                {category}
                                ·
                                {expense["date"]}
                            </div>

                        </div>

                        <div class="transaction-value">
                            −{money(float(expense["amount"]))}
                        </div>

                    </div>

                </div>
                """
            )

    else:

        st.info(
            "No expenses recorded yet.",
            icon="💳"
        )


# ============================================================
# ANALYTICS PAGE
# ============================================================

elif "Analytics" in navigation:

    html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="eyebrow">
                    {t("financial_analytics")}
                </div>

                <h1 class="hero-title">
                    {t("spending_analytics")}
                </h1>

                <p class="hero-subtitle">
                    {t("understand_spending")}
                </p>

            </div>

            <div class="ai-badge">
                📊 {t("ai_active")}
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # ANALYTICS CALCULATIONS
    # --------------------------------------------------------

    average_expense = (
        month_spent / len(month_expenses)
        if month_expenses
        else 0
    )

    if categories:

        highest_category = max(
            categories,
            key=categories.get
        )

        highest_category_amount = categories[
            highest_category
        ]

        highest_category_percent = (
            highest_category_amount / month_spent * 100
            if month_spent
            else 0
        )

    else:

        highest_category = "No data"
        highest_category_amount = 0
        highest_category_percent = 0


    # --------------------------------------------------------
    # ANALYTICS CARDS
    # --------------------------------------------------------

    a1, a2, a3, a4 = st.columns(
        4,
        gap="medium"
    )

    with a1:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    MONTHLY SPENDING
                </div>

                <div class="metric-value">
                    {money(month_spent)}
                </div>

                <div class="metric-note neutral">
                    Current month
                </div>

            </div>
            """
        )

    with a2:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    TRANSACTIONS
                </div>

                <div class="metric-value">
                    {len(month_expenses)}
                </div>

                <div class="metric-note neutral">
                    This month
                </div>

            </div>
            """
        )

    with a3:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    AVERAGE EXPENSE
                </div>

                <div class="metric-value">
                    {money(average_expense)}
                </div>

                <div class="metric-note neutral">
                    Per transaction
                </div>

            </div>
            """
        )

    with a4:

        html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    TOP CATEGORY
                </div>

                <div class="metric-value"
                     style="font-size:1.25rem;">
                    {highest_category}
                </div>

                <div class="metric-note">
                    {money(highest_category_amount)}
                    · {highest_category_percent:.0f}%
                </div>

            </div>
            """
        )


    st.markdown(
        "<div style='height:1.5rem'></div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CATEGORY + DAILY CHARTS
    # --------------------------------------------------------

    chart_left, chart_right = st.columns(
        [1, 1],
        gap="large"
    )


    # CATEGORY BREAKDOWN

    with chart_left:

        html(
            """
            <div class="panel">

                <p class="panel-title">
                    Category breakdown
                </p>

                <p class="panel-caption">
                    Where your money is going this month
                </p>

            </div>
            """
        )

        if categories:

            category_data = pd.DataFrame(
                {
                    "Category": list(
                        categories.keys()
                    ),
                    "Amount": list(
                        categories.values()
                    )
                }
            )

            category_data = category_data.sort_values(
                "Amount",
                ascending=False
            )

            st.bar_chart(
                category_data.set_index(
                    "Category"
                ),
                height=300
            )

        else:

            st.info(
                "Add expenses to see your category breakdown.",
                icon="📊"
            )


    # DAILY SPENDING

    with chart_right:

        html(
            """
            <div class="panel">

                <p class="panel-title">
                    Daily spending
                </p>

                <p class="panel-caption">
                    Your spending activity throughout the month
                </p>

            </div>
            """
        )

        if daily_spend:

            daily_data = pd.DataFrame(
                {
                    "Date": list(
                        daily_spend.keys()
                    ),
                    "Amount": list(
                        daily_spend.values()
                    )
                }
            )

            daily_data["Date"] = pd.to_datetime(
                daily_data["Date"]
            )

            daily_data = (
                daily_data
                .sort_values("Date")
                .set_index("Date")
            )

            st.line_chart(
                daily_data["Amount"],
                height=300
            )

        else:

            st.info(
                "Add expenses to see your daily spending trend.",
                icon="📈"
            )


    st.markdown(
        "<div style='height:1.5rem'></div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # TOP SPENDING CATEGORY INSIGHT
    # --------------------------------------------------------

    if categories:

        html(
            f"""
            <div class="ai-card">

                <div class="ai-label">
                    🤖 SPENDING INSIGHT
                </div>

                <div class="ai-title">
                    Your biggest spending area is {highest_category}
                </div>

                <div class="ai-text">
                    You have spent
                    <strong>{money(highest_category_amount)}</strong>
                    on {highest_category} this month,
                    which represents approximately
                    <strong>{highest_category_percent:.0f}%</strong>
                    of your monthly spending.
                </div>

                <div class="ai-chip">
                    Review this category regularly
                </div>

            </div>
            """
        )

    else:

        html(
            """
            <div class="ai-card">

                <div class="ai-label">
                    🤖 SPENDING INSIGHT
                </div>

                <div class="ai-title">
                    Your analytics are waiting
                </div>

                <div class="ai-text">
                    Add your first expense to unlock
                    detailed spending analytics.
                </div>

                <div class="ai-chip">
                    Add an expense to begin
                </div>

            </div>
            """
        )

# ============================================================
# SETTINGS PAGE
# ============================================================

elif navigation == "Settings":

    html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="eyebrow">
                    {t("settings")}
                </div>

                <h1 class="hero-title">
                    {t("settings_title")}
                </h1>

                <p class="hero-subtitle">
                    {t("settings_subtitle")}
                </p>

            </div>

        </div>
        """
    )

    html(
        f"""
        <div class="panel">

            <p class="panel-title">
                🌐 {t("language")}
            </p>

            <p class="panel-caption">
                {t("language_description")}
            </p>

        </div>
        """
    )

    language_options = [
        "English",
        "हिंदी",
        "Hinglish"
    ]

    current_language = st.session_state.get(
        "language",
        "English"
    )

    selected_language = st.selectbox(
        t("choose_language"),
        language_options,
        index=language_options.index(
            current_language
        ),
        key="settings_language"
    )

    if selected_language != current_language:

        update_user_language(
            user_id,
            selected_language
        )

        st.session_state.language = selected_language

        st.rerun()

# ============================================================
# AI ASSISTANT PAGE
# ============================================================

elif "AI Assistant" in navigation:

    html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="eyebrow">
                    INTELLIGENT FINANCE
                </div>

                <h1 class="hero-title">
                    AI Assistant
                </h1>

                <p class="hero-subtitle">
                    Ask Hisab Khata anything about your spending,
                    {username}.
                </p>

            </div>

            <div class="ai-badge">
                🤖 AI Online
            </div>

        </div>
        """
    )

    html(
    f"""
    <div class="panel">

        <p class="panel-title">
            💬 Ask your financial assistant
        </p>

        <p class="panel-caption">
            Hisab Khata AI can analyse your actual
            expenses and wallet balance.
        </p>

    </div>
    """
)

    question = st.text_area(
        "Your question",
        placeholder=(
            "Examples:\n"
            "• Where am I spending the most?\n"
            "• How much did I spend on food?\n"
            "• Analyse my spending this month.\n"
            "• Do I need to control my spending?"
        ),
        height=120,
    )

    if st.button(
        "✨ Ask Hisab Khata AI",
        use_container_width=True,
    ):

        if not question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "Hisab Khata AI is analysing your finances..."
            ):

                answer = ask_ai(
                    question=question,
                    expenses=expenses,
                    wallet_balance=wallet_balance,
                    username=username,
                    language=st.session_state.language,
                )
                
                
                if answer.startswith("Sorry, I couldn't connect"):
                    st.warning(
                        "🤖 AI is currently unavailable. "
                        "You can connect your API credits later."
                         )
                else:
                    with st.container(border=True):
                        st.markdown("### 🤖 Hisab Khata AI")
                        st.markdown(answer)


# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div
        style="
            text-align:center;
            margin-top:3rem;
            padding:1.2rem 0;
            color:#806F62;
            font-size:0.68rem;
            letter-spacing:0.02em;
        "
    >
        © 2026 Hisab Khata · All Rights Reserved
        <span style="margin:0 8px; color:#E8D9C8;">|</span>
        Designed by
        <span style="
            color:#16845B;
            font-weight:700;
        ">
            Aayush Varshney
        </span>
    </div>
    """
)