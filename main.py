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
# 2. 投稿カテゴリ（ターゲットの悩みに直結させる）
# ---------------------------------------------------------
# ここが重要です。「業界」ではなく「悩み」軸で回します。
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
# 3. Geminiの設定
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------------------------------------
# 4. ツイート本文を作る関数（信頼獲得・共感型）
# ---------------------------------------------------------
def generate_tweet_text(category_key, category_info):
    prompt = f"""
    あなたは就活支援歴10年以上、数千人をサポートしてきたプロのエージェント「ジリツ」です。
    現在は12月中旬〜1月。ターゲットは「まだ納得内定がない」「大手全落ちで焦っている」26卒・27卒の学生です。
    彼らの不安に寄り添いつつ、プロとしての権威性を示し、信頼を勝ち取るツイートを作成してください。

    【今回の投稿テーマ】
    {category_info['theme']}
    ({category_info['detail']})

    【ツイート作成のルール】
    1. **ターゲット**: 日東駒専・産近甲龍・地方国公立レベルで、自信を失いかけている学生。
    2. **トーン**: 
       - × 単なる励まし（「頑張ればできるよ！」）はNG。軽薄に見える。
       - ○ プロの分析（「過去のデータではこうだった。だから大丈夫」）で安心させる。
       - 語り口は「〜だ」「〜です」など、自信に満ちた落ち着いた口調。
    3. **構成**:
       - 冒頭：学生の「心の声」や「痛いところ」を突くフック。
       - 中盤：プロの知見に基づいた解決策や新しい視点。
       - 結び：「ジリツ」ならその答えを持っていることを匂わせる（宣伝しすぎない）。
    4. **禁止事項**: 嘘や架空の数字は使わない。ハッシュタグ以外でURLは貼らない。
    5. **文字数**: タグ込みで130文字〜140文字ギリギリまで使って密度を高くする。
    6. **必須タグ**: #就活 #26卒 #無い内定 #就活エージェント

    【出力例（あくまでトーンの参考）】
    『聞いたことない会社＝ブラック』という思い込みが、あなたの首を絞めています。私が10年見てきた中で、最強の勝ち組は『知名度ゼロの電子部品メーカー』に入り、30歳で年収1000万を超えた学生です。見るべきはCMの量ではなく、利益率と定着率。その見極め方、教えます。 #就活 #26卒 #隠れ優良企業
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

# ---------------------------------------------------------
# 5. 画像プロンプトを作る関数（エモい・抽象・図解風）
# ---------------------------------------------------------
def generate_image_prompt(tweet_text):
    prompt = f"""
    Based on the following tweet content, create a prompt for an AI image generator.
    The goal is to create an image that stops a user from scrolling on X (Twitter).

    Tweet Content:
    {tweet_text}

    Image Style Directions:
    1. **Mood**: Professional, slightly moody but hopeful, minimalist, high quality.
    2. **Visuals**: 
       - Use metaphors (e.g., a light in a maze, a stepping stone, a hidden gem, a ladder rising from fog).
       - OR a clean, aesthetic "Notion-style" illustration of a checklist or chart.
    3. **NO TEXT**: Do NOT try to include specific text or letters in the image.
    4. **Output**: ONLY the English prompt string. 
    
    Example prompts to emulate:
    - "A minimalist isometric illustration of a golden key hidden among grey stones, soft lighting, 3d render"
    - "A moody photography of a desk with a glowing resume, late night city background, shallow depth of field, cinematic lighting"
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Image Prompt Error: {e}")
        return "minimalist business illustration, growth and success, soft colors, high quality"

# ---------------------------------------------------------
# 6. 画像生成・ダウンロード
# ---------------------------------------------------------
def generate_and_download_image(image_prompt):
    # Pollinations AI (Flux model is good for artistic/realistic)
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(0, 99999)
    # URLエンコードなどはrequestsがよしなにやってくれることが多いが、念のため
    safe_prompt = requests.utils.quote(image_prompt)
    
    # model=flux は画質が良い傾向にある
    url = f"{base_url}{safe_prompt}?width=1080&height=1080&seed={seed}&nologo=true&model=flux"
    
    print(f"Generating Image: {url}")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            print(f"Image Gen Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Image Download Error: {e}")
        return None

# ---------------------------------------------------------
# 7. 投稿処理（安全装置付き）
# ---------------------------------------------------------
def post_to_x(text, image_data):
    # v1.1 API (画像アップロード用) の認証
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    # v2 Client (ツイート投稿用) の認証
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )

    # リプライ（誘導用）
    reply_text = """
    ▼納得内定への最短ルート（無料相談）
    https://www.jicoo.com/t/dX0f4ah7ZNbn/e/jiritsu?utm_source=bot

    ▼「ジリツ」のサービス詳細
    https://jiritsu-syukatsu.studio.site/
    """

    media_ids = []

    # --- 画像アップロードへの挑戦 ---
    if image_data:
        print("画像アップロードを試みます...")
        try:
            # ファイルポインタを先頭に戻す（念のため）
            image_data.seek(0)
            
            # v1.1 APIを使って画像をアップロード
            media = api.media_upload(filename="post_image.jpg", file=image_data)
            media_ids = [media.media_id]
            print(f"画像アップロード成功！ Media ID: {media.media_id}")
            
        except tweepy.errors.Forbidden as e:
            print("【警告】画像のアップロード権限がありませんでした (403 Forbidden)。")
            print("プラン制限の可能性があります。テキストのみで投稿を続行します。")
            media_ids = [] # 画像IDを空にする
        except Exception as e:
            print(f"【警告】画像アップロード中にエラーが発生しました: {e}")
            print("テキストのみで投稿を続行します。")
            media_ids = []

    # --- ツイート投稿 ---
    try:
        if media_ids:
            # 画像あり投稿
            res = client.create_tweet(text=text, media_ids=media_ids)
        else:
            # 画像なし（または失敗時）投稿
            res = client.create_tweet(text=text)
        
        tweet_id = res.data['id']
        print(f"✅ メイン投稿成功! ID: {tweet_id}")

        # --- リプライ投稿 ---
        time.sleep(2)
        try:
            client.create_tweet(text=reply_text.strip(), in_reply_to_tweet_id=tweet_id)
            print("✅ リプライ成功!")
        except Exception as e:
            print(f"リプライ投稿エラー（メインは成功しています）: {e}")

    except Exception as e:
        print(f"❌ 投稿エラー（致命的）: {e}")
        
# ---------------------------------------------------------
# メイン実行ブロック
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- START ---")
    
    # ランダムでカテゴリを選択
    cat_key = random.choice(list(CATEGORIES.keys()))
    cat_data = CATEGORIES[cat_key]
    print(f"Selected Category: {cat_data['theme']}")

    # 本文生成
    tweet = generate_tweet_text(cat_key, cat_data)
    
    if tweet:
        print(f"Tweet Text: \n{tweet}\n")
        
        # 画像プロンプト生成
        img_prompt = generate_image_prompt(tweet)
        print(f"Image Prompt: {img_prompt}")
        
        # 画像生成
        img_data = generate_and_download_image(img_prompt)
        
        # 投稿
        post_to_x(tweet, img_data)
    
    print("--- END ---")


