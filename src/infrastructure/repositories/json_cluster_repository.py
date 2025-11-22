"""JSON形式のクラスタリポジトリ"""

import json
from pathlib import Path
from typing import Dict, List

from src.domain.models.cluster import Cluster
from src.domain.repositories.cluster_repository import ClusterRepository


class JsonClusterRepository(ClusterRepository):
    """JSON形式でクラスタを保存・読み込むリポジトリ"""

    def save_all(self, clusters: List[Cluster], output_path: Path) -> None:
        """クラスタを一括保存

        Args:
            clusters: 保存するクラスタのリスト
            output_path: 出力先ファイルパス
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # クラスタをJSON形式に変換
        clusters_data = {
            "clusters": [
                {
                    "cluster_id": cluster.cluster_id,
                    "granularity": cluster.granularity,
                    "image_ids": cluster.image_ids,
                    "size": cluster.size,
                    "tag": cluster.get_tag(),
                    "hierarchical_tag": cluster.get_hierarchical_tag(),
                }
                for cluster in clusters
            ],
            "total_images": sum(cluster.size for cluster in clusters),
            "num_clusters": len(clusters),
        }

        with open(output_path, "w") as f:
            json.dump(clusters_data, f, indent=2)

    def load_all(self, input_path: Path) -> List[Cluster]:
        """クラスタを一括読み込み

        Args:
            input_path: 読み込み元ファイルパス

        Returns:
            クラスタのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Cluster file not found: {input_path}")

        with open(input_path, "r") as f:
            clusters_data = json.load(f)

        # Clusterオブジェクトのリストを構築
        clusters: List[Cluster] = []
        for cluster_info in clusters_data["clusters"]:
            cluster = Cluster(
                cluster_id=cluster_info["cluster_id"],
                image_ids=cluster_info["image_ids"],
                granularity=cluster_info["granularity"],
            )
            clusters.append(cluster)

        return clusters

    def get_image_to_cluster_map(
        self, clusters: List[Cluster]
    ) -> Dict[str, List[Cluster]]:
        """画像IDからクラスタへのマッピングを取得

        Args:
            clusters: クラスタのリスト

        Returns:
            画像ID -> クラスタリストの辞書
        """
        image_to_clusters: Dict[str, List[Cluster]] = {}

        for cluster in clusters:
            for image_id in cluster.image_ids:
                if image_id not in image_to_clusters:
                    image_to_clusters[image_id] = []
                image_to_clusters[image_id].append(cluster)

        return image_to_clusters
