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
    get_login_history,
    update_user_language,
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hisab Khata — Luxury Fintech & Private Ledger",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_database()

# ============================================================
# MULTILINGUAL SUPPORT
# ============================================================

TRANSLATIONS = {
    "English": {
        "overview": "Overview",
        "expenses": "Expenses",
        "wallets": "Wallet & Capital",
        "analytics": "Analytics",
        "ai_assistant": "AI Assistant",
        "settings": "Settings",
        "workspace": "WORKSPACE",
        "add_money": "Add money to wallet",
        "current_wallet": "Current Vault Balance",
        "total_available": "TOTAL AVAILABLE",
        "total_spent": "TOTAL SPENT",
        "this_month": "THIS MONTH",
        "recent_transactions": "Recent Transactions",
        "add_expense": "Add an Expense",
        "spending_activity": "Spending Activity",
        "financial_overview": "Editorial financial intelligence & daily liquidity overview.",
        "personal_finance": "PRIVATE CAPITAL GOVERNANCE",
        "ai_active": "✨ Neural AI Active",
        "increase_wallet": "Infuse liquidity into your sovereign expense vault.",
        "available_balance": "Available Liquidity",
        "monthly_expenses": "Monthly expenditure velocity",
        "latest_activity": "Audited transaction records",
        "transaction_ledger": "TRANSACTION LEDGER",
        "every_transaction": "Immutable records of your capital allocation.",
        "financial_analytics": "FINANCIAL ANALYTICS & VELOCITY",
        "spending_analytics": "Spending Analytics",
        "understand_spending": "Deep algorithmic breakdown of your expenditure profile.",
        "settings_title": "Preferences & Security",
        "settings_subtitle": "Manage sovereign parameters, language, and security protocols.",
        "language": "Interface Language",
        "language_description": "Select your primary language for dialogue and ledger curation.",
        "choose_language": "Choose your language",
    },
    "हिंदी": {
        "overview": "ओवरव्यू",
        "expenses": "खर्चे",
        "wallets": "वॉलेट और पूँजी",
        "analytics": "वित्तीय विश्लेषण",
        "ai_assistant": "AI सहायक",
        "settings": "सेटिंग्स",
        "workspace": "कार्यस्थल",
        "add_money": "वॉलेट में पैसे जोड़ें",
        "current_wallet": "वर्तमान वॉलेट राशि",
        "total_available": "कुल उपलब्ध पूँजी",
        "total_spent": "कुल खर्च",
        "this_month": "इस महीने का खर्च",
        "recent_transactions": "हाल के लेन-देन",
        "add_expense": "नया खर्च जोड़ें",
        "spending_activity": "खर्च की गतिविधि",
        "financial_overview": "आज आपके वित्तीय खर्च और बचत का संपूर्ण विवरण।",
        "personal_finance": "व्यक्तिगत वित्त प्रबंधन",
        "ai_active": "✨ AI Assistant सक्रिय है",
        "increase_wallet": "अपने खर्चों के लिए उपलब्ध राशि बढ़ाएँ।",
        "available_balance": "उपलब्ध शेष राशि",
        "monthly_expenses": "इस महीने के आपके खर्च",
        "latest_activity": "आपके हिसाब-किताब की नवीनतम गतिविधि",
        "transaction_ledger": "लेन-देन का हिसाब",
        "every_transaction": "आपके सभी लेन-देन एक ही सुरक्षित जगह पर।",
        "financial_analytics": "वित्तीय विश्लेषण",
        "spending_analytics": "खर्च का विश्लेषण",
        "understand_spending": "बारीकी से समझें कि आपका पैसा कहाँ जा रहा है।",
        "settings_title": "सेटिंग्स और सुरक्षा",
        "settings_subtitle": "अपने Hisab Khata की प्राथमिकताएँ और सुरक्षा बदलें।",
        "language": "भाषा",
        "language_description": "Hisab Khata में अपनी पसंदीदा भाषा चुनें।",
        "choose_language": "अपनी भाषा चुनें",
    },
    "Hinglish": {
        "overview": "Overview",
        "expenses": "Kharch Ledger",
        "wallets": "Wallet & Capital",
        "analytics": "Spending Analytics",
        "ai_assistant": "AI Assistant",
        "settings": "Settings",
        "workspace": "WORKSPACE",
        "add_money": "Wallet mein paise add karein",
        "current_wallet": "Current Vault Balance",
        "total_available": "TOTAL AVAILABLE",
        "total_spent": "TOTAL SPENT",
        "this_month": "IS MONTH KA KHARCH",
        "recent_transactions": "Recent Transactions",
        "add_expense": "Naya Expense Add Karein",
        "spending_activity": "Spending Activity",
        "financial_overview": "Aaj aapke finances ka complete luxury overview yahan hai.",
        "personal_finance": "PRIVATE CAPITAL ARCHITECTURE",
        "ai_active": "✨ AI Assistant Active",
        "increase_wallet": "Apne ledger ke liye liquidity balance badhayein.",
        "available_balance": "Available balance",
        "monthly_expenses": "Is month ke aapke expenditure patterns",
        "latest_activity": "Aapke ledger ki latest activity",
        "transaction_ledger": "TRANSACTION LEDGER",
        "every_transaction": "Aapke saare transactions ek luxury place mein.",
        "financial_analytics": "FINANCIAL ANALYTICS",
        "spending_analytics": "Spending Analytics",
        "understand_spending": "Samjhein aapka paisa kahan aur kaise consume ho raha hai.",
        "settings_title": "Settings & Security",
        "settings_subtitle": "Apni Hisab Khata preferences aur language manage karein.",
        "language": "Language Preference",
        "language_description": "Hisab Khata mein apni preferred communication language choose karein.",
        "choose_language": "Apni language choose karein",
    },
}

def t(key):
    lang = st.session_state.get("language", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)

def money(value):
    return f"₹{value:,.0f}"

def parse_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def category_icon(category):
    icons = {
        "Food & Dining": "🍷",
        "Transport": "🚘",
        "Shopping": "🛍️",
        "Bills & Utilities": "⚡",
        "Entertainment": "🎭",
        "Health": "🌿",
        "Education": "🏛️",
        "Other": "💳",
    }
    return icons.get(category or "Other", "💳")

def html(content):
    st.html(content)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "language" not in st.session_state:
    st.session_state.language = "English"

if "show_how_it_works" not in st.session_state:
    st.session_state.show_how_it_works = False

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"

# ============================================================
# LUXURY FINTECH DESIGN SYSTEM (CSS)
# Palette:
#   Deep Burgundy: #590907
#   Warm Cream Beige: #E8D2B5
#   Muted Sage Grey: #A5A79B
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800;900&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --burgundy: #590907;
    --burgundy-dark: #3A0504;
    --burgundy-deep: #220202;
    --burgundy-light: #771210;
    --burgundy-glow: rgba(89, 9, 7, 0.28);
    --burgundy-glass: rgba(89, 9, 7, 0.08);

    --cream: #E8D2B5;
    --cream-light: #FAF6F0;
    --cream-surface: #F4EAE0;
    --cream-card: #FFFFFF;
    --cream-gold: #DFC19F;
    --cream-border: rgba(232, 210, 181, 0.55);

    --sage: #A5A79B;
    --sage-light: #D9DBD1;
    --sage-dark: #65675C;
    --sage-border: rgba(165, 167, 155, 0.35);

    --text-primary: #231614;
    --text-secondary: #584A47;
    --text-muted: #847774;
    --text-on-dark: #FAF6F0;

    --glass-surface: rgba(255, 255, 255, 0.72);
    --glass-border: rgba(232, 210, 181, 0.55);
    --shadow-subtle: 0 4px 20px rgba(89, 9, 7, 0.04);
    --shadow-medium: 0 12px 36px rgba(89, 9, 7, 0.08);
    --shadow-luxury: 0 24px 60px rgba(89, 9, 7, 0.12);
}

html, body, [class*="css"] {
    font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
    background-color: var(--cream-light);
}

