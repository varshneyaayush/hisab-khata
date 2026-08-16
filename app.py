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
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Ledgerly | AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_database()


# ============================================================
# HELPERS
# ============================================================

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


# ============================================================
# PREMIUM DARK UI
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

:root {
    --bg: #06101c;
    --bg2: #0a1726;
    --card: #0d1b2b;
    --card2: #102236;
    --border: rgba(255,255,255,0.08);
    --text: #f5f7fa;
    --muted: #8191a8;
    --green: #19c37d;
    --green2: #0fa968;
    --gold: #d4af6a;
}

html,
body,
[class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 8% 0%,
            rgba(25,195,125,0.10),
            transparent 25%
        ),
        radial-gradient(
            circle at 92% 5%,
            rgba(212,175,106,0.09),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #06101c,
            #091625,
            #06101c
        );
    color: var(--text);
}

.block-container {
    max-width: 1450px;
    padding: 2rem 2.7rem 4rem;
}

#MainMenu,
footer {
    visibility: hidden;
}

header {
    visibility: visible !important;
    background: transparent !important;
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
    border-radius: 25px;
    background:
        linear-gradient(
            145deg,
            rgba(13,27,43,0.97),
            rgba(8,21,34,0.97)
        );
    border: 1px solid var(--border);
    box-shadow:
        0 30px 90px rgba(0,0,0,0.35);
    animation: fadeUp 0.7s ease both;
}

.login-logo {
    width: 58px;
    height: 58px;
    display: grid;
    place-items: center;
    border-radius: 17px;
    background:
        linear-gradient(
            135deg,
            var(--green),
            #0c9f67
        );
    box-shadow:
        0 12px 35px
        rgba(25,195,125,0.25);
    font-size: 1.5rem;
    margin-bottom: 1.2rem;
}

.login-title {
    color: white;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin: 0;
}

.login-subtitle {
    color: var(--muted);
    font-size: 0.82rem;
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
    background:
        linear-gradient(
            180deg,
            #040b15,
            #081525 55%,
            #040b15
        );
    border-right:
        1px solid
        rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] > div {
    padding: 1.4rem 1rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    color: white;
    font-size: 1.35rem;
    font-weight: 800;
    padding: 0.4rem 0.5rem 1.8rem;
}

.brand-icon {
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    background:
        linear-gradient(
            135deg,
            var(--green),
            #0d9e67
        );
    box-shadow:
        0 10px 30px
        rgba(25,195,125,0.25);
}

.sidebar-label {
    color: #60718a;
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    margin: 1rem 0 0.5rem 0.6rem;
}

section[data-testid="stSidebar"]
div[role="radiogroup"] {
    gap: 5px;
}

section[data-testid="stSidebar"] label {
    border-radius: 12px;
    padding: 0.68rem 0.7rem;
    transition: all 0.25s ease;
}

section[data-testid="stSidebar"] label:hover {
    background:
        rgba(25,195,125,0.07);
    transform: translateX(4px);
}

section[data-testid="stSidebar"] label p {
    color: #cad4e2 !important;
    font-size: 0.78rem;
    font-weight: 600;
}

.sidebar-user {
    margin-top: 2rem;
    padding: 1rem;
    border-radius: 15px;
    background:
        linear-gradient(
            135deg,
            rgba(25,195,125,0.08),
            rgba(212,175,106,0.05)
        );
    border: 1px solid var(--border);
}

.sidebar-user-name {
    color: white;
    font-size: 0.8rem;
    font-weight: 700;
}

.sidebar-user-balance {
    color: var(--green);
    font-size: 0.67rem;
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
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    border-radius: 23px;
    background:
        linear-gradient(
            135deg,
            #0a1828,
            #10263a,
            #0b1c2e
        );
    border: 1px solid var(--border);
    box-shadow:
        0 20px 60px
        rgba(0,0,0,0.25);
    animation: fadeUp 0.65s ease both;
}

.hero::before {
    content: "";
    position: absolute;
    width: 350px;
    height: 350px;
    right: -120px;
    top: -190px;
    border-radius: 50%;
    background:
        radial-gradient(
            circle,
            rgba(25,195,125,0.20),
            transparent 68%
        );
}

.hero-content {
    position: relative;
    z-index: 2;
}

