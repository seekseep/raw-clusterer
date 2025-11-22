# インストールガイド

## 依存関係のインストール

```bash
# 依存関係のインストール
uv sync

# 開発用依存関係も含める場合
uv sync --extra dev
```

## パスを通す（オプション）

プロジェクトディレクトリのどこからでも`raw-clusterer`コマンドを実行できるようにします。

### 1. シンボリックリンクを作成（推奨）

```bash
# プロジェクトディレクトリで実行
sudo ln -s "$(pwd)/bin/raw-clusterer" /usr/local/bin/raw-clusterer
```

これで、どこからでも`raw-clusterer`コマンドが使えます：

```bash
# どこからでも実行可能
raw-clusterer /path/to/raw_images
raw-clusterer --help
```

### 2. PATHに追加（代替方法）

シェルの設定ファイル（`.bashrc`, `.zshrc`など）に以下を追加：

```bash
# raw-clustererをPATHに追加
export PATH="/Users/seekseep/Development/github.com/seekseep/raw-clusterer/bin:$PATH"
```

設定を反映：

```bash
# bashの場合
source ~/.bashrc

# zshの場合
source ~/.zshrc
```

### 3. エイリアスを作成（最も簡単）

シェルの設定ファイルに以下を追加：

```bash
# raw-clustererのエイリアス
alias raw-clusterer='/Users/seekseep/Development/github.com/seekseep/raw-clusterer/bin/raw-clusterer'
```

## 使用方法

### パスを通した場合

```bash
# シンプルに実行
raw-clusterer /path/to/raw_images

# オプション付き
raw-clusterer /path/to/raw_images --clusters-fine 50 --clusters-coarse 25
```

### パスを通していない場合

```bash
# プロジェクトディレクトリから相対パスで実行
./bin/raw-clusterer /path/to/raw_images

# または直接Pythonモジュールとして実行
uv run python -m src.ui.cli.main /path/to/raw_images
```

## アンインストール

### シンボリックリンクを削除

```bash
sudo rm /usr/local/bin/raw-clusterer
```

### PATHから削除

シェルの設定ファイルから追加した行を削除して、設定を再読み込み。

### エイリアスを削除

シェルの設定ファイルから追加した行を削除して、設定を再読み込み。
