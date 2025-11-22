"""RAW画像エンティティ"""

from pathlib import Path
from typing import Optional


class RawImage:
    """RAW画像を表すエンティティ

    Attributes:
        path: RAWファイルのパス
        format: RAWファイルの形式（CR2, NEF等）
    """

    SUPPORTED_FORMATS = {".cr2", ".cr3", ".nef", ".arw", ".raf", ".dng"}

    def __init__(self, path: Path) -> None:
        """RAW画像エンティティを初期化

        Args:
            path: RAWファイルのパス

        Raises:
            ValueError: パスが存在しない、またはサポート外の形式の場合
        """
        if not path.exists():
            raise ValueError(f"RAW file does not exist: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        file_format = path.suffix.lower()
        if file_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported RAW format: {file_format}. "
                f"Supported formats: {self.SUPPORTED_FORMATS}"
            )

        self.path = path
        self.format = file_format

    @property
    def filename(self) -> str:
        """ファイル名を取得"""
        return self.path.name

    @property
    def stem(self) -> str:
        """拡張子なしのファイル名を取得"""
        return self.path.stem

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, RawImage):
            return False
        return self.path == other.path

    def __hash__(self) -> int:
        """ハッシュ値を取得"""
        return hash(self.path)

    def __repr__(self) -> str:
        """文字列表現"""
        return f"RawImage(path={self.path}, format={self.format})"