.stApp {
    background: 
        radial-gradient(circle at 0% 0%, rgba(89, 9, 7, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 100% 0%, rgba(165, 167, 155, 0.12) 0%, transparent 45%),
        radial-gradient(circle at 85% 65%, rgba(232, 210, 181, 0.18) 0%, transparent 40%),
        linear-gradient(180deg, #FAF6F0 0%, #F5ECE1 100%);
    color: var(--text-primary);
    min-height: 100vh;
}

.block-container {
    max-width: 1440px;
    padding: 1.8rem 2.8rem 4rem;
}

#MainMenu, footer {
    visibility: hidden;
}

header {
    visibility: visible !important;
    background: transparent !important;
}

/* Base text overrides */
p, span, label {
    color: var(--text-primary);
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Cinzel", "Cormorant Garamond", serif;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

/* =========================================================
   SIDEBAR (LUXURY FINTECH GLASS SYSTEM)
========================================================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(250, 246, 240, 0.94) 0%, rgba(244, 234, 224, 0.96) 60%, rgba(238, 226, 214, 0.98) 100%) !important;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border-right: 1px solid var(--cream-border) !important;
    box-shadow: 4px 0 25px rgba(89, 9, 7, 0.03);
}

section[data-testid="stSidebar"] > div {
    padding: 1.6rem 1.1rem;
}

.sidebar-brand-wrapper {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0.5rem 0.6rem 1.6rem;
    border-bottom: 1px solid var(--cream-border);
    margin-bottom: 1.4rem;
}

.sidebar-emblem {
    width: 44px;
    height: 44px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%);
    border: 1px solid var(--cream);
    box-shadow: 0 8px 20px var(--burgundy-glow);
    color: var(--cream);
    font-family: "Cinzel", serif;
    font-weight: 800;
    font-size: 1.15rem;
    letter-spacing: 0.05em;
}

.sidebar-brand-title {
    font-family: "Cinzel", serif;
    font-weight: 800;
    font-size: 1.25rem;
    color: var(--burgundy);
    letter-spacing: 0.04em;
    margin: 0;
    line-height: 1.15;
}

.sidebar-brand-subtitle {
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--sage-dark);
    margin-top: 2px;
}

.sidebar-section-label {
    color: var(--sage-dark);
    font-size: 0.64rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin: 1.4rem 0 0.6rem 0.6rem;
}

/* Radio buttons inside sidebar */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
}

section[data-testid="stSidebar"] label {
    border-radius: 14px;
    padding: 0.72rem 0.9rem;
    background: transparent;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    border: 1px solid transparent;
}

section[data-testid="stSidebar"] label:hover {
    background: rgba(89, 9, 7, 0.05);
    border-color: rgba(89, 9, 7, 0.15);
    transform: translateX(4px);
}

section[data-testid="stSidebar"] label[aria-checked="true"],
section[data-testid="stSidebar"] label:has(input:checked) {
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%) !important;
    border-color: var(--burgundy) !important;
    box-shadow: 0 8px 24px var(--burgundy-glow) !important;
}

section[data-testid="stSidebar"] label p {
    color: var(--text-secondary) !important;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.01em;
}

section[data-testid="stSidebar"] label[aria-checked="true"] p,
section[data-testid="stSidebar"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700;
}

.sidebar-user-card {
    margin-top: 1.8rem;
    padding: 1.1rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(14px);
    border: 1px solid var(--cream-border);
    box-shadow: var(--shadow-subtle);
}

.sidebar-user-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.sidebar-user-tier {
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--burgundy);
    background: rgba(89, 9, 7, 0.08);
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid rgba(89, 9, 7, 0.15);
}

.sidebar-user-name {
    color: var(--text-primary);
    font-size: 0.92rem;
    font-weight: 800;
    margin-top: 0.5rem;
}

.sidebar-user-vault {
    color: var(--burgundy);
    font-size: 0.82rem;
    font-weight: 700;
    margin-top: 2px;
}

/* =========================================================
   TOP NAVIGATION BAR (LUXURY FINTECH HEADER)
========================================================= */

.luxury-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.6rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--cream-border);
    box-shadow: var(--shadow-subtle);
    margin-bottom: 1.8rem;
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.topbar-crest {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%);
    color: var(--cream);
    display: grid;
    place-items: center;
    font-family: "Cinzel", serif;
    font-size: 0.95rem;
    border: 1px solid var(--cream);
}

.topbar-title {
    font-family: "Cinzel", serif;
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--burgundy);
    margin: 0;
}

.topbar-subtitle {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--sage-dark);
    margin: 0;
}

.topbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.topbar-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.4rem 0.85rem;
    border-radius: 999px;
    background: rgba(89, 9, 7, 0.06);
    border: 1px solid rgba(89, 9, 7, 0.14);
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--burgundy);
}

.topbar-date {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
}

/* =========================================================
   LANDING PAGE — DRAMATIC DIAGONAL BURGUNDY COMPOSITION
========================================================= */

.landing-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 2.2rem;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--cream-border);
    box-shadow: var(--shadow-subtle);
    margin-bottom: 2rem;
}

.landing-nav-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.landing-nav-logo {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%);
    border: 1px solid var(--cream);
    box-shadow: 0 8px 24px var(--burgundy-glow);
    display: grid;
    place-items: center;
    color: var(--cream);
    font-family: "Cinzel", serif;
    font-weight: 800;
    font-size: 1.2rem;
}

.landing-nav-name {
    font-family: "Cinzel", serif;
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: var(--burgundy);
    margin: 0;
}

.landing-nav-tagline {
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--sage-dark);
    margin-top: 1px;
}

.landing-nav-links {
    display: flex;
    align-items: center;
    gap: 28px;
}

.landing-nav-link {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-decoration: none;
    letter-spacing: 0.02em;
    transition: color 0.2s ease;
}

.landing-nav-link:hover {
    color: var(--burgundy);
}

/* DRAMATIC DIAGONAL HERO BANNER */
.hero-diagonal-banner {
    position: relative;
    overflow: hidden;
    min-height: 520px;
    border-radius: 32px;
    background: linear-gradient(135deg, #FAF6F0 0%, #F5EAE0 50%, #EFE3D4 100%);
    border: 1px solid var(--cream-border);
    box-shadow: var(--shadow-luxury);
    margin-bottom: 2.5rem;
}

/* The iconic diagonal burgundy slice */
.hero-diagonal-banner::before {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 52%;
    height: 100%;
    background: linear-gradient(145deg, #590907 0%, #3D0605 50%, #200202 100%);
    clip-path: polygon(25% 0%, 100% 0%, 100% 100%, 0% 100%);
    z-index: 1;
}

/* Diagonal accent divider line in warm cream */
.hero-diagonal-banner::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 52%;
    height: 100%;
    background: linear-gradient(145deg, transparent 0%, rgba(232, 210, 181, 0.4) 50%, transparent 100%);
    clip-path: polygon(24.5% 0%, 25.5% 0%, 0.5% 100%, -0.5% 100%);
    z-index: 2;
    pointer-events: none;
}

.hero-diagonal-grid {
    position: relative;
    z-index: 3;
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 2.5rem;
    padding: 3.5rem 3.8rem;
    min-height: 520px;
    align-items: center;
}

.hero-left-content {
    max-width: 560px;
}

.hero-editorial-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--burgundy);
    background: rgba(89, 9, 7, 0.06);
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    border: 1px solid rgba(89, 9, 7, 0.15);
    margin-bottom: 1.4rem;
}

.hero-editorial-title {
    font-family: "Cinzel", "Cormorant Garamond", serif;
    font-size: 3.3rem;
    font-weight: 800;
    line-height: 1.08;
    color: var(--burgundy);
    letter-spacing: -0.03em;
    margin: 0 0 1.2rem;
}

.hero-editorial-title span {
    font-family: "Cormorant Garamond", serif;
    font-style: italic;
    font-weight: 500;
    color: var(--text-primary);
}

.hero-editorial-desc {
    font-size: 1.02rem;
    line-height: 1.68;
    color: var(--text-secondary);
    margin-bottom: 2rem;
}

.hero-actions-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 2.4rem;
}

