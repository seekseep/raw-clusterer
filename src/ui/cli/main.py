"""CLIエントリーポイント"""

import argparse
import sys
from pathlib import Path

from src.application.use_cases.generate_thumbnails import GenerateThumbnails
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter
from src.infrastructure.repositories.file_raw_image_repository import (
    FileRawImageRepository,
)
from src.infrastructure.repositories.file_thumbnail_repository import (
    FileThumbnailRepository,
)
from src.ui.cli.presenters.console_presenter import ConsolePresenter
from src.ui.config.app_config import AppConfig


def main() -> None:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="RAW image organizer with automatic clustering"
    )
    parser.add_argument("directory", type=str, help="Directory containing RAW images")
    parser.add_argument(
        "--size",
        type=int,
        default=AppConfig.DEFAULT_THUMBNAIL_SIZE,
        help=f"Thumbnail size (default: {AppConfig.DEFAULT_THUMBNAIL_SIZE})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(AppConfig.DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {AppConfig.DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=AppConfig.DEFAULT_NUM_CLUSTERS,
        help=f"Number of clusters (default: {AppConfig.DEFAULT_NUM_CLUSTERS})",
    )

    args = parser.parse_args()

    # 設定を作成
    config = AppConfig.from_args(args)
    target_directory = Path(args.directory)

    # ディレクトリの検証
    if not target_directory.exists():
        ConsolePresenter.show_error(f"Directory does not exist: {target_directory}")
        sys.exit(1)

    if not target_directory.is_dir():
        ConsolePresenter.show_error(f"Path is not a directory: {target_directory}")
        sys.exit(1)

    # 依存性の構築
    raw_repository = FileRawImageRepository()
    thumbnail_repository = FileThumbnailRepository()
    converter = RawToJpegConverter(output_dir=config.output_dir, size=config.thumbnail_size)

    # ユースケースの実行
    use_case = GenerateThumbnails(raw_repository, thumbnail_repository, converter)

    try:
        ConsolePresenter.show_info(f"Scanning directory: {target_directory}")
        ConsolePresenter.show_info(f"Output directory: {config.output_dir}")
        ConsolePresenter.show_info(f"Thumbnail size: {config.thumbnail_size}px")

        thumbnails = use_case.execute(target_directory)
        ConsolePresenter.show_thumbnails(thumbnails)

    except Exception as e:
        ConsolePresenter.show_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
