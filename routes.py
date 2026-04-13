from flask import request, jsonify
from database import get_connection

def register_routes(app):
    @app.route("/")
    def index():
        return "Hello, World!"
    
    @app.route("/signup", methods=["POST"])
    def signup():
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
        return jsonify({
            "message": "User created successfully"
        }), 201
    
    @app.route("/login", methods=["POST"])
    def login():
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

        return jsonify({
            "message": "Login successful"
        }), 200