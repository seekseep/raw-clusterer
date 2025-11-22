"""特徴抽出ドメインサービス

このサービスはインターフェースのみを定義し、
実際の実装はInfrastructure層で行う
"""

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class FeatureExtractionService(ABC):
    """画像から特徴ベクトルを抽出するサービスのインターフェース"""

    @abstractmethod
    def extract(self, image_path: Path) -> np.ndarray:
        """画像から特徴ベクトルを抽出

        Args:
            image_path: 画像ファイルのパス

        Returns:
            特徴ベクトル（1次元numpy配列）

        Raises:
            FileNotFoundError: 画像ファイルが存在しない場合
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """使用しているモデル名を取得

        Returns:
            モデル名
        """
        pass
