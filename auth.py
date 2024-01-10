from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket
from icecream import ic
import requests
from app import Core, config, TOKEN_FILE
import webbrowser

HOST = "localhost"
PORT = 8000
OAUTH_ENDPOINT = Core.OAUTH_ENDPOINT
SCOPE = Core.SCOPE
VERSION = Core.VERSION


def extract_vk_auth_token_from_redirect():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(4)
    client_socket, address = server.accept()
    request = client_socket.recv(1024).decode()
    url = f"http://{HOST}"+request.split(" ")[1]
    message = "Кажется, аутентификация была успешна!"
    token = parse_qs(urlparse(url).query).get("access_token", [""])[0]
    if token == "":
        message = "Кажется, аутентификация пошла не по плану!"
    response = f'HTTP/1.1 200 OK\r\n\
    Content-Type: text/html; charset=utf-8\r\n\r\n\
    <html><head><meta charset="utf-8"></head><body>{message}</body></html>'.encode("utf-8")
    client_socket.send(response)
    return token


def vk_auth_with_local_webserver():
    webbrowser.open(f"{OAUTH_ENDPOINT}?client_id={config.vk_app_id}&\
           display=page&\
           redirect_uri={HOST}:{PORT}/&\
           scope={SCOPE}&\
           response_type=token&\
           v={VERSION}")
    return extract_vk_auth_token_from_redirect()


def read_token():
    token = ""
    with open(TOKEN_FILE, "a+") as f:
        token = f.read()
    return token


def test():
    ic(vk_auth_with_local_webserver())


if __name__ == "__main__":
    print("Тест запущен")
    test()
    print("Тест закончен")
