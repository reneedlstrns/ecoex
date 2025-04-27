import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from extensions import bcrypt, db
from models.user import User
from models.postings import Postings
from services import user_service
from services.user_service import validate_user, get_user_by_email, create_user
from utils import message_helper


def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            if validate_user(email, password):
                user_data = get_user_by_email(email)
                session['user_email'] = email
                session['user_id'] = user_data['user_id']
                return redirect(url_for('myprofile'))
            else:
                error_message = message_helper.ERROR_INVALID_USERNAME_OR_PASSWORD
                return render_template("login.html", error_message=error_message), 401
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop('user_email', None)
        return redirect(url_for('index'))

    @app.route("/updateProfile", methods=["POST"])
    def update_profile():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        user = db.session.get(User, session['user_id'])
        if not user:
            return redirect(url_for('edit_profile', error_message=message_helper.ERROR_USER_NOT_FOUND))

        data = request.form
        nick_name = data.get('nick_name')
        fname = data.get('fname')
        lname = data.get('lname')
        mobile = data.get('mobile')
        location_title = data.get('location_title')
        address = data.get('address')
        city = data.get('city')
        company = data.get('company')

        if not nick_name or not fname or not lname or not mobile or not location_title or not address or not city:
            return redirect(url_for('edit_profile', error_message=message_helper.ERROR_FILL_ALL_REQUIRED_FIELDS))

        response = user_service.update_user(user_id, nick_name, fname, lname, mobile, location_title, address, city,
                                            company)
        if 'error' in response:
            return redirect(url_for('edit_profile', error_message=response['error']))

        return redirect(url_for('myprofile', success_message=message_helper.SUCCESS_PROFILE_UPDATED))

    @app.route("/register", methods=["GET", "POST"])
    def registration():
        if request.method == 'POST':
            data = request.form
            nick_name = data.get('nick_name')
            fname = data.get('fname')
            lname = data.get('lname')
            mobile = data.get('mobile')
            location_title = data.get('location_title')
            address = data.get('address')
            city = data.get('city')
            company = data.get('company')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')

            if not nick_name or not fname or not lname or not mobile or not location_title or not address or not city or not email or not password or not confirm_password:
                return render_template("register.html", success=False,
                                       message=message_helper.ERROR_FILL_ALL_REQUIRED_FIELDS)

            if not user_service.is_valid_email(email):
                return render_template("register.html", success=False,
                                       message=message_helper.ERROR_INVALID_EMAIL_FORMAT)

            if not user_service.is_valid_password(password) or not user_service.is_valid_password(confirm_password):
                return render_template("register.html", success=False,
                                       message=message_helper.ERROR_DOES_NOT_MEET_PASSWORD_REQUIREMENTS)

            if password != confirm_password:
                return render_template("register.html", success=False, message=message_helper.ERROR_PASSWORD_MISMATCH)

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template("register.html", success=False,
                                       message=message_helper.ERROR_EMAIL_ALREADY_EXISTS)

            response = user_service.create_user(nick_name, fname, lname, mobile, location_title, address, city, company,
                                                email, password)
            if 'error' in response:
                return render_template("register.html", success=False, message=response['error'])

            return render_template("register.html", success=True,
                                   message=message_helper.SUCCESS_USER_CREATED)

        return render_template("register.html", success=False, message='')

    @app.route("/resetPassword", methods=["GET", "POST"])
    def reset_password():
        """
            Endpoint to reset a user's password
            """
        if request.method == 'POST':
            data = request.form
            email = data.get('email')
            existing_password = data.get('existing_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')

            if not email or not existing_password or not new_password or not confirm_password:
                return render_template("reset.html", success=False,
                                       message=message_helper.ERROR_FILL_ALL_REQUIRED_FIELDS)

            valid_new_password = user_service.is_valid_password(new_password)
            valid_confirm_password = user_service.is_valid_password(confirm_password)
            if not valid_new_password or not valid_confirm_password:
                return render_template("reset.html", success=False,
                                       message=message_helper.ERROR_DOES_NOT_MEET_PASSWORD_REQUIREMENTS)

            if new_password != confirm_password:
                return render_template("reset.html", success=False,
                                       message=message_helper.ERROR_PASSWORD_MISMATCH)

            if existing_password == new_password:
                return render_template("reset.html", success=False,
                                       message=message_helper.ERROR_CHOOSE_ANOTHER_PASSWORD)

            user = user_service.validate_user(email, existing_password)

            if user is None or user is False:
                return render_template("reset.html", success=False,
                                       message=message_helper.ERROR_INVALID_USERNAME_OR_PASSWORD)

            if user is True and new_password == confirm_password:
                response = user_service.reset_password(email, existing_password, new_password)
                if 'error' in response:
                    return render_template("reset.html", success=False, message=response['error'])

                return render_template("reset.html", success=True,
                                       message=message_helper.SUCCESS_PASSWORD_RESET)

        return render_template("reset.html", success=False, message='')

    @app.route('/api/create_user', methods=['POST'])
    def api_create_user():
        """
            Endpoint to create a user
            """
        try:
            data = request.get_json()
            nick_name = data.get('nick_name')
            fname = data.get('first_name')
            lname = data.get('last_name')
            mobile = data.get('mobile')
            location_title = data.get('location_title')
            address = data.get('address')
            city = data.get('city')
            company = data.get('company')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')

            if not all([nick_name, fname, lname, mobile, location_title, address, city, company, email, password,
                        confirm_password]):
                return jsonify({'error': message_helper.ERROR_FILL_ALL_REQUIRED_FIELDS}), 400

            if password != confirm_password:
                return jsonify({'error': message_helper.ERROR_PASSWORD_MISMATCH}), 400

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': message_helper.ERROR_EMAIL_ALREADY_EXISTS}), 400

            user = user_service.create_user(nick_name, fname, lname, mobile, location_title, address, city, company,
                                            email,
                                            password)
            return jsonify(user)
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/editProfile', methods=['GET'])
    def edit_profile():
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to login if user is not logged in

        try:
            # Retrieve the user by ID from the session
            user_id = session['user_id']
            user = User.query.get(user_id)
            if not user:
                return "User not found", 404

            # Pass the user object to the template
            return render_template('editprofile.html', user=user)
        except Exception as e:
            print(f"Error occurred: {e}")
            return "An error occurred", 500

    @app.route("/myprofile")
    def myprofile():
        success_message = request.args.get("success_message", None)
        error_message = request.args.get("error_message", None)

        if 'user_id' in session:
            user = User.query.get(session['user_id'])

            conn = get_db_connection()
            cursor = conn.cursor()

            # Donations for the logged-in user
            cursor.execute("""
                SELECT postings_id, donor_user_id, post_title, quantity, pick_up_location, description, post_status, collector_by_user_id 
                FROM postings
            """)
            donations = cursor.fetchall()

            # Total impact score
            cursor.execute("""
                SELECT COALESCE(SUM(score), 0) AS total_score 
                FROM postings 
                WHERE donor_user_id = ?
            """, (session["user_id"],))
            total_score = cursor.fetchone()["total_score"]

            # 💥 Get active connections for the user
            cursor.execute("""
                SELECT 
                    c.donor_user_id,
                    c.collector_user_id,
                    c.connection_status,
                    u1.fname || ' ' || u1.lname AS donor_name,
                    u2.fname || ' ' || u2.lname AS collector_name
                FROM connections c
                JOIN users u1 ON u1.user_id = c.donor_user_id
                JOIN users u2 ON u2.user_id = c.collector_user_id
                WHERE c.connection_status = 'Active' AND c.donor_user_id = ?
            """, (session["user_id"],))
            connection_rows = cursor.fetchall()

            # ✅ Count total connections where the user is either donor or collector
            cursor.execute("""
                SELECT COUNT(*) AS total_connections
                FROM connections
                WHERE donor_user_id = ? OR collector_user_id = ?
            """, (session["user_id"], session["user_id"]))
            total_connections = cursor.fetchone()["total_connections"]

            # 💥 Impact data (for impact.html)
            cursor.execute("""
                SELECT 
                    postings_id, 
                    post_title, 
                    post_date, 
                    pick_up_location, 
                    score
                FROM postings
                WHERE donor_user_id = ? AND is_deleted = 0
            """, (session['user_id'],))
            impact_rows = cursor.fetchall()

            conn.close()

            # Format connection data
            requests = [{
                'donor_name': row['donor_name'],
                'collector_name': row['collector_name'],
                'connection_status': row['connection_status']
            } for row in connection_rows]

            # Format impact
            impact_donations = []
            total_impact_score = 0
            for row in impact_rows:
                impact_donations.append({
                    'post_title': row['post_title'],
                    'score': row['score'],
                    'post_date': row['post_date'],
                    'pick_up_location': row['pick_up_location']
                })
                total_impact_score += row['score']

            return render_template(
                "myprofile.html",
                user=user,
                donations=donations,
                total_score=total_score,
                requests=requests,  # ✅ this is key!
                impact_donations=impact_donations,
                total_impact_score=total_impact_score,
                total_connections=total_connections,
                success_message=success_message,
                error_message=error_message
            )
        else:
            return redirect(url_for('login'))

    @app.route("/donations")
    def donations():
        if "user_id" not in session:
            return redirect(url_for("login"))

        user_id = session["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Only fetch donations posted by the logged-in user
        cursor.execute("""
            SELECT 
                post_id, 
                donor_user_id, 
                post_title, 
                quantity, 
                pick_up_location, 
                description, 
                post_status, 
                collected_by_user_id 
            FROM postings 
            WHERE donor_user_id = ? AND is_deleted = 0
        """, (user_id,))

        donations = cursor.fetchall()
        total_postings = len(donations)

        print(f"[DEBUG] User ID: {user_id}, Total Donations: {total_postings}")
        conn.close()

        return render_template("donations.html", donations=donations, total_postings=total_postings)

    @app.route('/collections')
    def collections():
        return render_template('collections.html')

    # IVY CODE FOR IMPACT
    @app.route('/impact')
    def impact():
        print("Impact route hit", flush=True)
        user_id = session['user_id']  # Assuming the user is logged in and their ID is in the session

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch the donations posted by the user, including the score for each donation
        cursor.execute("""
            SELECT 
                p.postings_id, 
                p.post_title, 
                p.post_date, 
                p.pick_up_location, 
                p.score
            FROM postings p
            WHERE p.donor_user_id = ? AND p.is_deleted = 0
        """, (user_id,))

        rows = cursor.fetchall()

        print(f"[DEBUG] Rows fetched from DB: {rows}", flush=True)  # Debug print for raw DB output

        # Prepare the donations data for the template
        donations = []
        total_score = 0  # Initialize total_score

        for row in rows:
            donations.append({
                'post_title': row['post_title'],
                'score': row['score'],
                'post_date': row['post_date'],
                'pick_up_location': row['pick_up_location']
            })
            print(f"[DEBUG] Donation data being added: {donations[-1]}")  # Debug print
            total_score += row['score']  # Accumulate the score

        print(f"[DEBUG] Total Impact Score: {total_score}")  # Debug print        
        conn.close()

        # Pass the donations data to the template
        return render_template('impact.html', donations=donations, total_score=total_score)

    # IVY CODE FOR CONNECTIONS
    @app.route('/connections')
    def connections():
        if "user_id" not in session:
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch connections with user names and connection status
        cursor.execute("""
            SELECT 
                c.donor_user_id,
                c.collector_user_id,
                c.connection_status,
                u1.fname || ' ' || u1.lname AS donor_name,
                u2.fname || ' ' || u2.lname AS collector_name
            FROM connections c
            JOIN users u1 ON u1.user_id = c.donor_user_id
            JOIN users u2 ON u2.user_id = c.collector_user_id
            WHERE c.connection_status = 'Active'
        """)

        rows = cursor.fetchall()
        print("[DEBUG] Raw rows from DB:")
        for row in rows:
            print(dict(row))  # 👈 print each row as a dictionary

        conn.close()

        # Prepare the data to be passed to the template
        requests = []
        for row in rows:
            requests.append({
                'donor_name': row['donor_name'],
                'collector_name': row['collector_name'],
                'connection_status': row['connection_status']
            })
        print("[DEBUG] Requests to be passed to template:", requests)
        # Pass the data to the template
        return render_template('connections.html', requests=requests)

    @app.route('/hub')
    def hub():
        return render_template('hub.html')

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

            new_posting_id = cursor.lastrowid  # Get the inserted Postings ID

            # Insert into `postings_audit` table
            cursor.execute(
                "INSERT INTO postings_audit (post_id, posted_by_user_id, post_status, post_title, post_date, item_id, quantity, pick_up_location, transaction_date, change_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    new_posting_id, session["user_id"], "new", title, post_date, item_id, quantity, pick_up_location,
                    post_date,
                    "User_posted"))

            conn.commit()
            conn.close()

            return redirect(url_for("myprofile"))  # ✅ Redirect back to profile after successful donation

        conn.close()
        return render_template("donate_form.html", items=items)  # NEW TEMPLATE

    # IVY CODE:
    @app.route('/request/<request_id>')
    def view_request(request_id):
        req = next((r for r in requests if r['id'] == request_id), None)
        if req:
            return render_template('view_request.html', request=req, username="Renee", impact_points=42, )
        else:
            return "Request not found", 404

    @app.route('/conversion/<conversion_id>')
    def view_conversion(conversion_id):
        conversion = next((c for c in conversions if c['id'] == conversion_id), None)
        if conversion:
            return render_template('view_conversion.html', conversion=conversion, username="Renee", impact_points=42, )
        else:
            return "Conversion not found", 404

    @app.route('/conversion/<conversion_id>/delete', methods=['POST'])
    def delete_conversion(conversion_id):
        global conversions
        conversions = [c for c in conversions if c['id'] != conversion_id]
        return redirect(url_for('impact'))

    # IVY CODE FOR DISCOVER
    @app.route('/discover', methods=['GET'])
    def discover():
        # Fetching query parameters from URL for filtering
        search_query = request.args.get('search', '').lower()  # Search term for title and description
        location = request.args.get('location', '').lower()  # Location filter

        # Debugging: Print the values of search_query and location
        print("Search query:", search_query)
        print("Location:", location)

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Base query for selecting posts
        query = """
            SELECT 
                p.postings_id, 
                p.post_title, 
                p.description, 
                p.post_date, 
                p.pick_up_location, 
                u.fname || ' ' || u.lname AS username
            FROM postings p
            JOIN users u ON p.donor_user_id = u.user_id
            WHERE p.post_status = 'New' 
                AND p.is_deleted = 0
        """

        # Adding filters if there are search and location values
        filters = []
        if search_query:
            query += " AND (LOWER(p.post_title) LIKE ? OR LOWER(p.description) LIKE ?)"
            filters.extend([f'%{search_query}%', f'%{search_query}%'])

        if location:
            query += " AND LOWER(p.pick_up_location) LIKE ?"
            filters.append(f'%{location}%')

        # Debugging: Print the final query and filters
        print("Final SQL query:", query)
        print("Filters:", filters)

        # Execute the query with filters
        cursor.execute(query, filters)
        posts = cursor.fetchall()

        # Total number of active, non-deleted postings (matching the same filters as shown)
        cursor.execute("""
            SELECT COUNT(*) AS total_postings 
            FROM postings 
            WHERE post_status = 'New' AND is_deleted = 0
        """)
        total_postings = cursor.fetchone()['total_postings']

        requested_ids = []

        if 'user_id' in session:
            cursor.execute("""
                SELECT DISTINCT item_id
                FROM postings_audit
                WHERE requested_by_user_id = ? AND change_type = 'Requested'
            """, (session['user_id'],))
            requested_ids = [row['item_id'] for row in cursor.fetchall()]

        # Close the connection
        conn.close()

        # Prepare posts data for the response (both for the template and live search)
        posts_list = []
        for post in posts:
            posts_list.append({
                'postings_id': post['postings_id'],
                'post_title': post['post_title'],
                'description': post['description'],
                'post_date': post['post_date'],
                'pick_up_location': post['pick_up_location'],
                'username': post['username']
            })
        # Debugging: Print the posts list to see if data is being fetched correctly
        print("Posts List:", posts_list)

        # If it's an AJAX request, return JSON, else render the template
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
            return jsonify({'posts': posts_list})
        else:
            return render_template('discover.html', posts=posts_list, search=search_query, location=location,
                                   total_postings=total_postings, requested_ids=requested_ids)

    # View donations via discover page 042625
    @app.route('/view_donation/<int:post_id>')
    def view_donation(post_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                p.post_title AS title, 
                p.description, 
                p.post_date AS date_posted, 
                p.pick_up_location AS location,
                p.post_title AS category,        
                u.fname || ' ' || u.lname AS username
            FROM postings p
            JOIN users u ON p.donor_user_id = u.user_id
            WHERE p.postings_id = ?
        """, (post_id,))

        post = cursor.fetchone()
        conn.close()

        if not post:
            return "Donation not found", 404

        return render_template('view_donation.html', post=post)

    @app.route('/request_collection/<int:post_id>', methods=['POST'])
    def request_collection(post_id):
        user_id = session.get('user_id')  # Or use Flask-Login's current_user.id

        if not user_id:
            return jsonify({'success': False, 'message': 'You must be logged in to request a donation.'})

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get original post data (and donor)
        cursor.execute("""
            SELECT p.*, u.user_id AS donor_user_id 
            FROM postings p
            JOIN users u ON p.donor_user_id = u.user_id
            WHERE p.postings_id = ?
        """, (post_id,))
        post = cursor.fetchone()

        if not post:
            conn.close()
            return jsonify({'success': False, 'message': 'Donation not found.'})

        # Check if user already requested this post (by searching audit records)
        cursor.execute("""
            SELECT 1 FROM postings_audit
            WHERE item_id = ? AND requested_by_user_id = ? AND change_type = 'Requested'
        """, (post_id, user_id))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return jsonify({'success': False, 'message': 'You already requested this donation.'})

        # Log the request into the audit table
        cursor.execute("""
            INSERT INTO postings_audit (
                posted_by_user_id,
                requested_by_user_id,
                post_title,
                description,
                post_status,
                post_date,
                collection_date,
                item_id,
                quantity,
                pick_up_location,
                approve_reject_date,
                change_type
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """, (
            post['donor_user_id'],
            user_id,
            post['post_title'],
            post['description'],
            post['post_status'],
            post['post_date'],
            post['item_id'],
            post['quantity'],
            post['pick_up_location'],
            'Requested'
        ))

        conn.commit()
        conn.close()

        return jsonify(
            {'success': True, 'message': 'Your request has been submitted!', 'button_text': 'Cancel Request'})

    @app.route('/cancel_request/<int:post_id>', methods=['POST'])
    def cancel_request(post_id):
        user_id = session.get('user_id')  # Or use Flask-Login's current_user.id

        if not user_id:
            return jsonify({'success': False, 'message': 'You must be logged in to cancel a request.'})

        conn = get_db_connection()
        cursor = conn.cursor()

        # Remove the request record from the postings_audit table
        cursor.execute("""
            DELETE FROM postings_audit
            WHERE item_id = ? AND requested_by_user_id = ? AND change_type = 'Requested'
        """, (post_id, user_id))

        conn.commit()
        conn.close()

        return jsonify(
            {'success': True, 'message': 'Your request has been canceled.', 'button_text': 'Request to Collect'})

    @app.route('/api/check_login_status')
    def check_login_status():
        return jsonify({"logged_in": "user_email" in session})


def create_app():
    app = Flask(__name__)
    app.secret_key = 'gMVyzFKCx%xpP^@k8DEghT7Abm2vQ92tj!jJiyZSt5qod!W&A&5V8yi3E3qtKZbdG8P#H@DyLz$#sinWA2@c2s*ZkU%PH$J7NepyBqKjZWPE9NP$Q%U2E@w%bQa&!4R9'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoexchange.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    csrf = CSRFProtect(app)

    # Initialize extensions
    bcrypt.init_app(app)
    db.init_app(app)

    # Register routes
    register_routes(app)

    return app


app = create_app()


# Database Connection
def get_db_connection():
    conn = sqlite3.connect("instance/ecoexchange.db")
    conn.row_factory = sqlite3.Row
    print("✅ Database connected successfully!")  # Debugging print
    return conn


# RUN THE FLASK APP
if __name__ == "__main__":
    print("✅ Flask app is starting...")
    with app.app_context():
        print(f"✅ SQLAlchemy is using the database connection: {db.engine.url}")
    app.run(debug=True)
