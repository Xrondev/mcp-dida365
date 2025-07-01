from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import logging
import threading
import base64
import secrets
import webbrowser
import httpx
from urllib.parse import urlencode
from dotenv import load_dotenv, find_dotenv
import os
from utils.token_mng import save_token, load_token
import time

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)


class CallbackServer:
    def __init__(
        self,
        state: str,
        host: str = "localhost",
        port: int = 11365,
    ):
        self.host = host
        self.port = port
        self.state = state
        self._server = None
        self._thread = None
        self.token_exchanged = threading.Event()

    def __enter__(self):
        """
        The context manager for callback server
        """
        svr = self

        class _CallbackHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress logging
                pass

            def do_GET(self):
                parsed_url = urlparse(self.path)
                match parsed_url.path:
                    case "/" | "/auth":
                        # Redirect to the auth page
                        params = {
                            "client_id": os.getenv("CLIENT_ID"),
                            "scope": os.getenv("SCOPE", "tasks:read tasks:write"),
                            "state": svr.state,
                            "redirect_uri": f"http://{svr.host}:{svr.port}/callback",
                            "response_type": "code",
                        }
                        logging.info(
                            f"Redirecting to {os.getenv('AUTH_URL')}?{urlencode(params)}"
                        )
                        self.send_response(302)
                        self.send_header(
                            "Location", f"{os.getenv('AUTH_URL')}?{urlencode(params)}"
                        )
                        self.end_headers()
                    case "/callback":
                        # Provider has redirected back with code
                        qs = parse_qs(parsed_url.query)
                        code = qs.get("code", [None])[0]
                        state = qs.get("state", [None])[0]

                        if state != svr.state:
                            self.send_error(
                                400, "Wrong state received, aborting as CSRF attack"
                            )
                            raise ValueError(
                                "Wrong state received, aborting as CSRF attack"
                            )

                        data = {
                            "code": code,
                            "grant_type": "authorization_code",
                            "scope": os.getenv("SCOPE", "tasks:read tasks:write"),
                            "redirect_uri": f"http://{svr.host}:{svr.port}/callback",
                        }

                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Authorization": f"Basic {base64.b64encode(f'{os.getenv("CLIENT_ID")}:{os.getenv("CLIENT_SECRET")}'.encode('ascii')).decode('ascii')}",
                            "User-Agent": "MCP-dida365/1.0",  # Ticktick requires UA, or else return 400
                        }
                        assert os.getenv("TOKEN_URL") is not None, (
                            "TOKEN_URL is not set"
                        )
                        response = httpx.post(
                            os.getenv("TOKEN_URL") or "",
                            data=data,
                            headers=headers,
                        )
                        response_json = response.json()
                        access_token = response_json.get("access_token")
                        expires_in = response_json.get("expires_in")

                        if response.status_code != 200 or not access_token:
                            self.send_error(
                                400,
                                f"Failed to get token, check your ClientID and ClientSecret, make sure on the provider's side redirect_uri is exactly {f'{svr.host}:{svr.port}/callback'}",
                            )

                            raise ValueError(
                                f"Failed to get token, check your ClientID and ClientSecret, make sure on the provider's side redirect_uri is exactly {f'{svr.host}:{svr.port}/callback'}"
                            )

                        save_token(access_token, expires_in)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write("OAuth Success".encode("utf-8"))
                        svr.token_exchanged.set()
                    case _:
                        self.send_error(404, "Not Found")

        self._server = HTTPServer((self.host, self.port), _CallbackHandler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="CallbackServer",
            daemon=True,
        )
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._server:
            self._server.shutdown()
        if self._thread:
            self._thread.join()


class Auth:
    def __init__(self):
        self.host = "localhost"
        self.port = int(os.getenv("PORT") or 11365)

    def run(self):
        token, expires_in = load_token()
        if token is None or expires_in < time.time():
            with CallbackServer(
                state=secrets.token_hex(16),
                host=self.host,
                port=self.port,
            ) as svr:
                if os.getenv("DOCKER_SERVER") not in ("1", "true", "True", "TRUE"):
                    try:
                        webbrowser.open(f"http://{self.host}:{self.port}/auth")
                    except Exception as e:
                        logging.error(f"Failed to open browser: {e}")
                else:
                    logging.info(
                        f"Please visit {self.host}:{self.port}/auth to authorize"
                    )
                svr.token_exchanged.wait()
        else:
            logging.info("Token is valid, skipping authorization")
