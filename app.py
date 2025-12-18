from flask import Flask, render_template, request
import mariadb
from config import DB_CONFIG

app = Flask(__name__)

# ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К БАЗЕ
def connect_db():
    try:
        return mariadb.connect(**DB_CONFIG)
    except mariadb.Error as e:
        print("Database temporarily unavailable, sorry for the inconvenience", e)
        return None


# ГЛАВНАЯ СТРАНИЦА
@app.route("/")
def home():
    return render_template("index.html")


# СТРАНИЦА ПОЛЬЗОВАТЕЛЕЙ
@app.route("/users")
def users_page():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, display_name, email FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template("users.html", users=users)


# ДОБАВИТЬ ПОДАРОК
@app.route("/add_gift", methods=["GET", "POST"])
def add_gift():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO gifts (title, description) VALUES (?, ?)",
            (title, description)
        )
        conn.commit()
        conn.close()

        return "🎁 Your gift successfully added!"

    return render_template("add_gift.html")


# 🔹 СТРАНИЦА FOR HIM (ВАЖНО!)
@app.route("/category/him")
def for_him():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, title, price, image
        FROM catalog_gifts
        WHERE category = 'him'
        ORDER BY is_popular DESC, created_at DESC
    """)

    gifts = cur.fetchall()
    conn.close()

    return render_template("category_him/him.html", gifts=gifts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["display_name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (display_name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("auth/register.html")


from flask import redirect


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            return f"Welcome, {user['display_name']}!"
        else:
            return "Invalid login"

    return render_template("auth/login.html")



# ❗ ЗАПУСК СЕРВЕРА — ТОЛЬКО ОДИН РАЗ И В КОНЦЕ
if __name__ == "__main__":
    app.run(debug=True)
