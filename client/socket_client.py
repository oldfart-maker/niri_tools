#!/usr/bin/env python3

import socket
import json

def send_command(sock_path, message):
    """Send an IPC message to Niri and return the JSON response.
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sock_path)
    """

    sock = connect_to_niri_socket(sock_path)

    if isinstance(message, dict):
        message = json.dumps(message)
    message += "\n"

    sock.sendall(message.encode("utf-8"))
    result = sock.recv(65536)
    sock.close()

    return json.loads(result.decode())

def connect_to_niri_socket(socket_path):
    """Connect to the given Unix domain socket path."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        return sock
    except Exception as e:
        print(f"❌ Error connecting to socket: {e}")
        return None

def subscribe_to_event_stream(sock):
    """Send the event-stream subscription and start reading events."""
    try:
        # Correct subscription message – just a quoted string, newline terminated
        subscribe_message = '{"EventStream": null}\n'        
        sock.sendall(subscribe_message.encode("utf-8"))
        print("✅ Subscribed to Niri event stream.\n")
    except Exception as e:
        print(f"❌ Failed to send subscription message: {e}")
        return

    buffer = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                print("🔌 Connection closed by Niri.")
                break

            buffer += chunk

            # Handle newline-delimited JSON (NDJSON)
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    event = json.loads(line.decode("utf-8"))
                    print("🔔 Event:")
                    print(json.dumps(event, indent=2))
                    print("-" * 40)
                except json.JSONDecodeError as err:
                    print(f"⚠️ Failed to decode JSON: {err}")
                    print(f"Raw line: {line}")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted — closing connection.")
    finally:
        sock.close()
        print("✅ Socket closed.")
    
