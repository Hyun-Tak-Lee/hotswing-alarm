import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree
from request_api import refresh_token, send_kakao_message
from util import read_file_content, write_json_file


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
        write_json_file("scraped_data.json", result)

    access_token_value = read_file_content("access_token")
    if not access_token_value:
        return

    schedules = result.get("parsed_data").get("schedules")
    if schedules:
        for s in schedules:
            if "정기모임" in s.get("title"):
                remaining_spots = s.get("people").get("max") - s.get("people").get(
                    "current"
                )

                if remaining_spots > 0:
                    send_kakao_message(
                        s,
                        access_token_value,
                    )


if __name__ == "__main__":
    while True:
        refresh_token()
        main()
        time.sleep(10)
