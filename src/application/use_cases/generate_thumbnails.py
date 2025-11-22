"""サムネイル生成ユースケース"""

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

from src.domain.models.raw_image import RawImage
from src.domain.models.thumbnail import Thumbnail
from src.domain.repositories.raw_image_repository import RawImageRepository
from src.domain.repositories.thumbnail_repository import ThumbnailRepository
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter


def _convert_thumbnail(args: tuple) -> Optional[Thumbnail]:
    """単一のRAW画像をサムネイルに変換（並列処理用）

    Args:
        args: (raw_image_path, cache_manager_base_dir, cache_dir, size) のタプル

    Returns:
        生成されたサムネイル、失敗時はNone
    """
    from pathlib import Path
    from src.domain.models.raw_image import RawImage
    from src.infrastructure.cache.cache_manager import CacheManager
    from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter

    raw_image_path, cache_manager_base_dir, cache_dir, size = args
    raw_image = RawImage(raw_image_path)
    # 各プロセスでCacheManagerを再作成（プロセス間で共有できないため）
    cache_manager = CacheManager(base_dir=Path(cache_manager_base_dir), cache_dir=Path(cache_dir))
    converter = RawToJpegConverter(size=size, cache_manager=cache_manager)
    return converter.convert(raw_image)


class GenerateThumbnails:
    """RAW画像からサムネイルを生成するユースケース"""

    def __init__(
        self,
        raw_repository: RawImageRepository,
        thumbnail_repository: ThumbnailRepository,
        converter: RawToJpegConverter,
        max_workers: int = 8,
    ) -> None:
        """サムネイル生成ユースケースを初期化

        Args:
            raw_repository: RAW画像リポジトリ
            thumbnail_repository: サムネイルリポジトリ
            converter: RAW→JPEG変換器
            max_workers: 並列処理のワーカー数（デフォルト: 8）
        """
        self._raw_repository = raw_repository
        self._thumbnail_repository = thumbnail_repository
        self._converter = converter
        self._max_workers = max_workers

    def execute(self, directory: Path) -> List[Thumbnail]:
        """指定ディレクトリのRAW画像からサムネイルを生成

        Args:
            directory: RAW画像が格納されているディレクトリ

        Returns:
            生成されたサムネイルのリスト
        """
        # RAW画像を取得
        raw_images = self._raw_repository.find_all(directory)

        # 並列処理でサムネイルを生成
        thumbnails: List[Thumbnail] = []
        raw_image_paths = [img.path for img in raw_images]

        # コンバーターの設定を取得
        size = self._converter._size
        cache_manager = self._converter._cache_manager
        if cache_manager is None:
            raise ValueError("CacheManager is required for thumbnail generation")

        cache_manager_base_dir = cache_manager.base_dir
        cache_dir = cache_manager.cache_dir

        with ProcessPoolExecutor(max_workers=self._max_workers) as executor:
            # 並列処理を開始
            futures = {
                executor.submit(_convert_thumbnail, (path, cache_manager_base_dir, cache_dir, size)): path
                for path in raw_image_paths
            }

            # 完了した順に結果を取得
            for i, future in enumerate(as_completed(futures), 1):
                path = futures[future]
                print(f"Converting {i}/{len(raw_images)}: {path.name}")

                try:
                    thumbnail = future.result()
                    if thumbnail:
                        self._thumbnail_repository.save(thumbnail)
                        thumbnails.append(thumbnail)
                except Exception as e:
                    print(f"Error converting {path.name}: {e}")

        print(f"Successfully generated {len(thumbnails)} thumbnails")
        return thumbnails
