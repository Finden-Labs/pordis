from client.client import Client
from server.server import run_server_threaded

import sys

def main():
    if "--serve" in sys.argv:
        run_server_threaded()
    else:
        Client()

if __name__ == "__main__":
    main()