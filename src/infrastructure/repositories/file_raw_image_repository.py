"""ファイルシステムベースのRAW画像リポジトリ実装"""

from pathlib import Path
from typing import List

from src.domain.models.raw_image import RawImage
from src.domain.repositories.raw_image_repository import RawImageRepository
from src.infrastructure.file_system.directory_scanner import DirectoryScanner


class FileRawImageRepository(RawImageRepository):
    """ファイルシステムを使用したRAW画像リポジトリの実装"""

    def __init__(self) -> None:
        """ファイルベースRAW画像リポジトリを初期化"""
        self._scanner = DirectoryScanner(extensions=RawImage.SUPPORTED_FORMATS)

    def find_all(self, directory: Path) -> List[RawImage]:
        """指定ディレクトリ以下のRAW画像を全て取得

        Args:
            directory: 検索対象のディレクトリパス

        Returns:
            RAW画像のリスト
        """
        file_paths = self._scanner.scan(directory)
        raw_images: List[RawImage] = []

        for path in file_paths:
            try:
                raw_image = RawImage(path)
                raw_images.append(raw_image)
            except ValueError as e:
                # サポート外の形式などはスキップ
                print(f"Skipping file {path}: {e}")

        return raw_images

    def find_by_path(self, path: Path) -> RawImage:
        """パスを指定してRAW画像を取得

        Args:
            path: RAWファイルのパス

        Returns:
            RAW画像

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: サポート外の形式の場合
        """
        if not path.exists():
            raise FileNotFoundError(f"RAW file not found: {path}")

        return RawImage(path)