.eyebrow {
    color: var(--gold);
    font-size: 0.64rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    margin-bottom: 0.45rem;
}

.hero-title {
    color: white;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin: 0;
}

.hero-subtitle {
    color: #91a0b5;
    font-size: 0.84rem;
    margin: 0.45rem 0 0;
}

.ai-badge {
    position: relative;
    z-index: 3;
    padding: 0.65rem 1rem;
    border-radius: 999px;
    background:
        rgba(25,195,125,0.08);
    border:
        1px solid
        rgba(25,195,125,0.25);
    color: #86efc0;
    font-size: 0.72rem;
    font-weight: 700;
}


/* =========================================================
   CARDS
========================================================= */

.metric-card {
    position: relative;
    overflow: hidden;
    min-height: 150px;
    padding: 1.35rem;
    border-radius: 19px;
    background:
        linear-gradient(
            145deg,
            #0d1b2b,
            #102236
        );
    border: 1px solid var(--border);
    box-shadow:
        0 15px 40px
        rgba(0,0,0,0.17);
    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease,
        border-color 0.3s ease;
    animation: fadeUp 0.75s ease both;
}

.metric-card:hover {
    transform: translateY(-7px);
    border-color:
        rgba(25,195,125,0.22);
    box-shadow:
        0 25px 55px
        rgba(0,0,0,0.30);
}

.metric-label {
    color: #77879e;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.09em;
}

.metric-value {
    color: #f6f8fb;
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-top: 0.5rem;
}

.metric-note {
    color: var(--green);
    font-size: 0.67rem;
    font-weight: 700;
    margin-top: 0.45rem;
}

.metric-note.neutral {
    color: #78889e;
}


/* =========================================================
   PANELS
========================================================= */

.panel {
    background:
        linear-gradient(
            145deg,
            #0d1b2b,
            #0c1928
        );
    border: 1px solid var(--border);
    border-radius: 19px;
    padding: 1.35rem;
    box-shadow:
        0 15px 40px
        rgba(0,0,0,0.15);
    animation: fadeUp 0.85s ease both;
}

.panel-title {
    color: #f1f5f9;
    font-size: 0.97rem;
    font-weight: 800;
    margin: 0;
}

.panel-caption {
    color: #718198;
    font-size: 0.69rem;
    margin: 0.3rem 0 1rem;
}


/* =========================================================
   AI CARD
========================================================= */

.ai-card {
    position: relative;
    overflow: hidden;
    min-height: 215px;
    padding: 1.5rem;
    border-radius: 19px;
    background:
        linear-gradient(
            135deg,
            #0d3428,
            #0b2923,
            #10221e
        );
    border:
        1px solid
        rgba(25,195,125,0.20);
    box-shadow:
        0 20px 50px
        rgba(25,195,125,0.10);
    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease;
}

.ai-card:hover {
    transform: translateY(-5px);
    box-shadow:
        0 25px 60px
        rgba(25,195,125,0.17);
}

.ai-label {
    color: #6ee7b7;
    font-size: 0.64rem;
    font-weight: 800;
    letter-spacing: 0.13em;
}

.ai-title {
    color: white;
    font-size: 1.1rem;
    font-weight: 800;
    margin: 0.7rem 0 0.55rem;
}

.ai-text {
    color: #b8c8c1;
    font-size: 0.77rem;
    line-height: 1.65;
}

.ai-chip {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.4rem 0.65rem;
    border-radius: 8px;
    background:
        rgba(25,195,125,0.10);
    color: #86efc0;
    font-size: 0.64rem;
    font-weight: 700;
}


/* =========================================================
   TRANSACTIONS
========================================================= */

.transaction {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 0;
    border-bottom:
        1px solid
        rgba(255,255,255,0.06);
    transition:
        transform 0.25s ease;
}

.transaction:hover {
    transform: translateX(5px);
}

.transaction-icon {
    width: 39px;
    height: 39px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background:
        rgba(212,175,106,0.08);
    border:
        1px solid
        rgba(212,175,106,0.10);
}

.transaction-copy {
    flex: 1;
}

.transaction-name {
    color: #e8edf4;
    font-size: 0.79rem;
    font-weight: 750;
}

