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
  # 基本的な使い方
  %(prog)s /path/to/raw_images

  # オプションを指定
  %(prog)s /path/to/raw_images --size 512 --clusters-fine 50 --clusters-coarse 10

  # Dry runモード（XMPを書き込まない）
  %(prog)s /path/to/raw_images --dry-run

  # 出力先を指定
  %(prog)s /path/to/raw_images --output /path/to/output
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
        default=str(AppConfig.DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {AppConfig.DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--clusters-fine",
        type=int,
        default=AppConfig.DEFAULT_NUM_CLUSTERS,
        dest="clusters_fine",
        help=f"Number of clusters for fine granularity (default: {AppConfig.DEFAULT_NUM_CLUSTERS})",
    )
    parser.add_argument(
        "--clusters-coarse",
        type=int,
        default=AppConfig.DEFAULT_NUM_CLUSTERS // 2,
        dest="clusters_coarse",
        help=f"Number of clusters for coarse granularity (default: {AppConfig.DEFAULT_NUM_CLUSTERS // 2})",
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
