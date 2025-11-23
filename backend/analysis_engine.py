import pandas as pd
import random
import datetime
import os

def load_and_process_data(source):
    """
    CSVファイルを読み込み、データ処理と拡張を行う関数。
    
    Args:
        source (str or file-like): CSVファイルのパス または ファイルオブジェクト
        
    Returns:
        pd.DataFrame: 処理済みのDataFrame
    """
    if isinstance(source, str):
        if not os.path.exists(source):
            raise FileNotFoundError(f"指定されたファイルが見つかりません: {source}")

    try:
        # CSVを読み込む
        df = pd.read_csv(source)
        
        # 必須カラムの確認
        if '注文日時' not in df.columns:
            # テストデータなどが英語ヘッダーの場合のフォールバック対応（必要に応じて）
            if 'Date' in df.columns:
                df.rename(columns={'Date': '注文日時'}, inplace=True)
            else:
                raise ValueError("CSVファイルに「注文日時」カラムが含まれていません。")

        # 「注文日時」をdatetime型に変換
        df['注文日時'] = pd.to_datetime(df['注文日時'])
        
        # シミュレーション用データの生成（フォールバック用）
        weather_conditions = ['晴れ', '雨', '曇り']

        # 店舗情報の取得（最初の行から取得）
        store_name = "東京" # デフォルト
        if '店舗名' in df.columns and not df['店舗名'].isnull().all():
            store_name = df['店舗名'].iloc[0]
        
        # 座標の取得
        from external_services import get_location, get_weather_data
        lat, lon = None, None
        try:
            coords = get_location(store_name)
            if coords:
                lat, lon = coords
                print(f"Coordinates found for {store_name}: {lat}, {lon}")
            else:
                print(f"Coordinates not found for {store_name}, using fallback.")
        except Exception as e:
            print(f"Error getting coordinates: {e}")

        # 日付ごとの天気データを取得（APIコール数削減のため）
        unique_dates = df['注文日時'].dt.date.unique()
        weather_cache = {}

        for d in unique_dates:
            # datetimeオブジェクトに変換（時間は正午とする）
            dt = datetime.datetime.combine(d, datetime.time(12, 0))
            
            # get_weather_dataはエラー時にダミーデータを返すので、そのまま使用
            if lat is not None and lon is not None:
                weather_info = get_weather_data(lat, lon, dt)
            else:
                # 座標がない場合もダミーデータを使用（get_weather_dataのダミーと同じ形式で）
                weather_info = {"weather": "晴れ", "temp": 25}
            
            weather_cache[d] = weather_info

        # 行ごとにデータを付与
        def augment_row(row):
            date = row['注文日時']
            d = date.date()
            
            # 天気・気温 (キャッシュから取得)
            w_info = weather_cache.get(d, {"weather": "晴れ", "temp": 25})
            weather = w_info['weather']
            temp = w_info['temp']

            # イベントフラグの付与 (9/14, 9/21)
            is_event_day = (date.day == 14 or date.day == 21)
            event_flag = 1 if is_event_day else 0

            # トレンドスコアの付与 (0-100)
            trend_score = random.randint(30, 90)
            if is_event_day:
                trend_score += 10 # イベント日はトレンドも高いとする

            return pd.Series([weather, temp, event_flag, trend_score])

        # 新しいカラムを追加
        df[['天気', '気温', 'イベントあり', 'トレンドスコア']] = df.apply(augment_row, axis=1)

        return df

    except Exception as e:
        raise RuntimeError(f"データ処理中にエラーが発生しました: {str(e)}")