.hero-pill-metrics {
    display: flex;
    align-items: center;
    gap: 24px;
    padding-top: 1.4rem;
    border-top: 1px solid var(--cream-border);
}

.hero-pill-item-val {
    font-family: "Cinzel", serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--burgundy);
}

.hero-pill-item-lbl {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--sage-dark);
}

/* RIGHT HERO: FLOATING TRANSLUCENT GLASS CARD & PREVIEWS */
.hero-right-visual {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1.5rem 0;
}

.floating-glass-card {
    position: relative;
    width: 100%;
    max-width: 410px;
    height: 250px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.28) 0%, rgba(232, 210, 181, 0.15) 100%);
    backdrop-filter: blur(28px) saturate(190%);
    -webkit-backdrop-filter: blur(28px) saturate(190%);
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-top: 1px solid rgba(255, 255, 255, 0.85);
    box-shadow: 
        0 30px 60px -10px rgba(0, 0, 0, 0.35),
        0 10px 25px rgba(89, 9, 7, 0.25),
        inset 0 1px 1px rgba(255, 255, 255, 0.6);
    padding: 1.8rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: floatCard 6s ease-in-out infinite alternate;
}

@keyframes floatCard {
    0% { transform: translateY(0px) rotate(0deg); }
    100% { transform: translateY(-10px) rotate(-1deg); }
}

.card-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.card-brand-mark {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #FAF6F0;
    font-family: "Cinzel", serif;
    font-weight: 800;
    font-size: 0.88rem;
    letter-spacing: 0.1em;
}

.card-chip {
    width: 44px;
    height: 32px;
    border-radius: 6px;
    background: linear-gradient(135deg, #E8D2B5 0%, #C4A47E 100%);
    border: 1px solid #FAF6F0;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
}

.card-balance-block {
    margin: 0.8rem 0;
}

.card-balance-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: rgba(250, 246, 240, 0.75);
}

.card-balance-value {
    font-family: "Cinzel", serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #FAF6F0;
    letter-spacing: 0.02em;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.card-bottom-row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}

.card-number {
    font-family: "Space Grotesk", monospace;
    font-size: 0.88rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    color: rgba(250, 246, 240, 0.9);
}

.card-holder {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #E8D2B5;
}

/* FLOATING TRANSACTION PREVIEWS AROUND CARD */
.floating-tx-chip {
    position: absolute;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.65rem 1rem;
    border-radius: 16px;
    background: rgba(250, 246, 240, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(232, 210, 181, 0.8);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
    z-index: 4;
    transition: transform 0.3s ease;
}

.floating-tx-chip:hover {
    transform: scale(1.04);
}

.floating-tx-top {
    top: -24px;
    right: 15px;
}

.floating-tx-bottom {
    bottom: -28px;
    left: 20px;
}

.floating-tx-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: var(--burgundy);
    color: var(--cream);
    display: grid;
    place-items: center;
    font-size: 0.9rem;
}

.floating-tx-text {
    display: flex;
    flex-direction: column;
}

.floating-tx-name {
    font-size: 0.78rem;
    font-weight: 750;
    color: var(--text-primary);
}

.floating-tx-val {
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--burgundy);
}

/* =========================================================
   FEATURE PILLARS (EDITORIAL FINTECH HIGHLIGHTS)
========================================================= */

.pillar-card {
    position: relative;
    padding: 2rem;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--cream-border);
    border-top: 1px solid rgba(255, 255, 255, 0.85);
    box-shadow: var(--shadow-subtle);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.pillar-card:hover {
    transform: translateY(-6px);
    border-color: var(--cream);
    box-shadow: var(--shadow-medium);
}

.pillar-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%);
    color: var(--cream);
    display: grid;
    place-items: center;
    font-size: 1.25rem;
    box-shadow: 0 8px 20px var(--burgundy-glow);
    margin-bottom: 1.2rem;
}

.pillar-title {
    font-family: "Cinzel", serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--burgundy);
    margin: 0 0 0.5rem;
}

.pillar-desc {
    font-size: 0.86rem;
    line-height: 1.6;
    color: var(--text-secondary);
    margin: 0;
}

/* =========================================================
   AUTHENTICATION CARD (LOGIN / CREATE ACCOUNT)
========================================================= */

.auth-glass-card {
    max-width: 480px;
    margin: 0 auto;
    padding: 2.4rem;
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--cream-border);
    border-top: 1px solid rgba(255, 255, 255, 0.95);
    box-shadow: var(--shadow-luxury);
}

.auth-crest {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%);
    border: 1px solid var(--cream);
    box-shadow: 0 10px 28px var(--burgundy-glow);
    display: grid;
    place-items: center;
    color: var(--cream);
    font-family: "Cinzel", serif;
    font-size: 1.6rem;
    margin: 0 auto 1.2rem;
}

.auth-header-title {
    text-align: center;
    font-family: "Cinzel", serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--burgundy);
    margin: 0 0 0.4rem;
}

.auth-header-subtitle {
    text-align: center;
    font-size: 0.86rem;
    color: var(--sage-dark);
    margin: 0 0 1.6rem;
}

/* =========================================================
   DASHBOARD HERO & METRICS
========================================================= */

.dash-hero {
    position: relative;
    overflow: hidden;
    padding: 2.2rem 2.6rem;
    border-radius: 28px;
    background: linear-gradient(135deg, #FAF6F0 0%, #F5EAE0 60%, #EFE3D4 100%);
    border: 1px solid var(--cream-border);
    box-shadow: var(--shadow-medium);
    margin-bottom: 2rem;
}

.dash-hero-eyebrow {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--burgundy);
    margin-bottom: 0.4rem;
}

.dash-hero-title {
    font-family: "Cinzel", serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--burgundy);
    margin: 0 0 0.4rem;
}

.dash-hero-subtitle {
    font-size: 0.92rem;
    color: var(--text-secondary);
    margin: 0;
}

.metric-card-luxury {
    position: relative;
    overflow: hidden;
    padding: 1.6rem;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--cream-border);
    border-top: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: var(--shadow-subtle);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    min-height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-card-luxury:hover {
    transform: translateY(-5px);
    border-color: var(--cream);
    box-shadow: var(--shadow-medium);
}

.metric-card-luxury.burgundy-card {
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%);
    border-color: var(--burgundy-light);
    color: #FAF6F0;
    box-shadow: 0 14px 35px var(--burgundy-glow);
}

.metric-card-luxury.burgundy-card .metric-lbl {
    color: rgba(250, 246, 240, 0.8);
}

.metric-card-luxury.burgundy-card .metric-val {
    color: #FAF6F0;
}

.metric-card-luxury.burgundy-card .metric-note {
    color: var(--cream);
}

.metric-lbl {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--sage-dark);
}

.metric-val {
    font-family: "Cinzel", serif;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--burgundy);
    margin: 0.4rem 0;
}

.metric-note {
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--text-secondary);
}

/* =========================================================
   PANELS & AI CARDS
========================================================= */

.panel-luxury {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--cream-border);
    border-top: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 22px;
    padding: 1.6rem;
    box-shadow: var(--shadow-subtle);
    margin-bottom: 1.5rem;
}

.panel-title-luxury {
    font-family: "Cinzel", serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--burgundy);
    margin: 0;
}

.panel-subtitle-luxury {
    font-size: 0.78rem;
    color: var(--sage-dark);
    margin: 0.3rem 0 1rem;
}

.ai-card-luxury {
    position: relative;
    overflow: hidden;
    padding: 1.8rem;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(250, 246, 240, 0.9) 0%, rgba(244, 234, 224, 0.85) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--cream);
    box-shadow: var(--shadow-subtle);
    transition: all 0.3s ease;
}

.ai-card-luxury:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
}

.ai-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--burgundy);
    background: rgba(89, 9, 7, 0.08);
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    border: 1px solid rgba(89, 9, 7, 0.16);
}

.ai-title-luxury {
    font-family: "Cinzel", serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--burgundy);
    margin: 0.8rem 0 0.5rem;
}

.ai-body-luxury {
    font-size: 0.88rem;
    line-height: 1.65;
    color: var(--text-secondary);
}

