  # 🚀 InstaCore — Social Media App

InstaCore is a full-stack social media web application where users can create posts, upload images, like posts, and manage their content.

🌐 **Live App:** https://instacore-toq2.onrender.com

---

## ✨ Features

* 🔐 User Authentication (Signup/Login)
* 📝 Create, Edit, Delete Posts
* ❤️ Like / Unlike Posts
* 🖼️ Image Upload (Cloudinary)
* 📱 Responsive UI
* ☁️ Cloud Database (PostgreSQL on Render)

---

## 🛠️ Tech Stack

**Frontend**

* HTML, CSS, JavaScript

**Backend**

* Python (Flask)

**Database**

* PostgreSQL (Render)

**Media Storage**

* Cloudinary

**Deployment**

* Render

---

## 📂 Project Structure

```
INSTA_CORE_app/
│
├── app.py
├── routes.py
├── database.py
├── utils.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   └── feed.html
│
├── static/
│   ├── style.css
│   ├── auth.js
│   └── feed.js
│
└── .env
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/instacore.git
cd instacore
```

---

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Setup environment variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url

CLOUD_NAME=your_cloud_name
API_KEY=your_api_key
API_SECRET=your_api_secret
```

---

### 5. Run the app

```
python app.py
```

---

## 🧠 How It Works

1. User logs in → session created
2. User creates post →

   * Image uploaded to Cloudinary
   * Data stored in PostgreSQL
3. Feed fetches posts from DB
4. UI renders posts dynamically

---

## 🤝 Contributing

Feel free to fork this project and improve it.

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 💡 Author

Built with ❤️ by Nishkarsh
