import json

def handle_file_upload(uploaded_file, favorites):
    """업로드된 파일 처리"""
    try:
        uploaded_favorites = json.load(uploaded_file)
        if isinstance(uploaded_favorites, list):
            favorites = uploaded_favorites
            return favorites, "업로드된 즐겨찾기를 성공적으로 불러왔습니다."
        else:
            return favorites, "올바른 JSON 형식이 아닙니다."
    except Exception as e:
        return favorites, f"업로드 실패: {e}"
