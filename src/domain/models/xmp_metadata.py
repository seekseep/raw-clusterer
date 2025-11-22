"""XMPメタデータエンティティ"""

from pathlib import Path
from typing import List, Set

from src.domain.models.raw_image import RawImage


class XmpMetadata:
    """XMPメタデータを表すエンティティ

    Attributes:
        raw_image: 対象のRAW画像
        keywords: キーワードのセット（dc:subject）
        hierarchical_keywords: 階層キーワードのセット（lr:hierarchicalSubject）
    """

    def __init__(
        self,
        raw_image: RawImage,
        keywords: Set[str] = None,
        hierarchical_keywords: Set[str] = None,
    ) -> None:
        """XMPメタデータエンティティを初期化

        Args:
            raw_image: 対象のRAW画像
            keywords: キーワードのセット
            hierarchical_keywords: 階層キーワードのセット
        """
        self.raw_image = raw_image
        self.keywords = keywords or set()
        self.hierarchical_keywords = hierarchical_keywords or set()

    @property
    def xmp_path(self) -> Path:
        """XMPファイルのパスを取得"""
        return self.raw_image.path.with_suffix(".XMP")

    def add_keyword(self, keyword: str) -> None:
        """キーワードを追加

        Args:
            keyword: 追加するキーワード
        """
        self.keywords.add(keyword)

    def add_hierarchical_keyword(self, hierarchical_keyword: str) -> None:
        """階層キーワードを追加

        Args:
            hierarchical_keyword: 追加する階層キーワード
        """
        self.hierarchical_keywords.add(hierarchical_keyword)

    def add_keywords_from_tags(self, tags: List[str]) -> None:
        """タグからキーワードを生成して追加

        Args:
            tags: クラスタタグのリスト（例: ["ai_cluster_fine_001", "ai_cluster_coarse_002"]）
        """
        for tag in tags:
            # 通常のキーワードとして追加
            self.add_keyword(tag)

            # 階層キーワードとして追加（例: AI/cluster/fine/001）
            hierarchical = self._tag_to_hierarchical(tag)
            self.add_hierarchical_keyword(hierarchical)

    def _tag_to_hierarchical(self, tag: str) -> str:
        """タグを階層キーワードに変換

        Args:
            tag: タグ（例: "ai_cluster_fine_001"）

        Returns:
            階層キーワード（例: "AI/cluster/fine/001"）
        """
        # "ai_cluster_fine_001" -> ["ai", "cluster", "fine", "001"]
        parts = tag.split("_")

        if len(parts) >= 4 and parts[0] == "ai" and parts[1] == "cluster":
            # AI/cluster/fine/001 の形式に変換
            level = parts[2]  # "fine" or "coarse"
            number = parts[3]  # "001"
            return f"AI/cluster/{level}/{number}"

        # パースできない場合はそのまま返す
        return tag

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, XmpMetadata):
            return False
        return (
            self.raw_image == other.raw_image
            and self.keywords == other.keywords
            and self.hierarchical_keywords == other.hierarchical_keywords
        )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"XmpMetadata(raw_image={self.raw_image.filename}, "
            f"keywords={len(self.keywords)}, "
            f"hierarchical_keywords={len(self.hierarchical_keywords)})"
        )
