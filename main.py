import os
import tweepy
import google.generativeai as genai
from datetime import datetime

# ---------------------------------------------------------
# 1. 環境変数からキーを読み込む
# ---------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# ---------------------------------------------------------
# 2. Geminiでツイート本文を生成する
# ---------------------------------------------------------
def generate_tweet_content():
    genai.configure(api_key=GEMINI_API_KEY)
    # 無料枠で使える軽量モデルを指定
    model = genai.GenerativeModel("gemini-pro")
    
    # プロンプト（指示文）
    # 日によって内容を変えたい場合は、ここに曜日判定などを入れると良いです
    prompt = """
    あなたはキャリアアドバイザーです。
    日本の新卒就活生（26卒・27卒）に向けて、元気が出る、または役に立つアドバイスを1つ考えてください。
    
    【条件】
    - 文字数はハッシュタグ込みで130文字以内（厳守）
    - 最後に #就活 #26卒 などのタグをつける
    - 説教臭くならず、寄り添うトーンで
    - 出力はツイート本文のみにすること
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 3. Xに投稿する
# ---------------------------------------------------------
def post_to_x(content):
    # API v2を使用
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    
    try:
        response = client.create_tweet(text=content)
        print(f"投稿成功！ ID: {response.data['id']}")
        print(f"内容: {content}")
    except Exception as e:
        print(f"投稿エラー: {e}")

# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
if __name__ == "__main__":
    print("---処理開始---")
    try:
        tweet_text = generate_tweet_content()
        post_to_x(tweet_text)
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    print("---処理終了---")
