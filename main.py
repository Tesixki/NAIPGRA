"""
Gradio WebUIを使ったイラスト生成チャットサービス
"""

import os
import gradio as gr
from datetime import datetime
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

    def save_generated_image(self, image_data: bytes) -> str:
        """
        生成された画像をoutputsディレクトリに保存

        Args:
            image_data (bytes): 画像のバイナリデータ

        Returns:
            str: 保存されたファイルのパス
        """
        # outputsディレクトリを作成（存在しない場合）
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            os.makedirs(outputs_dir)
            print(f"📁 {outputs_dir}ディレクトリを作成しました")

        # ファイル名を生成（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        filepath = os.path.join(outputs_dir, filename)

        # 画像を保存
        try:
            with open(filepath, "wb") as f:
                f.write(image_data)
            print(f"💾 画像を保存しました: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ 画像保存エラー: {e}")
            return ""

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
                prompt_data = self.chatgpt.enhance_illustration_prompt(user_input)
            else:
                # フォールバック用の構造化データ（位置指定なし）
                prompt_data = {
                    "characterCount": 1,
                    "prompt": "masterpiece, best_quality, high_resolution",
                    "characterPrompts": [
                        {
                            "prompt": user_input
                            # positionは任意項目なので省略
                        }
                    ],
                }

            # ステップ2: NovelAI v4.5でキャラクター座標対応画像生成
            status_message = "🎨 NovelAI v4.5で画像生成中..."
            chat_history[-1]["content"] = status_message
            yield chat_history, "", None

            if self.novelai:
                # 構造化プロンプトデータをNovelAIに渡す
                image_data = self.novelai.generate_image(prompt_data)

                if image_data:
                    # PIL Imageに変換
                    image = self.novelai.image_to_pil(image_data)

                    # outputsディレクトリに画像を保存
                    saved_path = self.save_generated_image(image_data)

                    # 成功メッセージ
                    character_info = ""
                    for i, char in enumerate(prompt_data.get("characterPrompts", [])):
                        position = char.get("position")
                        position_text = (
                            f" (位置: {position})" if position else " (位置指定なし)"
                        )
                        character_info += f"**キャラクター{i + 1}**{position_text}: {char.get('prompt', '')}\n"

                    save_info = f"\n**保存先:** {saved_path}" if saved_path else ""

                    success_message = f"""
✅ **イラスト生成完了！**

**キャラクター数:** {prompt_data.get("characterCount", 1)}

**背景・環境:**
{prompt_data.get("prompt", "")}

{character_info}{save_info}

**生成時刻:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
                    chat_history[-1]["content"] = success_message
                    yield chat_history, "", image

                else:
                    error_message = (
                        "❌ 画像生成に失敗しました。APIキーや設定を確認してください。"
                    )
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
        margin: 0 auto !important;
        padding: 20px !important;
    }
    
    .chat-container {
        height: 600px !important;
    }
    
    /* メインコンテナを中央配置 */
    .main {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    /* タイトルを中央揃え */
    .markdown h1, .markdown h2 {
        text-align: center !important;
        margin-bottom: 1rem !important;
    }
    
    /* レスポンシブデザイン */
    @media (max-width: 768px) {
        .gradio-container {
            max-width: 95% !important;
            padding: 10px !important;
        }
    }
    
    /* コンポーネント間の余白調整 */
    .block {
        margin-bottom: 1rem !important;
    }
    
    /* ダウンロードボタンのスタイル */
    .download-btn {
        width: 100% !important;
        margin-top: 10px !important;
    }
    """

    with gr.Blocks(
        css=custom_css, title="イラスト生成チャットサービス", theme=gr.themes.Soft()
    ) as demo:
        # ヘッダーセクション
        with gr.Column(elem_classes="main"):
            gr.Markdown("# 🎨 イラスト生成チャットサービス")
            gr.Markdown(
                "希望するイラストの内容を入力してください。AIが詳細な説明に変換し、高品質なイラストを生成します。"
            )

        # メインコンテンツを中央配置のコンテナで囲む
        with gr.Column(elem_classes="main"):
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="チャット",
                        height=600,
                        show_copy_button=True,
                        type="messages",
                    )

                    with gr.Row():
                        user_input = gr.Textbox(
                            placeholder="例: 金髪の女の子が桜の木の下で笑っている",
                            label="イラストの希望を入力",
                            lines=2,
                            scale=4,
                        )
                        submit_btn = gr.Button("生成", variant="primary", scale=1)

                    gr.Examples(
                        examples=[
                            "可愛い猫の女の子が花畑で笑っている",
                            "金髪で青い目の魔法使いが本を読んでいる",
                            "制服を着た女子高生が教室で勉強している",
                            "和服を着た美少女が竹林を歩いている",
                        ],
                        inputs=user_input,
                    )

                with gr.Column(scale=1):
                    generated_image = gr.Image(
                        label="生成されたイラスト", type="pil", height=600
                    )

                    download_btn = gr.DownloadButton(
                        label="📥 画像をダウンロード",
                        visible=False,
                        variant="secondary",
                    )

        # イベントハンドラー
        def submit_and_generate(user_input, chat_history):
            for result in service.process_user_request(user_input, chat_history):
                yield result

        def clear_chat():
            return [], ""

        def on_image_change(image):
            """画像が変更されたときのハンドラー"""
            if image is not None:
                # 画像ファイルを一時保存してダウンロード用のパスを生成
                import tempfile
                import uuid

                # 一意なファイル名を生成
                filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
                filepath = os.path.join(tempfile.gettempdir(), filename)

                # PIL画像を保存
                image.save(filepath, "PNG")

                return gr.DownloadButton(
                    label="📥 画像をダウンロード", value=filepath, visible=True
                )
            else:
                return gr.DownloadButton(label="📥 画像をダウンロード", visible=False)

        # クリアボタンを中央配置
        with gr.Row():
            clear_btn = gr.Button("🗑️ チャットをクリア", variant="secondary", scale=1)

        # イベントハンドラー設定
        submit_btn.click(
            submit_and_generate,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input, generated_image],
        ).then(on_image_change, inputs=[generated_image], outputs=[download_btn])

        user_input.submit(
            submit_and_generate,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input, generated_image],
        ).then(on_image_change, inputs=[generated_image], outputs=[download_btn])

        clear_btn.click(clear_chat, inputs=[], outputs=[chatbot, user_input]).then(
            lambda: gr.DownloadButton(label="📥 画像をダウンロード", visible=False),
            inputs=[],
            outputs=[download_btn],
        )

    return demo


