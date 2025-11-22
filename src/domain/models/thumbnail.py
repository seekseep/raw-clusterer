"""サムネイル画像エンティティ"""

from pathlib import Path
from typing import Optional

from src.domain.models.raw_image import RawImage


class Thumbnail:
    """サムネイル画像を表すエンティティ

    Attributes:
        path: サムネイル画像ファイルのパス
        source: 元のRAW画像
        size: サムネイルのサイズ（長辺のピクセル数）
    """

    def __init__(self, path: Path, source: RawImage, size: Optional[int] = None) -> None:
        """サムネイルエンティティを初期化

        Args:
            path: サムネイル画像ファイルのパス
            source: 元のRAW画像
            size: サムネイルのサイズ（長辺のピクセル数）
        """
        self.path = path
        self.source = source
        self.size = size

    @property
    def filename(self) -> str:
        """ファイル名を取得"""
        return self.path.name

    @property
    def exists(self) -> bool:
        """サムネイルファイルが存在するか確認"""
        return self.path.exists()

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, Thumbnail):
            return False
        return self.path == other.path and self.source == other.source

    def __hash__(self) -> int:
        """ハッシュ値を取得"""
        return hash((self.path, self.source))

    def __repr__(self) -> str:
        """文字列表現"""
        return f"Thumbnail(path={self.path}, source={self.source.path}, size={self.size})"
