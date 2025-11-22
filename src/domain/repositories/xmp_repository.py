"""XMPリポジトリのインターフェース"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src.domain.models.xmp_metadata import XmpMetadata


class XmpRepository(ABC):
    """XMPリポジトリのインターフェース"""

    @abstractmethod
    def load(self, xmp_path: Path) -> Optional[XmpMetadata]:
        """XMPファイルを読み込み

        Args:
            xmp_path: XMPファイルのパス

        Returns:
            XMPメタデータ、ファイルが存在しない場合はNone
        """
        pass

    @abstractmethod
    def save(self, xmp_metadata: XmpMetadata) -> None:
        """XMPメタデータを保存

        Args:
            xmp_metadata: 保存するXMPメタデータ
        """
        pass

    @abstractmethod
    def exists(self, xmp_path: Path) -> bool:
        """XMPファイルが存在するか確認

        Args:
            xmp_path: XMPファイルのパス

        Returns:
            存在する場合True
        """
        pass
