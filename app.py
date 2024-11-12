from flask import Flask, render_template, send_file, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_path

app = Flask(__name__)
socketio = SocketIO(app)

# Admin-controlled page number, initially set to the first page
current_page = 1
admin_sid = None  # Socket ID for the admin

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf')
def serve_pdf():
    return send_file("GCCF  V.pdf", as_attachment=False)

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    global admin_sid
    print(f"Client disconnected: {request.sid}")
    if request.sid == admin_sid:
        admin_sid = None
        emit('admin_left', broadcast=True)

@socketio.on('join')
def handle_join(role):
    global admin_sid
    join_room('viewers')
    
    if role == 'admin':
        admin_sid = request.sid
        emit('set_role', {'role': 'admin'}, room=request.sid)
    else:
        emit('set_role', {'role': 'viewer'}, room=request.sid)
        emit('update_page', {'page': current_page}, room=request.sid)  # Sync to current page

@socketio.on('change_page')
def change_page(data):
    global current_page
    page = data.get('page', 1)
    
    # If admin changes the page, broadcast to all
    if request.sid == admin_sid:
        current_page = page
        emit('update_page', {'page': current_page}, room='viewers')

if __name__ == '_main_':
    socketio.run(app, debug=True)