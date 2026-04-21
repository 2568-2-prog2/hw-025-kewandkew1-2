import socket
import json
from dice import Dice

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8081))
server_socket.listen(1)

print("Server is listening on port 8081...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")

    request = client_socket.recv(4096).decode('utf-8')

    print("REQUEST:")
    print(request)
    print("-" * 50)

    if request.startswith("POST /roll_dice"):

        parts = request.split("\r\n\r\n", 1)
        if len(parts) < 2:
            response = "HTTP/1.1 400 Bad Request\r\n\r\nMissing body"
            client_socket.sendall(response.encode('utf-8'))
            client_socket.close()
            continue

        body = parts[1].strip()

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid JSON"
            client_socket.sendall(response.encode('utf-8'))
            client_socket.close()
            continue

        if "probabilities" not in payload or "number_of_random" not in payload:
            response = "HTTP/1.1 400 Bad Request\r\n\r\nMissing fields"
            client_socket.sendall(response.encode('utf-8'))
            client_socket.close()
            continue

        try:
            probabilities = payload["probabilities"]
            n = payload["number_of_random"]

            dice = Dice(probabilities)
            results = dice.roll_many(n)

            response_data = {
                "status": "success",
                "results": results
            }

            response_json = json.dumps(response_data)

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "\r\n"
                f"{response_json}"
            )

        except Exception as e:
            response = (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: application/json\r\n"
                "\r\n"
                f'{{"status":"error","message":"{str(e)}"}}'
            )

    elif request.startswith("GET /myjson"):
        response_data = {"status": "success", "message": "Hello, KU!"}
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "\r\n"
            f"{json.dumps(response_data)}"
        )

    elif request.startswith("GET"):
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            "<html><body><h1>Hello, World!</h1></body></html>"
        )

    else:
        response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()

    print("Waiting for next request...\n")