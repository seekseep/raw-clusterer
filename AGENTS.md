# AI エージェント作業ガイドライン

## 必須事項

### TODO管理

**重要: 作業開始前に必ず [TODO.md](TODO.md) を参照し、最新の状態に更新すること**

- 作業開始時: TODO.mdから次のタスクを確認
- 作業中: 進捗状況をTODO.mdに反映
- 作業完了時: 完了したタスクを「完了したタスク」セクションに移動

### コミット規則

**重要: コミット実行は必ずユーザーが行う。AIエージェントはコミットメッセージの提案のみ行うこと。**

**各機能実装が完了したら、コミットメッセージを作成してユーザーに提示すること**

コミットメッセージのフォーマット:
```
<type>: <subject>

<body>
```

#### Type一覧
- `feat`: 新機能の追加
- `fix`: バグ修正
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `docs`: ドキュメント更新
- `chore`: ビルド、設定ファイルなどの更新

#### 例
```
feat: RAWファイルをJPEGサムネイルに変換する機能を実装

- RawImageエンティティとThumbnailエンティティを作成
- RawToJpegConverterでrawpyとPillowを使用した変換処理を実装
- GenerateThumbnailsユースケースで一括変換フローを構築
```

**コミット単位**: TODO.mdの各大項目（1, 2, 3...）が完了したタイミング

---

## コードフォーマット規則（厳守）

### Pythonコードスタイル

**必ず以下のルールを遵守すること:**

#### 1. フォーマッター
- **Black** を使用（行幅: 100文字）
- **isort** を使用（import文の自動整理）

#### 2. 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| **関数名** | snake_case | `generate_thumbnails()`, `extract_features()` |
| **変数名** | snake_case | `raw_image`, `cluster_id`, `embedding_vector` |
| **クラス名** | PascalCase | `RawImage`, `ThumbnailRepository`, `ClusteringService` |
| **定数** | UPPER_SNAKE_CASE | `MAX_CLUSTERS`, `DEFAULT_THUMBNAIL_SIZE` |
| **プライベートメソッド** | _snake_case | `_validate_path()`, `_convert_color_space()` |
| **プライベート変数** | _snake_case | `_cache`, `_model` |

#### 3. 型ヒント

**必須: すべての関数とメソッドに型ヒントを付与**

```python
from pathlib import Path
from typing import List, Optional

def generate_thumbnail(
    raw_path: Path,
    output_path: Path,
    size: int = 512
) -> Optional[Path]:
    """RAW画像からサムネイルを生成する

    Args:
        raw_path: RAWファイルのパス
        output_path: 出力先のパス
        size: サムネイルの長辺サイズ

    Returns:
        成功時は出力パス、失敗時はNone
    """
    pass
```

#### 4. Docstring

**必須: すべての公開関数・クラス・メソッドにdocstringを記載**

フォーマット: **Google Style**

```python
class RawImage:
    """RAW画像を表すエンティティ

    Attributes:
        path: RAWファイルのパス
        format: RAWファイルの形式（CR2, NEF等）
        created_at: 作成日時
    """

    def __init__(self, path: Path) -> None:
        """RAW画像エンティティを初期化

        Args:
            path: RAWファイルのパス

        Raises:
            ValueError: パスが存在しない場合
        """
        pass
```

#### 5. インポート順序

isortに従う（以下の順序）:

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルアプリケーション/ライブラリ

```python
# 標準ライブラリ
from pathlib import Path
from typing import List, Optional

# サードパーティ
import numpy as np
from PIL import Image

# ローカル
from src.domain.models.raw_image import RawImage
from src.domain.repositories.thumbnail_repository import ThumbnailRepository
```

#### 6. その他

- 1行の最大文字数: **100文字**
- インデント: **スペース4つ**
- 文字列リテラル: ダブルクォート `"` を優先
- 末尾カンマ: 複数行のリスト・辞書には付与

---

## アーキテクチャ責任範囲

### DDDレイヤーの責務（厳守）

#### Domain層
**責任範囲:**
- ビジネスロジックとドメインルールの定義
- エンティティ、値オブジェクトの実装
- リポジトリ**インターフェースのみ**定義（実装はInfrastructure層）
- ドメインサービス（複数エンティティにまたがるロジック）

**禁止事項:**
- 外部ライブラリ（rawpy, Pillow, torch等）への直接依存
- ファイルI/O処理
- データベースアクセス

**例:**
```python
# ✅ OK: 純粋なドメインロジック
class Cluster:
    def __init__(self, cluster_id: int, image_ids: List[str]) -> None:
        if cluster_id < 0:
            raise ValueError("cluster_id must be non-negative")
        self.cluster_id = cluster_id
        self.image_ids = image_ids

    def add_image(self, image_id: str) -> None:
        """画像をクラスタに追加"""
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)

# ❌ NG: 外部ライブラリへの依存
class Cluster:
    def save_to_json(self, path: Path) -> None:  # Infrastructure層の責務
        import json
        with open(path, "w") as f:
            json.dump(self.__dict__, f)
```

