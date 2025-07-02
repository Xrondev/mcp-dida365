from utils.auth import Auth
from server.mcp import mcp


def main():
    Auth().run()
    mcp.run()


if __name__ == "__main__":
    main()
