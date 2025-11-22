"""RAW画像からJPEGサムネイルへの変換処理"""

from pathlib import Path
from typing import Optional

import rawpy
from PIL import Image

from src.domain.models.raw_image import RawImage
from src.domain.models.thumbnail import Thumbnail


class RawToJpegConverter:
    """RAW画像をJPEGサムネイルに変換するクラス"""

    def __init__(
        self, output_dir: Path, size: int = 512, base_dir: Optional[Path] = None
    ) -> None:
        """RAW→JPEG変換器を初期化

        Args:
            output_dir: サムネイル出力先ディレクトリ
            size: サムネイルの長辺サイズ（ピクセル）
            base_dir: 元のRAW画像のベースディレクトリ（相対パス計算用）
        """
        self._output_dir = output_dir
        self._size = size
        self._base_dir = base_dir

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
        if self._base_dir:
            # ベースディレクトリからの相対パスを計算
            try:
                relative_path = raw_image.path.relative_to(self._base_dir)
                # 拡張子をjpgに変更
                output_relative_path = relative_path.with_suffix(".jpg")
                return self._output_dir / output_relative_path
            except ValueError:
                # relative_to が失敗した場合はファイル名のみ使用
                pass

        # ベースディレクトリが指定されていない場合はファイル名のみ
        thumbnail_filename = raw_image.stem + ".jpg"
        return self._output_dir / thumbnail_filename
