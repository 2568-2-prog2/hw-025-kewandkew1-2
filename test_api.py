import unittest
import json
import threading
import socket
import time
import requests


def start_server():
    from dice import Dice

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('localhost', 8082))
    srv.listen(5)

    while True:
        client_socket, _ = srv.accept()

        request = client_socket.recv(4096).decode('utf-8')

        if request.startswith("POST /roll_dice"):
            try:
                body = request.split("\r\n\r\n", 1)[1].strip()
                payload = json.loads(body)

                probabilities = payload["probabilities"]
                n = payload["number_of_random"]

                dice = Dice(probabilities)  # ✅ FIX
                results = dice.roll_many(n)

                response_data = {
                    "status": "success",
                    "results": results
                }

                response_json = json.dumps(response_data)
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n\r\n"
                    f"{response_json}"
                )

            except Exception as e:
                response = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Type: application/json\r\n\r\n"
                    f'{{"status":"error","message":"{str(e)}"}}'
                )

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()


# start server thread
t = threading.Thread(target=start_server, daemon=True)
t.start()
time.sleep(0.5)


class TestAPI(unittest.TestCase):

    def call_api(self, payload):
        return requests.post("http://localhost:8082/roll_dice", json=payload).json()

    def test_status_success(self):
        result = self.call_api({
            "probabilities": [1/6]*6,
            "number_of_random": 10
        })
        self.assertEqual(result["status"], "success")

    def test_results_length(self):
        result = self.call_api({
            "probabilities": [1/6]*6,
            "number_of_random": 10
        })
        self.assertEqual(len(result["results"]), 10)

    def test_results_values_in_range(self):
        result = self.call_api({
            "probabilities": [1/6]*6,
            "number_of_random": 60
        })
        for v in result["results"]:
            self.assertIn(v, [1, 2, 3, 4, 5, 6])

    def test_biased_dice(self):
        result = self.call_api({
            "probabilities": [1, 0, 0, 0, 0, 0],
            "number_of_random": 20
        })
        self.assertTrue(all(v == 1 for v in result["results"]))

    def test_four_sided_dice(self):
        result = self.call_api({
            "probabilities": [0.25]*4,
            "number_of_random": 20
        })
        for v in result["results"]:
            self.assertIn(v, [1, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()