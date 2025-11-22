# 📄 RAW 自動分類ツール 要件定義（Markdown版）

## 概要

本ツールは、macOS（M1）上で動作するローカル Python アプリケーションであり、
指定されたディレクトリ以下の RAW 画像を自動的に検出し、

1. **RAW → JPEG の縮小サムネイル生成**
2. **画像特徴量の抽出とクラスタリング**
3. **Lightroom 用 XMP メタデータへのタグ付与**

を一括で実行する。

ユーザーは CLI からディレクトリを一つ指定するだけで処理を開始できる。

---

## 対象ファイル形式

* RAW フォーマット
  `CR2`, `CR3`, `NEF`, `ARW`, `RAF`, `DNG` など一般的な RAW を対象とする
* RAW に対応する生成物

  * 縮小 JPEG
  * XMP メタデータ（存在しない場合は新規生成）

---

## 全体フロー

### 1. RAW → JPEG 変換

* 指定したディレクトリ以下を再帰的に探索し、すべての RAW ファイルを検出する。
* 各 RAW を読み込み、長辺 512px 程度に縮小された JPEG を生成。
* 出力構造は `thumbs/` 以下に RAW と同じ相対パスで保存する。
* 使用ライブラリ：

  * `rawpy`
  * `Pillow`

---

### 2. 画像特徴量の抽出・クラスタリング

* 生成した JPEG 画像に対して、以下の処理を実行：

  * ResNet50 または CLIP 系モデルによる画像埋め込み（特徴ベクトル）生成
  * 特徴ベクトルを `embeddings.npy` + `meta.json` として保存
  * `MiniBatchKMeans`（または HDBSCAN）でクラスタリング
  * 各画像のクラスタID を `clusters.json` に保存
* 特徴ベクトル次元は利用モデルに依存（例：2048次元）。

---

### 3. XMP メタデータ作成／更新

* `clusters.json` の結果に基づき、各 RAW に対応する `.xmp` を処理する。
* XMP が存在しない場合は Lightroom が読める最小構造の XMP を新規生成する。
* 以下のキーワードを XMP に追加する。

  * `dc:subject` → `ai_cluster_003` など
  * `lr:hierarchicalSubject` → `AI/cluster/003` など階層キーワード
* 既存 XMP には追記する。重複キーワードは追加しない。
* Lightroom Classic では「メタデータ → メタデータをファイルから読み込み」により同期できる。

---

## CLI 仕様

```
python organizer.py /path/to/target_dir
```

### 引数

* 第一引数：RAW を含むディレクトリパス
* オプション（任意）：

  * `--size 512` → JPEG の長辺サイズ
  * `--clusters 50` → KMeans のクラスタ数
  * `--model resnet50` → 使用モデル指定
  * `--dry-run` → XMP 書き込みなし

---

## 出力物

* `thumbs/` 以下に生成される JPEG
* `embeddings.npy`, `meta.json`
* `clusters.json`
* RAW と同階層に生成される `.xmp` ファイル

---

## 動作環境

* macOS (Apple Silicon / M1)
* Python 3.10+
* 使用ライブラリ
  `rawpy`, `Pillow`, `torch`, `torchvision`, `scikit-learn`, `numpy`

---

## 目的

大量の RAW 写真を自動的に分類し、Lightroom で「AI が判定した似たグループ」を
キーワードとして利用できるようにすることで、人手での仕分け作業を大幅に軽減する。

# 使用技術

* Python 3.10+
* uv

---

## ディレクトリ構造（DDDレイヤー化アーキテクチャ）

```
raw-clusterer/
├── src/
│   ├── domain/                      # ドメイン層：ビジネスロジック・ドメインモデル
│   │   ├── models/                  # エンティティ・値オブジェクト
│   │   │   ├── raw_image.py         # RAW画像エンティティ
│   │   │   ├── thumbnail.py         # サムネイルエンティティ
│   │   │   ├── embedding.py         # 埋め込みベクトル値オブジェクト
│   │   │   ├── cluster.py           # クラスタエンティティ
│   │   │   └── xmp_metadata.py      # XMPメタデータエンティティ
│   │   ├── repositories/            # リポジトリインターフェース
│   │   │   ├── raw_image_repository.py
│   │   │   ├── thumbnail_repository.py
│   │   │   ├── embedding_repository.py
│   │   │   ├── cluster_repository.py
│   │   │   └── xmp_repository.py
│   │   └── services/                # ドメインサービス
│   │       ├── clustering_service.py    # クラスタリングロジック
│   │       └── feature_extraction_service.py  # 特徴抽出ロジック
│   │
│   ├── application/                 # アプリケーション層：ユースケース
│   │   ├── use_cases/
│   │   │   ├── generate_thumbnails.py       # サムネイル生成ユースケース
│   │   │   ├── extract_features.py          # 特徴量抽出ユースケース
│   │   │   ├── cluster_images.py            # クラスタリングユースケース
│   │   │   ├── update_xmp_metadata.py       # XMP更新ユースケース
│   │   │   └── organize_raw_images.py       # 全体orchestration
│   │   └── dto/                     # データ転送オブジェクト
│   │       └── cluster_result.py
│   │
│   ├── infrastructure/              # インフラ層：外部依存実装
│   │   ├── repositories/            # リポジトリ実装
│   │   │   ├── file_raw_image_repository.py
│   │   │   ├── file_thumbnail_repository.py
│   │   │   ├── numpy_embedding_repository.py
│   │   │   ├── json_cluster_repository.py
│   │   │   └── file_xmp_repository.py
│   │   ├── ml/                      # 機械学習関連実装
│   │   │   ├── models/
│   │   │   │   ├── resnet_model.py
│   │   │   │   └── clip_model.py
│   │   │   └── clustering/
│   │   │       ├── kmeans_clusterer.py
│   │   │       └── hdbscan_clusterer.py
│   │   ├── converters/              # 変換処理
│   │   │   └── raw_to_jpeg_converter.py
│   │   └── file_system/             # ファイルシステム操作
│   │       └── directory_scanner.py
│   │
│   └── ui/                          # UI層：ユーザーインターフェース
│       ├── cli/                     # CLIインターフェース
│       │   ├── main.py              # エントリーポイント
│       │   ├── commands/
│       │   │   └── organize_command.py
│       │   └── presenters/          # 出力フォーマッター
│       │       └── console_presenter.py
│       └── config/                  # 設定管理
│           └── app_config.py
│
├── tests/                           # テストコード（層構造に対応）
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── ui/
│
├── outputs/                         # 生成物（gitignore対象）
│   ├── thumbs/
│   ├── embeddings.npy
│   ├── meta.json
│   └── clusters.json
│
├── pyproject.toml
├── uv.lock
└── README.md
```

