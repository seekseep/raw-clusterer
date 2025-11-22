"""HDBSCANクラスタラー"""

import warnings
import numpy as np
from hdbscan import HDBSCAN

from src.domain.services.clustering_service import ClusteringService

# hdbscanライブラリ内部のsklearn非推奨警告を抑制
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.utils.deprecation")


class HDBSCANClusterer(ClusteringService):
    """HDBSCANを使用したクラスタリングサービス

    データの密度に基づいて自動的にクラスタ数を決定します。
    KMeansと異なり、事前にクラスタ数を指定する必要がありません。
    """

    def __init__(
        self,
        min_cluster_size: int = 5,
        min_samples: int = 3,
        cluster_selection_epsilon: float = 0.0,
        metric: str = "euclidean",
    ) -> None:
        """HDBSCANクラスタラーを初期化

        Args:
            min_cluster_size: クラスタとみなす最小サンプル数
            min_samples: コアポイントとみなすための近傍サンプル数
            cluster_selection_epsilon: クラスタ選択の閾値（0.0で自動）
            metric: 距離メトリック
        """
        self._min_cluster_size = min_cluster_size
        self._min_samples = min_samples
        self._model = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            cluster_selection_epsilon=cluster_selection_epsilon,
            metric=metric,
        )
        self._n_clusters = 0  # fit後に設定される

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """クラスタリングを実行してラベルを予測

        Args:
            vectors: 特徴ベクトル（N x D の2次元配列、N:サンプル数、D:次元数）

        Returns:
            クラスタラベル（N個の整数配列）
            ノイズポイントは -1 でラベリングされます

        Raises:
            ValueError: 入力が2次元配列でない場合
        """
        if vectors.ndim != 2:
            raise ValueError(f"Vectors must be 2-dimensional, got {vectors.ndim}")

        labels = self._model.fit_predict(vectors)

        # ノイズ（-1）を除いたクラスタ数を計算
        unique_labels = np.unique(labels)
        self._n_clusters = len(unique_labels[unique_labels >= 0])

        # ノイズポイントを最も近いクラスタに割り当て
        if -1 in labels:
            labels = self._reassign_noise(vectors, labels)

        return labels

    def _reassign_noise(self, vectors: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """ノイズポイントを最も近いクラスタに再割り当て

        Args:
            vectors: 特徴ベクトル
            labels: クラスタラベル（ノイズは-1）

        Returns:
            再割り当て後のラベル
        """
        noise_mask = labels == -1
        if not noise_mask.any():
            return labels

        # クラスタの中心を計算
        unique_labels = np.unique(labels[labels >= 0])
        if len(unique_labels) == 0:
            # 全てノイズの場合は全て0に割り当て
            return np.zeros_like(labels)

        centroids = np.array([
            vectors[labels == label].mean(axis=0)
            for label in unique_labels
        ])

        # ノイズポイントを最も近い中心に割り当て
        noise_vectors = vectors[noise_mask]
        distances = np.linalg.norm(
            noise_vectors[:, np.newaxis] - centroids[np.newaxis, :],
            axis=2
        )
        closest_clusters = unique_labels[distances.argmin(axis=1)]

        labels[noise_mask] = closest_clusters
        return labels

    def get_n_clusters(self) -> int:
        """クラスタ数を取得

        Returns:
            クラスタ数（fit_predict実行後の値）
        """
        return self._n_clusters