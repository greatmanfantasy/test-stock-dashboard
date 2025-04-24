import json
import os

FAVORITES_FILE = "favorites.json"

def load_favorites():
    """즐겨찾기 파일에서 종목 목록 로드"""
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    """즐겨찾기 목록을 파일에 저장"""
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def get_stock_name(ticker):
    """종목 티커를 사용해 종목명 조회"""
    try:
        return yf.Ticker(ticker).info.get("shortName", "Unknown")
    except:
        return "Unknown"
