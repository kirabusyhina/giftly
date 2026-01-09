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

@app.route("/generate", methods=["GET", "POST"])
def generate_gift():
    generated = []
    form_data = {
        "category": "any",
        "budget": "",
        "occasion": "",
        "interests": "",
        "description": ""
    }

    if request.method == "POST":
        category = request.form.get("category", "any").strip().lower()
        budget_raw = request.form.get("budget", "").strip()
        occasion = request.form.get("occasion", "").strip().lower()
        interests = request.form.get("interests", "").strip().lower()
        description = request.form.get("description", "").strip().lower()

        form_data = {
            "category": category,
            "budget": budget_raw,
            "occasion": occasion,
            "interests": interests,
            "description": description
        }

        # budget -> float or None
        budget = None
        try:
            if budget_raw:
                budget = float(budget_raw)
        except ValueError:
            budget = None

        # keywords for scoring
        keywords = []
        for chunk in [occasion, interests, description]:
            for w in chunk.replace(",", " ").split():
                w = w.strip()
                if len(w) >= 3:
                    keywords.append(w)

        conn = connect_db()

        # ===== fallback gifts (if DB not available) =====
        fallback_gifts = [
            {"title": "Wireless Headphones", "price": 99.99, "image": "images/headphones_for_him.avif", "category": "him"},
            {"title": "Minimal Leather Wallet", "price": 49.99, "image": "images/wallet_for_him.webp", "category": "him"},
            {"title": "Smart Water Bottle", "price": 39.99, "image": "images/bottle_for_him.webp", "category": "him"},
            {"title": "Luxury Candle Set", "price": 39.99, "image": "images/candle_for_her.webp", "category": "her"},
            {"title": "Skincare Gift Box", "price": 59.99, "image": "images/skincare_for_her.webp", "category": "her"},
            {"title": "Handmade Ceramic Mug", "price": 29.99, "image": "images/mug_for_her.webp", "category": "her"},
        ]

        # ===== get gifts from DB (or fallback) =====
        gifts = []
        if conn is None:
            gifts = fallback_gifts
        else:
            cur = conn.cursor(dictionary=True)

            # safest select: only columns we are confident you use elsewhere
            base_sql = """
                SELECT title, price, image, category
                FROM catalog_gifts
                WHERE 1=1
            """
            params = []

            if category in ("him", "her"):
                base_sql += " AND category = ?"
                params.append(category)

            if budget is not None:
                base_sql += " AND price IS NOT NULL AND price <= ?"
                params.append(budget)

            base_sql += " ORDER BY is_popular DESC, created_at DESC"

            cur.execute(base_sql, params)
            gifts = cur.fetchall()
            conn.close()

            # if table empty -> fallback (nice UX)
            if not gifts:
                gifts = fallback_gifts

        # ===== scoring =====
        def score_gift(g):
            title = (g.get("title") or "").lower()

            # simple keyword matching in title
            s = 0
            for k in keywords:
                if k in title:
                    s += 3

            # light category preference boost
            if category in ("him", "her") and g.get("category") == category:
                s += 2

            # price closeness bonus (prefer close to budget but not over)
            if budget is not None and g.get("price") is not None:
                try:
                    p = float(g["price"])
                    if p <= budget:
                        # closer -> higher
                        s += max(0, int(5 - (budget - p) / max(1, budget) * 10))
                except:
                    pass

            return s

        # sort by score, then popularity-ish fallback (already ordered, but we re-sort)
        generated = sorted(gifts, key=score_gift, reverse=True)[:9]

    return render_template("generate.html", gifts=generated, form_data=form_data)


# ❗ ЗАПУСК СЕРВЕРА — ТОЛЬКО ОДИН РАЗ И В КОНЦЕ
if __name__ == "__main__":
    app.run(debug=True)
