"""画像クラスタリングユースケース"""

from pathlib import Path
from typing import List

import numpy as np

from src.application.dto.cluster_result import ClusterResult
from src.domain.models.cluster import Cluster
from src.domain.models.embedding import Embedding
from src.domain.repositories.cluster_repository import ClusterRepository
from src.domain.services.clustering_service import ClusteringService


class ClusterImages:
    """画像をクラスタリングするユースケース"""

    def __init__(
        self,
        clustering_service: ClusteringService,
        cluster_repository: ClusterRepository,
    ) -> None:
        """画像クラスタリングユースケースを初期化

        Args:
            clustering_service: クラスタリングサービス
            cluster_repository: クラスタリポジトリ
        """
        self._clustering_service = clustering_service
        self._cluster_repository = cluster_repository

    def execute(
        self, embeddings: List[Embedding], granularity: int, output_path: Path
    ) -> ClusterResult:
        """埋め込みベクトルをクラスタリング

        Args:
            embeddings: 埋め込みベクトルのリスト
            granularity: 詳細度レベル（1: 細かい、2: 粗い）
            output_path: クラスタ結果の出力先ファイルパス

        Returns:
            クラスタリング結果
        """
        print(f"\nClustering {len(embeddings)} images...")
        print(f"Granularity: {granularity} (1=fine, 2=coarse)")
        print(f"Number of clusters: {self._clustering_service.get_n_clusters()}")

        # 埋め込みベクトルを2次元配列に変換
        vectors = np.array([emb.vector for emb in embeddings])

        # クラスタリング実行
        labels = self._clustering_service.fit_predict(vectors)

        # Clusterオブジェクトを構築
        clusters: List[Cluster] = []
        unique_labels = np.unique(labels)

        for label in unique_labels:
            # このクラスタに属する画像IDを取得
            indices = np.where(labels == label)[0]
            image_ids = [embeddings[i].image_id for i in indices]

            cluster = Cluster(
                cluster_id=int(label), image_ids=image_ids, granularity=granularity
            )
            clusters.append(cluster)

        # クラスタを保存
        self._cluster_repository.save_all(clusters, output_path)
        print(f"Saved {len(clusters)} clusters to {output_path}")

        # 統計情報を表示
        cluster_sizes = [cluster.size for cluster in clusters]
        print(f"\nCluster statistics:")
        print(f"  Min size: {min(cluster_sizes)}")
        print(f"  Max size: {max(cluster_sizes)}")
        print(f"  Average size: {np.mean(cluster_sizes):.1f}")

        # ClusterResultを返す
        return ClusterResult(clusters=clusters, granularity=granularity)
