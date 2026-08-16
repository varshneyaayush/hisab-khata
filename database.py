import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE LOCATION
# ============================================================

DATABASE_PATH = (
    Path(__file__).parent
    / "data"
    / "expenses.db"
)


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # WALLETS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # --------------------------------------------------------
    # EXPENSES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # --------------------------------------------------------
    # LOGIN HISTORY
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TEXT NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # --------------------------------------------------------
    # MIGRATION FOR OLD EXPENSE DATABASE
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(expenses)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "user_id" not in columns:

        cursor.execute("""
            ALTER TABLE expenses
            ADD COLUMN user_id INTEGER
        """)

    connection.commit()

    connection.close()


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(username, password):

    username = username.strip()

    if not username or not password:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (
                username,
                password,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            username,
            hash_password(password),
            datetime.now().isoformat()
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO wallets (
                user_id,
                balance,
                updated_at
            )
            VALUES (?, ?, ?)
        """, (
            user_id,
            0,
            datetime.now().isoformat()
        ))

        connection.commit()

        return user_id

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


def login_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username
        FROM users
        WHERE username = ?
        AND password = ?
    """, (
        username.strip(),
        hash_password(password)
    ))

    user = cursor.fetchone()

    if user:

        cursor.execute("""
            INSERT INTO login_history (
                user_id,
                login_time
            )
            VALUES (?, ?)
        """, (
            user["id"],
            datetime.now().isoformat()
        ))

        connection.commit()

    connection.close()

    if user:
        return dict(user)

    return None


def get_user(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username, created_at
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    if user:
        return dict(user)

    return None


# ============================================================
# WALLET FUNCTIONS
# ============================================================

def get_wallet(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT balance
        FROM wallets
        WHERE user_id = ?
    """, (user_id,))

    wallet = cursor.fetchone()

    connection.close()

    if wallet:
        return float(wallet["balance"])

    return 0.0


def set_wallet(user_id, amount):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE wallets
        SET balance = ?,
            updated_at = ?
        WHERE user_id = ?
    """, (
        float(amount),
        datetime.now().isoformat(),
        user_id
    ))

    connection.commit()

    connection.close()


def add_money(user_id, amount):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE wallets
        SET balance = balance + ?,
            updated_at = ?
        WHERE user_id = ?
    """, (
        float(amount),
        datetime.now().isoformat(),
        user_id
    ))

    connection.commit()

    connection.close()


def subtract_money(user_id, amount):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE wallets
        SET balance = balance - ?,
            updated_at = ?
        WHERE user_id = ?
    """, (
        float(amount),
        datetime.now().isoformat(),
        user_id
    ))

    connection.commit()

    connection.close()


# ============================================================
# EXPENSE FUNCTIONS
# ============================================================

def add_expense(
    user_id,
    amount,
    description,
    category,
    date
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (
            user_id,
            amount,
            description,
            category,
            date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        float(amount),
        description,
        category,
        date
    ))

    connection.commit()

    connection.close()


def get_expenses(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            user_id,
            amount,
            description,
            category,
            date
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
    """, (user_id,))

    expenses = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return expenses


# ============================================================
# LOGIN HISTORY
# ============================================================

def get_login_history(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT login_time
        FROM login_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    history = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return history


# ============================================================
# DATABASE TEST
# ============================================================

if __name__ == "__main__":

    create_database()

    print(
        "Ledgerly database initialized successfully!"
    )