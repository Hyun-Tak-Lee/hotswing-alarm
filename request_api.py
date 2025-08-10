import json
from typing import Union
import requests
from util import read_file_content, write_file_content


def refresh_token():
    refresh_token_value = read_file_content("refresh_token")
    if not refresh_token_value:
        return

    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    data = {
        "grant_type": "refresh_token",
        "client_id": "299313409980678e0dcfe9e06e1f6bf0",
        "refresh_token": refresh_token_value,
    }

    response = requests.post(token_url, headers=headers, data=data)

    # access_token이 존재하면 파일에 저장
    access_token = response.json().get("access_token")
    print(access_token)
    if access_token:
        write_file_content("access_token", access_token)

    # refresh_token이 존재하면 파일에 저장
    refresh_token_new = response.json().get("refresh_token")
    if refresh_token_new:
        write_file_content("refresh_token", refresh_token_new)


def authorize():
    code = read_file_content("code")
    if not code:
        return
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    data = {
        "grant_type": "authorization_code",
        "client_id": "299313409980678e0dcfe9e06e1f6bf0",
        "redirect_uri": "https://example.com/oauth",
        "code": code,
    }

    response = requests.post(token_url, headers=headers, data=data)
    print(f"Status Code: {response.status_code}")

    # JSON 응답인 경우 파싱하여 출력
    try:
        json_response = response.json()
        print(
            f"JSON Response: {json.dumps(json_response, indent=2, ensure_ascii=False)}"
        )
    except json.JSONDecodeError:
        print("Response is not JSON format")

    return response


def get_precise_address(place_name):
    """
    카카오 로컬 API를 사용해 장소 이름으로 정확한 주소를 검색합니다.
    가장 첫 번째 검색 결과를 사용합니다.
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {"299313409980678e0dcfe9e06e1f6bf0"}"}
    params = {"query": place_name}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 200번대가 아닐 경우 예외 발생
        search_results = response.json().get("documents")

        if search_results:
            # 검색 결과가 있으면 첫 번째 장소의 도로명 주소를 반환
            # 도로명 주소가 없는 경우를 대비해 일반 주소(address_name)도 확인
            first_result = search_results[0]
            precise_address = first_result.get("road_address_name") or first_result.get(
                "address_name"
            )
            print(f"주소 변환 성공: '{place_name}' -> '{precise_address}'")
            return precise_address
        else:
            print(f"주소 변환 실패: '{place_name}'에 대한 검색 결과가 없습니다.")
            return None  # 검색 결과가 없으면 None 반환

    except Exception as e:
        print(f"카카오 로컬 API 호출 오류: {e}")
        return None


def send_kakao_message(schedules, access_token_value):
    # uuids 파일에서 읽어와 각 행을 리스트로 변환
    uuids_content = read_file_content("uuids")
    uuids = None
    if uuids_content:
        uuids = [uuid.strip() for uuid in uuids_content.split("\n") if uuid.strip()]

    # uuids가 존재하면 친구에게 메시지 전송, 없으면 나에게 메모 전송
    if uuids:
        kakao_url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
    else:
        kakao_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Authorization": f"Bearer {access_token_value}",
    }
    remaining_spots = schedules.get("people").get("max") - schedules.get("people").get(
        "current"
    )
    message_data = {
        "template_object": json.dumps(
            {
                "object_type": "location",
                "content": {
                    "title": schedules.get("title"),
                    "description": f"장소: {schedules.get('place')}\n남은 인원: {remaining_spots}",
                    "image_url": "https://d228e474i2d5yf.cloudfront.net/478b6c1e-2924-11ef-977b-0a4bff98db511s.png",
                    "image_width": 800,
                    "image_height": 400,
                    "link": {
                        "web_url": "https://developers.kakao.com",
                        "mobile_web_url": "https://developers.kakao.com/mobile",
                        "android_execution_params": "platform=android",
                        "ios_execution_params": "platform=ios",
                    },
                },
                "address": f"{get_precise_address(schedules.get("place"))}",
                "address_title": schedules.get("place"),
            }
        )
    }
    if uuids:
        message_data["receiver_uuids"] = json.dumps(uuids)

    try:
        kakao_response = requests.post(kakao_url, headers=headers, data=message_data)
        if kakao_response.status_code == 200:
            print("KAKAO API 성공")
            print(kakao_response.text)
        else:
            print(f"KAKAO API 실패: {kakao_response.status_code}")
            print(kakao_response.text)
    except Exception as e:
        print(f"KAKAO API Error: {str(e)}")


if __name__ == "__main__":
    authorize()
