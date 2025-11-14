from flask import Flask, g, redirect, url_for
from flask_login import LoginManager, current_user
import pymysql

# 🧩 MySQL Configuration
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "socialmedia_application"

# ------------------------------
# Database helper
# ------------------------------
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# ------------------------------
# Flask App Factory
# ------------------------------
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asdfaskjdfgahet'

    # Manage per-request database connection
    @app.before_request
    def before_request():
        g.db = get_db_connection()
        g.cursor = g.db.cursor()

    @app.teardown_request
    def teardown_request(exception=None):
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

    # ------------------------------
    # Import blueprints
    # ------------------------------
    from .views import views
    from .auth import auth
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(views, url_prefix="/")

    # ------------------------------
    # Flask-Login setup
    # ------------------------------
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = None  # Disable automatic messages to prevent loop
    login_manager.init_app(app)

    from .auth import DBUser, get_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        user_dict = get_user_by_id(user_id)
        if user_dict:
            return DBUser(user_dict)
        return None

    # ------------------------------
    # Simple test route
    # ------------------------------
    @app.route('/test')
    def test():
        return "App is working!"

    # ------------------------------
    # Handle 404
    # ------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return "Page not found", 404

    # ------------------------------
    # Ensure DB exists
    # ------------------------------
    create_database()

    print("✅ Flask app initialized and connected to MySQL.")
    return app


# ------------------------------
# Create DB & Tables if missing
# ------------------------------
def create_database():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        conn.commit()
        conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(150) NOT NULL,
            first_name VARCHAR(150),
            last_name VARCHAR(150),
            profile_picture VARCHAR(1000),
            bio VARCHAR(1500),
            links VARCHAR(500),
            date_joined DATETIME
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS post (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100),
            content VARCHAR(5000),
            image VARCHAR(1000),
            category VARCHAR(100),
            drafts boolean default false,
            tags VARCHAR(500),
            date DATETIME,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `like` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            post_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dislike (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            post_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            post_id INT,
            data VARCHAR(1000),
            date DATETIME,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reply_comment (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            comment_id INT,
            post_id INT,
            data VARCHAR(1000),
            date DATETIME,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (comment_id) REFERENCES comment(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment_like (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            post_id INT,
            comment_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
            FOREIGN KEY (comment_id) REFERENCES comment(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_request (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT,
            receiver_id INT,
            status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
            date_sent DATETIME,
            date_responded DATETIME,
            FOREIGN KEY (sender_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES user(id) ON DELETE CASCADE,
            UNIQUE KEY unique_request (sender_id, receiver_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendship (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user1_id INT,
            user2_id INT,
            date_created DATETIME,
            FOREIGN KEY (user1_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (user2_id) REFERENCES user(id) ON DELETE CASCADE,
            UNIQUE KEY unique_friendship (user1_id, user2_id)
        )
        """)

        conn.commit()
        conn.close()
        print("✅ All tables created successfully in MySQL.")
    except Exception as e:
        print("❌ Error creating database or tables:", e)
