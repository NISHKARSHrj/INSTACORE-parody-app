from flask import Flask
from database import init_db
from routes import register_routes
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

init_db()
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

