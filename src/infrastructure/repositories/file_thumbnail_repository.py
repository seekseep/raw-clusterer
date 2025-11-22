"""ファイルシステムベースのサムネイルリポジトリ実装"""

from pathlib import Path
from typing import List

from src.domain.models.thumbnail import Thumbnail
from src.domain.repositories.thumbnail_repository import ThumbnailRepository


class FileThumbnailRepository(ThumbnailRepository):
    """ファイルシステムを使用したサムネイルリポジトリの実装"""

    def save(self, thumbnail: Thumbnail) -> None:
        """サムネイルを保存

        Note:
            実際の保存処理はRawToJpegConverterで行われるため、
            このメソッドは存在確認のみ実施

        Args:
            thumbnail: 保存するサムネイル
        """
        if not thumbnail.exists:
            raise ValueError(f"Thumbnail file does not exist: {thumbnail.path}")

    def find_all(self, directory: Path) -> List[Thumbnail]:
        """指定ディレクトリ以下のサムネイルを全て取得

        Args:
            directory: 検索対象のディレクトリパス

        Returns:
            サムネイルのリスト
        """
        if not directory.exists():
            return []

        thumbnails: List[Thumbnail] = []
        for path in directory.rglob("*.jpg"):
            if path.is_file():
                # Note: ここではsource情報が不明なため、簡易的な実装
                # 実際にはメタデータから復元する必要がある
                pass

        return thumbnails

    def exists(self, thumbnail: Thumbnail) -> bool:
        """サムネイルが存在するか確認

        Args:
            thumbnail: 確認するサムネイル

        Returns:
            存在する場合True
        """
        return thumbnail.exists