def analyze_sales(df):
    """
    売上データを分析し、集計結果を返す関数。
    
    Args:
        df (pd.DataFrame): load_and_process_dataで処理されたDataFrame
        
    Returns:
        dict: 分析結果を含む辞書
    """
    try:
        # 売上カラムの特定と計算
        if '単価（税込）' in df.columns and '数量' in df.columns:
            df['売上'] = df['単価（税込）'] * df['数量']
            sales_col = '売上'
        elif 'Price' in df.columns:
            sales_col = 'Price'
        elif '売上' in df.columns:
            sales_col = '売上'
        else:
             raise ValueError("売上データのカラム（単価（税込）+数量, Price, 売上）が見つかりません。")

        # 日付カラムの作成（集計用）
        df['日付'] = df['注文日時'].dt.date

        # 1. 日別の集計
        # 売上合計
        daily_sales = df.groupby('日付')[sales_col].sum()
        # 客数（注文番号のユニーク数、なければ行数）
        if '注文番号' in df.columns:
            daily_customers = df.groupby('日付')['注文番号'].nunique()
        else:
            daily_customers = df.groupby('日付').size()
        
        # DataFrameにまとめて計算
        daily_stats = pd.DataFrame({
            'total_sales': daily_sales,
            'customer_count': daily_customers,
            'avg_trend': df.groupby('日付')['トレンドスコア'].mean(),
            'has_event': df.groupby('日付')['イベントあり'].max()
        })
        
        # 客単価 = 売上合計 / 客数
        daily_stats['avg_spend'] = daily_stats['total_sales'] / daily_stats['customer_count']
        
        # dict形式に変換（indexは日付文字列にする）
        daily_analysis = daily_stats.reset_index()
        daily_analysis['日付'] = daily_analysis['日付'].astype(str)
        daily_result = daily_analysis.to_dict(orient='records')

        # 2. 天気ごとの平均売上
        # 天気データがある行のみ対象
        weather_df = df.dropna(subset=['天気'])
        
        if not weather_df.empty:
            # 天気ごとの日別売上平均を算出したい場合
            # まず日別・天気別に集計してから平均をとるのが正確だが、
            # ここでは簡易的に「天気ごとの全売上平均」ではなく「その天気の日の1日あたり平均売上」を出すべきか、
            # 単に「その天気の時のレコードあたりの平均単価」か要件による。
            # 要件: "天気ごとの平均売上" -> 通常は "Average Sales per Day with that Weather"
            
            # 日付と天気でグルーピングして日別売上を出す
            daily_weather_sales = weather_df.groupby(['日付', '天気'])[sales_col].sum().reset_index()
            # 天気ごとに平均を算出
            weather_avg_sales = daily_weather_sales.groupby('天気')[sales_col].mean().reset_index()
            weather_avg_sales.rename(columns={sales_col: 'avg_sales'}, inplace=True)
            weather_result = weather_avg_sales.to_dict(orient='records')
        else:
            weather_result = []

        return {
            "daily_analysis": daily_result,
            "weather_analysis": weather_result
        }

    except Exception as e:
        raise RuntimeError(f"データ分析中にエラーが発生しました: {str(e)}")

import google.generativeai as genai
import io
from config import Config

class LLMAnalyst:
    def __init__(self):
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not configured for LLMAnalyst.")

    def analyze_query(self, df, user_query):
        """
        ユーザーの質問に基づいてDataFrameを分析するコードを生成・実行する。
        """
        if not self.model:
            return {
                "answer": "APIキーが設定されていないため、AI分析を利用できません。",
                "data": [],
                "chartType": "bar"
            }

        # カラム情報の取得
        buffer = io.StringIO()
        df.info(buf=buffer)
        columns_info = buffer.getvalue()

        # プロンプトの作成
        prompt = f"""
        あなたはデータアナリストです。以下のDataFrameのカラム情報 `{columns_info}` を元に、
        ユーザーの質問 `{user_query}` に答えるためのPython Pandasコードのみを生成してください。
        
        要件:
        1. コードは `df` 変数を直接使用してください。
        2. 分析結果（集計データ）は `result_df` という変数に格納してください。
           - `result_df` は、グラフ化しやすいように reset_index() などを適宜行ってください。
        3. グラフの種類を `chart_type` 変数（文字列: 'bar', 'line', 'pie', 'scatter'）に格納してください。
        4. グラフのX軸に使用するカラム名を `x_key` 変数（文字列）に格納してください。
        5. グラフのY軸に使用するカラム名を `y_key` 変数（文字列）に格納してください。
        6. 分析結果の要約コメントを `summary_text` 変数（文字列）に格納してください。
        7. コードのみを出力し、Markdownのバッククォートは含めないでください。
        """

        try:
            response = self.model.generate_content(prompt)
            generated_code = response.text.strip()
            
            # Markdown除去
            generated_code = generated_code.replace("```python", "").replace("```", "")
            
            print(f"Generated Code:\n{generated_code}")

            # コード実行
            local_vars = {'df': df, 'pd': pd}
            exec(generated_code, {}, local_vars)
            
            result_df = local_vars.get('result_df')
            chart_type = local_vars.get('chart_type', 'bar')
            x_key = local_vars.get('x_key', '')
            y_key = local_vars.get('y_key', '')
            summary_text = local_vars.get('summary_text', '分析が完了しました。')

            # 結果の整形
            if result_df is not None:
                # datetime型などをJSONシリアライズ可能にする
                if '日付' in result_df.columns:
                    result_df['日付'] = result_df['日付'].astype(str)
                
                # 全てのTimestamp型を文字列に変換
                for col in result_df.select_dtypes(include=['datetime', 'datetimetz']).columns:
                    result_df[col] = result_df[col].astype(str)

                data_list = result_df.to_dict(orient='records')
            else:
                data_list = []

            return {
                "answer": summary_text,
                "data": data_list,
                "chartType": chart_type,
                "xKey": x_key,
                "yKey": y_key
            }

        except Exception as e:
            print(f"LLM Analysis Error: {e}")
            return {
                "answer": f"分析中にエラーが発生しました: {str(e)}",
                "data": [],
                "chartType": "bar"
            }
