"""クラスタエンティティ"""

from typing import List


class Cluster:
    """画像クラスタを表すエンティティ

    Attributes:
        cluster_id: クラスタID
        image_ids: クラスタに含まれる画像IDのリスト
        granularity: 詳細度レベル（1: 細かい、2: 粗い）
    """

    def __init__(
        self, cluster_id: int, image_ids: List[str], granularity: int = 1
    ) -> None:
        """クラスタエンティティを初期化

        Args:
            cluster_id: クラスタID
            image_ids: クラスタに含まれる画像IDのリスト
            granularity: 詳細度レベル（1 or 2）

        Raises:
            ValueError: cluster_idが負、またはgranularityが1か2でない場合
        """
        if cluster_id < 0:
            raise ValueError("cluster_id must be non-negative")

        if granularity not in (1, 2):
            raise ValueError("granularity must be 1 or 2")

        self.cluster_id = cluster_id
        self.image_ids = list(image_ids)
        self.granularity = granularity

    @property
    def size(self) -> int:
        """クラスタに含まれる画像数を取得"""
        return len(self.image_ids)

    def add_image(self, image_id: str) -> None:
        """画像をクラスタに追加

        Args:
            image_id: 追加する画像ID
        """
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)

    def remove_image(self, image_id: str) -> None:
        """画像をクラスタから削除

        Args:
            image_id: 削除する画像ID
        """
        if image_id in self.image_ids:
            self.image_ids.remove(image_id)

    def contains(self, image_id: str) -> bool:
        """画像がクラスタに含まれるか確認

        Args:
            image_id: 確認する画像ID

        Returns:
            含まれる場合True
        """
        return image_id in self.image_ids

    def get_tag(self) -> str:
        """クラスタのタグを生成

        Returns:
            タグ文字列（例: "fine_003", "coarse_042"）
        """
        level_name = "fine" if self.granularity == 1 else "coarse"
        return f"{level_name}_{self.cluster_id:03d}"

    def get_hierarchical_tag(self) -> str:
        """階層キーワードを生成

        Returns:
            階層タグ文字列（例: "cluster/fine/003", "cluster/coarse/042"）
        """
        level_name = "fine" if self.granularity == 1 else "coarse"
        return f"cluster/{level_name}/{self.cluster_id:03d}"

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, Cluster):
            return False
        return (
            self.cluster_id == other.cluster_id
            and self.granularity == other.granularity
            and set(self.image_ids) == set(other.image_ids)
        )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"Cluster(id={self.cluster_id}, granularity={self.granularity}, "
            f"size={self.size})"
        )
