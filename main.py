import os
import tweepy
import google.generativeai as genai
import random
import requests
import io
import time
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------
# 1. 環境変数 (変更なし)
# ---------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# ---------------------------------------------------------
# 2. Gemini設定
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------------------------------------
# 3. 戦略的カテゴリ設定（時間帯で切り替えるネタ帳）
# ---------------------------------------------------------
# 【昼用】論理・ハック・データ (8:00 - 20:00)
DAY_CATEGORIES = {
    "logic_structure": "業界構造の解説。BtoCではなくBtoBの利益率やシェアを見るべき論理的な理由。",
    "hack_criteria": "優良企業を見抜く具体的な数字条件（平均勤続年数15年以上、離職率5%以下など）。",
    "market_value": "3年後、5年後の市場価値。どこに入るかより、どんなスキルが身につくか。",
}

# 【夜用】本音・毒舌・伴走 (20:00 - 02:00)
NIGHT_CATEGORIES = {
    "tough_love": "【本音・毒舌】大手病の学生への愛ある厳しい指摘。「プライドで飯は食えない」。",
    "empathy_story": "【伴走・共感】NNTの不安への寄り添い。「俺も全落ちしたけど大丈夫」という過去の開示。",
    "anxiety_relief": "【焦り解消】周りと比較してしまう深夜の不安を打ち消す、プロ視点の「大丈夫」な根拠。",
}

# ---------------------------------------------------------
# 4. 「ライブ感」を出すための枕詞（ランダム挿入）
# ---------------------------------------------------------
LIVE_OPENERS = [
    "さっき面談した学生が言ってたんだけど、",
    "正直、ここだけの話。",
    "あえて厳しいことを言うけど、",
    "これ、まだ気づいてない人多いんだけど、",
    "今の時期、みんな焦りすぎ。",
    "ふと思ったんだけど、",
]

# ---------------------------------------------------------
# 5. ツイート生成関数（戦略の中核）
# ---------------------------------------------------------
def generate_strategic_tweet():
    # 日本時間の現在時刻を取得
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    current_hour = now.hour
    
    # 時間帯によるモード切替
    if 20 <= current_hour or current_hour < 2:
        # --- 夜モード（感情・本音） ---
        mode = "Night Mode (Emotional/Honest)"
        cat_key = random.choice(list(NIGHT_CATEGORIES.keys()))
        theme_detail = NIGHT_CATEGORIES[cat_key]
        opener = random.choice(LIVE_OPENERS) if random.random() > 0.5 else "" # 50%で枕詞をつける
        
        system_instruction = f"""
        あなたは「就活エージェントの個人アカウント」の中の人です。
        現在は深夜帯。ターゲットは不安で眠れない、または焦っている26卒・27卒。
        
        【キャラ設定】
        - 企業公式のような堅苦しい言葉は禁止。
        - 語り口は「〜だよね」「〜だと思う」「正直〜だ」など、人間味のある口語（Twitter構文）。
        - 感情を出してください（呆れ、応援、共感）。
        
        【今回のテーマ】
        {theme_detail}
        
        【必須ルール】
        - 冒頭に「{opener}」というフレーズを自然に組み込んで書き始めてください（文脈に合わなければ微調整可）。
        - 嘘はつかないが、実体験のように語る。
        - プロだから知っている「ビジネスの本質」や「業界の裏側の面白さ」を語るように伝える。
        - 文字数はハッシュタグ込みで135文字以内。
        - ハッシュタグ: #就活 #26卒 #27卒 #NNT
        """
        
    else:
        # --- 昼モード（論理・有益） ---
        mode = "Day Mode (Logical/Hack)"
        cat_key = random.choice(list(DAY_CATEGORIES.keys()))
        theme_detail = DAY_CATEGORIES[cat_key]
        
        system_instruction = f"""
        あなたは「就活戦略家」の個人アカウントです。
        現在は日中。ターゲットは移動中や企業研究中の学生。
        
        【キャラ設定】
        - 感情よりも「有益性」重視。ドライで論理的。
        - 知的で論理的な「です・ます」調、または落ち着いた「言い切り」にする。
        - 具体的な数字や条件を提示する。
        
        【今回のテーマ】
        {theme_detail}
        
        【必須ルール】
        - 結論から書く。
        - 最後に「このリスト欲しい人いる？」や「保存推奨」など、反応を促す言葉を入れる。
        - 文字数はハッシュタグ込みで135文字以内。
        - ハッシュタグ: #就活 #26卒 #就活攻略
        """

    print(f"🕒 Current Hour: {current_hour} ({mode})")
    print(f"📝 Category: {cat_key}")

    try:
        response = model.generate_content(system_instruction)
        text = response.text.strip().replace("「", "").replace("」", "")
        
        # 安全装置：長すぎる場合はカット
        if len(text) > 138:
            text = text[:135] + "..."
            
        return text, mode
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None, None