### 各層の責務

#### Domain層（ドメイン層）
- ビジネスロジックとドメインモデルを定義
- 外部依存を持たず、純粋なビジネスルールのみ
- リポジトリはインターフェースのみ定義

#### Application層（アプリケーション層）
- ユースケースの実装
- ドメインオブジェクトを組み合わせて処理フローを制御
- トランザクション境界の管理

#### Infrastructure層（インフラ層）
- 外部ライブラリやフレームワークへの依存を集約
- リポジトリの具体実装
- ML モデル、ファイルI/O、データ永続化の実装

#### UI層（ユーザーインターフェース層）
- CLIインターフェースの実装
- ユーザー入力の受付と出力の整形
- Applicationレイヤーへの処理依頼

---

## 使用方法

### インストール

```bash
# 依存関係のインストール
uv sync

# 開発用依存関係も含める場合
uv sync --extra dev
```

### 基本的な使い方

```bash
# RAW画像が含まれるディレクトリを指定
uv run python -m src.ui.cli.main /path/to/raw_images
```

### オプション

```bash
# サムネイルサイズを指定（デフォルト: 512px）
uv run python -m src.ui.cli.main /path/to/raw_images --size 512

# クラスタ数を指定
uv run python -m src.ui.cli.main /path/to/raw_images \
  --clusters-fine 50 \    # 詳細度1のクラスタ数（デフォルト: 50）
  --clusters-coarse 25    # 詳細度2のクラスタ数（デフォルト: 25）

# 出力先を指定
uv run python -m src.ui.cli.main /path/to/raw_images --output /path/to/output

# Dry runモード（XMPファイルを実際には書き込まない）
uv run python -m src.ui.cli.main /path/to/raw_images --dry-run
```

### 処理フロー

1. **サムネイル生成**: RAW画像をJPEG（512px）に変換
2. **特徴抽出**: ResNet50で2048次元の特徴ベクトルを抽出
3. **クラスタリング（詳細度1）**: ほぼ同じ被写体を細かく分類
4. **クラスタリング（詳細度2）**: 同じ場所・似た被写体を粗く分類
5. **XMP生成**: RAW画像と同階層にXMPファイルを作成

### 出力ファイル

```
/path/to/raw_images/
├── DSC00001.ARW        # 元のRAW画像
├── DSC00001.xmp        # ← 生成されたXMPファイル
├── DSC00002.ARW
├── DSC00002.xmp
└── ...

outputs/ (または --output で指定したディレクトリ)
├── thumbs/             # サムネイル画像
│   ├── DSC00001.jpg
│   └── ...
├── embeddings.npy      # 特徴ベクトル
├── meta.json           # メタデータ
├── clusters_fine.json  # 詳細度1のクラスタ結果
└── clusters_coarse.json # 詳細度2のクラスタ結果
```

### Lightroomでの使用

1. Lightroom Classicを開く
2. XMPファイルが生成されたディレクトリをカタログに追加
3. メニューから **メタデータ → メタデータをファイルから読み込み** を選択
4. キーワードリストで **AI/cluster** を確認
   - `AI/cluster/fine/001`, `AI/cluster/fine/002`, ...
   - `AI/cluster/coarse/001`, `AI/cluster/coarse/002`, ...
5. キーワードで絞り込んで似た写真をまとめて確認・選別

### テスト

```bash
# テストデータのセットアップ（32枚のRAW画像をコピー）
uv run python scripts/setup_test_data.py

# フルパイプラインテスト
uv run python scripts/tests/test_full_pipeline.py

# XMP生成テスト
uv run python scripts/tests/test_xmp_generation.py
```

詳細は[scripts/README.md](scripts/README.md)を参照してください。