.transaction-meta {
    color: #718198;
    font-size: 0.65rem;
    margin-top: 3px;
}

.transaction-value {
    color: #e8edf4;
    font-size: 0.8rem;
    font-weight: 800;
}


/* =========================================================
   BUDGET BAR
========================================================= */

.budget-bar {
    width: 100%;
    height: 7px;
    margin-top: 0.8rem;
    border-radius: 999px;
    background:
        rgba(255,255,255,0.07);
    overflow: hidden;
}

.budget-fill {
    height: 100%;
    border-radius: 999px;
    background:
        linear-gradient(
            90deg,
            var(--green),
            var(--gold)
        );
    transition: width 1s ease;
}


/* =========================================================
   FORM
========================================================= */

div[data-testid="stForm"] {
    background:
        linear-gradient(
            145deg,
            #0d1b2b,
            #102236
        );
    border:
        1px solid
        var(--border);
    border-radius:
        19px;
    padding:
        1.3rem;
    box-shadow:
        0 15px 40px
        rgba(0,0,0,0.15);
}

div[data-testid="stForm"] label {
    color:
        #93a1b4 !important;
    font-size:
        0.72rem !important;
    font-weight:
        700 !important;
}

div[data-testid="stFormSubmitButton"] button {
    background:
        linear-gradient(
            135deg,
            var(--green),
            var(--green2)
        );
    color:
        #03130c;
    border:
        0;
    border-radius:
        11px;
    min-height:
        2.7rem;
    font-weight:
        800;
    transition:
        all 0.2s ease;
}

div[data-testid="stFormSubmitButton"] button:hover {
    transform:
        translateY(-2px);
    box-shadow:
        0 12px 30px
        rgba(25,195,125,0.20);
}


/* =========================================================
   INPUTS
========================================================= */

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius:
        10px !important;
    border-color:
        rgba(255,255,255,0.10)
        !important;
    background:
        #091625
        !important;
    color:
        #edf2f7
        !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color:
        var(--green)
        !important;
    box-shadow:
        0 0 0 2px
        rgba(25,195,125,0.10)
        !important;
}


/* =========================================================
   BUTTONS
========================================================= */

div.stButton > button {
/* Premium Hero AI Button */

    button[kind="secondary"] {
        transition: all 0.25s ease !important;
    }

    div[data-testid="stHorizontalBlock"] button {
        border-radius: 999px !important;
    }

    div[data-testid="stHorizontalBlock"] button:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(25,195,125,0.45) !important;
        background: rgba(25,195,125,0.10) !important;
        box-shadow: 0 10px 30px rgba(25,195,125,0.15) !important;
    }
    border-radius:
        10px;
    border:
        1px solid
        rgba(255,255,255,0.08);
    background:
        rgba(255,255,255,0.04);
    color:
        #dce5ef;
    font-weight:
        700;
    transition:
        all 0.25s ease;
}

div.stButton > button:hover {
    border-color:
        rgba(25,195,125,0.30);
    background:
        rgba(25,195,125,0.07);
    transform:
        translateY(-2px);
}