.ai-chip-luxury {
    display: inline-block;
    margin-top: 1.1rem;
    padding: 0.45rem 0.85rem;
    border-radius: 12px;
    background: rgba(89, 9, 7, 0.06);
    border: 1px solid rgba(89, 9, 7, 0.15);
    color: var(--burgundy);
    font-size: 0.74rem;
    font-weight: 800;
}

/* =========================================================
   TRANSACTION ROWS (LUXURY LEDGER SYSTEM)
========================================================= */

.transaction-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.95rem 1.1rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--cream-border);
    margin-bottom: 0.6rem;
    transition: all 0.22s ease;
}

.transaction-row:hover {
    transform: translateX(4px);
    background: #FFFFFF;
    border-color: var(--cream);
    box-shadow: var(--shadow-subtle);
}

.tx-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.tx-icon-frame {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: rgba(89, 9, 7, 0.06);
    border: 1px solid rgba(89, 9, 7, 0.12);
    display: grid;
    place-items: center;
    font-size: 1.15rem;
}

.tx-info-desc {
    font-size: 0.88rem;
    font-weight: 750;
    color: var(--text-primary);
}

.tx-info-meta {
    font-size: 0.72rem;
    color: var(--sage-dark);
    margin-top: 2px;
}

.tx-amount {
    font-family: "Cinzel", serif;
    font-size: 0.96rem;
    font-weight: 800;
    color: var(--burgundy);
}

/* =========================================================
   FORMS, INPUTS & BUTTONS
========================================================= */

div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.78) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--cream-border) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 22px !important;
    padding: 1.6rem !important;
    box-shadow: var(--shadow-subtle) !important;
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
    letter-spacing: 0.02em !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
    border: 1px solid var(--cream-border) !important;
    background: #FFFFFF !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.2s ease !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--burgundy) !important;
    box-shadow: 0 0 0 3px rgba(89, 9, 7, 0.12) !important;
}

/* Primary buttons */
div[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
    background: linear-gradient(135deg, var(--burgundy) 0%, var(--burgundy-dark) 100%) !important;
    color: #FAF6F0 !important;
    border: 1px solid rgba(232, 210, 181, 0.3) !important;
    border-radius: 12px !important;
    min-height: 2.85rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    box-shadow: 0 8px 24px var(--burgundy-glow) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stFormSubmitButton"] button:hover,
button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 30px rgba(89, 9, 7, 0.4) !important;
    background: linear-gradient(135deg, var(--burgundy-light) 0%, var(--burgundy) 100%) !important;
}

/* Secondary & Standard buttons */
div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid var(--cream-border) !important;
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div.stButton > button:hover {
    border-color: var(--burgundy) !important;
    background: rgba(89, 9, 7, 0.05) !important;
    color: var(--burgundy) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-subtle) !important;
}

/* =========================================================
   RESPONSIVE DESIGN
========================================================= */

@media (max-width: 960px) {
    .block-container {
        padding: 1rem 1.2rem;
    }
    .hero-diagonal-banner::before {
        width: 100%;
        height: 40%;
        top: auto;
        bottom: 0;
        clip-path: polygon(0 15%, 100% 0%, 100% 100%, 0% 100%);
    }
    .hero-diagonal-grid {
        grid-template-columns: 1fr;
        padding: 2.2rem 1.8rem;
    }
    .hero-editorial-title {
        font-size: 2.4rem;
    }
    .landing-nav-links {
        display: none;
    }
    .floating-tx-chip {
        display: none;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# LANDING PAGE & AUTHENTICATION (WHEN LOGGED OUT)
# Recreating the exact visual direction of the reference image:
# - Premium navigation bar with Hisab Khata branding
# - Elegant logo treatment
# - Large, bold editorial typography
# - Dramatic diagonal burgundy composition
# - Sage grey and warm beige background sections
# - Floating translucent glass financial balance card
# - Attractive transaction previews
# ============================================================

if not st.session_state.logged_in:

    # 1. LUXURY NAVIGATION BAR
    html(
        """
        <nav class="landing-nav">
            <div class="landing-nav-brand">
                <div class="landing-nav-logo">HK</div>
                <div>
                    <h2 class="landing-nav-name">HISAB KHATA</h2>
                    <div class="landing-nav-tagline">Haute Wealth & Neural FinTech</div>
                </div>
            </div>
            <div class="landing-nav-links">
                <span class="landing-nav-link">Private Capital</span>
                <span class="landing-nav-link">Sovereign Vault</span>
                <span class="landing-nav-link">Neural Intelligence</span>
                <span class="landing-nav-link">Ledger Audit</span>
            </div>
        </nav>
        """
    )

    # 2. DRAMATIC DIAGONAL BURGUNDY HERO COMPOSITION
    html(
        """
        <div class="hero-diagonal-banner">
            <div class="hero-diagonal-grid">
                
                <!-- Left: Warm Cream & Sage Grey Editorial Section -->
                <div class="hero-left-content">
                    <div class="hero-editorial-eyebrow">
                        <span>✦</span> PRIVATE CAPITAL ARCHITECTURE
                    </div>
                    
                    <h1 class="hero-editorial-title">
                        Financial Precision,<br>
                        <span>Curated in Grandeur.</span>
                    </h1>
                    
                    <p class="hero-editorial-desc">
                        Hisab Khata elevates daily expense management into an editorial symphony of precision. 
                        Govern your capital reserves, illuminate hidden spending velocities, and consult private 
                        neural intelligence — engineered with bespoke glassmorphic refinement.
                    </p>
                    
                    <div class="hero-pill-metrics">
                        <div>
                            <div class="hero-pill-item-val">₹ 18.5 Cr+</div>
                            <div class="hero-pill-item-lbl">Ledgers Governed</div>
                        </div>
                        <div>
                            <div class="hero-pill-item-val">99.98%</div>
                            <div class="hero-pill-item-lbl">Audit Accuracy</div>
                        </div>
                        <div>
                            <div class="hero-pill-item-val">100%</div>
                            <div class="hero-pill-item-lbl">Data Sovereignty</div>
                        </div>
                    </div>
                </div>

                <!-- Right: Dramatic Diagonal Burgundy Section with Floating Glass Card -->
                <div class="hero-right-visual">
                    
                    <!-- Floating Top Transaction Chip -->
                    <div class="floating-tx-chip floating-tx-top">
                        <div class="floating-tx-icon">🛍️</div>
                        <div class="floating-tx-text">
                            <span class="floating-tx-name">Savile Row Bespoke</span>
                            <span class="floating-tx-val">−₹ 18,500</span>
                        </div>
                    </div>

                    <!-- Translucent Glass Financial Balance Card -->
                    <div class="floating-glass-card">
                        <div class="card-top-row">
                            <div class="card-brand-mark">
                                <span>⚜️</span> HISAB KHATA · SOVEREIGN
                            </div>
                            <div class="card-chip"></div>
                        </div>
                        
                        <div class="card-balance-block">
                            <div class="card-balance-label">Total Liquid Capital</div>
                            <div class="card-balance-value">₹ 2,48,500.00</div>
                        </div>
                        
                        <div class="card-bottom-row">
                            <div>
                                <div class="card-number">•••• •••• •••• 9418</div>
                                <div class="card-holder">AAYUSH VARSHNEY</div>
                            </div>
                            <div style="font-size: 1.5rem; color: #E8D2B5;">◈</div>
                        </div>
                    </div>

                    <!-- Floating Bottom Transaction Chip -->
                    <div class="floating-tx-chip floating-tx-bottom">
                        <div class="floating-tx-icon">📈</div>
                        <div class="floating-tx-text">
                            <span class="floating-tx-name">Private Equity Dividend</span>
                            <span class="floating-tx-val" style="color: #1B7A4D;">+₹ 95,000</span>
                        </div>
                    </div>

                </div>

            </div>
        </div>
        """
    )

    # 3. INTERACTIVE AUTHENTICATION & ACCESS PORTAL
    auth_col1, auth_col2 = st.columns([1.1, 1], gap="large")

    with auth_col1:
        html(
            """
            <div style="padding: 1.5rem 0;">
                <div class="hero-editorial-eyebrow">
                    <span>◈</span> THE SOVEREIGN SYSTEM
                </div>
                <h2 style="font-family: 'Cinzel', serif; font-size: 2.1rem; color: #590907; margin-bottom: 1rem;">
                    Bespoke Financial Architecture
                </h2>
                <p style="font-size: 0.98rem; line-height: 1.7; color: #584A47; margin-bottom: 1.8rem;">
                    Step into an uncompromising standard of wealth governance. Designed for individuals who demand 
                    clarity, discretion, and high aesthetic discipline.
                </p>
            </div>
            """
        )

        p1, p2 = st.columns(2)
        with p1:
            html(
                """
                <div class="pillar-card">
                    <div class="pillar-icon-box">💼</div>
                    <div>
                        <div class="pillar-title">Vault Architecture</div>
                        <div class="pillar-desc">Multi-tier liquidity buffers with real-time runway tracking and zero latency updates.</div>
                    </div>
                </div>
                """
            )
        with p2:
            html(
                """
                <div class="pillar-card">
                    <div class="pillar-icon-box">🤖</div>
                    <div>
                        <div class="pillar-title">Neural Advisory</div>
                        <div class="pillar-desc">Contextual AI that analyses ledger trends in English, Hindi, and Hinglish.</div>
                    </div>
                </div>
                """
            )

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        p3, p4 = st.columns(2)
        with p3:
            html(
                """
                <div class="pillar-card">
                    <div class="pillar-icon-box">📊</div>
                    <div>
                        <div class="pillar-title">Editorial Analytics</div>
                        <div class="pillar-desc">Bespoke velocity metrics, burn rates, and categorical expenditure distributions.</div>
                    </div>
                </div>
                """
            )
        with p4:
            html(
                """
                <div class="pillar-card">
                    <div class="pillar-icon-box">🔒</div>
                    <div>
                        <div class="pillar-title">Cryptographic Safety</div>
                        <div class="pillar-desc">Local SHA-256 encrypted authentication and sovereign SQLite ledger protection.</div>
                    </div>
                </div>
                """
            )

    with auth_col2:
        html(
            """
            <div class="auth-glass-card">
                <div class="auth-crest">HK</div>
                <h2 class="auth-header-title">Enter Your Ledger</h2>
                <p class="auth-header-subtitle">Select mode and enter your private credentials</p>
            </div>
            """
        )

        auth_mode = st.radio(
            "Account Access Mode",
            ["Sign In", "Create Sovereign Account"],
            horizontal=True,
            label_visibility="collapsed",
        )

        auth_lang = st.selectbox(
            "🌐 Communication Language",
            ["English", "हिंदी", "Hinglish"],
            key="landing_lang_select"
        )

        login_user_input = st.text_input(
            "Username",
            placeholder="Enter your member username",
            key="login_user_input"
        )

        login_pass_input = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your security passphrase",
            key="login_pass_input"
        )

        if auth_mode == "Create Sovereign Account":
            confirm_pass_input = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm your security passphrase",
                key="signup_confirm_pass"
            )

            if st.button("Establish Ledger Account", use_container_width=True, type="primary"):
                if not login_user_input.strip():
                    st.error("Please provide a valid username.")
                elif not login_pass_input:
                    st.error("Please enter a security passphrase.")
                elif login_pass_input != confirm_pass_input:
                    st.error("Passwords do not match.")
                elif len(login_pass_input) < 4:
                    st.error("Passphrase must be at least 4 characters.")
                else:
                    new_uid = create_user(login_user_input, login_pass_input, auth_lang)
                    if new_uid:
                        st.success("Sovereign account created successfully. You may now Sign In.")
                    else:
                        st.error("That username already exists in the ledger registry.")
        else:
            if st.button("Sign In to Sovereign Vault", use_container_width=True, type="primary"):
                user = login_user(login_user_input, login_pass_input)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.language = user["language"]
                    st.rerun()
                else:
                    st.error("Invalid username or passphrase.")

        st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)

        # FAST 1-CLICK DEMO ACCESS
        if st.button("⚜️ Quick Access Demo (Aayush)", use_container_width=True):
            user = get_user(1)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]
                st.session_state.language = "Hinglish"
                st.rerun()
            else:
                demo_id = create_user("Aayush", "demo123", "English")
                st.session_state.logged_in = True
                st.session_state.user_id = demo_id
                st.session_state.username = "Aayush"
                st.session_state.language = "English"
                st.rerun()

    # LUXURY EDITORIAL FOOTER (LOGGED OUT)
    html(
        """
        <div style="text-align: center; margin-top: 4.5rem; padding: 2rem 0; border-top: 1px solid rgba(232, 210, 181, 0.45); color: #847774; font-size: 0.76rem; letter-spacing: 0.08em;">
            HISAB KHATA · PRIVATE WEALTH & EXPENSE ARCHITECTURE
            <span style="margin: 0 12px; color: #590907;">◈</span>
            HAUTE FINTECH EDITION
            <span style="margin: 0 12px; color: #590907;">◈</span>
            DESIGNED BY <strong style="color: #590907;">AAYUSH VARSHNEY</strong>
        </div>
        """
    )
    st.stop()


