"""
Gradio WebUIを使ったイラスト生成チャットサービス
"""

import os
import gradio as gr
import asyncio
from datetime import datetime
from PIL import Image
import io
from dotenv import load_dotenv

# 自作モジュールをインポート
from chatGPT import ChatGPTProcessor
from novelai import NovelAIGenerator

# 環境変数を読み込み
load_dotenv()

class IllustrationChatService:
    def __init__(self):
        """イラスト生成チャットサービスを初期化"""
        print("サービスを初期化中...")
        
        try:
            self.chatgpt = ChatGPTProcessor()
            print("✓ ChatGPT初期化完了")
        except Exception as e:
            print(f"✗ ChatGPT初期化エラー: {e}")
            self.chatgpt = None
        
        # DanbotNL処理を削除

        try:
            self.novelai = NovelAIGenerator()
            print("✓ NovelAI初期化完了")
        except Exception as e:
            print(f"✗ NovelAI初期化エラー: {e}")
            self.novelai = None
        
        print("サービス初期化完了")
    
    def process_user_request(self, user_input: str, chat_history: list):
        """
        ユーザーのリクエストを処理してイラストを生成
        
        Args:
            user_input (str): ユーザーの入力
            chat_history (list): チャット履歴
            
        Returns:
            tuple: (更新されたチャット履歴, 空文字列, 生成された画像)
        """
        if not user_input.strip():
            return chat_history, "", None
        
        # チャット履歴にユーザーの入力を追加
        chat_history.append({"role": "user", "content": user_input})
        
        try:
            # ステップ1: ChatGPTでイラスト内容を補完
            status_message = "🤖 ChatGPTでイラスト内容を補完中..."
            chat_history.append({"role": "assistant", "content": status_message})
            yield chat_history, "", None
            
            if self.chatgpt:
                enhanced_description = self.chatgpt.enhance_illustration_prompt(user_input)
            else:
                enhanced_description = user_input
            
            # ステップ2: NovelAI APIで画像生成
            status_message = "🎨 NovelAI APIで画像生成中..."
            chat_history[-1]["content"] = status_message
            yield chat_history, "", None
            
            if self.novelai:
                # ChatGPTの出力を直接NovelAIに渡す
                image_data = self.novelai.generate_image(enhanced_description)
                
                if image_data:
                    # PIL Imageに変換
                    image = self.novelai.image_to_pil(image_data)
                    
                    # 成功メッセージ
                    success_message = f"""
✅ **イラスト生成完了！**

**補完された説明:**
{enhanced_description}

**生成時刻:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    chat_history[-1]["content"] = success_message
                    yield chat_history, "", image
                    
                else:
                    error_message = "❌ 画像生成に失敗しました。APIキーや設定を確認してください。"
                    chat_history[-1]["content"] = error_message
                    yield chat_history, "", None
            else:
                error_message = "❌ NovelAI APIが利用できません。"
                chat_history[-1]["content"] = error_message
                yield chat_history, "", None
                
        except Exception as e:
            error_message = f"❌ エラーが発生しました: {str(e)}"
            chat_history[-1]["content"] = error_message
            yield chat_history, "", None
    


def create_gradio_interface():
    """Gradio WebUIを作成"""
    service = IllustrationChatService()
    
    # カスタムCSS
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .chat-container {
        height: 600px !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="イラスト生成チャットサービス") as demo:
        gr.Markdown("# 🎨 イラスト生成チャットサービス")
        gr.Markdown("希望するイラストの内容を入力してください。AIが詳細な説明に変換し、高品質なイラストを生成します。")
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="チャット",
                    height=600,
                    show_copy_button=True,
                    type="messages"
                )
                
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="例: 金髪の女の子が桜の木の下で笑っている",
                        label="イラストの希望を入力",
                        lines=2,
                        scale=4
                    )
                    submit_btn = gr.Button("生成", variant="primary", scale=1)
                
                gr.Examples(
                    examples=[
                        "可愛い猫の女の子が花畑で笑っている",
                        "金髪で青い目の魔法使いが本を読んでいる",
                        "制服を着た女子高生が教室で勉強している",
                        "和服を着た美少女が竹林を歩いている"
                    ],
                    inputs=user_input
                )
            
            with gr.Column(scale=1):
                generated_image = gr.Image(
                    label="生成されたイラスト",
                    type="pil",
                    height=600
                )
                
                download_btn = gr.DownloadButton(
                    label="画像をダウンロード",
                    visible=False
                )
        
        # イベントハンドラー
        def submit_and_generate(user_input, chat_history):
            for result in service.process_user_request(user_input, chat_history):
                yield result
        
        def clear_chat():
            return [], ""
        
        def on_image_change(image):
            if image is not None:
                return gr.DownloadButton(visible=True)
            return gr.DownloadButton(visible=False)
        
        # イベントバインディング
        submit_event = submit_btn.click(
            fn=submit_and_generate,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input, generated_image],
            show_progress=True
        )
        
        user_input.submit(
            fn=submit_and_generate,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input, generated_image],
            show_progress=True
        )
        
        generated_image.change(
            fn=on_image_change,
            inputs=[generated_image],
            outputs=[download_btn]
        )
        
        # クリアボタン
        clear_btn = gr.Button("チャットをクリア", variant="secondary")
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, user_input]
        )
    
    return demo

def main():
    """メイン関数"""
    print("🚀 イラスト生成チャットサービスを起動中...")
    
    # 環境変数から設定を取得
    port = int(os.getenv("GRADIO_PORT", 7860))
    host = os.getenv("GRADIO_HOST", "127.0.0.1")
    
    # Gradio WebUIを作成・起動
    demo = create_gradio_interface()
    
    print(f"📱 WebUIが起動しました: http://{host}:{port}")
    print("🎯 ブラウザでアクセスして、イラスト生成をお楽しみください！")
    
    demo.launch(
        server_name=host,
        server_port=port,
        share=False,  # 公開する場合はTrueに変更
        show_error=True,
        favicon_path=None
    )

if __name__ == "__main__":
    main()
