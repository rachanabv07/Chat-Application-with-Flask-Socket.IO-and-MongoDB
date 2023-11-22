from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "secret"
app.config["MONGO_URI"] = "mongodb+srv://rachana:test@cluster0.adge1qk.mongodb.net/ChatApp"

socketio = SocketIO(app)
mongo = PyMongo(app)

users = {}

@socketio.on("connect")
def handle_connect():
    print("Client connected!")

@socketio.on("user_join")
def handle_user_join(username):
    print(f"User {username} joined!")
    users[username] = request.sid

@socketio.on("new_message")
def handle_new_message(message):
    print(f"New message: {message}")
    username = next((user for user, sid in users.items() if sid == request.sid), None)

    try:
        # Ensure that the mongo object is not None
        if mongo is not None:
            # Store message in MongoDB
            mongo.db.messages.insert_one({
                "username": username,
                "message": message,
                "timestamp": datetime.now()
            })

            emit("chat", {"message": message, "username": username}, broadcast=True)
        else:
            print("MongoDB connection is None. Check your MongoDB URI.")
    except Exception as e:
        print(f"Error inserting message into MongoDB: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_messages")
def get_messages():
    messages = list(mongo.db.messages.find())
    return jsonify(messages)

if __name__ == "__main__":
    socketio.run(app)