def find_available_port(start_port: int = 7860, max_attempts: int = 10) -> int:
    """利用可能なポートを見つける"""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue

    raise OSError(
        f"ポート {start_port} から {start_port + max_attempts - 1} の範囲で利用可能なポートが見つかりませんでした"
    )


def main():
    """メイン関数"""
    print("🚀 イラスト生成チャットサービスを起動中...")

    # 環境変数から設定を取得
    requested_port = int(os.getenv("GRADIO_PORT", 7860))
    host = os.getenv("GRADIO_HOST", "127.0.0.1")

    # Gradio WebUIを作成
    demo = create_gradio_interface()

    # ポート競合時のエラーハンドリング
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # 最初は指定されたポートを試す
            if attempt == 0:
                port = requested_port
            else:
                # ポート競合の場合、利用可能なポートを検索
                print(f"⚠️  ポート {requested_port} が使用中です。別のポートを検索中...")
                port = find_available_port(requested_port + 1)

            print(f"📱 WebUIを起動中: http://{host}:{port}")
            print("🎯 ブラウザでアクセスして、イラスト生成をお楽しみください！")

            demo.launch(
                server_name=host,
                server_port=port,
                share=False,  # 公開する場合はTrueに変更
                show_error=True,
                favicon_path=None,
                prevent_thread_lock=False,
            )
            break  # 成功したらループを抜ける

        except OSError as e:
            if "Cannot find empty port" in str(e) or "Address already in use" in str(e):
                if attempt < max_retries - 1:
                    print(f"❌ ポート {port} でエラー: {e}")
                    print(f"🔄 再試行中... ({attempt + 1}/{max_retries})")
                    continue
                else:
                    print(
                        "❌ 利用可能なポートが見つかりませんでした。以下を確認してください:"
                    )
                    print("   1. 他のGradioアプリケーションが起動していないか")
                    print("   2. ファイアウォール設定")
                    print("   3. .envでGRADIO_PORTを別の値に設定")
                    raise
            else:
                print(f"❌ 予期しないエラー: {e}")
                raise
        except Exception as e:
            print(f"❌ WebUI起動エラー: {e}")
            raise


if __name__ == "__main__":
    main()
