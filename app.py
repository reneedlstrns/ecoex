from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "RENEE"

# IVY CODE:
# ✅ Global Data (Mock)
requests = [
    {
        'id': 'req1',
        'sender_name': 'Alex Johnson',
        'item_name': 'Food Packaging',
        'time': '2 hours ago',
        'description': 'used food packaging',
        'status': 'not collected',
        'location': 'Makati City'
    },
    {
        'id': 'req2',
        'sender_name': 'Maria Gomez',
        'item_name': 'Plastic Bottles',
        'time': 'Yesterday',
        'description': '1L water bottles',
        'status': 'not collected',
        'location': 'Lipa City'
    },
    {
        'id': 'req3',
        'sender_name': 'John Wick',
        'item_name': 'Cans',
        'time': 'Just now',
        'description': 'food cans',
        'status': 'not collected',
        'location': 'Malolos City'
    }
]

conversions = [
    {
        'id': 'conv1',
        'waste_item': 'Plastic Bottles',
        'product': 'Classroom Chairs',
        'time': '2 days ago',
        'description': 'Used bottles were molded into chairs for schools.'
    },
    {
        'id': 'conv2',
        'waste_item': 'Paper bags',
        'product': 'Paper vase',
        'time': '5 hours ago',
        'description': 'Converted into paper vase.'
    },
    {
        'id': 'conv3',
        'waste_item': 'Old Newspapers',
        'product': 'Recycled Paper',
        'time': '1 week ago',
        'description': 'Turned into eco-friendly paper sheets.'
    }
]

donation_posts = [
    {
        'id': 'post1',
        'title': 'Glass Jars',
        'category': 'Glass',
        'description': 'Clean glass jars with lids, previously used for sauces.',
        'username': 'Ella Santos',
        'location': 'Quezon City',
        'date_posted': 'April 10, 2025'
    },
    {
        'id': 'post2',
        'title': 'Shredded Documents',
        'category': 'Paper',
        'description': 'Confidential shredded papers in sealed bags.',
        'username': 'Marco Cruz',
        'location': 'Pasig City',
        'date_posted': 'January 12, 2025'
    },
    {
        'id': 'post3',
        'title': 'Empty Shampoo Bottles',
        'category': 'Plastic',
        'description': 'Various brands of empty, rinsed shampoo bottles.',
        'username': 'Tina Yu',
        'location': 'Cebu City',
        'date_posted': 'March 4, 2025'
    },
    {
        'id': 'post4',
        'title': 'Aluminum Foil Scraps',
        'category': 'Metal',
        'description': 'Used but clean aluminum foil collected from a catering event.',
        'username': 'Jorge Lim',
        'location': 'Davao City',
        'date_posted': 'February 16, 2025'
    },
    {
        'id': 'post5',
        'title': 'Office File Folders',
        'category': 'Paper',
        'description': 'Paper folders from a recent office cleanup.',
        'username': 'Alicia Ramos',
        'location': 'Makati City',
        'date_posted': 'March 20, 2025'
    },
    {
        'id': 'post6',
        'title': 'Old CDs and DVD Cases',
        'category': 'Plastic',
        'description': 'Outdated media and cases available for creative reuse.',
        'username': 'Kenji Tan',
        'location': 'Baguio City',
        'date_posted': 'April 25, 2025'
    },
    {
        'id': 'post7',
        'title': 'Torn Manila Envelopes',
        'category': 'Paper',
        'description': 'Damaged but dry envelopes from school use.',
        'username': 'Bianca Go',
        'location': 'San Fernando',
        'date_posted': 'April 30, 2025'
    },
    {
        'id': 'post8',
        'title': 'Aluminum Food Trays',
        'category': 'Metal',
        'description': 'Used food trays from a family event. Rinsed clean.',
        'username': 'Liam Reyes',
        'location': 'Taguig City',
        'date_posted': 'February 8, 2025'
    },
    {
        'id': 'post9',
        'title': 'Plastic Plant Pots',
        'category': 'Plastic',
        'description': 'Various sizes of plastic pots no longer in use.',
        'username': 'Isabel Cruz',
        'location': 'Laguna',
        'date_posted': 'January 27, 2025'
    },
    {
        'id': 'post10',
        'title': 'Paperback Books',
        'category': 'Paper',
        'description': 'Old textbooks and novels for recycling or reuse.',
        'username': 'Nico De Leon',
        'location': 'Iloilo City',
        'date_posted': 'March 31, 2025'
    }
]
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

    return render_template("myprofile.html", donations=donations, total_score=total_score, requests = requests, conversions = conversions)


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
    return render_template('impact.html', conversions=conversions)

@app.route('/connections')
def connections():
    return render_template('connections.html', requests=requests)

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

#IVY CODE:
@app.route('/request/<request_id>')
def view_request(request_id):
    req = next((r for r in requests if r['id'] == request_id), None)
    if req:
        return render_template('view_request.html', request=req, username="Renee",
        impact_points=42,)
    else:
        return "Request not found", 404


@app.route('/conversion/<conversion_id>')
def view_conversion(conversion_id):
    # Find the conversion by ID
    conversion = next((c for c in conversions if c['id'] == conversion_id), None)
    if conversion:
        # Render the conversion details (this will be inserted into the dynamic content container)
        return render_template('view_conversion.html', conversion=conversion, username="Renee",
        impact_points=42,)
    else:
        return "Conversion not found", 404

@app.route('/conversion/<conversion_id>/delete', methods=['POST'])
def delete_conversion(conversion_id):
    global conversions
    conversions = [c for c in conversions if c['id'] != conversion_id]
    return redirect(url_for('impact'))


@app.route('/discover')
def discover():
    search_query = request.args.get('search', '').lower()
    category = request.args.get('category', '').lower()
    location = request.args.get('location', '').lower()

    filtered_posts = []
    for post in donation_posts:
        matches_search = search_query in post['title'].lower() or search_query in post['description'].lower()
        matches_category = category in post['category'].lower() if category else True

        if matches_search and matches_category:
            filtered_posts.append(post)

    return render_template('discover.html', posts=filtered_posts, search=search_query, category=category,
                           donation_posts=donation_posts)


@app.route('/donation/<post_id>')
def view_donation(post_id):
    post = next((p for p in donation_posts if p['id'] == post_id), None)
    if post:
        return render_template('view_donation.html', post=post)
    else:
        return "Donation post not found", 404


@app.route('/request-collection/<post_id>', methods=['POST'])
def request_collection(post_id):
    # You can implement actual logic here (e.g. save the request, update DB, etc.)
    print(f"Collection requested for post: {post_id}")
    return redirect(url_for('discover'))

# RUN THE FLASK APP
if __name__ == "__main__":
    print("✅ Flask app is starting...")
    app.run(debug=True)
