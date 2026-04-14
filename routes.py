import os
from flask import request, jsonify, render_template, redirect,session
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename
from database import get_connection
from datetime import datetime
from utils import UPLOAD_FOLDER, configure,ALLOWED_EXTENSIONS, allowed_files

load_dotenv()

def register_routes(app):

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.secret_key = os.getenv("SECRET_KEY")

    if not app.secret_key:
            import secrets
            app.secret_key = secrets.token_hex(32)
            print("⚠️  WARNING: No SECRET_KEY in .env file. Using random key!")
    
    if not os.path.isdir(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


    @app.route("/")
    def home():
        return redirect("/login")
    
    @app.route("/feed")
    def feed():
        if "user_id" not in session:
            return redirect("/login")

        return render_template("feed.html", user_id=session["user_id"])

    # signup in the application
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "GET":
            return render_template("signup.html")
        data = request.get_json()
        name = data.get("name")
        password = data.get("password")

        if not name or not password:
            return jsonify({
                "error": "Name and Password are required"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                "error": "User already exists"
            }), 400
        
        cursor.execute("INSERT INTO users (user_name, user_password) VALUES (?, ?)", (name, password))
        conn.commit()
        conn.close()
        return redirect("/login")
    
    # login in the application
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        data = request.get_json()
        name = data.get("name")
        password = data.get("password")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE user_name = ? AND user_password = ?", (name, password)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                "error": "Invalid credentials"
            }), 401
        
        session["user_id"] = user[0]

        return redirect("/feed")
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")
    # post a new post
    @app.route("/posts", methods = ["POST"])
    def create_post():
        user_id =request.form.get("user_id")
        content = request.form.get("content", "")
        image = request.files.get("image")

        if not user_id:
            return jsonify({
                "error": "User ID is required"
            }), 400
        
        image_path = None

        if image and allowed_files(image.filename):
            filename = secure_filename(image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(save_path)
            image_path = filename 

        timestamp = datetime.utcnow().isoformat()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO posts (user_id, content, image_path, timestamp) VALUES(?,?,?,?)", (user_id, content, image_path, timestamp))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Post created successfully"
        })
    
    # get posts
    @app.route("/posts", methods=["GET"])
    def get_posts():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT posts.id, posts.content, posts.image_path, posts.timestamp, users.user_name, COUNT(likes.id) as like_count 
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN likes ON posts.id = likes.post_id
            GROUP BY posts.id
            ORDER BY posts.id DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return jsonify([
            {
                "id": r[0],
                "content": r[1],
                "image": r[2],
                "timestamp": r[3],
                "user": r[4],
                "like_count": r[5]
            }
            for r in rows
        ])
    
    @app.route("/like", methods=["POST"])
    def like_post():
        data = request.get_json()
        user_id = data.get("user_id")
        post_id = data.get("post_id")

        if not user_id or not post_id:
            return jsonify({
                "error": "User ID and Post ID are required"
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))

        existing = cursor.fetchone()
        if existing:
            # unlike
            cursor.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
            action = "unliked"
        else:
            cursor.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (user_id,post_id))
            action = "liked"

        conn.commit()
        conn.close()

        return jsonify({
            "message": f"Post {action} successfully"
        }), 201
    
    @app.route("/dltposts", methods=["DELETE"])
    def dltpost():
        data = request.get_json()
        post_id  = data.get("post_id")
        if not post_id:
            return jsonify({
                "error": "Post ID is required"
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,)), 200
        conn.commit()
        conn.close()

        return  jsonify({
            "message": "Post deleted successfully"
        })

    @app.route("/dltuser", methods=["DELETE"])
    def dltuser():
        data = request.get_json()
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({
                "error": "User ID is required"
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,)), 200
        cursor.execute("DELETE FROM posts WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "message": "User deleted successfully"
        })