import os
import cloudinary
import cloudinary.uploader
from flask import request, jsonify, render_template, redirect,session
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename
from database import get_connection
from datetime import datetime
from utils import UPLOAD_FOLDER,  configure,ALLOWED_EXTENSIONS, allowed_files
from dotenv import load_dotenv
load_dotenv()
configure()

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

        cursor.execute("SELECT * FROM users WHERE user_name = %s", (name,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                "error": "User already exists"
            }), 400
        try:
            cursor.execute("INSERT INTO users (user_name, user_password) VALUES (%s, %s)", (name, password))
            conn.commit()
            return jsonify({
            "message": "Signup successful"
            })
    
        except:
            conn.rollback()
            conn.close()
            return jsonify({
                "error": "USER already exists"
            }), 400
        conn.close()

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
            "SELECT * FROM users WHERE user_name = %s AND user_password = %s", (name, password)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                "error": "Invalid credentials"
            }), 401
        
        session["user_id"] = user[0]
        session["user_name"] = user[1]

        return jsonify({
        "message": "Login successful"
        })
    
    @app.route("/logout")
    def logout():
        session.clear()
        return jsonify({
            "message": "Logged out successfully"
        })
    
    @app.route("/me")
    def me():
        if "user_id" not in session:
            return jsonify({"error": "not logged in"}), 401
        return jsonify({
            "user_id":   session["user_id"],
            "user_name": session["user_name"]
        })
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
            ext = image.filename.rsplit(".", 1)[1].lower()
            if ext in ["mp4", "mov", "avi", "mkv"]:
                upload_res = cloudinary.uploader.upload(
                    image,
                    resource_type = "video"
                )
            else:
                upload_res = cloudinary.uploader.upload(image)
            
            image_path = upload_res["secure_url"]

        timestamp = datetime.utcnow().isoformat()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO posts (user_id, content, image_path, timestamp) VALUES(%s,%s,%s,%s)", (user_id, content, image_path, timestamp))

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
            SELECT posts.id, posts.content, posts.image_path, posts.timestamp, users.user_name, posts.user_id, COUNT(likes.id) as like_count 
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN likes ON posts.id = likes.post_id
            GROUP BY posts.id, posts.content, posts.image_path, posts.timestamp, users.user_name, posts.user_id
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
                "user_id": r[5],
                "like_count": r[6]
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

        cursor.execute("SELECT * FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))

        existing = cursor.fetchone()
        if existing:
            # unlike
            cursor.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
            action = "unliked"
        else:
            cursor.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id,post_id))
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

        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,)), 200
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

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,)), 200
        cursor.execute("DELETE FROM posts WHERE user_id = %s", (user_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "message": "User deleted successfully"
        })
    

    @app.route("/editpost", methods=["PUT"])
    def editpost():
        data = request.get_json()

        post_id = data.get("post_id")
        content = data.get("content")

        if not post_id:
            return jsonify({
                "error": "Post ID is required"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE posts
            SET content = %s
            WHERE id = %s
        """, (content, post_id))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Post updated successfully"
        })