# ============================================================
# LOGGED IN APPLICATION DASHBOARD
# Includes:
#   1. Overview Dashboard
#   2. Expense Management
#   3. Income & Wallet Management
#   4. Analytics & Reports
#   5. AI Financial Assistant
#   6. Profile & Settings
# ============================================================

user_id = st.session_state.user_id
current_user = get_user(user_id)
username = current_user["username"] if current_user else "Member"
wallet_balance = get_wallet(user_id)
expenses = get_expenses(user_id)

total_spent = sum(float(exp["amount"]) for exp in expenses)
remaining_balance = max(wallet_balance, 0)
today = date.today()

month_expenses = []
for exp in expenses:
    exp_date = parse_date(exp["date"])
    if exp_date and exp_date.year == today.year and exp_date.month == today.month:
        month_expenses.append(exp)

month_spent = sum(float(exp["amount"]) for exp in month_expenses)

categories = defaultdict(float)
daily_spend = defaultdict(float)

for exp in month_expenses:
    cat = exp["category"] or "Other"
    amt = float(exp["amount"])
    categories[cat] += amt
    daily_spend[exp["date"]] += amt

if categories:
    top_category = max(categories, key=categories.get)
    top_category_amount = categories[top_category]
    top_category_percent = (top_category_amount / month_spent * 100) if month_spent > 0 else 0
else:
    top_category = "No category yet"
    top_category_amount = 0
    top_category_percent = 0