#### Application層
**責任範囲:**
- ユースケースの実装（ビジネスフローの制御）
- ドメインオブジェクトの組み合わせ
- トランザクション境界の管理
- リポジトリ（インターフェース）の使用

**禁止事項:**
- リポジトリの具体的な実装（Infrastructure層の責務）
- UI表示ロジック

**例:**
```python
# ✅ OK: ユースケースとして適切
class GenerateThumbnails:
    def __init__(
        self,
        raw_repository: RawImageRepository,  # インターフェース
        thumbnail_repository: ThumbnailRepository,  # インターフェース
        converter: RawToJpegConverter  # Infrastructure層の実装
    ) -> None:
        self._raw_repository = raw_repository
        self._thumbnail_repository = thumbnail_repository
        self._converter = converter

    def execute(self, directory: Path) -> List[Thumbnail]:
        """指定ディレクトリのRAW画像からサムネイルを生成"""
        raw_images = self._raw_repository.find_all(directory)
        thumbnails = []

        for raw_image in raw_images:
            thumbnail = self._converter.convert(raw_image)
            self._thumbnail_repository.save(thumbnail)
            thumbnails.append(thumbnail)

        return thumbnails
```

#### Infrastructure層
**責任範囲:**
- リポジトリの具体的な実装
- 外部ライブラリ（rawpy, Pillow, torch等）との連携
- ファイルI/O処理
- MLモデルのラッパー実装

**禁止事項:**
- ビジネスロジックの実装（Domain層の責務）

**例:**
```python
# ✅ OK: 外部ライブラリを使った具体実装
class RawToJpegConverter:
    def convert(self, raw_image: RawImage, size: int = 512) -> Thumbnail:
        """RAW画像をJPEGサムネイルに変換"""
        import rawpy
        from PIL import Image

        with rawpy.imread(str(raw_image.path)) as raw:
            rgb = raw.postprocess()

        img = Image.fromarray(rgb)
        img.thumbnail((size, size))

        output_path = self._get_output_path(raw_image.path)
        img.save(output_path, "JPEG")

        return Thumbnail(path=output_path, source=raw_image)
```

#### UI層
**責任範囲:**
- ユーザー入力の受付
- 出力の整形と表示
- Applicationレイヤーへの処理依頼
- CLI引数のパース

**禁止事項:**
- ビジネスロジックの実装
- データ永続化処理

**例:**
```python
# ✅ OK: UIとして適切
class OrganizeCommand:
    def __init__(self, use_case: OrganizeRawImages) -> None:
        self._use_case = use_case

    def execute(self, args: argparse.Namespace) -> None:
        """CLIコマンドを実行"""
        result = self._use_case.execute(
            directory=Path(args.directory),
            thumbnail_size=args.size,
            num_clusters=args.clusters
        )

        # 結果を整形して出力
        ConsolePresenter.show_result(result)
```

---

## 作業フロー

1. **TODO.mdを確認** → 次のタスクを把握
2. **設計** → 責任範囲を意識してクラス・関数を設計
3. **実装** → コードフォーマット規則を厳守
4. **テスト** → 単体テストを作成・実行
5. **TODO.md更新** → 完了タスクを移動
6. **コミットメッセージ提案** → 適切なコミットメッセージを作成してユーザーに提示（コミット実行はユーザーが行う）

---

## チェックリスト（実装前に確認）

- [ ] TODO.mdを参照したか？
- [ ] 実装する層の責任範囲を理解したか？
- [ ] 関数名・変数名はsnake_caseか？
- [ ] クラス名はPascalCaseか？
- [ ] 型ヒントを付与したか？
- [ ] Docstringを記載したか？
- [ ] 外部ライブラリへの依存は適切な層か？
- [ ] テストを作成したか？
- [ ] 作業完了後にコミットメッセージを提案したか？

---

## 検証用ディレクトリ

**以下のディレクトリを検証・テストに使用可能:**

- `/Users/seekseep/Pictures/レタッチ/20251112_兵庫前期`
- `/Users/seekseep/Pictures/レタッチ/20251117_兵庫後期`

**重要: ファイル削除の禁止**

- **絶対にファイルやディレクトリの削除を行わないこと**
- 読み取りと新規ファイル作成のみ許可
- 既存ファイルの上書きも慎重に行うこと

---

## 参考リンク

- [TODO.md](TODO.md) - タスク管理
- [README.md](README.md) - プロジェクト概要とディレクトリ構造
- Black: https://black.readthedocs.io/
- isort: https://pycqa.github.io/isort/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
