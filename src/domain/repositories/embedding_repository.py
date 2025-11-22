"""埋め込みベクトルリポジトリのインターフェース"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.domain.models.embedding import Embedding


class EmbeddingRepository(ABC):
    """埋め込みベクトルリポジトリのインターフェース"""

    @abstractmethod
    def save_all(self, embeddings: List[Embedding], output_path: Path) -> None:
        """埋め込みベクトルを一括保存

        Args:
            embeddings: 保存する埋め込みベクトルのリスト
            output_path: 出力先パス
        """
        pass

    @abstractmethod
    def load_all(self, input_path: Path) -> List[Embedding]:
        """埋め込みベクトルを一括読み込み

        Args:
            input_path: 読み込み元パス

        Returns:
            埋め込みベクトルのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
        """
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """埋め込みベクトルファイルが存在するか確認

        Args:
            path: 確認するパス

        Returns:
            存在する場合True
        """
        pass
