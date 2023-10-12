import base64
import json
import os
import socket
import threading

# Define the server's address and port
HOST = '127.0.0.1'
PORT = 12345

# Create a client socket and set socket options
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


# Function to download a file from the server
def download_file(payload, client_name):
    # Extract file name and content from the payload
    name = payload.get("file_name")
    content = payload.get("file_content")

    # Create a directory to store files if it doesn't exist
    if not os.path.exists(f"files_{client_name}"):
        os.makedirs(f"files_{client_name}")

    # Write the received file content to a file in the client's directory
    with open(os.path.join(f"files_{client_name}", name), "wb") as file:
        file.write(base64.b64decode(content))

    print(f"\nReceived file: {name}")


# Function to list files in the client's directory
def list_client_files(folder_path):
    files = []
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            files.append(filename)
    return files


# Function to handle media files in the payload
def media_files(payload):
    files = payload.get("files", [])

    if files:
        print("\nAvailable media files:")
        for i, name in enumerate(files, start=1):
            print(f"{i}. {name}")
    else:
        print("\nNo files available.")


def get_file_path():
    file_path = input("Enter the path to the file: ")
    if not file_path:
        print("Invalid file path.")
        return

    if not os.path.exists(file_path):
        print("File not found.")
        return

    return file_path


# Function to continuously receive messages from the server
def receive_messages():
    while True:
        message = client_socket.recv(262144).decode('utf-8')

        if not message:
            break

        try:
            message_dict = json.loads(message)

            try:
                message_type = message_dict.get("message_type")
                payload = message_dict.get("payload")

                if message_type == "file":
                    download_file(payload, client_name)

                elif message_type == "media":
                    media_files(payload)
            except:
                print(f"\nReceived: {message_dict}")

        except json.JSONDecodeError:
            print(f"\nReceived: {message}")


# Get the client's username and room name
client_name = input("Enter your username: ")
room_name = input("Enter the room name: ")

# Create a connection message to send to the server
connect_message = {
    "message_type": "connect",
    "payload": {
        "name": client_name,
        "room": room_name
    }
}

# Send the connection message to the server
client_socket.send(json.dumps(connect_message).encode('utf-8'))

# Create a thread to continuously receive messages
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Main loop for user interaction
while True:
    text = input("Enter a message ('exit' for quit, 'u' for upload, 'm' for media, 'd' for download): ")

    if not text:
        continue

    if text.lower() == 'exit':
        break

    elif text.lower() == 'u':
        # Upload files to the server
        file_path = get_file_path()

        if not file_path:
            continue

        file_name = os.path.basename(file_path)

        with open(file_path, "rb") as file:
            content = base64.b64encode(file.read()).decode('utf-8')

        upload_file_message = {
            "message_type": "upload",
            "payload": {
                "file_name": file_name,
                "file_content": content,
            }
        }
        client_socket.send(json.dumps(upload_file_message).encode('utf-8'))
        continue

    elif text.lower() == 'm':
        # Request a list of media files from the server
        files_list_request = {
            "message_type": "media",
            "payload": {}
        }

        client_socket.send(json.dumps(files_list_request).encode('utf-8'))

    elif text.lower() == 'd':
        # Download a file from the server
        file_name = input("File for download: ")

        if not file_name:
            print("Invalid file name.")
            continue

        download_file_request = {
            "message_type": "download",
            "payload": {
                "file_name": file_name
            }
        }

        client_socket.send(json.dumps(download_file_request).encode('utf-8'))

    else:
        # Send a regular text message to the server
        message = {
            "message_type": "message",
            "payload": {
                "text": text
            }
        }
        client_socket.send(json.dumps(message).encode('utf-8'))

# Close the client socket when done
client_socket.close()
