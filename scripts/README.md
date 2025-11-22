# スクリプト

## セットアップ

### テストデータの準備

```bash
uv run python scripts/setup_test_data.py
```

32枚のRAW画像を`test_data/raw_images/`にコピーします。

## テストスクリプト

### 1. 単一ファイル変換テスト

```bash
uv run python scripts/tests/test_single.py
```

1枚のRAW画像をJPEGに変換するシンプルなテスト。

### 2. ネストしたディレクトリ構造テスト

```bash
uv run python scripts/tests/test_nested_dir.py
```

ネストしたディレクトリ構造での相対パス保持を確認するテスト。

### 3. クラスタリング機能テスト

```bash
uv run python scripts/tests/test_clustering.py
```

10枚の画像でクラスタリング機能を検証するテスト。

### 4. フルパイプライン統合テスト（推奨）

```bash
uv run python scripts/tests/test_full_pipeline.py
```

32枚のテストデータを使用した完全な統合テスト：

1. RAW → JPEGサムネイル生成
2. ResNet50による特徴抽出
3. 詳細度1（Fine）でクラスタリング（8クラスタ）
4. 詳細度2（Coarse）でクラスタリング（4クラスタ）
5. タグ表示

**出力例:**

```
フルパイプライン統合テスト（32枚のテストデータ）
==================================================================

[Step 1/5] サムネイル生成
Generated 32 thumbnails

[Step 2/5] 特徴抽出（ResNet50）
Extracted 32 feature vectors (2048次元)

[Step 3/5] クラスタリング - 詳細度1（Fine: ほぼ同じ被写体）
Number of clusters: 8

[Step 4/5] クラスタリング - 詳細度2（Coarse: 同じ場所・似た被写体）
Number of clusters: 4

[Step 5/5] 生成されたタグ
DSC00762: ai_cluster_fine_001, ai_cluster_coarse_002
...
```

## ディレクトリ構造

```
scripts/
├── README.md              # このファイル
├── setup_test_data.py     # テストデータセットアップ
└── tests/
    ├── test_single.py           # 単一ファイルテスト
    ├── test_nested_dir.py       # ネスト構造テスト
    ├── test_clustering.py       # クラスタリングテスト
    └── test_full_pipeline.py    # 統合テスト（推奨）
```

## 出力先

すべてのテストスクリプトは`outputs/`以下に結果を出力します：

- `outputs/test_single/` - 単一ファイルテスト
- `outputs/test_nested/` - ネスト構造テスト
- `outputs/test_clustering/` - クラスタリングテスト
- `outputs/test_full_pipeline/` - 統合テスト
