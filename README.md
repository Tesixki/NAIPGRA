# 🎨 NAIPGRA - NovelAI イラスト生成チャットサービス

GradioのWebUIでユーザーが希望するイラストを生成するチャットサービスです。

## 📋 概要

このプロジェクトは、ユーザーの自然な日本語入力を高品質なイラストに変換するWebアプリケーションです。

### 🔄 生成フロー

1. **ユーザー入力** → ユーザーが希望するイラストの詳細をチャットで入力
2. **GPT-4o処理** → LangChainのGPT-4oでDanbooruタグ形式に変換・補完
3. **NovelAI生成** → NovelAI v4.5c (Curated)で高品質画像生成（832x1216解像度）
4. **結果表示** → Gradioチャットに画像とログを表示

## ✨ 特徴

- 🤖 **GPT-4o活用**: 自然な日本語からDanbooruタグへの高精度変換
- 🎨 **NovelAI v4.5c**: 最新モデルによる高品質アニメ風イラスト生成
- 💻 **GPU対応**: CUDA対応で高速処理（RTX 3080等）
- 🌐 **WebUI**: 美しいGradioインターフェース
- 📱 **リアルタイム**: 処理状況をリアルタイムで表示

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の設定を追加：

```env
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here

# NovelAI API設定
NOVELAI_USERNAME=your_novelai_username_here
NOVELAI_PASSWORD=your_novelai_password_here

# Gradio設定（オプション）
GRADIO_PORT=7860
GRADIO_HOST=127.0.0.1
```

### 3. アプリケーションの起動

```bash
python main.py
```

ブラウザで `http://127.0.0.1:7860` にアクセスしてください。

## 📁 ファイル構成

```
NAIPGRA/
├── main.py              # メインアプリケーション（Gradio WebUI）
├── chatGPT.py          # GPT-4oによるプロンプト変換
├── novelai.py          # NovelAI API画像生成
├── requirements.txt    # 依存パッケージ
├── .env               # 環境変数（作成が必要）
├── .gitignore         # Git除外設定
└── README.md          # このファイル
```

## 🛠️ 技術スタック

- **フロントエンド**: Gradio WebUI
- **AI処理**: 
  - OpenAI GPT-4o (LangChain経由)
  - NovelAI v4.5c Curated
- **画像処理**: PIL (Pillow)
- **並行処理**: asyncio, aiohttp
- **環境管理**: python-dotenv

## 💡 使用例

### 入力例
```
猫の女の子が花畑で笑っている
```

### GPT-4o変換例
```
1girl, cat_ears, cat_tail, blonde_hair, blue_eyes, smile, happy, flower_field, 
outdoor, spring, cherry_blossom, cute, kawaii, anime_style, masterpiece, best_quality
```

### 出力
832x1216の高品質アニメ風イラスト

## ⚙️ 設定

### GPU使用
CUDA対応GPUがある場合、自動的にGPU処理が有効になります：
- NVIDIA RTX 3080での動作確認済み
- CPU処理にも対応

### NovelAI設定
- **モデル**: NovelAI v4.5c (Anime_v45_Curated)
- **解像度**: 832x1216（縦長・スマホ壁紙に最適）
- **品質**: 高品質設定（steps=28, scale=5.0）

## 🔧 トラブルシューティング

### よくある問題

1. **APIキーエラー**
   - `.env`ファイルの設定を確認
   - OpenAI/NovelAIアカウントの有効性を確認

2. **GPU認識されない**
   - CUDA対応PyTorchをインストール：
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   ```

3. **ポート競合**
   - `.env`で`GRADIO_PORT`を変更（例：7861）

## 📝 ライセンス

このプロジェクトは個人・学習目的での使用を想定しています。

## 🙏 謝辞

- [NovelAI](https://novelai.net/) - 高品質画像生成API
- [OpenAI](https://openai.com/) - GPT-4o言語モデル  
- [Gradio](https://gradio.app/) - WebUIフレームワーク
- [LangChain](https://langchain.com/) - AI統合フレームワーク

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesでお知らせください。

---

**注意**: このツールはAPIクレジットを消費します。使用前に各サービスの料金体系をご確認ください。
