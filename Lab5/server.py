import base64
import json
import os
import socket
import threading

# Define the server's address and port
HOST = '127.0.0.1'
PORT = 12345

# Create a server socket and set socket options
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the server socket to the host and port
server_socket.bind((HOST, PORT))

# Start listening for incoming connections
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

# Create dictionaries to manage clients, chat rooms, and user information
clients = {}  # Dictionary to track clients and their associated rooms
chat_rooms = {}  # Dictionary to track chat rooms and their associated clients
users = {}  # Dictionary to track user information


# Function to list media files available in the chat room
def media(client_socket):
    # Check if the "media" directory exists; if not, create it
    if not os.path.exists("media"):
        os.makedirs("media")

    # Get the room name associated with the client
    room_name = clients.get(client_socket)
    chat_dir = os.path.join("media", room_name)

    files = []

    # List files in the chat room's directory
    if os.path.exists(chat_dir):
        for filename in os.listdir(chat_dir):
            if os.path.isfile(os.path.join(chat_dir, filename)):
                files.append(filename)

    return files


# Function to handle the upload of a file from a client
def handle_file_upload(payload, client_socket):
    file_name = payload.get("file_name")
    room_name = clients.get(client_socket)
    file_content = payload.get("file_content")
    sender = users[client_socket]

    # Check if the "media" directory exists; if not, create it
    if not os.path.exists("media"):
        os.makedirs("media")

    chat_dir = os.path.join("media", room_name)

    if not os.path.exists(chat_dir):
        os.makedirs(chat_dir)

    # Write the received file content to a file in the chat room's directory
    with open(os.path.join(chat_dir, file_name), "wb") as file:
        file.write(base64.b64decode(file_content))

    # Broadcast a notification to all clients in the chat room
    message_user = f"{sender} uploaded the file: {file_name}"
    if room_name in chat_rooms:
        for client in chat_rooms[room_name]:
            if client != client_socket:
                client.send(message_user.encode('utf-8'))


# Function to send a file to a client
def send_file(file_name, file_content, client_socket):
    file_message = {
        "message_type": "file",
        "payload": {
            "file_name": file_name,
            "file_content": file_content,
        }
    }
    client_socket.send(json.dumps(file_message).encode('utf-8'))


# Function to handle the request to download a file
def send_download_file(payload, client_socket):
    if not os.path.exists("media"):
        os.makedirs("media")

    room_name = clients.get(client_socket)

    if not room_name:
        return

    file_name = payload.get("file_name")
    chat_dir = os.path.join("media", room_name)

    # Check if the requested file exists, and if so, send it to the client
    if os.path.exists(os.path.join(chat_dir, file_name)):
        with open(os.path.join(chat_dir, file_name), "rb") as file:
            file_content = base64.b64encode(file.read()).decode('utf-8')
            send_file(file_name, file_content, client_socket)
    else:
        client_socket.send("File not found".encode('utf-8'))


# Function to send a list of available media files to a client
def send_media(client_socket):
    server_files = media(client_socket)

    if not server_files or len(server_files) == 0:
        client_socket.send("No files found".encode('utf-8'))
        return

    files_list_message = {
        "message_type": "media",
        "payload": {
            "files": server_files
        }
    }

    client_socket.send(json.dumps(files_list_message).encode('utf-8'))


# Function to send a connection acknowledgment message to a client
def send_connect(client_socket):
    message = "Connected to the room."
    connect_ack_message = {
        "message_type": "connect_ack",
        "payload": {
            "message": message
        }
    }

    client_socket.send(json.dumps(connect_ack_message["payload"]["message"]).encode('utf-8'))


# Function to send a notification message to a client
def send_notification(client_socket, notification_message):
    notification = {
        "message_type": "notification",
        "payload": {
            "message": notification_message
        }
    }
    client_socket.send(json.dumps(notification["payload"]["message"]).encode('utf-8'))


# Function to handle a client's connection and messages
def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")

    try:
        while True:
            # Receive a message from the client
            message = client_socket.recv(262144).decode('utf-8')

            if not message:
                break

            print(f"Received from {client_address}: {message}")

            try:
                message_dict = json.loads(message)
                message_type = message_dict.get("message_type")
                payload = message_dict.get("payload")

                if message_type == "connect":
                    client_name = payload.get("name")
                    room_name = payload.get("room")

                    # Check if the chat room exists; if not, create it
                    if room_name not in chat_rooms:
                        chat_rooms[room_name] = []

                    # Add the client to the chat room and store user information
                    chat_rooms[room_name].append(client_socket)
                    clients[client_socket] = room_name
                    users[client_socket] = client_name

                    # Broadcast a notification that a user has joined the room
                    notification_message = f"{client_name} has joined the room."
                    for client in chat_rooms[room_name]:
                        if client != client_socket:
                            send_notification(client, notification_message)

                elif message_type == "message":
                    text = payload.get("text")
                    room = clients.get(client_socket)
                    sender = users[client_socket]

                    # Create a message to broadcast to all clients in the room
                    message = {
                        "message_type": "message",
                        "payload": {
                            "sender": sender,
                            "room": room,
                            "message": text
                        }
                    }

                    # Broadcast the message to all clients in the room
                    if room in chat_rooms:
                        for client in chat_rooms[room]:
                            if client != client_socket:
                                client.send(
                                    json.dumps(
                                        message["payload"]["sender"] + ": " + message["payload"]["message"]).encode(
                                        'utf-8'))

                elif message_type == "upload":
                    handle_file_upload(payload, client_socket)

                elif message_type == "media":
                    # Send a list of available media files to the client
                    send_media(client_socket)

                elif message_type == "download":
                    # Handle the request to download a file
                    send_download_file(payload, client_socket)
            except json.JSONDecodeError:
                pass

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")


    finally:
        # Clean up and handle client disconnection
        room_name = clients.get(client_socket)

        if room_name:
            chat_rooms[room_name].remove(client_socket)

            # Broadcast a notification that a user has left the room
            username = users[client_socket]
            notification_message = f"{username} has left the room."

            # Remove client-related information
            del clients[client_socket]
            del users[client_socket]

            # Broadcast the notification to all clients in the room
            for client in chat_rooms[room_name]:
                send_notification(client, notification_message)

        # Close the client socket
        client_socket.close()

# Main loop to accept incoming client connections and create client handler threads
while True:
    client_socket, client_address = server_socket.accept()
    clients[client_socket] = None
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
