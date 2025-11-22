"""クラスタリング結果DTO"""

from typing import Dict, List

from src.domain.models.cluster import Cluster


class ClusterResult:
    """クラスタリング結果を表すDTO

    Attributes:
        clusters: クラスタのリスト
        image_to_tags: 画像ID -> タグリストのマッピング
        granularity: 詳細度レベル
    """

    def __init__(self, clusters: List[Cluster], granularity: int) -> None:
        """クラスタリング結果DTOを初期化

        Args:
            clusters: クラスタのリスト
            granularity: 詳細度レベル
        """
        self.clusters = clusters
        self.granularity = granularity
        self.image_to_tags = self._build_image_to_tags_map()

    def _build_image_to_tags_map(self) -> Dict[str, List[str]]:
        """画像IDからタグへのマッピングを構築

        Returns:
            画像ID -> タグリストの辞書
        """
        image_to_tags: Dict[str, List[str]] = {}

        for cluster in self.clusters:
            for image_id in cluster.image_ids:
                if image_id not in image_to_tags:
                    image_to_tags[image_id] = []

                image_to_tags[image_id].append(cluster.get_tag())

        return image_to_tags

    @property
    def total_images(self) -> int:
        """クラスタリングされた画像の総数を取得"""
        return len(self.image_to_tags)

    @property
    def num_clusters(self) -> int:
        """クラスタ数を取得"""
        return len(self.clusters)

    def get_tags_for_image(self, image_id: str) -> List[str]:
        """指定画像のタグを取得

        Args:
            image_id: 画像ID

        Returns:
            タグのリスト
        """
        return self.image_to_tags.get(image_id, [])

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"ClusterResult(granularity={self.granularity}, "
            f"num_clusters={self.num_clusters}, total_images={self.total_images})"
        )
