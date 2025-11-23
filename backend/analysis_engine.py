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
        
        # シミュレーション用データの生成
        weather_conditions = ['晴れ', '雨', '曇り']
        
        # 行ごとにループしてデータを付与（ベクトル処理も可能だが、条件分岐が複雑なためapplyまたはループを使用）
        def augment_row(row):
            date = row['注文日時']
            
            # 2025年9月の日付に対する処理
            if date.year == 2025 and date.month == 9:
                # 天気と気温のランダム生成
                weather = random.choice(weather_conditions)
                temp = random.randint(20, 35)
                
                # イベントフラグの付与 (9/14, 9/21)
                is_event_day = (date.day == 14 or date.day == 21)
                event_flag = 1 if is_event_day else 0

                # トレンドスコアの付与 (0-100)
                trend_score = random.randint(30, 90)
                if is_event_day:
                    trend_score += 10 # イベント日はトレンドも高いとする
                
                return pd.Series([weather, temp, event_flag, trend_score])
            else:
                # 対象外の日付はデフォルト値またはNone
                return pd.Series([None, None, 0, 0])

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
