"""
ChatGPTを使用してユーザーの入力をイラスト生成用の詳細な説明に変換するモジュール
"""

import os
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
            model="gpt-4o",
            temperature=0.7
        )
    
    def enhance_illustration_prompt(self, user_input: str) -> str:
        """
        ユーザーの入力をイラスト生成用の詳細な説明に変換
        
        Args:
            user_input (str): ユーザーからの入力テキスト
            
        Returns:
            str: 詳細なイラスト説明
        """
        system_prompt = """
あなたはイラスト生成AIのプロンプトエンジニアです。
ユーザーの簡単な要求を、Danbooruのタグ形式で羅列してください。また背景や特徴をいいかんじに情報を加えて
以下の要素を含めてタグ形式で「,」で区切って羅列してください、カテゴリーで分けるように書かないでください：
- キャラクターの外見（髪色、目の色、服装、表情など）
- ポーズや動作
- 背景や環境
- 画風やスタイル
- 色彩や雰囲気

Danbooruのタグ形式を意識してください
"""
        
        human_prompt = f"""
以下のユーザーの要求を、詳細なイラストの説明に変換してください：

{user_input}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            print("ChatGPT API呼び出し中...")
            response = self.llm(messages)
            print(f"ChatGPT返答:\n{response.content}")
            return response.content
        except Exception as e:
            print(f"ChatGPT APIエラー: {e}")
            return f"エラーが発生しました: {str(e)}"

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