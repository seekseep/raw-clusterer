"""コンソール出力プレゼンター"""

from typing import Dict, List

from src.application.dto.cluster_result import ClusterResult
from src.domain.models.thumbnail import Thumbnail


class ConsolePresenter:
    """コンソールへの出力を整形するクラス"""

    @staticmethod
    def show_thumbnails(thumbnails: List[Thumbnail]) -> None:
        """サムネイル生成結果を表示

        Args:
            thumbnails: 生成されたサムネイルのリスト
        """
        print("\n" + "=" * 60)
        print(f"Generated {len(thumbnails)} thumbnails")
        print("=" * 60)

        for thumbnail in thumbnails:
            print(f"  ✓ {thumbnail.source.filename} -> {thumbnail.filename}")

        print("=" * 60 + "\n")

    @staticmethod
    def show_error(message: str) -> None:
        """エラーメッセージを表示

        Args:
            message: エラーメッセージ
        """
        print(f"\n❌ Error: {message}\n")

    @staticmethod
    def show_info(message: str) -> None:
        """情報メッセージを表示

        Args:
            message: 情報メッセージ
        """
        print(f"ℹ️  {message}")

    @staticmethod
    def show_cluster_result(result: ClusterResult) -> None:
        """クラスタリング結果を表示

        Args:
            result: クラスタリング結果
        """
        print("\n" + "=" * 60)
        granularity_name = "Fine (ほぼ同じ被写体)" if result.granularity == 1 else "Coarse (同じ場所・似た被写体)"
        print(f"Clustering Result - Granularity {result.granularity}: {granularity_name}")
        print("=" * 60)
        print(f"Total images: {result.total_images}")
        print(f"Number of clusters: {result.num_clusters}")
        print("=" * 60 + "\n")

    @staticmethod
    def show_image_tags(image_to_tags: Dict[str, List[str]], max_display: int = 20) -> None:
        """画像とタグのマッピングを表示

        Args:
            image_to_tags: 画像ID -> タグリストの辞書
            max_display: 最大表示件数
        """
        print("\n" + "=" * 60)
        print("Image Tags")
        print("=" * 60)

        for i, (image_id, tags) in enumerate(sorted(image_to_tags.items())):
            if i >= max_display:
                remaining = len(image_to_tags) - max_display
                print(f"\n... and {remaining} more images")
                break

            tags_str = ", ".join(tags)
            print(f"{image_id}: {tags_str}")

        print("=" * 60 + "\n")
