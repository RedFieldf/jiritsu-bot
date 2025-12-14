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
# 2. ガチャ用データ（業界 × 切り口）
# ---------------------------------------------------------
INDUSTRIES = [
    # メーカー
    "食品・農林・水産", "建設・住宅・インテリア", "繊維・化学・薬品・化粧品",
    "鉄鋼・金属・鉱業", "機械・プラント", "電子・電気機器",
    "自動車・輸送用機器", "精密・医療機器", "印刷・事務機器関連", "スポーツ・玩具",
    # 商社
    "総合商社", "専門商社",
    # 小売
    "百貨店・スーパー", "コンビニ", "専門店",
    # 金融
    "銀行・証券", "クレジット・信販・リース", "生保・損保",
    # サービス・インフラ
    "不動産", "鉄道・航空・運輸・物流", "電力・ガス・エネルギー",
    "フードサービス", "ホテル・旅行", "医療・福祉",
    "アミューズメント・レジャー", "コンサルティング・調査", "人材サービス", "教育",
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
# 3. Geminiでツイート生成
# ---------------------------------------------------------
def generate_tweet_content():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    target_industry = random.choice(INDUSTRIES)
    target_topic = random.choice(TOPICS)

    prompt = f"""
    あなたは、難関企業への内定を支援する「戦略的キャリアコーチ（ジリツ運営）」です。
    今日は就活生のために、以下の【対象業界】について、【解説テーマ】に沿った有益なツイートを1つ作成してください。

    【対象業界】
    {target_industry}

    【解説テーマ】
    {target_topic}

    【ツイート作成のルール】
    1. 攻撃的な言葉は使わず、知的で論理的な「です・ます」調、または落ち着いた「言い切り」にする。
    2. プロだから知っている「ビジネスの本質」や「業界の裏側の面白さ」を語る。
    3. 「業界動向」の場合は、最新トレンド（DX、グローバル、サステナビリティ等）を絡める。
    4. 文字数はハッシュタグ込みで135文字以内。
    5. 最後に必ず #就活 #26卒 #27卒 #28卒 をつける。
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 4. Xに投稿＆リプライ（スレッド作成）
# ---------------------------------------------------------
def post_to_x(content):
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )

    # 固定の宣伝文言
    reply_text = """
    我々ジリツは納得内定獲得に向けたご支援をしております。
    👇無料相談はこちらから👇
    https://www.jicoo.com/t/dX0f4ah7ZNbn/e/jiritsu?utm_source=twitter
    """
    
    try:
        # 1. まずメインのツイートを投稿
        response = client.create_tweet(text=content)
        tweet_id = response.data['id']
        print(f"メイン投稿成功！ ID: {tweet_id}")
        print(f"内容: {content}")

        # 2. そのツイートにぶら下げる形で宣伝を投稿
        response_reply = client.create_tweet(
            text=reply_text.strip(),
            in_reply_to_tweet_id=tweet_id
        )
        print(f"宣伝リプライ成功！ ID: {response_reply.data['id']}")

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