# Financial Runway Calculation
days_in_month = today.day
daily_burn_rate = (month_spent / days_in_month) if days_in_month > 0 else 0
runway_days = int(wallet_balance / daily_burn_rate) if daily_burn_rate > 0 else 999


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    html(
        """
        <div class="sidebar-brand-wrapper">
            <div class="sidebar-emblem">HK</div>
            <div>
                <h1 class="sidebar-brand-title">HISAB KHATA</h1>
                <div class="sidebar-brand-subtitle">Haute Wealth Ledger</div>
            </div>
        </div>
        """
    )

    html(
        f"""
        <div class="sidebar-section-label">
            {t("workspace")}
        </div>
        """
    )

    nav_options = {
        f"🏛️  {t('overview')}": "Overview",
        f"💳  {t('expenses')}": "Expenses",
        f"💼  {t('wallets')}": "Wallets",
        f"📊  {t('analytics')}": "Analytics",
        f"🤖  {t('ai_assistant')}": "AI Assistant",
        f"⚙️  {t('settings')}": "Settings",
    }

    selected_nav_label = st.radio(
        "Workspace Navigation",
        list(nav_options.keys()),
        label_visibility="collapsed",
    )
    navigation = nav_options[selected_nav_label]

    # Sidebar user balance widget
    html(
        f"""
        <div class="sidebar-user-card">
            <div class="sidebar-user-header">
                <span class="sidebar-user-tier">Sovereign Tier</span>
                <span style="color: #590907; font-size: 0.85rem;">◈</span>
            </div>
            <div class="sidebar-user-name">⚜️ {username}</div>
            <div class="sidebar-user-vault">Vault · {money(remaining_balance)}</div>
        </div>
        """
    )

    st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)

    if st.button("🚪 Sovereign Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.rerun()


# ============================================================
# TOP NAVIGATION BAR
# ============================================================

hour = datetime.now().hour
if hour < 12:
    greeting = "Good morning"
elif hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

current_date_str = datetime.now().strftime("%A, %d %B %Y")

html(
    f"""
    <div class="luxury-topbar">
        <div class="topbar-left">
            <div class="topbar-crest">HK</div>
            <div>
                <h3 class="topbar-title">{greeting}, {username}</h3>
                <p class="topbar-subtitle">Hisab Khata Private Ledger & Liquidity Architecture</p>
            </div>
        </div>
        <div class="topbar-right">
            <div class="topbar-badge">
                <span>●</span> Neural AI Online
            </div>
            <div class="topbar-date">
                📅 {current_date_str}
            </div>
        </div>
    </div>
    """
)


# ============================================================
# 1. OVERVIEW DASHBOARD
# ============================================================

if navigation == "Overview":

    # Hero Banner
    html(
        f"""
        <div class="dash-hero">
            <div class="dash-hero-eyebrow">
                {t("personal_finance")}
            </div>
            <h1 class="dash-hero-title">
                {greeting}, {username} ⚜️
            </h1>
            <p class="dash-hero-subtitle">
                {t("financial_overview")} Current liquidity runway is estimated at <strong>{runway_days if runway_days < 900 else '365+'} days</strong>.
            </p>
        </div>
        """
    )

    # 4 PRIMARY METRIC CARDS
    m1, m2, m3, m4 = st.columns(4, gap="medium")

    with m1:
        html(
            f"""
            <div class="metric-card-luxury burgundy-card">
                <div class="metric-lbl">{t("total_available")}</div>
                <div class="metric-val">{money(wallet_balance)}</div>
                <div class="metric-note">Liquid Sovereign Capital</div>
            </div>
            """
        )

    with m2:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">{t("total_spent")}</div>
                <div class="metric-val">{money(total_spent)}</div>
                <div class="metric-note">{len(expenses)} total ledger entries</div>
            </div>
            """
        )

    with m3:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">{t("this_month")}</div>
                <div class="metric-val">{money(month_spent)}</div>
                <div class="metric-note">{len(month_expenses)} entries this month</div>
            </div>
            """
        )

    with m4:
        health_status = "Optimal Reserve" if wallet_balance > month_spent else "Active Allocation"
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">ESTIMATED RUNWAY</div>
                <div class="metric-val">{runway_days if runway_days < 900 else '365+'} D</div>
                <div class="metric-note" style="color: #590907; font-weight: 800;">{health_status}</div>
            </div>
            """
        )

    st.markdown("<div style='height: 1.6rem'></div>", unsafe_allow_html=True)

    # QUICK WALLET REPLENISHMENT & CHARTS ROW
    left_dash_col, right_dash_col = st.columns([1.6, 1], gap="large")

    with left_dash_col:
        html(
            f"""
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">{t("spending_activity")}</h4>
                <div class="panel-subtitle-luxury">{t("monthly_expenses")}</div>
            </div>
            """
        )

        if daily_spend:
            chart_df = pd.DataFrame({
                "Date": list(daily_spend.keys()),
                "Amount": list(daily_spend.values()),
            })
            chart_df["Date"] = pd.to_datetime(chart_df["Date"])
            chart_df = chart_df.sort_values("Date").set_index("Date")
            st.bar_chart(chart_df["Amount"], height=240)
        else:
            st.info("Your spending trajectory will render here once expenses are logged.", icon="📊")

    with right_dash_col:
        # AI SMART INSIGHT CARD
        if categories:
            insight_msg = f"{top_category} constitutes your primary allocation this month with {money(top_category_amount)} recorded ({top_category_percent:.0f}% of total outflow)."
            chip_lbl = f"Top Outflow · {top_category}"
        else:
            insight_msg = "Record your first expense to activate Hisab Khata's deep spending pattern recognition algorithms."
            chip_lbl = "Awaiting initial ledger entry"

        html(
            f"""
            <div class="ai-card-luxury">
                <div class="ai-badge-pill">
                    <span>🤖</span> SMART LEDGER INSIGHT
                </div>
                <div class="ai-title-luxury">Spend with Intention</div>
                <div class="ai-body-luxury">
                    {insight_msg} You maintain <strong>{money(wallet_balance)}</strong> in available liquidity reserves.
                </div>
                <div class="ai-chip-luxury">
                    {chip_lbl}
                </div>
            </div>
            """
        )

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        # QUICK CAPITAL INJECTION ACCORDION / WIDGET
        with st.expander("⚡ Quick Capital Injection to Vault", expanded=False):
            quick_add_amt = st.number_input("Infuse Capital (₹)", min_value=0.0, step=1000.0, key="quick_add_vault")
            if st.button("Credit Capital", use_container_width=True, type="primary"):
                if quick_add_amt > 0:
                    add_money(user_id, quick_add_amt)
                    st.success(f"{money(quick_add_amt)} added to sovereign vault.")
                    st.rerun()

    st.markdown("<div style='height: 1.6rem'></div>", unsafe_allow_html=True)

    # RECENT TRANSACTIONS + QUICK ADD EXPENSE
    tx_col, add_col = st.columns([1.5, 1], gap="large")

    with tx_col:
        html(
            f"""
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">{t("recent_transactions")}</h4>
                <div class="panel-subtitle-luxury">{t("latest_activity")}</div>
            </div>
            """
        )

        if expenses:
            for exp in expenses[:6]:
                cat = exp["category"] or "Other"
                html(
                    f"""
                    <div class="transaction-row">
                        <div class="tx-left">
                            <div class="tx-icon-frame">{category_icon(cat)}</div>
                            <div>
                                <div class="tx-info-desc">{exp["description"]}</div>
                                <div class="tx-info-meta">{cat} · {exp["date"]}</div>
                            </div>
                        </div>
                        <div class="tx-amount">−{money(float(exp["amount"]))}</div>
                    </div>
                    """
                )
        else:
            st.info("No expense records found. Add your first transaction on the right.", icon="💳")

    with add_col:
        html(
            f"""
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">{t("add_expense")}</h4>
                <div class="panel-subtitle-luxury">Record a verified capital outflow</div>
            </div>
            """
        )

        with st.form("quick_expense_form", clear_on_submit=True):
            exp_amt = st.number_input("Amount (₹)", min_value=0.0, step=50.0)
            exp_desc = st.text_input("Description", placeholder="e.g. Bespoke tailoring / Swiggy Gourmet")
            exp_cat = st.selectbox(
                "Category",
                [
                    "Food & Dining",
                    "Transport",
                    "Shopping",
                    "Bills & Utilities",
                    "Entertainment",
                    "Health",
                    "Education",
                    "Other",
                ]
            )
            exp_dt = st.date_input("Date", value=today, max_value=today)
            submit_exp = st.form_submit_button("Record Transaction", use_container_width=True)

            if submit_exp:
                if exp_amt <= 0:
                    st.error("Please enter an amount greater than zero.")
                elif exp_amt > wallet_balance:
                    st.error(f"Insufficient vault liquidity. Current reserve: {money(wallet_balance)}.")
                elif not exp_desc.strip():
                    st.error("Please provide a valid description.")
                else:
                    add_expense(user_id, exp_amt, exp_desc.strip(), exp_cat, exp_dt.isoformat())
                    subtract_money(user_id, exp_amt)
                    st.success(f"{money(exp_amt)} successfully logged!")
                    st.rerun()


# ============================================================
# 2. EXPENSE MANAGEMENT
# ============================================================

elif navigation == "Expenses":

    html(
        f"""
        <div class="dash-hero">
            <div class="dash-hero-eyebrow">{t("transaction_ledger")}</div>
            <h1 class="dash-hero-title">{username} — {t("expenses")}</h1>
            <p class="dash-hero-subtitle">{t("every_transaction")}</p>
        </div>
        """
    )

    # Filtering controls
    filter_col1, filter_col2, filter_col3 = st.columns([1.5, 1.5, 1], gap="medium")

    with filter_col1:
        cat_filter = st.selectbox(
            "Filter by Category",
            ["All Categories", "Food & Dining", "Transport", "Shopping", "Bills & Utilities", "Entertainment", "Health", "Education", "Other"]
        )

    with filter_col2:
        search_query = st.text_input("Search Ledger by Description", placeholder="Type keywords...")

    with filter_col3:
        st.markdown("<div style='height: 1.8rem'></div>", unsafe_allow_html=True)
        if st.button("✨ Ask AI About Expenses", use_container_width=True):
            st.session_state["open_ai"] = True
            st.rerun()

    # Filter evaluation
    filtered_expenses = expenses
    if cat_filter != "All Categories":
        filtered_expenses = [e for e in filtered_expenses if (e["category"] or "Other") == cat_filter]
    if search_query.strip():
        filtered_expenses = [e for e in filtered_expenses if search_query.lower() in e["description"].lower()]

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # Metrics summary for filtered
    filtered_total = sum(float(e["amount"]) for e in filtered_expenses)
    f1, f2, f3 = st.columns(3)
    with f1:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">FILTERED ENTRIES</div>
                <div class="metric-val">{len(filtered_expenses)}</div>
                <div class="metric-note">Matching records</div>
            </div>
            """
        )
    with f2:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">TOTAL ALLOCATED</div>
                <div class="metric-val">{money(filtered_total)}</div>
                <div class="metric-note">Sum of filtered transactions</div>
            </div>
            """
        )
    with f3:
        avg_filtered = (filtered_total / len(filtered_expenses)) if filtered_expenses else 0
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">AVERAGE TICKET</div>
                <div class="metric-val">{money(avg_filtered)}</div>
                <div class="metric-note">Per transaction</div>
            </div>
            """
        )

    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    # Expense List
    if filtered_expenses:
        for exp in filtered_expenses:
            cat = exp["category"] or "Other"
            html(
                f"""
                <div class="transaction-row">
                    <div class="tx-left">
                        <div class="tx-icon-frame">{category_icon(cat)}</div>
                        <div>
                            <div class="tx-info-desc">{exp["description"]}</div>
                            <div class="tx-info-meta">{cat} · Date: {exp["date"]}</div>
                        </div>
                    </div>
                    <div class="tx-amount">−{money(float(exp["amount"]))}</div>
                </div>
                """
            )
    else:
        st.info("No matching expense transactions found in the sovereign ledger.", icon="💳")


