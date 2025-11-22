"""RAW画像リポジトリのインターフェース"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.domain.models.raw_image import RawImage


class RawImageRepository(ABC):
    """RAW画像リポジトリのインターフェース"""

    @abstractmethod
    def find_all(self, directory: Path) -> List[RawImage]:
        """指定ディレクトリ以下のRAW画像を全て取得

        Args:
            directory: 検索対象のディレクトリパス

        Returns:
            RAW画像のリスト
        """
        pass

    @abstractmethod
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
        pass