/* =========================================================
   ANIMATIONS
========================================================= */

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(18px);
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
        font-size: 1.5rem;
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
                    Ledgerly
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
                        password
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

            Ledgerly

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

    navigation = st.radio(
    "Navigation",
    [
        "🏠  Overview",
        "💳  Expenses",
        "📊  Analytics",
        "🤖  AI Assistant",
        "⚙️  Settings",
    ],
        label_visibility="collapsed",
    )
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
                    PERSONAL FINANCE
                </div>

                <h1 class="hero-title">
                    {greeting}, {username} 👋
                </h1>

                <p class="hero-subtitle">
                    Here's your financial overview for today.
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
            """
            <div class="panel">

                <p class="panel-title">
                    💰 Add money to wallet
                </p>

                <p class="panel-caption">
                    Increase the amount available
                    for your expenses.
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
                    Current wallet
                </p>

                <div
                    style="
                        color:#19c37d;
                        font-size:2rem;
                        font-weight:800;
                        margin-top:0.6rem;
                    "
                >
                    {money(wallet_balance)}
                </div>

                <p class="panel-caption">
                    Available balance
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
                    TOTAL AVAILABLE
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
                    TOTAL SPENT
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
                    THIS MONTH
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
            """
            <div class="panel">

                <p class="panel-title">
                    Spending activity
                </p>

                <p class="panel-caption">
                    Your expenses this month
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
                "Ledgerly will start identifying "
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
            """
            <div class="panel">

                <p class="panel-title">
                    Recent transactions
                </p>

                <p class="panel-caption">
                    Latest activity from your ledger
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
                    color:#f1f5f9;
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
                    TRANSACTION LEDGER
                </div>

                <h1 class="hero-title">
                    {username}'s expenses
                </h1>

                <p class="hero-subtitle">
                    Every transaction in one place.
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
                    FINANCIAL ANALYTICS
                </div>

                <h1 class="hero-title">
                    Your spending analytics
                </h1>

                <p class="hero-subtitle">
                    A deeper look at where your money goes, {username}.
                </p>

            </div>

            <div class="ai-badge">
                📊 Smart Analytics
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
                    Ask Ledgerly anything about your spending,
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
    """
    <div class="panel">

        <p class="panel-title">
            💬 Ask your financial assistant
        </p>

        <p class="panel-caption">
            Ledgerly AI can analyse your actual
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
        "✨ Ask Ledgerly AI",
        use_container_width=True,
    ):

        if not question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "Ledgerly AI is analysing your finances..."
            ):

                answer = ask_ai(
                    question=question,
                    expenses=expenses,
                    wallet_balance=wallet_balance,
                    username=username,
                )
                
                
                if answer.startswith("Sorry, I couldn't connect"):
                    st.warning(
                        "🤖 AI is currently unavailable. "
                        "You can connect your API credits later."
                         )
                else:
                    with st.container(border=True):
                        st.markdown("### 🤖 Ledgerly AI")
                        st.markdown(answer)

# ============================================================
# SETTINGS PAGE
# ============================================================

elif "Settings" in navigation:

    html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="eyebrow">
                    ACCOUNT SETTINGS
                </div>

                <h1 class="hero-title">
                    Settings
                </h1>

                <p class="hero-subtitle">
                    Manage your Ledgerly account and wallet.
                </p>

            </div>

            <div class="ai-badge">
                ⚙️ Account
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    settings_left, settings_right = st.columns(
        [1, 1],
        gap="large"
    )


    with settings_left:

        html(
            f"""
            <div class="panel">

                <p class="panel-title">
                    👤 Profile
                </p>

                <p class="panel-caption">
                    Your Ledgerly account information
                </p>

                <div style="
                    margin-top:1rem;
                    padding:1rem;
                    border-radius:12px;
                    background:rgba(255,255,255,0.035);
                    border:1px solid rgba(255,255,255,0.06);
                ">

                    <div style="
                        color:#718198;
                        font-size:.65rem;
                        font-weight:700;
                    ">
                        USERNAME
                    </div>

                    <div style="
                        color:#f1f5f9;
                        font-size:1.05rem;
                        font-weight:800;
                        margin-top:.3rem;
                    ">
                        {username}
                    </div>

                </div>

            </div>
            """
        )


    # --------------------------------------------------------
    # WALLET
    # --------------------------------------------------------

    with settings_right:

        html(
            f"""
            <div class="panel">

                <p class="panel-title">
                    💰 Wallet
                </p>

                <p class="panel-caption">
                    Current available balance
                </p>

                <div style="
                    color:#19c37d;
                    font-size:2rem;
                    font-weight:800;
                    margin-top:.8rem;
                ">
                    {money(wallet_balance)}
                </div>

                <p class="panel-caption">
                    Available to spend
                </p>

            </div>
            """
        )


    st.markdown(
        "<div style='height:1.5rem'></div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # ACCOUNT ACTIONS
    # --------------------------------------------------------

    html(
        """
        <div class="panel">

            <p class="panel-title">
                🔐 Account actions
            </p>

            <p class="panel-caption">
                Manage your current session.
            </p>

        </div>
        """
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="settings_logout"
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""

        st.rerun()

# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div
        style="
            text-align:center;
            margin-top:3rem;
            color:#617289;
            font-size:0.65rem;
        "
    >
        Ledgerly · Intelligent personal finance
    </div>
    """
)