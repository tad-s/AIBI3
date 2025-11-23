import requests
from datetime import datetime
from config import Config

def get_location(store_name):
    """
    Google Maps Geocoding APIを使用して店舗名の緯度経度を取得する。
    APIキーが未設定またはエラーの場合はNoneを返す（呼び出し元でデフォルト座標を使用するなど対応）。
    """
    if not Config.is_maps_api_configured():
        print("Google Maps API Key not configured.")
        return None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": store_name,
        "key": Config.GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding API Error: {data['status']}")
            return None
    except Exception as e:
        print(f"Geocoding Request Failed: {e}")
        return None

def get_weather_data(lat, lon, date_obj):
    """
    OpenWeatherMap APIを使用して指定日の天気を取得する。
    APIキーが未設定、エラー、またはデータがない場合は
    安全策としてダミーデータ（晴れ/25度）を返す。
    """
    # ダミーデータ（フォールバック用）
    DUMMY_DATA = {"weather": "晴れ", "temp": 25}

    if not Config.is_weather_api_configured():
        print("OpenWeatherMap API Key not configured. Using dummy data.")
        return DUMMY_DATA

    # One Call API 3.0 expects timestamp
    try:
        timestamp = int(date_obj.timestamp())
        url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        params = {
            "lat": lat,
            "lon": lon,
            "dt": timestamp,
            "appid": Config.OPENWEATHER_API_KEY,
            "units": "metric", # Celsius
            "lang": "ja"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            weather_data = data['data'][0]
            # APIの天気を日本語に簡易変換（必要であれば辞書マッピング）
            # ここではAPIがlang=jaで返してくれるdescriptionを使うか、mainを使うか
            # main: Rain, Clouds, Clear -> 簡易変換
            main_weather = weather_data['weather'][0]['main']
            
            weather_map = {
                "Clear": "晴れ",
                "Clouds": "曇り",
                "Rain": "雨",
                "Snow": "雪",
                "Mist": "曇り",
                "Drizzle": "雨",
                "Thunderstorm": "雨"
            }
            weather_ja = weather_map.get(main_weather, "晴れ") # デフォルトは晴れ

            return {
                "weather": weather_ja,
                "temp": weather_data['temp']
            }
        
        print("Weather data not found in API response. Using dummy data.")
        return DUMMY_DATA

    except Exception as e:
        print(f"Weather API Request Failed: {e}. Using dummy data.")
        return DUMMY_DATA
