#!/usr/bin/env python3

from client.socket_path import get_niri_socket_path
from client.socket_client import connect_to_niri_socket
from client.socket_client import subscribe_to_event_stream

def main():
    socket_path = get_niri_socket_path()
    if not socket_path:
        return

    sock = connect_to_niri_socket(socket_path)
    if not sock:
        return

    subscribe_to_event_stream(sock)

if __name__ == "__main__":
    main()