# ============================================================
# 3. WALLET & CAPITAL MANAGEMENT
# ============================================================

elif navigation == "Wallets":

    html(
        f"""
        <div class="dash-hero">
            <div class="dash-hero-eyebrow">CAPITAL GOVERNANCE</div>
            <h1 class="dash-hero-title">Sovereign Vault & Liquidity</h1>
            <p class="dash-hero-subtitle">Govern your capital balance, set liquidity targets, and inspect reserve runway.</p>
        </div>
        """
    )

    w_left, w_right = st.columns([1.2, 1], gap="large")

    with w_left:
        # Full Sovereign Glass Card
        html(
            f"""
            <div class="floating-glass-card" style="max-width: 100%; height: 260px; animation: none; background: linear-gradient(135deg, rgba(89, 9, 7, 0.95) 0%, rgba(58, 5, 4, 0.98) 100%);">
                <div class="card-top-row">
                    <div class="card-brand-mark">
                        <span>⚜️</span> HISAB KHATA · PRIMARY VAULT
                    </div>
                    <div class="card-chip"></div>
                </div>
                
                <div class="card-balance-block">
                    <div class="card-balance-label">Current Sovereign Liquidity</div>
                    <div class="card-balance-value">{money(wallet_balance)}</div>
                </div>
                
                <div class="card-bottom-row">
                    <div>
                        <div class="card-number">•••• •••• •••• 9418</div>
                        <div class="card-holder">{username.upper()} · SOVEREIGN MEMBER</div>
                    </div>
                    <div style="font-size: 1.6rem; color: #E8D2B5;">◈</div>
                </div>
            </div>
            """
        )

        st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

        # Quick preset infusion chips
        html(
            """
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">Instant Liquidity Presets</h4>
                <div class="panel-subtitle-luxury">One-click capital infusion into your active vault</div>
            </div>
            """
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("+ ₹1,000", use_container_width=True):
                add_money(user_id, 1000)
                st.success("₹1,000 credited.")
                st.rerun()
        with c2:
            if st.button("+ ₹5,000", use_container_width=True):
                add_money(user_id, 5000)
                st.success("₹5,000 credited.")
                st.rerun()
        with c3:
            if st.button("+ ₹10,000", use_container_width=True):
                add_money(user_id, 10000)
                st.success("₹10,000 credited.")
                st.rerun()
        with c4:
            if st.button("+ ₹25,000", use_container_width=True):
                add_money(user_id, 25000)
                st.success("₹25,000 credited.")
                st.rerun()

    with w_right:
        # Add Money Form
        html(
            f"""
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">{t("add_money")}</h4>
                <div class="panel-subtitle-luxury">{t("increase_wallet")}</div>
            </div>
            """
        )

        custom_add = st.number_input("Custom Injection Amount (₹)", min_value=0.0, step=1000.0, key="wallet_page_add")
        if st.button("Infuse Capital to Vault", use_container_width=True, type="primary"):
            if custom_add <= 0:
                st.error("Please enter an amount greater than zero.")
            else:
                add_money(user_id, custom_add)
                st.success(f"{money(custom_add)} added to your sovereign vault.")
                st.rerun()

        st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)

        # Recalibrate / Set Wallet
        with st.expander("⚙️ Recalibrate Total Vault Balance"):
            new_target = st.number_input("Set Absolute Vault Target (₹)", min_value=0.0, value=wallet_balance, step=5000.0)
            if st.button("Confirm Vault Recalibration", use_container_width=True):
                set_wallet(user_id, new_target)
                st.success(f"Vault recalibrated to {money(new_target)}.")
                st.rerun()


# ============================================================
# 4. ANALYTICS & REPORTS
# ============================================================

