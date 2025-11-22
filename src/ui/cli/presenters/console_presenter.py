"""コンソール出力プレゼンター"""

from typing import List

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
