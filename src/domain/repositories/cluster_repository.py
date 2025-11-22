"""クラスタリポジトリのインターフェース"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from src.domain.models.cluster import Cluster


class ClusterRepository(ABC):
    """クラスタリポジトリのインターフェース"""

    @abstractmethod
    def save_all(self, clusters: List[Cluster], output_path: Path) -> None:
        """クラスタを一括保存

        Args:
            clusters: 保存するクラスタのリスト
            output_path: 出力先パス
        """
        pass

    @abstractmethod
    def load_all(self, input_path: Path) -> List[Cluster]:
        """クラスタを一括読み込み

        Args:
            input_path: 読み込み元パス

        Returns:
            クラスタのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
        """
        pass

    @abstractmethod
    def get_image_to_cluster_map(
        self, clusters: List[Cluster]
    ) -> Dict[str, List[Cluster]]:
        """画像IDからクラスタへのマッピングを取得

        Args:
            clusters: クラスタのリスト

        Returns:
            画像ID -> クラスタリストの辞書
        """
        pass
