from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins='*')

# List to store chat messages
chat_history = []

# Set to store active users
active_users = set()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        return render_template('chat.html', username=username, chat_history=chat_history)
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    active_users.add(username)
    # Send the active users to the new user
    socketio.emit('active users', list(active_users), room=request.sid)
    socketio.emit('user joined', username, room=room, include_self=False)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    active_users.remove(username)
    socketio.emit('user left', username, room=room, include_self=False)

@socketio.on('chat message')
def handle_message(data):
    username = data['username']
    message = data['message']
    room = data['room']
    chat_entry = {'username': username, 'message': message}
    chat_history.append(chat_entry)
    socketio.emit('chat message', chat_entry, room=room)

if __name__ == '__main__':
    socketio.run(app)
