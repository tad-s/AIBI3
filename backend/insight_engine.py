import pandas as pd
import google.generativeai as genai
from config import Config

class InsightEngine:
    def __init__(self):
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not configured for InsightEngine.")

    def generate_proactive_insights(self, df):
        """
        データフレームを分析し、能動的なインサイトとアクション提案を生成する。
        """
        if not self.model:
            return {
                "insights": ["APIキーが設定されていないため、インサイトを生成できません。"],
                "actions": []
            }

        try:
            # 1. データスキャン (簡易集計)
            # 日別売上
            daily_sales = df.groupby(df['注文日時'].dt.date)['数量'].sum() * df['単価（税込）'].mean() # 概算
            
            # イベント有無別平均
            event_sales = df[df['イベントあり'] == 1]['数量'].sum()
            no_event_sales = df[df['イベントあり'] == 0]['数量'].sum()
            
            # 天気別平均
            weather_sales = df.groupby('天気')['数量'].sum()

            summary_stats = f"""
            データ期間: {df['注文日時'].min()} ~ {df['注文日時'].max()}
            総売上(概算): {daily_sales.sum()}
            イベント日平均販売数: {event_sales}
            非イベント日平均販売数: {no_event_sales}
            天気別販売数: {weather_sales.to_dict()}
            """

            # 2. プロンプト生成
            prompt = f"""
            あなたはプロのデータコンサルタントです。以下の飲食店売上データの集計結果を分析し、
            経営者にとって有益な「気づき（インサイト）」と「具体的なアクション提案」を生成してください。

            データ集計結果:
            {summary_stats}

            要件:
            1. **インサイト**: 売上の特徴、外部要因（天気・イベント）との相関など、重要な発見を3点挙げてください。
            2. **アクション**: インサイトに基づき、明日から実行できる具体的な改善アクションを3点提案してください。
            3. 出力は以下のJSON形式のみとしてください。Markdownのバッククォートは含めないでください。
            {{
                "insights": ["インサイト1", "インサイト2", "インサイト3"],
                "actions": ["アクション1", "アクション2", "アクション3"]
            }}
            """

            # 3. 生成
            response = self.model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "")
            
            import json
            result = json.loads(text)
            return result

        except Exception as e:
            print(f"Insight Generation Error: {e}")
            return {
                "insights": ["分析中にエラーが発生しました。"],
                "actions": []
            }
