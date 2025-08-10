import json
import os


def read_file_content(filename):
    """
    파일 이름을 인자로 받아 파일 내용을 읽어오는 함수

    Args:
        filename (str): 읽을 파일의 이름

    Returns:
        str: 파일 내용 (줄바꿈 문자 제거됨)
        None: 파일 읽기 실패 시
    """
    try:
        if not os.path.exists(filename):
            print(f"파일이 존재하지 않습니다: {filename}")
            return None

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return content
    except Exception as e:
        print(f"{filename} 파일 읽기 오류: {str(e)}")
        return None


def write_file_content(filename, content):
    """
    파일 이름과 내용을 인자로 받아 파일에 쓰는 함수

    Args:
        filename (str): 쓸 파일의 이름
        content (str): 파일에 쓸 내용

    Returns:
        bool: 성공 시 True, 실패 시 False
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{filename} 파일에 내용이 저장되었습니다.")
        return True
    except Exception as e:
        print(f"{filename} 파일 저장 오류: {str(e)}")
        return False


def read_json_file(filename):
    """
    JSON 파일을 읽어오는 함수

    Args:
        filename (str): 읽을 JSON 파일의 이름

    Returns:
        dict: JSON 데이터
        None: 파일 읽기 실패 시
    """
    try:
        if not os.path.exists(filename):
            print(f"파일이 존재하지 않습니다: {filename}")
            return None

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"{filename} JSON 파일 읽기 오류: {str(e)}")
        return None


def write_json_file(filename, data):
    """
    JSON 데이터를 파일에 쓰는 함수

    Args:
        filename (str): 쓸 JSON 파일의 이름
        data (dict): 파일에 쓸 JSON 데이터

    Returns:
        bool: 성공 시 True, 실패 시 False
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{filename} JSON 파일에 데이터가 저장되었습니다.")
        return True
    except Exception as e:
        print(f"{filename} JSON 파일 저장 오류: {str(e)}")
        return False
