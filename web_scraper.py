import time
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from lxml import etree


def scrape_somoim_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        dom = etree.HTML(response.text)

        result = {"url": url, "status_code": response.status_code, "parsed_data": {}}

        try:
            title_element = soup.find("h1")
            if title_element:
                result["parsed_data"]["title"] = title_element.get_text(strip=True)

            schedules = []
            schedule_section = dom.xpath(
                "/html/body/div/div[1]/div/main/div[1]/div/div/div/section[2]/div/div/div[2]"
            )
            for d in schedule_section:
                schedule_info = dict()
                schedule_info["title"] = d.xpath("./h3/text()")[0]
                schedule_info["date"] = d.xpath("./div[1]/p/text()")[0]
                schedule_info["place"] = d.xpath("./div[2]/p/text()")[0]
                schedule_info["cost"] = d.xpath("./div[3]/p/text()")[0]
                schedule_info["people"] = {
                    "current": int(d.xpath("./div[4]/span/span[1]/text()")[0]),
                    "max": int(d.xpath("./div[4]/span/span[3]/text()")[0]),
                }
                schedules.append(schedule_info)

            if schedules:
                result["parsed_data"]["schedules"] = schedules

            member_count = None
            for element in soup.find_all(["div", "span", "p"]):
                text = element.get_text(strip=True)
                if "멤버" in text and any(char.isdigit() for char in text):
                    import re

                    numbers = re.findall(r"\d+", text)
                    if numbers:
                        member_count = numbers[0]
                        break

            if member_count:
                result["parsed_data"]["member_count"] = member_count

        except Exception as e:
            result["parsed_data"]["error"] = f"데이터 파싱 중 오류: {str(e)}"

        return result

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "error": f"요청 오류: {str(e)}",
        }
    except Exception as e:
        return {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "error": f"예상치 못한 오류: {str(e)}",
        }


def save_to_file(data, filename="scraped_data.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"데이터가 {filename}에 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류: {str(e)}")


def authorize():
    try:
        with open("code", "r", encoding="utf-8") as f:
            code = f.read().strip()
    except Exception as e:
        print(f"code 파일 읽기 오류: {str(e)}")
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


def refresh_token():
    try:
        with open("refresh_token", "r", encoding="utf-8") as f:
            refresh_token_value = f.read().strip()
    except Exception as e:
        print(f"refresh_token 파일 읽기 오류: {str(e)}")
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
        try:
            with open("access_token", "w", encoding="utf-8") as f:
                f.write(access_token)
            print(f"access_token이 파일에 저장되었습니다.")
        except Exception as e:
            print(f"access_token 파일 저장 오류: {str(e)}")

    # refresh_token이 존재하면 파일에 저장
    refresh_token_new = response.json().get("refresh_token")
    if refresh_token_new:
        try:
            with open("refresh_token", "w", encoding="utf-8") as f:
                f.write(refresh_token_new)
            print(f"refresh_token이 파일에 저장되었습니다.")
        except Exception as e:
            print(f"refresh_token 파일 저장 오류: {str(e)}")


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


def main():
    """메인 함수"""
    url = "https://www.somoim.co.kr/478b6c1e-2924-11ef-977b-0a4bff98db511"  # 핫스윙

    print("웹페이지 스크래핑을 시작합니다...")
    print(f"URL: {url}")

    result = scrape_somoim_page(url)
    if "error" in result:
        print(f"오류 발생: {result['error']}")
    else:
        print(f"상태 코드: {result['status_code']}")
        save_to_file(result)

    try:
        with open("access_token", "r", encoding="utf-8") as f:
            access_token_value = f.read().strip()
    except Exception as e:
        print(f"access_token 파일 읽기 오류: {str(e)}")
        return

    kakao_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Authorization": f"Bearer {access_token_value}",
    }

    schedules = result.get("parsed_data").get("schedules")
    if schedules:
        for s in schedules:
            if "화요정모" in s.get("title"):
                remaining_spots = s.get("people").get("max") - s.get("people").get(
                    "current"
                )

                if remaining_spots > 0:
                    message_data = {
                        "template_object": json.dumps(
                            {
                                "object_type": "location",
                                "content": {
                                    "title": s.get("title"),
                                    "description": f"장소: {s.get('place')}\n남은 인원: {remaining_spots}",
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
                                "address": f"{get_precise_address(s.get("place"))}",
                                "address_title": s.get("place"),
                            }
                        )
                    }

                    try:
                        kakao_response = requests.post(
                            kakao_url, headers=headers, data=message_data
                        )
                        if kakao_response.status_code == 200:
                            print("KAKAO API 성공")
                            print(kakao_response.text)
                        else:
                            print(f"KAKAO API 실패: {kakao_response.status_code}")
                            print(kakao_response.text)
                    except Exception as e:
                        print(f"KAKAO API Error: {str(e)}")


if __name__ == "__main__":
    while True:
        refresh_token()
        main()
        time.sleep(10)
