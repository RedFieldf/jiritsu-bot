import os
import google.generativeai as genai

# 環境変数からキーを読み込む
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print("--- 診断開始 ---")

# 1. キーが読み込めているか確認
if GEMINI_API_KEY:
    print("APIキー: 読み込み成功")
else:
    print("APIキー: 読み込み失敗（設定されていません）")

# 2. 使えるモデル一覧を表示する
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("\n【このキーで利用可能なモデル一覧】")
    
    # generateContent（文章生成）に対応しているモデルだけを表示
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            available_models.append(m.name)
            
    if not available_models:
        print("利用可能なモデルが見つかりませんでした。")
        
except Exception as e:
    print(f"\nエラーが発生しました: {e}")

print("--- 診断終了 ---")
