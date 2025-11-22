"""サムネイルリポジトリのインターフェース"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.domain.models.thumbnail import Thumbnail


class ThumbnailRepository(ABC):
    """サムネイルリポジトリのインターフェース"""

    @abstractmethod
    def save(self, thumbnail: Thumbnail) -> None:
        """サムネイルを保存

        Args:
            thumbnail: 保存するサムネイル
        """
        pass

    @abstractmethod
    def find_all(self, directory: Path) -> List[Thumbnail]:
        """指定ディレクトリ以下のサムネイルを全て取得

        Args:
            directory: 検索対象のディレクトリパス

        Returns:
            サムネイルのリスト
        """
        pass

    @abstractmethod
    def exists(self, thumbnail: Thumbnail) -> bool:
        """サムネイルが存在するか確認

        Args:
            thumbnail: 確認するサムネイル

        Returns:
            存在する場合True
        """
        pass
