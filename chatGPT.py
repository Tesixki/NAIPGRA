"""
ChatGPTを使用してユーザーの入力をNovelAI v4.5用の構造化プロンプトに変換するモジュール
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class ChatGPTProcessor:
    def __init__(self):
        """ChatGPTプロセッサーを初期化"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY環境変数が設定されていません")
        
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model="gpt-5",
            temperature=0.7
        )
    
    def enhance_illustration_prompt(self, user_input: str) -> dict:
        """
        ユーザーの入力をNovelAI v4.5用の構造化プロンプトに変換
        
        Args:
            user_input (str): ユーザーからの入力テキスト
            
        Returns:
            dict: 構造化されたプロンプト情報
        """
        system_prompt = """
あなたはNovelAI v4.5画像生成のプロンプトエンジニアです。
ユーザーの要求を以下のJSON形式で出力してください：

{
  "characterCount": キャラクター数(1-6),
  "prompt": "背景、景色、物などの環境要素のDanbooruタグ",
  "characterPrompts": [
    {
      "prompt": "キャラクター1の特徴・表情・ポーズ・体の写り具合のDanbooruタグ",
      "position": "座標(A1-E5の中から選択)、任意項目でありキャラの座標を指定する必要でない場合は入れないこと"
    }
  ]
}

ルール：
1. characterCountは検出されたキャラクター数（1-6）
2. promptにはキャラクターの数(1girlや2boysなど)と環境・背景・物・景色のタグのみ
3. characterPromptsには各キャラクターの外見・表情・ポーズ・体の写り具合、版権キャラクターならそれに相応するDanbooruタグを挿入
4. positionはキャラクターの頭を画面内の座標（A1=左上、E5=右下、C3=中央）
5. 全てDanbooruタグ形式（英語、アンダースコア区切り）
6. 必ずJSON形式で出力（マークダウン不要）

例：
入力「金髪の女の子が図書館で本を読んでいる」
出力：
{
  "characterCount": 1,
  "prompt": "library, bookshelf, indoor, wooden_table, books, warm_lighting, masterpiece, best_quality",
  "characterPrompts": [
    {
      "prompt": "1girl, blonde_hair, blue_eyes, reading, sitting, upper_body, school_uniform, gentle_smile, holding_book",
      "position": "C3"
    }
  ]
}
"""
        
        human_prompt = f"""
以下のユーザーの要求をJSON形式で構造化してください：

{user_input}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            print("ChatGPT API呼び出し中...")
            response = self.llm.invoke(messages)
            print(f"ChatGPT返答:\n{response.content}")
            
            # JSONパース
            try:
                parsed_response = json.loads(response.content)
                return parsed_response
            except json.JSONDecodeError as e:
                print(f"JSON解析エラー: {e}")
                # フォールバック：シンプルな構造を返す
                return {
                    "characterCount": 1,
                    "prompt": "masterpiece, best_quality, high_resolution",
                    "characterPrompts": [
                        {
                            "prompt": response.content.replace('\n', ', '),
                            "position": "C3"
                        }
                    ]
                }
                
        except Exception as e:
            print(f"ChatGPT APIエラー: {e}")
            return {
                "characterCount": 1,
                "prompt": "masterpiece, best_quality",
                "characterPrompts": [
                    {
                        "prompt": f"エラーが発生しました: {str(e)}",
                        "position": "C3"
                    }
                ]
            }

def test_chatgpt():
    """テスト用関数"""
    try:
        processor = ChatGPTProcessor()
        test_input = "可愛い猫の女の子が花畑で笑っている"
        result = processor.enhance_illustration_prompt(test_input)
        print("入力:", test_input)
        print("出力:", result)
        return result
    except Exception as e:
        print(f"テストエラー: {e}")

if __name__ == "__main__":
    test_chatgpt()