"""XMPメタデータ更新ユースケース"""

from pathlib import Path
from typing import Dict, List

from src.application.dto.cluster_result import ClusterResult
from src.domain.models.raw_image import RawImage
from src.domain.models.xmp_metadata import XmpMetadata
from src.domain.repositories.raw_image_repository import RawImageRepository
from src.domain.repositories.xmp_repository import XmpRepository


class UpdateXmpMetadata:
    """XMPメタデータを更新するユースケース"""

    def __init__(
        self,
        raw_repository: RawImageRepository,
        xmp_repository: XmpRepository,
    ) -> None:
        """XMPメタデータ更新ユースケースを初期化

        Args:
            raw_repository: RAW画像リポジトリ
            xmp_repository: XMPリポジトリ
        """
        self._raw_repository = raw_repository
        self._xmp_repository = xmp_repository

    def execute(
        self,
        directory: Path,
        cluster_results: List[ClusterResult],
        dry_run: bool = False,
    ) -> int:
        """クラスタリング結果をXMPメタデータとして書き込む

        Args:
            directory: RAW画像が格納されているディレクトリ
            cluster_results: クラスタリング結果のリスト（詳細度1, 2など）
            dry_run: Trueの場合は実際には書き込まない

        Returns:
            更新したXMPファイルの数
        """
        print(f"\nUpdating XMP metadata...")
        print(f"Directory: {directory}")
        print(f"Dry run: {dry_run}")

        # RAW画像を取得
        raw_images = self._raw_repository.find_all(directory)
        print(f"Found {len(raw_images)} RAW images")

        # 画像IDからタグへのマッピングを統合
        image_to_tags: Dict[str, List[str]] = {}
        for result in cluster_results:
            for image_id, tags in result.image_to_tags.items():
                if image_id not in image_to_tags:
                    image_to_tags[image_id] = []
                image_to_tags[image_id].extend(tags)

        # 各RAW画像のXMPを更新
        updated_count = 0
        for i, raw_image in enumerate(raw_images, 1):
            # 画像IDを取得（ファイル名のstem）
            image_id = raw_image.stem

            # このRAW画像に対応するタグを取得
            tags = image_to_tags.get(image_id, [])

            if not tags:
                print(f"  [{i}/{len(raw_images)}] {raw_image.filename}: No tags, skipping")
                continue

            # XMPメタデータを作成
            xmp_metadata = XmpMetadata(raw_image=raw_image)
            xmp_metadata.add_keywords_from_tags(tags)

            if dry_run:
                print(
                    f"  [{i}/{len(raw_images)}] {raw_image.filename}: "
                    f"Would add {len(tags)} tags (dry run)"
                )
            else:
                # 既存のXMPとマージして保存
                self._xmp_repository.merge_and_save(xmp_metadata)
                updated_count += 1
                print(
                    f"  [{i}/{len(raw_images)}] {raw_image.filename}: "
                    f"Updated with {len(tags)} tags"
                )

        if not dry_run:
            print(f"\nSuccessfully updated {updated_count} XMP files")
        else:
            print(f"\nWould update {len([img for img in raw_images if img.stem in image_to_tags])} XMP files (dry run)")

        return updated_count
