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


@app.route("/category/him")
def for_him():
    conn = connect_db()

    # ЕСЛИ БАЗА НЕДОСТУПНА
    if conn is None:
        gifts = [
            {
                "title": "Wireless Headphones",
                "price": 99.99,
                "image": "images/headphones_for_him.avif"
            },
            {
                "title": "Minimal Leather Wallet",
                "price": 49.99,
                "image": "images/wallet_for_him.webp"
            },
            {
                "title": "Smart Water Bottle",
                "price": 34.99,
                "image": "images/bottle_for_him.webp"
            }
        ]
        return render_template("category_him/him.html", gifts=gifts)

    # ЕСЛИ БАЗА ДОСТУПНА
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT title, price, image
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



@app.route("/category/her")
def for_her():
    conn = connect_db()

    # ЕСЛИ БАЗА НЕДОСТУПНА (fallback)
    if conn is None:
        gifts = [
            {
                "title": "Luxury Candle Set",
                "price": 39.99,
                "image": "images/candle_for_her.jpg"
            },
            {
                "title": "Skincare Gift Box",
                "price": 59.99,
                "image": "images/skincare_for_her.webp"
            },
            {
                "title": "Handmade Ceramic Mug",
                "price": 29.99,
                "image": "images/mug_for_her.webp"
            }
        ]
        return render_template("category_her/her.html", gifts=gifts)

    # ЕСЛИ БАЗА ДОСТУПНА
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT title, price, image
        FROM catalog_gifts
        WHERE category = 'her'
        ORDER BY is_popular DESC, created_at DESC
    """)
    gifts = cur.fetchall()
    conn.close()

    return render_template("category_her/her.html", gifts=gifts)



# ❗ ЗАПУСК СЕРВЕРА — ТОЛЬКО ОДИН РАЗ И В КОНЦЕ
if __name__ == "__main__":
    app.run(debug=True)
