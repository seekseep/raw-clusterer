"""MiniBatchKMeansクラスタラー"""

import numpy as np
from sklearn.cluster import MiniBatchKMeans

from src.domain.services.clustering_service import ClusteringService


class KMeansClusterer(ClusteringService):
    """MiniBatchKMeansを使用したクラスタリングサービス"""

    def __init__(
        self,
        n_clusters: int,
        batch_size: int = 256,
        random_state: int = 42,
    ) -> None:
        """KMeansクラスタラーを初期化

        Args:
            n_clusters: クラスタ数
            batch_size: MiniBatchKMeansのバッチサイズ
            random_state: 乱数シード
        """
        self._n_clusters = n_clusters
        self._model = MiniBatchKMeans(
            n_clusters=n_clusters,
            batch_size=batch_size,
            random_state=random_state,
            n_init=10,
        )

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """クラスタリングを実行してラベルを予測

        Args:
            vectors: 特徴ベクトル（N x D の2次元配列、N:サンプル数、D:次元数）

        Returns:
            クラスタラベル（N個の整数配列）

        Raises:
            ValueError: 入力が2次元配列でない場合
        """
        if vectors.ndim != 2:
            raise ValueError(f"Vectors must be 2-dimensional, got {vectors.ndim}")

        labels = self._model.fit_predict(vectors)
        return labels

    def get_n_clusters(self) -> int:
        """クラスタ数を取得

        Returns:
            クラスタ数
        """
        return self._n_clusters
