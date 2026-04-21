import requests

def call_api(base_url, payload):
    try:
        response = requests.post(base_url, json=payload)
        response.raise_for_status()

        print("RAW RESPONSE:")
        print(response.text)

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None
    except ValueError:
        print("Response is not valid JSON")
        print(response.text)
        return None


if __name__ == "__main__":
    url = "http://127.0.0.1:8081/roll_dice"

    data = {
        "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
        "number_of_random": 10
    }

    print("Calling API...")
    result = call_api(url, data)

    if result is not None:
        print("\nPARSED RESULT:")
        for k, v in result.items():
            print(k, v)