import os
import tweepy
import google.generativeai as genai
import random

# ---------------------------------------------------------
# 1. 環境変数
# ---------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# ---------------------------------------------------------
# 2. ガチャ用データ（頂いた業界分類表を完全網羅）
# ---------------------------------------------------------
# 頂いた画像の分類に基づき、具体的なセクターをリスト化しました
INDUSTRIES = [
    # メーカー
    "食品・農林・水産", "建設・住宅・インテリア", "繊維・化学・薬品・化粧品",
    "鉄鋼・金属・鉱業", "機械・プラント", "電子・電気機器",
    "自動車・輸送用機器", "精密・医療機器", "印刷・事務機器関連",
    "スポーツ・玩具",
    
    # 商社
    "総合商社", "専門商社",
    
    # 小売
    "百貨店・スーパー", "コンビニ", "専門店",
    
    # 金融
    "銀行・証券", "クレジット・信販・リース", "生保・損保",
    
    # サービス・インフラ
    "不動産", "鉄道・航空・運輸・物流", "電力・ガス・エネルギー",
    "フードサービス", "ホテル・旅行", "医療・福祉",
    "アミューズメント・レジャー", "コンサルティング・調査",
    "人材サービス", "教育",
    
    # ソフトウェア・通信
    "ソフトウェア", "インターネット", "通信",
    
    # 広告・出版・マスコミ
    "放送", "新聞", "出版", "広告",
    
    # 官公庁・公社
    "官公庁", "公社・団体"
]

TOPICS = [
    "事業内容（ビジネスモデルの『収益源』を鋭く解説）",
    "最新の業界動向（日経新聞レベルのトレンド・将来性）",
    "仕事内容・職種（現場のリアルと求められる能力）",
    "魅力・やりがい（市場価値やキャリアの広がり）"
]

# ---------------------------------------------------------
# 3. Geminiで「知的で鋭いツイート」を生成
# ---------------------------------------------------------
def generate_tweet_content():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # ランダム決定
    target_industry = random.choice(INDUSTRIES)
    target_topic = random.choice(TOPICS)

    # プロンプト（指示書）
    prompt = f"""
    あなたは、難関企業への内定を支援する「戦略的キャリアコーチ（ジリツ運営）」です。
    今日は就活生のために、以下の【対象業界】について、【解説テーマ】に沿った有益なツイートを1つ作成してください。

    【対象業界】
    {target_industry}

    【解説テーマ】
    {target_topic}

    【ツイート作成のルール（トーン＆マナー）】
    1. 攻撃的な言葉は使わない。知的で論理的な「です・ます」調、または落ち着いた「言い切り」にする。
    2. Wikipediaのような表面的な説明は避け、プロだから知っている「ビジネスの本質」や「業界の裏側の面白さ」を語る。
    3. 読んだ学生が「なるほど、そういう視点があったか」と視座が高まる内容にする。
    4. 「業界動向」の場合は、最新トレンド（DX、グローバル、サステナビリティ、少子化、円安など）を絡める。
    5. 文字数はハッシュタグ込みで135文字以内。
    6. 最後に必ず #就活 #26卒 #ジリツ #{target_industry.replace("・", "_")} をつける。

    【良い例：不動産の場合】
    「デベロッパーの仕事は、単に建物を造るだけではありません。地権者、行政、建設会社…数えきれない利害関係者をまとめ上げる『調整力』こそが本質です。数百億円のプロジェクトを動かす責任感は、他では味わえない醍醐味と言えるでしょう。 #就活 #26卒 #ジリツ #不動産」
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 4. Xに投稿する
# ---------------------------------------------------------
def post_to_x(content):
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
