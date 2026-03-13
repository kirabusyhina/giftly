from flask import Flask, render_template, request, redirect
import mariadb
from config import DB_CONFIG

app = Flask(__name__)

# ===== DATABASE CONNECTION =====
def connect_db():
    try:
        return mariadb.connect(**DB_CONFIG)
    except mariadb.Error as e:
        print("Database temporarily unavailable:", e)
        return None


# ===== HOME PAGE =====
@app.route("/")
def home():
    return render_template("index.html")


# ===== USERS PAGE =====
@app.route("/users")
def users_page():
    conn = connect_db()
    if conn is None:
        return "Database unavailable"

    cur = conn.cursor()
    cur.execute("SELECT id, display_name, email FROM users")
    users = cur.fetchall()
    conn.close()

    return render_template("users.html", users=users)


# ===== ADD GIFT =====
@app.route("/add_gift", methods=["GET", "POST"])
def add_gift():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        conn = connect_db()
        if conn is None:
            return "Database unavailable"

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO gifts (title, description) VALUES (?, ?)",
            (title, description)
        )
        conn.commit()
        conn.close()

        return "🎁 Your gift successfully added!"

    return render_template("add_gift.html")


# ===== CATEGORY: FOR HIM =====
@app.route("/category/him")
def for_him():
    conn = connect_db()

    if conn is None:
        gifts = [
            {"title": "Wireless Headphones", "price": 99.99, "image": "images/headphones_for_him.avif"},
            {"title": "Minimal Leather Wallet", "price": 49.99, "image": "images/wallet_for_him.webp"},
            {"title": "Smart Water Bottle", "price": 34.99, "image": "images/bottle_for_him.webp"},
        ]
        return render_template("category_him/him.html", gifts=gifts)

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


# ===== REGISTER =====
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["display_name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        if conn is None:
            return "Database unavailable"

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (display_name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("auth/register.html")


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        if conn is None:
            return "Database unavailable"

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


# ===== CATEGORY: FOR HER =====
@app.route("/category/her")
def for_her():
    conn = connect_db()

    if conn is None:
        gifts = [
            {"title": "Luxury Candle Set", "price": 39.99, "image": "images/candle_for_her.jpg"},
            {"title": "Skincare Gift Box", "price": 59.99, "image": "images/skincare_for_her.webp"},
            {"title": "Handmade Ceramic Mug", "price": 29.99, "image": "images/mug_for_her.webp"},
        ]
        return render_template("category_her/her.html", gifts=gifts)

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


# ===== GENERATE GIFT =====
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

        # ===== convert budget =====
        budget = None
        try:
            if budget_raw:
                budget = float(budget_raw)
        except ValueError:
            budget = None

        # ===== keywords =====
        keywords = []
        for chunk in [occasion, interests, description]:
            for w in chunk.replace(",", " ").split():
                w = w.strip()
                if len(w) >= 3:
                    keywords.append(w)

        keywords = list(set(keywords))

        conn = connect_db()

        fallback_gifts = [
            {"title": "Wireless Headphones", "price": 99.99, "image": "images/headphones_for_him.avif", "category": "him", "tags": ["tech", "music", "audio"]},
            {"title": "Minimal Leather Wallet", "price": 49.99, "image": "images/wallet_for_him.webp", "category": "him", "tags": ["fashion", "accessories"]},
            {"title": "Smart Water Bottle", "price": 39.99, "image": "images/bottle_for_him.webp", "category": "him", "tags": ["tech","lifestyle", "health"]},
            {"title": "Luxury Candle Set", "price": 39.99, "image": "images/candle_for_her.jpg", "category": "her", "tags": ["home", "fragrance"]},
            {"title": "Skincare Gift Box", "price": 59.99, "image": "images/skincare_for_her.webp", "category": "her", "tags": ["beauty", "skincare"]},
            {"title": "Handmade Ceramic Mug", "price": 29.99, "image": "images/mug_for_her.webp", "category": "her", "tags": ["home", "kitchen"]},
        ]

        if conn is None:
            gifts = fallback_gifts
        else:
            cur = conn.cursor(dictionary=True)

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
                base_sql += " AND price <= ?"
                params.append(budget)

            base_sql += " ORDER BY is_popular DESC, created_at DESC"

            cur.execute(base_sql, params)
            gifts = cur.fetchall()
            conn.close()

            if not gifts:
                gifts = fallback_gifts

        # ===== scoring =====
        def score_gift(g):
            
            title = (g.get("title") or "").lower()
            tags = g.get("tags", [])

            score = 0
            
            for k in keywords: 
                if k in title:
                    score += 3
                if k in " ".join(tags):
                    score += 5

            if category in ("him", "her") and g.get("category") == category:
                score += 2

            if budget is not None and g.get("price") is not None:
                try:
                    p = float(g["price"])
                    if p <= budget:
                        score += max(0, int(5 - (budget - p) / max(1, budget) * 10))
                except:
                    pass
                
            return score


        scored = [(g, score_gift(g)) for g in gifts]
        filtered = [(g, s) for g, s in scored if s > 0]
        generated = [g for g, s in sorted(filtered, key=lambda x: x[1], reverse=True)[:9]]

        if not generated:
            generated = gifts[:6]

    return render_template("generate.html", gifts=generated, form_data=form_data)


# ===== RUN SERVER =====
if __name__ == "__main__":
    app.run(debug=True)