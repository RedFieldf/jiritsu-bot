import os
import tweepy
import google.generativeai as genai
import random
import requests
import io
import time

# ---------------------------------------------------------
# 1. 環境変数
# ---------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# ---------------------------------------------------------
# 2. 投稿カテゴリ設定（時間帯で制御するための準備）
# ---------------------------------------------------------
CATEGORIES = {
    "mindset_reset": {
        "theme": "メンタル・焦りの解消",
        "detail": "周りが内定式を終えて焦る学生に対し、10年の経験から「今からでも間に合う理由」と「焦ってブラックに行く危険性」を説く。"
    },
    "hidden_gems": {
        "theme": "隠れ優良企業の推奨",
        "detail": "知名度は低いが、利益率が高く、離職率が低いBtoBメーカーや専門商社の魅力を紹介。「知名度＝安定ではない」ことを教える。"
    },
    "interview_hacks": {
        "theme": "面接・選考突破の裏技",
        "detail": "「ガクチカがない」「早期選考で落ちた」人向けに、人事が見ている意外なポイントや、即効性のある逆質問などのテクニック。"
    },
    "career_vision": {
        "theme": "5年後のキャリア論",
        "detail": "「どこに入社するか」より「入社後どう育つか」が重要だと説く。ファーストキャリアで身につけるべきスキルや視点について。"
    },
    "real_story": {
        "theme": "逆転内定の事例紹介",
        "detail": "FランやNNT（無い内定）から、戦略を変えて優良企業に受かった過去の学生の成功事例（匿名）を紹介し、勇気づける。"
    }
}

# ---------------------------------------------------------
# 3. Gemini設定
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------------------------------------
# 4. ツイート生成関数
# ---------------------------------------------------------
def generate_tweet_text(category_key, category_info):
    prompt = f"""
    あなたは就活支援歴10年以上、数千人をサポートしてきたプロのエージェント「ジリツ」です。
    現在は12月中旬〜1月。ターゲットは「まだ納得内定がない」「大手全落ちで焦っている」26卒・27卒の学生です。
    
    【今回の投稿テーマ】
    {category_info['theme']}
    ({category_info['detail']})

    【ツイート作成ルール】
    1. ターゲット: 自信を失いかけている学生。
    2. トーン: プロの分析で安心させる。語り口は「〜だ」「〜です」など、自信に満ちた落ち着いた口調。
    3. 構成: 学生の不安へのフック → プロの視点での解決策 → 「ジリツ」への信頼感。
    4. 禁止: 嘘、架空の数字。
    5. 表記: 過度な「」などの記号は削除し、自然な文章にする。
    6. 文字数: タグ込みで135文字前後。
    7. 必須タグ: #就活 #26卒 #無い内定 #就活エージェント

    出力例:
    知名度だけで企業を選び、3年で辞める先輩を山ほど見てきました。逆に知名度はなくても利益率が高いBtoB企業で、20代でエースになり年収1000万を超えた人もいます。見るべきはCMではなく決算書。その読み解き方、教えます。 #就活 #26卒 #隠れ優良企業
    """
    try:
        response = model.generate_content(prompt)
        # カギカッコなどを掃除して自然にする
        clean_text = response.text.strip().replace("「", "").replace("」", "").replace("『", "").replace("』", "")
        return clean_text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

# ---------------------------------------------------------
# 5. 画像プロンプト生成関数
# ---------------------------------------------------------
def generate_image_prompt(tweet_text):
    prompt = f"""
    Create an English prompt for an AI image generator based on this tweet:
    "{tweet_text}"
    
    Style: Minimalist, Professional, Abstract, Corporate Memphis style or Notion style illustration.
    Subject: Career growth, hidden success, light in darkness, stepping stones.
    Constraint: NO TEXT in the image.
    Output: ONLY the prompt string.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "minimalist career success illustration, abstract, no text"

# ---------------------------------------------------------
# 6. 画像生成・ダウンロード
# ---------------------------------------------------------
def generate_and_download_image(image_prompt):
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(0, 99999)
    safe_prompt = requests.utils.quote(image_prompt)
    url = f"{base_url}{safe_prompt}?width=1080&height=1080&seed={seed}&nologo=true&model=flux"
    
    print(f"Generating Image: {url}")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except Exception as e:
        print(f"Image Error: {e}")
    return None

# ---------------------------------------------------------
# 7. 投稿処理（二段構えの安全装置付き）
# ---------------------------------------------------------
def post_to_x(text, image_data):
    # 認証セットアップ
    client = tweepy.Client(
        consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    reply_text = """
    ▼納得内定への最短ルート（無料相談）
    https://www.jicoo.com/t/dX0f4ah7ZNbn/e/jiritsu?utm_source=bot

    ▼「ジリツ」のサービス詳細
    https://jiritsu-syukatsu.studio.site/
    """

    media_ids = []
    
    # 1. 画像アップロードを試みる
    if image_data:
        try:
            image_data.seek(0)
            media = api.media_upload(filename="post.jpg", file=image_data)
            media_ids = [media.media_id]
            print(f"画像アップロード成功 Media ID: {media.media_id}")
        except Exception as e:
            print(f"画像アップロード失敗: {e}")
            media_ids = []

    # 2. 投稿を試みる（ここが重要）
    tweet_id = None
    try:
        if media_ids:
            print("画像付き投稿を試みます...")
            res = client.create_tweet(text=text, media_ids=media_ids)
            tweet_id = res.data['id']
            print(f"✅ 画像付きで投稿成功！ ID: {tweet_id}")
    except Exception as e:
        print(f"❌ 画像付き投稿に失敗 (Error: {e})")
        print("🔄 テキストのみで再試行します...")
        try:
            # 画像なしでリトライ
            res = client.create_tweet(text=text)
            tweet_id = res.data['id']
            print(f"✅ テキストのみで投稿成功！ ID: {tweet_id}")
        except Exception as e2:
            print(f"❌ テキスト投稿も失敗: {e2}")

    # 3. リプライ（成功していれば）
    if tweet_id:
        try:
            time.sleep(2)
            client.create_tweet(text=reply_text.strip(), in_reply_to_tweet_id=tweet_id)
            print("✅ 誘導リプライ成功")
        except:
            pass

# ---------------------------------------------------------
# メイン実行
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- START ---")
    cat_key = random.choice(list(CATEGORIES.keys()))
    cat_data = CATEGORIES[cat_key]
    print(f"Category: {cat_data['theme']}")

    tweet = generate_tweet_text(cat_key, cat_data)
    if tweet:
        print(f"Tweet: {tweet}")
        img_prompt = generate_image_prompt(tweet)
        img_data = generate_and_download_image(img_prompt)
        post_to_x(tweet, img_data)
    
    print("--- END ---")
