"""クラスタリングドメインサービス

このサービスはインターフェースのみを定義し、
実際の実装はInfrastructure層で行う
"""

from abc import ABC, abstractmethod
from typing import List

import numpy as np


class ClusteringService(ABC):
    """埋め込みベクトルをクラスタリングするサービスのインターフェース"""

    @abstractmethod
    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """クラスタリングを実行してラベルを予測

        Args:
            vectors: 特徴ベクトル（N x D の2次元配列、N:サンプル数、D:次元数）

        Returns:
            クラスタラベル（N個の整数配列）

        Raises:
            ValueError: 入力が2次元配列でない場合
        """
        pass

    @abstractmethod
    def get_n_clusters(self) -> int:
        """クラスタ数を取得

        Returns:
            クラスタ数
        """
        pass
