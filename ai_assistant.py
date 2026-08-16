import os

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


# ============================================================
# OPENAI CLIENT
# ============================================================

client = OpenAI(
    api_key=api_key
)


# ============================================================
# AI ASSISTANT
# ============================================================

def ask_ai(question, expenses, wallet_balance, username):

    expense_text = ""

    if expenses:

        for expense in expenses:

            expense_text += (
                f"- ₹{float(expense['amount']):,.0f} | "
                f"{expense['description']} | "
                f"{expense['category'] or 'Other'} | "
                f"{expense['date']}\n"
            )

    else:

        expense_text = "No expenses recorded yet."


    prompt = f"""
You are Hisab Khata, an intelligent personal finance assistant.

User:
{username}

Current wallet balance:
₹{wallet_balance:,.0f}

Expense history:
{expense_text}

User's question:
{question}

Instructions:

1. Answer using the user's actual financial data.
2. Never invent transactions or amounts.
3. Use Indian Rupees (₹).
4. Keep answers clear and concise.
5. Give practical spending insights when useful.
6. If calculations are required, calculate them from the provided data.
7. Do not provide professional investment or financial advice.
8. Be friendly and helpful.
"""


    try:

        response = client.responses.create(
            model="gpt-5.6",
            input=prompt
        )

        return response.output_text


    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "quota" in error_text.lower()
        ):

            return (
                "AI is temporarily unavailable because "
                "the API usage limit has been reached.\n\n"
                "Your Hisab Khata data is safe. "
                "Add API credits later to activate AI again."
            )

        return (
            "AI is temporarily unavailable right now.\n\n"
            "Please try again later."
        )