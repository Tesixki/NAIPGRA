"""
NovelAI-APIライブラリを使用してキャラクター座標対応画像を生成するモジュール（v4.5対応）
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

    async def _generate_image_async(self, prompt_data: dict, negative_prompt: str = "", **kwargs) -> Optional[bytes]:
        """
        NovelAI v4.5 キャラクター座標対応画像生成
        参考: https://github.com/Aedial/novelai-api/blob/main/example/generate_image_v4.py
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

            # プロンプトデータから情報を抽出
            main_prompt = prompt_data.get("prompt", "masterpiece, best_quality")
            character_prompts = prompt_data.get("characterPrompts", [])
            character_count = prompt_data.get("characterCount", 1)
            
            print(f"キャラクター数: {character_count}")
            print(f"メインプロンプト: {main_prompt}")
            
            # キャラクタープロンプトをv4形式に変換
            v4_character_prompts = []
            for i, char_data in enumerate(character_prompts):
                char_prompt = char_data.get("prompt", "1girl")
                position = char_data.get("position")  # Noneの場合もある
                
                char_entry = {"prompt": char_prompt}
                if position:  # positionが指定されている場合のみ追加
                    char_entry["position"] = position
                    print(f"キャラクター{i+1}: {char_prompt} (位置: {position})")
                else:
                    print(f"キャラクター{i+1}: {char_prompt} (位置指定なし)")
                
                v4_character_prompts.append(char_entry)

            async with aiohttp.ClientSession() as session:
                api = NovelAIAPI(session)
                
                print("NovelAI APIログイン中...")
                await api.high_level.login(self.username, self.password)
                print("NovelAI APIログイン完了")

                print("画像生成開始... (832x1216)")
                print("モデル: NovelAI v4.5c (Anime_v45_Curated)")
                
                # プリセットを作成
                preset = ImagePreset.from_default_config(model)
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

                # v4形式: キャラクタープロンプトをpreset.charactersに設定
                if len(v4_character_prompts) > 0:
                    print("キャラクタープロンプトをpreset.charactersに設定中...")
                    # 公式サンプルに基づき、preset.charactersに設定
                    preset.characters = v4_character_prompts
                    print(f"設定されたキャラクター数: {len(v4_character_prompts)}")
                    for i, char in enumerate(v4_character_prompts):
                        print(f"  キャラクター{i+1}: {char}")
                
                # 画像生成実行
                async for _, image_bytes in api.high_level.generate_image(
                    prompt=main_prompt,
                    model=model,
                    preset=preset
                ):
                        print("画像生成完了")
                        return image_bytes

                print("画像生成に失敗しました")
                return None

        except Exception as e:
            print(f"画像生成エラー: {e}")
            return None

    def generate_image(self, prompt_data: dict, negative_prompt: str = "", **kwargs) -> Optional[bytes]:
        """
        同期インターフェース - 内部で非同期処理を実行
        """
        try:
            # イベントループの適切な処理
            try:
                asyncio.get_running_loop()
                print("既存のイベントループで実行中...")
                # 既存ループがある場合は新しいスレッドで実行
                import concurrent.futures
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            self._generate_image_async(prompt_data, negative_prompt, **kwargs)
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
                    self._generate_image_async(prompt_data, negative_prompt, **kwargs)
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
        
        # テスト用の構造化プロンプト
        test_prompt_data = {
            "characterCount": 2,
            "prompt": "library, bookshelf, indoor, warm_lighting, masterpiece, best_quality",
            "characterPrompts": [
                {
                    "prompt": "1girl, blonde_hair, blue_eyes, reading, sitting, upper_body, school_uniform, gentle_smile",
                    "position": "B2"
                },
                {
                    "prompt": "1girl, brown_hair, green_eyes, standing, full_body, casual_clothes, happy",
                    "position": "D4"
                }
            ]
        }
        
        print("テスト画像生成開始...")
        image_data = generator.generate_image(test_prompt_data)
        
        if image_data:
            success = generator.save_image(image_data, "test_v4_output.png")
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