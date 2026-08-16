import os

from dotenv import load_dotenv
from openai import OpenAI


# Load .env file
load_dotenv()


# Get API key
api_key = os.getenv("OPENAI_API_KEY")


# Create OpenAI client
client = OpenAI(
    api_key=api_key
)


def ask_ai(question, expenses, wallet_balance, username):
    """
    Send the user's financial data and question
    to the AI and return a helpful answer.
    """

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
You are Ledgerly, an intelligent personal finance assistant.

User name:
{username}

Current wallet balance:
₹{wallet_balance:,.0f}

User's expense history:
{expense_text}

User's question:
{question}

Instructions:

1. Answer based on the user's actual financial data.
2. Do not invent transactions or amounts.
3. Keep the answer clear and easy to understand.
4. Give practical financial insights when useful.
5. If the user asks about spending, calculate from the provided data.
6. Use Indian Rupees (₹).
7. Do not provide professional financial or investment advice.
8. Be friendly and concise.
"""


    try:

        response = client.responses.create(
            model="gpt-5.6",
            input=prompt
        )

        return response.output_text

    except Exception as error:

    error_text = str(error)

    if "429" in error_text or "quota" in error_text.lower():

        return (
            "AI is temporarily unavailable because "
            "the API usage limit has been reached. "
            "Your Ledgerly data is safe. "
            "Add API credits later to activate AI again."
        )

    return (
        "AI is temporarily unavailable right now. "
        "Please try again later."
    )