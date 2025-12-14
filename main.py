import os
import tweepy
import google.generativeai as genai
import random
import requests
import io

# ---------------------------------------------------------
# 1. 環境変数
# ---------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# ---------------------------------------------------------
# 2. ガチャ用データ（業界 × 海外風フック）
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

# 海外トレンドを取り入れた「切り口」
TOPICS = [
    "Controversial Hook（常識を否定する逆張り論）",
    "Insider Truth（業界の裏側・ぶっちゃけ話）",
    "Underdog Strategy（学歴フィルターの突破法）",
    "Future Vision（10年後の市場価値からの逆算）"
]

# ---------------------------------------------------------
# 3. Geminiの設定
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------------------------------------
# 4. ツイート本文を作る関数（ターゲット特化）
# ---------------------------------------------------------
def generate_tweet_text(industry, topic):
    prompt = f"""
    あなたは「大逆転内定専門支援サービス『ジリツ』」の辛口かつ愛のあるキャリアコーチです。
    特に【日東駒専・産近甲龍・地方国公立】から、難関企業（商社・コンサル・大手メーカー等）への下克上を狙う学生に向けてツイートを作成してください。

    【対象業界】
    {industry}

    【今回の切り口】
    {topic}

    【ツイート作成のルール（海外のCareer Influencerスタイル）】
    1. **ターゲットへの呼びかけ**: 「日東駒専・産近甲龍から{industry}を狙うなら〜」「学歴フィルターで諦めるな」といった文脈を入れる。
    2. **Strong Hook（掴み）**: 冒頭で「就活の常識」を否定するか、ドキッとする数字や事実を提示する。
    3. **Authenticity（本音）**: 綺麗事は禁止。「正直、学歴フィルターはある。だが突破口はある」という現実的なハック術を語る。
    4. **Actionable（具体的）**: 精神論だけでなく「今何をすべきか」を示唆する。
    5. **ブランディング**: 文中に自然に「日東駒専・産近甲龍ならジリツ」「逆転内定のジリツ」というニュアンスを含める（毎回同じ定型文にならないように工夫）。
    6. 文字数はタグ込み135文字以内。
    7. タグは #就活 #26卒 #27卒 #逆転内定 #{industry.replace("・", "_")} を使用。

    【良い例】
    「『商社は高学歴の遊び場』だと思ってる？半分正解で半分間違いだ。日東駒専から入り込む隙間は『泥臭い現場力』のアピールにある。スマートさは求めてない。誰よりも汗をかけるか？その覚悟がある奴だけがジリツに来い。 #就活 #26卒 #逆転内定 #総合商社」
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 5. 画像生成用の「指示」を作る関数（インスタ/図解風）
# ---------------------------------------------------------
def generate_image_prompt(industry, tweet_text):
    prompt = f"""
    Based on the following tweet, create an English prompt for generating an image that looks like a **"Viral Instagram Career Post"** or **"Modern Infographic"**.

    Tweet Content:
    {tweet_text}

    Target Industry:
    {industry}

    Rules for the Image Prompt:
    1.  **Style**: Minimalist, Bold Typography, High Contrast, Vector Art style, or "Aesthetic Notion-style illustration".
    2.  **Visual Metaphor**: Use visual metaphors for "Underdog success", "Breaking barriers", "Strategy", or "Future growth".
    3.  **No Text**: Do not include specific text in the image (AI text generation is poor), but make it look like a chart, graph, or symbolic illustration.
    4.  **Vibe**: Motivational, Professional, yet Trendy (Gen Z style).
    5.  **Output**: ONLY the English prompt string. Start with "A trendy flat illustration of..." or "A minimalist 3D render of..."
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 6. 画像を生成してダウンロードする関数
# ---------------------------------------------------------
def generate_and_download_image(image_prompt):
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(0, 10000)
    # インスタ風の正方形、かつ高品質なモデルを指定
    url = f"{base_url}{image_prompt}?width=1080&height=1080&seed={seed}&nologo=true&model=flux"
    
    print(f"画像生成中...: {url}")
    response = requests.get(url)
    
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        print("画像生成に失敗しました")
        return None

# ---------------------------------------------------------
# 7. Xに投稿する（画像添付あり）
# ---------------------------------------------------------
def post_with_image(text, image_data):
    # API v1.1 (画像アップロード)
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    # API v2 (ツイート投稿)
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )

    # 固定リプライ（コンバージョンへの誘導）
    reply_text = """
    日東駒専・産近甲龍からの大逆転内定なら「ジリツ」。
    
    学歴フィルターを突破する戦略、教えます。
    無料相談はこちらから👇
    https://www.jicoo.com/t/dX0f4ah7ZNbn/e/jiritsu?utm_source=bot
    """

    try:
        media_id = None
        if image_data:
            media = api.media_upload(filename="image.jpg", file=image_data)
            media_id = media.media_id
            print("画像アップロード成功")

        if media_id:
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=text)
            
        tweet_id = response.data['id']
        print(f"メイン投稿成功！ ID: {tweet_id}")

        client.create_tweet(text=reply_text.strip(), in_reply_to_tweet_id=tweet_id)
        print("宣伝リプライ成功！")

    except Exception as e:
        print(f"投稿エラー: {e}")

# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
if __name__ == "__main__":
    print("---処理開始---")
    try:
        # ネタ決め
        industry = random.choice(INDUSTRIES)
        topic = random.choice(TOPICS)
        print(f"今日のテーマ: {industry} × {topic}")

        # ツイート文章生成
        tweet_text = generate_tweet_text(industry, topic)
        print(f"生成されたツイート: {tweet_text}")

        # 画像プロンプト生成
        img_prompt = generate_image_prompt(industry, tweet_text)
        print(f"画像指示(英語): {img_prompt}")

        # 画像生成
        image_data = generate_and_download_image(img_prompt)

        # 投稿
        post_with_image(tweet_text, image_data)

    except Exception as e:
        print(f"予期せぬエラー: {e}")
    print("---処理終了---")
