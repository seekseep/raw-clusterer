"""CLIエントリーポイント"""

import argparse
import sys

from src.ui.cli.commands.organize_command import OrganizeCommand
from src.ui.config.app_config import AppConfig


def main() -> None:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="RAW image organizer with automatic clustering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 基本的な使い方（HDBSCANで自動クラスタリング）
  %(prog)s /path/to/raw_images

  # KMeansでクラスタ数を指定
  %(prog)s /path/to/raw_images --algorithm kmeans --clusters-fine 50 --clusters-coarse 10

  # HDBSCANのパラメータを調整
  %(prog)s /path/to/raw_images --algorithm hdbscan --min-cluster-size 10 --min-samples 5

  # Dry runモード（XMPを書き込まない）
  %(prog)s /path/to/raw_images --dry-run
        """,
    )

    # 必須引数
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing RAW images"
    )

    # オプション引数
    parser.add_argument(
        "--size",
        type=int,
        default=AppConfig.DEFAULT_THUMBNAIL_SIZE,
        help=f"Thumbnail size in pixels (default: {AppConfig.DEFAULT_THUMBNAIL_SIZE})",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for cache files (optional, defaults to .raw_clusterer_cache in input directory)",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="hdbscan",
        choices=["kmeans", "hdbscan"],
        help="Clustering algorithm to use (default: hdbscan)",
    )
    parser.add_argument(
        "--clusters-fine",
        type=int,
        default=AppConfig.DEFAULT_NUM_CLUSTERS,
        dest="clusters_fine",
        help=f"Number of clusters for fine granularity (default: {AppConfig.DEFAULT_NUM_CLUSTERS}, only used with kmeans)",
    )
    parser.add_argument(
        "--clusters-coarse",
        type=int,
        default=AppConfig.DEFAULT_NUM_CLUSTERS // 2,
        dest="clusters_coarse",
        help=f"Number of clusters for coarse granularity (default: {AppConfig.DEFAULT_NUM_CLUSTERS // 2}, only used with kmeans)",
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=5,
        dest="min_cluster_size",
        help="Minimum cluster size for HDBSCAN (default: 5, only used with hdbscan)",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=3,
        dest="min_samples",
        help="Minimum samples for HDBSCAN (default: 3, only used with hdbscan)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Do not write XMP files, just show what would be done",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="resnet50",
        choices=["resnet50"],
        help="Model to use for feature extraction (default: resnet50)",
    )

    args = parser.parse_args()

    # コマンドを実行
    command = OrganizeCommand()
    try:
        command.execute(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