elif navigation == "Analytics":

    html(
        f"""
        <div class="dash-hero">
            <div class="dash-hero-eyebrow">{t("financial_analytics")}</div>
            <h1 class="dash-hero-title">{t("spending_analytics")}</h1>
            <p class="dash-hero-subtitle">{t("understand_spending")}</p>
        </div>
        """
    )

    avg_exp = (month_spent / len(month_expenses)) if month_expenses else 0

    # 4 Analytics Metric Cards
    a1, a2, a3, a4 = st.columns(4, gap="medium")

    with a1:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">MONTHLY SPEND</div>
                <div class="metric-val">{money(month_spent)}</div>
                <div class="metric-note">Current month outflow</div>
            </div>
            """
        )

    with a2:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">TRANSACTIONS</div>
                <div class="metric-val">{len(month_expenses)}</div>
                <div class="metric-note">Total this month</div>
            </div>
            """
        )

    with a3:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">AVERAGE TICKET</div>
                <div class="metric-val">{money(avg_exp)}</div>
                <div class="metric-note">Per transaction</div>
            </div>
            """
        )

    with a4:
        html(
            f"""
            <div class="metric-card-luxury">
                <div class="metric-lbl">DOMINANT CATEGORY</div>
                <div class="metric-val" style="font-size: 1.35rem;">{top_category}</div>
                <div class="metric-note">{money(top_category_amount)} · {top_category_percent:.0f}%</div>
            </div>
            """
        )

    st.markdown("<div style='height: 1.8rem'></div>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        html(
            """
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">Category Allocation</h4>
                <div class="panel-subtitle-luxury">Where your capital is flowing this month</div>
            </div>
            """
        )
        if categories:
            cat_df = pd.DataFrame({
                "Category": list(categories.keys()),
                "Amount": list(categories.values()),
            }).sort_values("Amount", ascending=False).set_index("Category")
            st.bar_chart(cat_df["Amount"], height=280)
        else:
            st.info("Log expenses to display categorical breakdown.", icon="📊")

    with chart_col2:
        html(
            """
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">Daily Expenditure Velocity</h4>
                <div class="panel-subtitle-luxury">Day-by-day cash burn analysis</div>
            </div>
            """
        )
        if daily_spend:
            daily_df = pd.DataFrame({
                "Date": list(daily_spend.keys()),
                "Amount": list(daily_spend.values()),
            })
            daily_df["Date"] = pd.to_datetime(daily_df["Date"])
            daily_df = daily_df.sort_values("Date").set_index("Date")
            st.line_chart(daily_df["Amount"], height=280)
        else:
            st.info("Log daily expenses to trace spending velocity trends.", icon="📈")

    st.markdown("<div style='height: 1.8rem'></div>", unsafe_allow_html=True)

    # Detailed Category Breakdown Table
    if categories:
        html(
            """
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">Comprehensive Category Breakdown</h4>
                <div class="panel-subtitle-luxury">Audited distribution of monthly capital allocation</div>
            </div>
            """
        )
        for cat, amt in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = (amt / month_spent * 100) if month_spent > 0 else 0
            html(
                f"""
                <div class="transaction-row">
                    <div class="tx-left">
                        <div class="tx-icon-frame">{category_icon(cat)}</div>
                        <div>
                            <div class="tx-info-desc">{cat}</div>
                            <div class="tx-info-meta">{pct:.1f}% of total monthly burn</div>
                        </div>
                    </div>
                    <div class="tx-amount">{money(amt)}</div>
                </div>
                """
            )


# ============================================================
# 5. AI FINANCIAL ASSISTANT
# ============================================================

elif navigation == "AI Assistant":

    html(
        f"""
        <div class="dash-hero">
            <div class="dash-hero-eyebrow">INTELLIGENT PRIVATE ADVISORY</div>
            <h1 class="dash-hero-title">Hisab Khata Neural AI</h1>
            <p class="dash-hero-subtitle">Ask anything about your ledger, spending velocity, or financial runway, {username}.</p>
        </div>
        """
    )

    html(
        """
        <div class="panel-luxury">
            <h4 class="panel-title-luxury">💬 Consult Your Neural Advisor</h4>
            <div class="panel-subtitle-luxury">Hisab Khata AI directly interrogates your live database and active wallet reserves.</div>
        </div>
        """
    )

    # Suggested Prompts Chips
    st.write("✨ **Quick Editorial Prompts:**")
    q1, q2, q3, q4 = st.columns(4)
    suggested_q = ""
    with q1:
        if st.button("Where am I spending most?", use_container_width=True):
            suggested_q = "Where am I spending the most money this month?"
    with q2:
        if st.button("Analyse spending velocity", use_container_width=True):
            suggested_q = "Analyse my daily spending velocity and suggest 3 ways to optimize my runway."
    with q3:
        if st.button("How much spent on food?", use_container_width=True):
            suggested_q = "How much did I spend on Food & Dining so far?"
    with q4:
        if st.button("Calculate vault runway", use_container_width=True):
            suggested_q = "Based on my current expenses and wallet balance, what is my remaining financial runway?"

    user_ai_question = st.text_area(
        "Your Financial Query",
        value=suggested_q,
        placeholder="Type your question here in English, Hindi, or Hinglish...",
        height=110,
    )

    if st.button("⚜️ Ask Hisab Khata AI", use_container_width=True, type="primary"):
        if not user_ai_question.strip():
            st.warning("Please type a question for the AI assistant.")
        else:
            with st.spinner("Hisab Khata Neural Advisor is examining your ledger..."):
                ai_reply = ask_ai(
                    question=user_ai_question,
                    expenses=expenses,
                    wallet_balance=wallet_balance,
                    username=username,
                    language=st.session_state.language,
                )

                if ai_reply.startswith("Sorry, I couldn't connect"):
                    st.warning("🤖 AI service is temporarily offline. Your data is safe.")
                else:
                    html(
                        f"""
                        <div class="ai-card-luxury" style="margin-top: 1.5rem;">
                            <div class="ai-badge-pill">
                                <span>◈</span> HISAB KHATA INTELLIGENCE REPORT
                            </div>
                            <div class="ai-title-luxury">Analysis for {username}</div>
                            <div class="ai-body-luxury" style="white-space: pre-wrap; margin-top: 0.8rem; font-size: 0.94rem;">
{ai_reply}
                            </div>
                        </div>
                        """
                    )


# ============================================================
# 6. SETTINGS & PROFILE
# ============================================================

elif navigation == "Settings":

    html(
        f"""
        <div class="dash-hero">
            <div class="dash-hero-eyebrow">{t("settings")}</div>
            <h1 class="dash-hero-title">{t("settings_title")}</h1>
            <p class="dash-hero-subtitle">{t("settings_subtitle")}</p>
        </div>
        """
    )

    set_col1, set_col2 = st.columns(2, gap="large")

    with set_col1:
        html(
            f"""
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">🌐 {t("language")}</h4>
                <div class="panel-subtitle-luxury">{t("language_description")}</div>
            </div>
            """
        )

        lang_choices = ["English", "हिंदी", "Hinglish"]
        cur_lang = st.session_state.get("language", "English")
        new_lang = st.selectbox(
            t("choose_language"),
            lang_choices,
            index=lang_choices.index(cur_lang),
            key="dashboard_language_select"
        )

        if new_lang != cur_lang:
            update_user_language(user_id, new_lang)
            st.session_state.language = new_lang
            st.success(f"Language updated to {new_lang}.")
            st.rerun()

        st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

        html(
            """
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">🛡️ Cryptographic Security</h4>
                <div class="panel-subtitle-luxury">Your security credentials are encrypted using SHA-256 with zero third-party telemetry.</div>
            </div>
            """
        )

    with set_col2:
        # User details card
        created_at_val = current_user.get("created_at", "N/A") if current_user else "N/A"
        html(
            f"""
            <div class="panel-luxury">
                <h4 class="panel-title-luxury">👤 Member Sovereign Profile</h4>
                <div class="panel-subtitle-luxury">Account registry details</div>
                
                <div style="margin-top: 1rem; font-size: 0.88rem; line-height: 2;">
                    <div><strong>Member Identity:</strong> {username}</div>
                    <div><strong>Registry ID:</strong> #{user_id}</div>
                    <div><strong>Access Tier:</strong> <span style="color: #590907; font-weight: 800;">Private Sovereign</span></div>
                    <div><strong>Account Established:</strong> {created_at_val[:10] if len(created_at_val) >= 10 else created_at_val}</div>
                </div>
            </div>
            """
        )

        # Login Audit History
        login_history = get_login_history(user_id)
        if login_history:
            html(
                """
                <div class="panel-luxury">
                    <h4 class="panel-title-luxury">📜 Recent Audit Logins</h4>
                    <div class="panel-subtitle-luxury">Immutable session timestamps</div>
                </div>
                """
            )
            for item in login_history[:4]:
                html(
                    f"""
                    <div style="font-size: 0.78rem; padding: 0.4rem 0; border-bottom: 1px solid rgba(232, 210, 181, 0.4); color: #584A47;">
                        🕒 Session authenticated at: <strong>{item['login_time'][:19]}</strong>
                    </div>
                    """
                )


# ============================================================
# LUXURY FOOTER (LOGGED IN)
# ============================================================

html(
    """
    <div style="text-align: center; margin-top: 4.5rem; padding: 2rem 0; border-top: 1px solid rgba(232, 210, 181, 0.45); color: #847774; font-size: 0.76rem; letter-spacing: 0.08em;">
        HISAB KHATA · PRIVATE WEALTH & EXPENSE ARCHITECTURE
        <span style="margin: 0 12px; color: #590907;">◈</span>
        HAUTE FINTECH EDITION
        <span style="margin: 0 12px; color: #590907;">◈</span>
        DESIGNED BY <strong style="color: #590907;">AAYUSH VARSHNEY</strong>
    </div>
    """
)