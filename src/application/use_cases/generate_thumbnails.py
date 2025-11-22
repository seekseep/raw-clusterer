"""サムネイル生成ユースケース"""

from pathlib import Path
from typing import List

from src.domain.models.thumbnail import Thumbnail
from src.domain.repositories.raw_image_repository import RawImageRepository
from src.domain.repositories.thumbnail_repository import ThumbnailRepository
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter


class GenerateThumbnails:
    """RAW画像からサムネイルを生成するユースケース"""

    def __init__(
        self,
        raw_repository: RawImageRepository,
        thumbnail_repository: ThumbnailRepository,
        converter: RawToJpegConverter,
    ) -> None:
        """サムネイル生成ユースケースを初期化

        Args:
            raw_repository: RAW画像リポジトリ
            thumbnail_repository: サムネイルリポジトリ
            converter: RAW→JPEG変換器
        """
        self._raw_repository = raw_repository
        self._thumbnail_repository = thumbnail_repository
        self._converter = converter

    def execute(self, directory: Path) -> List[Thumbnail]:
        """指定ディレクトリのRAW画像からサムネイルを生成

        Args:
            directory: RAW画像が格納されているディレクトリ

        Returns:
            生成されたサムネイルのリスト
        """
        # RAW画像を取得
        raw_images = self._raw_repository.find_all(directory)
        print(f"Found {len(raw_images)} RAW images")

        # 各RAW画像をサムネイルに変換
        thumbnails: List[Thumbnail] = []
        for i, raw_image in enumerate(raw_images, 1):
            print(f"Converting {i}/{len(raw_images)}: {raw_image.filename}")

            thumbnail = self._converter.convert(raw_image)
            if thumbnail:
                self._thumbnail_repository.save(thumbnail)
                thumbnails.append(thumbnail)

        print(f"Successfully generated {len(thumbnails)} thumbnails")
        return thumbnails