# ---------------------------------------------------------
# 6. 画像プロンプト生成（保存用コンテンツ）
# ---------------------------------------------------------
def generate_image_prompt(tweet_text):
    # 画像は「図解」「まとめ」っぽくする
    prompt = f"""
    Create a prompt for an AI image generator based on this tweet: "{tweet_text}"
    Style: Minimalist infographic style, Notion style, or clean corporate memphis.
    Subject: A simple visual summary or symbolic representation of the career advice.
    Constraint: NO TEXT inside the image.
    Output: ONLY the prompt string.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "minimalist business illustration, abstract, notion style, no text"

# ---------------------------------------------------------
# 7. 画像生成・ダウンロード
# ---------------------------------------------------------
def generate_and_download_image(image_prompt):
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(0, 99999)
    safe_prompt = requests.utils.quote(image_prompt)
    url = f"{base_url}{safe_prompt}?width=1080&height=1350&seed={seed}&nologo=true&model=flux" # 4:5比率に変更（スマホで見やすい）
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except Exception as e:
        print(f"Image Error: {e}")
    return None

# ---------------------------------------------------------
# 8. 投稿処理
# ---------------------------------------------------------
def post_to_x(text, image_data=None):
    client = tweepy.Client(
        consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    # 固定のリプライ（Jicoo誘導）
    reply_text = """
▼大手全落ち/NNTからの逆転ルート（無料相談）
https://www.jicoo.com/t/dX0f4ah7ZNbn/e/jiritsu?utm_source=twitter
    """

    media_ids = []
    if image_data:
        try:
            image_data.seek(0)
            media = api.media_upload(filename="post.jpg", file=image_data)
            media_ids = [media.media_id]
            print("🖼️ 画像アップロード成功")
        except Exception as e:
            print(f"⚠️ 画像アップロード失敗（Freeプランの可能性）: {e}")

    # 投稿実行
    tweet_id = None
    try:
        if media_ids:
            res = client.create_tweet(text=text, media_ids=media_ids)
        else:
            res = client.create_tweet(text=text)
        
        tweet_id = res.data['id']
        print(f"✅ 投稿成功 ID: {tweet_id}")
        
    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
        # リトライロジックなどはここに記述可能

    # リプライ（誘導）
    if tweet_id:
        try:
            time.sleep(2)
            client.create_tweet(text=reply_text.strip(), in_reply_to_tweet_id=tweet_id)
            print("🔗 誘導リプライ送信完了")
        except Exception as e:
            print(f"⚠️ リプライ失敗: {e}")

# ---------------------------------------------------------
# メイン実行
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- START ---")
    
    # 1. テキスト生成（時間帯で自動切り替え）
    tweet_text, current_mode = generate_strategic_tweet()
    
    if tweet_text:
        print(f"📢 Generated Tweet:\n{tweet_text}\n")
        
        # 2. 画像生成判定（3回に1回、約33%の確率で画像をつける）
        # ※毎回つけるとbot感が出るため。画像があるときは「保存」を狙う。
        should_attach_image = random.random() < 0.33
        
        img_data = None
        if should_attach_image:
            print("🎨 画像を生成します...")
            img_prompt = generate_image_prompt(tweet_text)
            img_data = generate_and_download_image(img_prompt)
        else:
            print("📝 今回はテキストのみで勝負します。")

        # 3. 投稿
        post_to_x(tweet_text, img_data)
    
    print("--- END ---")


