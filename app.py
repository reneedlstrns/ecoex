import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from extensions import bcrypt, db
from models.user import User
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

    @app.route('/editprofile')
    def edit_profile():
        return render_template('editprofile.html')

    @app.route("/myprofile")
    def myprofile():
        if 'user_email' in session:
            user = get_user_by_email(session['user_email'])

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
                    u2.fname || ' ' || u2.lname AS collector_name,
                    postings.post_title       
                FROM connections c
                JOIN users u1 ON u1.user_id = c.donor_user_id
                JOIN users u2 ON u2.user_id = c.collector_user_id
                LEFT JOIN postings ON c.postings_id = postings.postings_id  -- Join with postings to get the post title
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
                'connection_status': row['connection_status'],
                'post_title': row['post_title']  # Adding the post title here
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
                total_connections=total_connections
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
    
    #IVY CODE FOR IMPACT
    @app.route('/impact')
    def impact():
        print("Impact route hit", flush=True)
        user_id = session['user_id']  # Assuming the user is logged in and their ID is in the session

<<<<<<< HEAD
     
    @app.route('/connections')
    def connections():
        if 'user_email' in session:
            user_id = session['user_id']

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT u.user_id, u.fname, u.lname, u.email
                FROM users u
                JOIN postings p ON u.user_id = p.donor_user_id
                WHERE p.collector_by_user_id = ?
                UNION
                SELECT DISTINCT u.user_id, u.fname, u.lname, u.email
                FROM users u
                JOIN postings p ON u.user_id = p.collector_by_user_id
                WHERE p.donor_user_id = ?;
            """, (user_id, user_id))

            connections = cursor.fetchall()
            conn.close()

            return render_template('connections.html', connections=connections)
        else:
            return redirect(url_for('login'))
 
   
=======
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

    #IVY CODE FOR CONNECTIONS
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


>>>>>>> 71379b21b9863e0553111f63ee596f2004041649
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

            new_posting_id = cursor.lastrowid  # Get the inserted posting ID

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
    
    #IVY CODE FOR DISCOVER
    @app.route('/discover', methods=['GET'])
    def discover():
<<<<<<< HEAD
        # Get filter parameters from the request (search, category, location)
        search_query = request.args.get('search', '').lower()
        category = request.args.get('category', '').lower()
        location = request.args.get('location', '').lower()

         # Query the database for posts that are not deleted
        filtered_posts = Posting.query.filter(Posting.is_deleted == False)

        # Apply search filter on title and description
        if search_query:
            filtered_posts = filtered_posts.filter(
                (Posting.post_title.ilike(f'%{search_query}%')) |
                (Posting.description.ilike(f'%{search_query}%'))
            )

        # Apply category filter (assuming 'category' is stored in 'post_title' or a related column)
        if category:
            filtered_posts = filtered_posts.filter(
                Posting.post_title.ilike(f'%{category}%')
            )

            return render_template('discover.html', posts=filtered_posts, search=search_query, category=category,
                                   donation_posts=donation_posts)
        # Apply location filter (assuming 'location' is stored in 'pick_up_location' or a related column)
        if location:
            filtered_posts = filtered_posts.filter(
                Posting.pick_up_location.ilike(f'%{location}%')
            )

        # Execute the query and get the filtered list of posts
        filtered_posts = filtered_posts.all()

        # Render the template with the filtered posts and search params
        return render_template('discover.html', posts=filtered_posts, search=search_query, category=category, location=location)
=======
        # Fetching query parameters from URL for filtering
        search_query = request.args.get('search', '').lower()  # Search term for title and description
        location = request.args.get('location', '').lower()   # Location filter
    
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
                u.fname || ' ' || u.lname AS username, 
                u.location_title AS location
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


        # Close the connection
        conn.close()

        # Prepare posts data for the response (both for the template and live search)
        posts_list = []
        for post in posts:
            posts_list.append({
                'id': post['postings_id'],
                'title': post['post_title'],
                'description': post['description'],
                'date_posted': post['post_date'],
                'location': post['pick_up_location'],
                'username': post['username'],
                'location_title': post['location'],
            })

        # If it's an AJAX request, return JSON, else render the template
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
            return jsonify({'posts': posts_list})
        else:
            return render_template('discover.html', posts=posts_list, search=search_query, location=location, total_postings=total_postings)


>>>>>>> 71379b21b9863e0553111f63ee596f2004041649

    @app.route('/donation/<post_id>')
    def view_donation(post_id):
        post = next((p for p in donation_posts if p['id'] == post_id), None)
        if post:
            return render_template('view_donation.html', post=post)
        else:
            return "Donation post not found", 404

    @app.route('/request-collection/<post_id>', methods=['POST'])
    def request_collection(post_id):
        print(f"Collection requested for post: {post_id}")
        return redirect(url_for('discover'))


def create_app():
    app = Flask(__name__)
    app.secret_key = "RENEE"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoexchange.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    bcrypt.init_app(app)
    db.init_app(app)

    # Register routes
    register_routes(app)

    return app


app = create_app()


# Database Connection
def get_db_connection():
    conn = sqlite3.connect("ecoexchange.db")
    conn.row_factory = sqlite3.Row
    print("✅ Database connected successfully!")  # Debugging print
    return conn





def create_app():
        app = Flask(__name__)
        app.secret_key = "RENEE"
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoexchange.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize extensions
        bcrypt.init_app(app)
        db.init_app(app)

        # Register routes
        register_routes(app)

        return app


# RUN THE FLASK APP
if __name__ == "__main__":
    print("✅ Flask app is starting...")
    app = create_app()
    with app.app_context():
        print(f"✅ SQLAlchemy is using the database connection: {db.engine.url}")
    app.run(debug=True)
