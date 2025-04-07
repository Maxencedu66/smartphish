import requests

if __name__ == "__main__":
    # url = "http://127.0.0.1/?rid=ihcu0Wp"
    url = "http://127.0.0.1/?rid=kGL0zhs"
    headers = {
        # "User-Agent": "Mozilla/5.0 (Android 14; Mobile; rv:130.0) Gecko/130.0 Firefox/130.0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }
    input("Press Enter to send the request...")
    response = requests.get(url, headers=headers)
    print(response.json())