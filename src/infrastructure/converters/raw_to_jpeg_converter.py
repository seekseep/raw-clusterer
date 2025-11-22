"""RAW画像からJPEGサムネイルへの変換処理"""

from pathlib import Path
from typing import Optional

import rawpy
from PIL import Image

from src.domain.models.raw_image import RawImage
from src.domain.models.thumbnail import Thumbnail
from src.infrastructure.cache.cache_manager import CacheManager


class RawToJpegConverter:
    """RAW画像をJPEGサムネイルに変換するクラス"""

    def __init__(
        self,
        size: int = 512,
        cache_manager: Optional[CacheManager] = None,
    ) -> None:
        """RAW→JPEG変換器を初期化

        Args:
            size: サムネイルの長辺サイズ（ピクセル）
            cache_manager: キャッシュマネージャー（指定時は.cache/thumbnailsに出力）
        """
        self._size = size
        self._cache_manager = cache_manager

    def convert(self, raw_image: RawImage) -> Optional[Thumbnail]:
        """RAW画像をJPEGサムネイルに変換

        Args:
            raw_image: 変換元のRAW画像

        Returns:
            生成されたサムネイル、失敗時はNone
        """
        try:
            # RAW画像を読み込んでRGBに変換
            with rawpy.imread(str(raw_image.path)) as raw:
                rgb = raw.postprocess()

            # PIL Imageに変換してサムネイル化
            img = Image.fromarray(rgb)
            img.thumbnail((self._size, self._size), Image.Resampling.LANCZOS)

            # 出力パスを決定して保存
            output_path = self._get_output_path(raw_image)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "JPEG", quality=85, optimize=True)

            # キャッシュマネージャーがある場合はマッピングを記録
            if self._cache_manager:
                self._cache_manager.add_raw_thumbnail_mapping(
                    raw_image.path, output_path
                )

            return Thumbnail(path=output_path, source=raw_image, size=self._size)

        except Exception as e:
            print(f"Failed to convert {raw_image.path}: {e}")
            return None

    def _get_output_path(self, raw_image: RawImage) -> Path:
        """サムネイルの出力パスを取得

        Args:
            raw_image: RAW画像

        Returns:
            サムネイルの出力パス
        """
        if self._cache_manager:
            # キャッシュマネージャーがある場合は.cache/thumbnailsに出力
            base_dir = self._cache_manager.base_dir
            output_dir = self._cache_manager.thumbnails_dir

            try:
                # ベースディレクトリからの相対パスを計算
                relative_path = raw_image.path.relative_to(base_dir)
                # 拡張子をjpgに変更
                output_relative_path = relative_path.with_suffix(".jpg")
                return output_dir / output_relative_path
            except ValueError:
                # relative_toが失敗した場合はファイル名のみ使用
                thumbnail_filename = raw_image.stem + ".jpg"
                return output_dir / thumbnail_filename
        else:
            # 後方互換性のため、キャッシュマネージャーがない場合の動作を残す
            raise ValueError("CacheManager is required for RawToJpegConverter")
