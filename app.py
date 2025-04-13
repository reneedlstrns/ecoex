from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "RENEE"

# Database Connection
def get_db_connection():
    conn = sqlite3.connect("ecoexchange.db")
    conn.row_factory = sqlite3.Row
    print("✅ Database connected successfully!")  # Debugging print
    return conn

# LOGIN ROUTE (DUMMY FORM, NEED TO CHANGE WITH VINCE CODE)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["fname"] = user["fname"]
            return redirect(url_for("myprofile"))
        else:
            return "Invalid credentials. Please try again."

    return render_template("login.html")

# HOME PAGE
@app.route('/')
def index():
    return render_template('index.html')

# OTHER ROUTES
@app.route('/editprofile')
def edit_profile():
    return render_template('editprofile.html')

@app.route("/myprofile")
def myprofile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT postings_id, donor_user_id, post_title, quantity, pick_up_location, description, post_status, collector_by_user_id FROM postings")
    donations = cursor.fetchall()

    cursor.execute("SELECT COALESCE(SUM(score), 0) AS total_score FROM postings WHERE donor_user_id = ?",
                   (session["user_id"],))
    total_score = cursor.fetchone()["total_score"]

    conn.close()

    return render_template("myprofile.html", donations=donations, total_score=total_score)


@app.route("/donations")
def donations():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT post_id, donor_user_id, post_title, quantity, pick_up_location, description, post_status, collected_by_user_id FROM postings")
    donations = cursor.fetchall()

    conn.close()

    return render_template("donations.html", donations=donations)

@app.route('/collections')
def collections():
    return render_template('collections.html')

@app.route('/impact')
def impact():
    return render_template('impact.html')

@app.route('/connections')
def connections():
    return render_template('connections.html')

@app.route('/discover')
def discover():
    return render_template('discover.html')

@app.route('/hub')
def hub():
    return render_template('hub.html')

#DONATE ROUTE
@app.route("/donate", methods=["GET", "POST"])
def donate():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_name, description, score FROM items")
    items = cursor.fetchall()

    if request.method == "POST":
        title = request.form["post_title"]
        quantity = int(request.form["quantity"])
        pick_up_location = request.form["pick_up_location"]
        description = request.form["description"]
        item_id = request.form["item_id"]
        post_date = datetime.today().strftime('%Y-%m-%d')

        # Check for an existing similar donation
        cursor.execute(
            "SELECT * FROM postings WHERE donor_user_id = ? AND item_id = ? AND quantity = ? AND pick_up_location = ? AND post_date = ?",
            (session["user_id"], item_id, quantity, pick_up_location, post_date))
        existing_post = cursor.fetchone()

        if existing_post:
            return "❌ Error: A similar donation already exists!", 400

        # Fetch item score for calculation
        cursor.execute("SELECT score FROM items WHERE item_id = ?", (item_id,))
        item_score = cursor.fetchone()[0]
        calculated_score = quantity * item_score

        # Insert new donation into `postings` table
        cursor.execute(
            "INSERT INTO postings (donor_user_id, post_title, quantity, pick_up_location, description, post_status, post_date, item_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (session["user_id"], title, quantity, pick_up_location, description, "new", post_date, item_id))

        new_posting_id = cursor.lastrowid  # Get the inserted posting ID

        # Insert into `postings_audit` table
        cursor.execute(
            "INSERT INTO postings_audit (post_id, posted_by_user_id, post_status, post_title, post_date, item_id, quantity, pick_up_location, transaction_date, change_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (new_posting_id, session["user_id"], "new", title, post_date, item_id, quantity, pick_up_location, post_date,
             "User_posted"))

        conn.commit()
        conn.close()

        return redirect(url_for("myprofile"))  # ✅ Redirect back to profile after successful donation

    conn.close()
    return render_template("donate_form.html", items=items)  # NEW TEMPLATE

# RUN THE FLASK APP
if __name__ == "__main__":
    print("✅ Flask app is starting...")
    app.run(debug=True)