import pandas as pd
import jpholiday
import datetime
import random
from external_services import get_location, get_weather_data

class DataManager:
    def __init__(self):
        pass

    def get_enriched_data(self, source):
        """
        CSVデータを読み込み、外部データ（カレンダー、天気、イベント、トレンド）を結合する。
        """
        try:
            # 1. CSV読み込み
            df = pd.read_csv(source)
            
            # 必須カラム確認
            if '注文日時' not in df.columns:
                if 'Date' in df.columns:
                    df.rename(columns={'Date': '注文日時'}, inplace=True)
                else:
                    raise ValueError("CSVファイルに「注文日時」カラムが含まれていません。")

            df['注文日時'] = pd.to_datetime(df['注文日時'])
            
            # 店舗名取得
            store_name = "東京"
            if '店舗名' in df.columns and not df['店舗名'].isnull().all():
                store_name = df['店舗名'].iloc[0]

            # 2. 座標取得 (External Service)
            lat, lon = None, None
            try:
                coords = get_location(store_name)
                if coords:
                    lat, lon = coords
            except Exception as e:
                print(f"Location Error: {e}")

            # 日付ごとのキャッシュ
            unique_dates = df['注文日時'].dt.date.unique()
            date_cache = {}

            for d in unique_dates:
                # 3. カレンダー情報
                is_holiday = jpholiday.is_holiday(d) or d.weekday() >= 5 # 土日祝
                is_payday = d.day in [10, 25] or (d.day == (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1).day - 1) # 簡易的な末日判定
                
                # 4. 天気情報 (External Service)
                dt = datetime.datetime.combine(d, datetime.time(12, 0))
                weather_info = {"weather": "晴れ", "temp": 25} # Default
                if lat and lon:
                    weather_info = get_weather_data(lat, lon, dt)
                
                # 5. イベント・トレンド情報 (Mock/Logic)
                # 9/14, 9/21はイベントありとする（既存ロジック踏襲）
                is_event_day = (d.day == 14 or d.day == 21)
                
                # トレンド指数 (Mock)
                trend_score = random.randint(40, 80)
                if is_event_day:
                    trend_score += 15
                if is_holiday:
                    trend_score += 10

                date_cache[d] = {
                    "is_holiday": 1 if is_holiday else 0,
                    "is_payday": 1 if is_payday else 0,
                    "weather": weather_info['weather'],
                    "temp": weather_info['temp'],
                    "is_event": 1 if is_event_day else 0,
                    "trend_score": min(100, trend_score)
                }

            # データ結合
            def augment_row(row):
                d = row['注文日時'].date()
                info = date_cache.get(d, {})
                return pd.Series([
                    info.get('weather', '晴れ'),
                    info.get('temp', 25),
                    info.get('is_event', 0),
                    info.get('trend_score', 50),
                    info.get('is_holiday', 0),
                    info.get('is_payday', 0)
                ])

            df[['天気', '気温', 'イベントあり', 'トレンドスコア', '休日フラグ', '給料日フラグ']] = df.apply(augment_row, axis=1)
            
            return df

        except Exception as e:
            raise RuntimeError(f"Data Enrichment Error: {str(e)}")
