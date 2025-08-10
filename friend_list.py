import requests
from request_api import refresh_token
from util import read_file_content


def get_friends():
    url = "https://kapi.kakao.com/v1/api/talk/friends"
    refresh_token()
    access_token_value = read_file_content("access_token")
    if not access_token_value:
        return

    headers = {
        "Authorization": f"Bearer {access_token_value}",
    }
    response = requests.get(url, headers=headers)
    print(response.json())


if __name__ == "__main__":
    get_friends()
