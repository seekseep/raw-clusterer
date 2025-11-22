# RAW Clusterer

AIによるRAW画像の自動分類ツール

## 目的

大量のRAW写真を自動的に分類し、Adobe Lightroom Classicで「AIが判定した似たグループ」をキーワードとして利用できるようにすることで、人手での仕分け作業を大幅に軽減します。

## できること

1. **RAW画像のサムネイル生成**
   指定したディレクトリ以下のRAW画像（CR2, CR3, NEF, ARW, RAF, DNGなど）を自動検出し、JPEG（512px）サムネイルを生成します。

2. **AI自動クラスタリング**
   ResNet50で画像の特徴を抽出し、似た写真をグループ化します。HDBSCANによる自動クラスタリング、またはKMeansで指定したクラスタ数での分類が可能です。

3. **Lightroom用XMPタグ付け**
   各RAW画像と同じ場所にXMPファイルを生成し、階層キーワード（`AI/cluster/fine/001`など）を付与します。Lightroomで「メタデータをファイルから読み込み」を実行すると、クラスタごとに写真を絞り込めます。

---

## インストール方法

### 1. リポジトリをクローン

```bash
git clone https://github.com/seekseep/raw-clusterer.git
cd raw-clusterer
```

### 2. 依存関係をインストール

```bash
uv sync
```

### 3. 実行ファイルを準備

```bash
chmod +x bin/raw-clusterer
```

### 4. パスを通す（オプション）

コマンドをどこからでも実行できるようにします：

```bash
# シンボリックリンクを作成
sudo ln -s "$(pwd)/bin/raw-clusterer" /usr/local/bin/raw-clusterer
```

または、`.zshrc`や`.bashrc`にPATHを追加：

```bash
export PATH="$PATH:/path/to/raw-clusterer/bin"
```

---

## 使い方

### 基本的な使い方（推奨）

```bash
raw-clusterer . --min-cluster-size 2 --min-samples 1
```

カレントディレクトリのRAW画像を処理します。以下の処理が自動実行されます：

1. サムネイル生成
2. 特徴抽出
3. クラスタリング（HDBSCANで自動）
4. XMPファイル生成

※ `--min-cluster-size 2 --min-samples 1` により、少数の写真でも効果的にクラスタリングできます。

### よく使うオプション

```bash
# 別のディレクトリを指定
raw-clusterer /path/to/raw_images --min-cluster-size 2 --min-samples 1

# KMeansでクラスタ数を指定（細かい分類50個、粗い分類25個）
raw-clusterer . --algorithm kmeans --clusters-fine 50 --clusters-coarse 25

# HDBSCANのパラメータ調整（より大きなクラスタを作る）
raw-clusterer . --min-cluster-size 10 --min-samples 5

# XMPを書き込まずに結果だけ確認
raw-clusterer . --min-cluster-size 2 --min-samples 1 --dry-run

# 出力先を変更
raw-clusterer . --min-cluster-size 2 --min-samples 1 --output /path/to/output
```

### 全オプション

```
usage: raw-clusterer [-h] [--size SIZE] [--output OUTPUT]
                     [--algorithm {kmeans,hdbscan}]
                     [--clusters-fine CLUSTERS_FINE]
                     [--clusters-coarse CLUSTERS_COARSE]
                     [--min-cluster-size MIN_CLUSTER_SIZE]
                     [--min-samples MIN_SAMPLES]
                     [--dry-run] [--model {resnet50}]
                     directory

オプション:
  --size SIZE                   サムネイルサイズ（デフォルト: 512）
  --output OUTPUT               出力先ディレクトリ
  --algorithm {kmeans,hdbscan}  アルゴリズム（デフォルト: hdbscan）
  --clusters-fine CLUSTERS_FINE クラスタ数（細）（デフォルト: 50、KMeansのみ）
  --clusters-coarse CLUSTERS_COARSE クラスタ数（粗）（デフォルト: 25、KMeansのみ）
  --min-cluster-size            HDBSCANの最小クラスタサイズ（デフォルト: 5）
  --min-samples                 HDBSCANの最小サンプル数（デフォルト: 3）
  --dry-run                     XMPを書き込まない（確認用）
  --model {resnet50}            特徴抽出モデル（デフォルト: resnet50）
```

---

## Lightroomでの利用方法

1. Adobe Lightroom Classicを開く
2. RAW画像のフォルダをカタログに追加（XMPファイルが同じ階層にあると自動的に読み込まれます）
3. 左パネルの「キーワードリスト」に **AI/cluster** が表示されます
   - `AI/cluster/fine/001`, `AI/cluster/fine/002`, ...（細かい分類）
   - `AI/cluster/coarse/001`, `AI/cluster/coarse/002`, ...（粗い分類）
4. キーワードをクリックして絞り込み、似た写真をまとめて確認・選別できます

※ XMPファイルはRAW画像と同じディレクトリに自動生成されるため、Lightroomが自動的に認識します。手動でメタデータを読み込む必要はありません。

---

## 出力ファイル

```
/path/to/raw_images/
├── DSC00001.ARW        # 元のRAW画像
├── DSC00001.xmp        # ← 生成されたXMPファイル
├── DSC00002.ARW
├── DSC00002.xmp
└── ...

.raw_clusterer_cache/ （または --output で指定したディレクトリ）
├── thumbs/             # サムネイル画像
├── embeddings.npy      # 特徴ベクトル
├── meta.json           # メタデータ
├── clusters_fine.json  # 詳細クラスタ結果
└── clusters_coarse.json # 粗いクラスタ結果
```

---

## 動作環境

- macOS（Apple Silicon / M1推奨）
- Python 3.10以上
- 必要なライブラリ：rawpy, Pillow, PyTorch, scikit-learn, HDBSCAN

---

# 技術詳細

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

## 処理フロー

1. **サムネイル生成**: RAW画像をJPEG（512px）に変換
2. **特徴抽出**: ResNet50で2048次元の特徴ベクトルを抽出
3. **クラスタリング（詳細）**: ほぼ同じ被写体を細かく分類
4. **クラスタリング（粗）**: 同じ場所・似た被写体を粗く分類
5. **XMP生成**: RAW画像と同階層にXMPファイルを作成

## 開発者向け情報

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

### 開発用依存関係のインストール

```bash
uv sync --extra dev
```
