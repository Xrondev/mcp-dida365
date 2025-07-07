import logging
from utils.auth import Auth
from server.mcp import mcp
import sys
import traceback

logging.basicConfig(
    level=logging.INFO,
)


def main():
    try:
        Auth().run()
        mcp.run()
    except Exception as e:
        logging.error(f"Error: {e}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
