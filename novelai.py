"""
NovelAI-APIライブラリを使用して画像を生成するモジュール（公式ドキュメントに基づく正しい実装）
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from PIL import Image
import io

try:
    import aiohttp
    from novelai_api import NovelAIAPI
    from novelai_api.ImagePreset import ImageModel, ImagePreset
except ImportError:
    print("NovelAI-API または aiohttp がインストールされていません。")
    print("pip install novelai-api aiohttp を実行してください。")
    NovelAIAPI = None

# 環境変数を読み込み
load_dotenv()

class NovelAIGenerator:
    def __init__(self):
        """NovelAI画像生成器を初期化"""
        if NovelAIAPI is None:
            raise ImportError("NovelAI-API ライブラリが見つかりません")

        self.username = os.getenv("NOVELAI_USERNAME")
        self.password = os.getenv("NOVELAI_PASSWORD")
        if not self.username or not self.password:
            raise ValueError("NOVELAI_USERNAME と NOVELAI_PASSWORD を .env に設定してください")

        print("NovelAI生成器を初期化完了")

    async def _generate_image_async(self, prompt: str, negative_prompt: str = "", **kwargs) -> Optional[bytes]:
        """
        公式ドキュメントに基づく正しい画像生成実装
        参考: https://aedial.github.io/novelai-api/
        """
        try:
            # NovelAI v4.5c - 要件定義書に基づく正しいモデル名
            model = ImageModel.Anime_v45_Curated
            
            # デフォルトのネガティブプロンプト
            default_negative = (
                "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, "
                "cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
            )
            full_negative_prompt = f"{default_negative}, {negative_prompt}" if negative_prompt else default_negative

            async with aiohttp.ClientSession() as session:
                api = NovelAIAPI(session)
                
                print("NovelAI APIログイン中...")
                await api.high_level.login(self.username, self.password)
                print("NovelAI APIログイン完了")

                # 公式ドキュメントに基づく正しいプリセット作成方法
                print("プリセットを作成中...")
                preset = ImagePreset.from_default_config(model)
                
                # 要件定義書の設定を適用
                preset.width = 832
                preset.height = 1216
                preset.steps = 28
                preset.scale = 5.0
                preset.seed = kwargs.get("seed", 0)
                preset.n_samples = 1
                preset.uc = full_negative_prompt
                preset.qualityToggle = True
                preset.sm = False
                preset.sm_dyn = False

                print(f"画像生成開始... ({preset.width}x{preset.height})")
                print(f"モデル: NovelAI v4.5c (Anime_v45_Curated)")
                print(f"プロンプト: {prompt[:100]}...")
                
                # 公式ドキュメントの例に基づく正しい呼び出し方法
                # async for _, img in api.high_level.generate_image(prompt, model, preset):
                async for _, image_bytes in api.high_level.generate_image(prompt, model, preset):
                    print("画像生成完了")
                    return image_bytes

                print("画像生成に失敗しました")
                return None

        except Exception as e:
            print(f"画像生成エラー: {e}")
            return None

    def generate_image(self, prompt: str, negative_prompt: str = "", **kwargs) -> Optional[bytes]:
        """
        同期インターフェース - 内部で非同期処理を実行
        """
        try:
            # イベントループの適切な処理
            try:
                loop = asyncio.get_running_loop()
                print("既存のイベントループで実行中...")
                # 既存ループがある場合は新しいスレッドで実行
                import concurrent.futures
                import threading
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            self._generate_image_async(prompt, negative_prompt, **kwargs)
                        )
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
                    
            except RuntimeError:
                # イベントループが存在しない場合は通常の方法で実行
                print("新しいイベントループで実行中...")
                return asyncio.run(
                    self._generate_image_async(prompt, negative_prompt, **kwargs)
                )
                
        except Exception as e:
            print(f"画像生成エラー: {e}")
            return None

    def save_image(self, image_data: bytes, filename: str) -> bool:
        """画像データをファイルに保存"""
        try:
            with open(filename, "wb") as f:
                f.write(image_data)
            print(f"画像を保存しました: {filename}")
            return True
        except Exception as e:
            print(f"画像保存エラー: {e}")
            return False

    def image_to_pil(self, image_data: bytes) -> Optional[Image.Image]:
        """バイナリデータをPIL Imageに変換"""
        try:
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            print(f"PIL Image変換エラー: {e}")
            return None


def test_novelai():
    """テスト用関数"""
    try:
        generator = NovelAIGenerator()
        test_prompt = "1girl, blonde_hair, blue_eyes, smile, school_uniform, cherry_blossom, outdoors, masterpiece, best_quality"
        
        print("テスト画像生成開始...")
        image_data = generator.generate_image(test_prompt)
        
        if image_data:
            success = generator.save_image(image_data, "test_output.png")
            if success:
                print("テスト画像生成・保存完了")
                return image_data
        else:
            print("テスト画像生成失敗")
            return None
            
    except Exception as e:
        print(f"テストエラー: {e}")
        return None

if __name__ == "__main__":
    test_novelai()