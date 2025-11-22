"""XMPメタデータ更新ユースケース"""

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.application.dto.cluster_result import ClusterResult
from src.domain.models.raw_image import RawImage
from src.domain.models.xmp_metadata import XmpMetadata
from src.domain.repositories.raw_image_repository import RawImageRepository
from src.domain.repositories.xmp_repository import XmpRepository


def _update_single_xmp(
    raw_image_path: Path,
    directory: Path,
    tags: List[str],
    dry_run: bool
) -> Tuple[str, bool, int]:
    """単一のXMPファイルを更新（並列処理用）

    Args:
        raw_image_path: RAW画像のパス
        directory: ベースディレクトリ
        tags: 追加するタグのリスト
        dry_run: ドライランモード

    Returns:
        (ファイル名, 成功/失敗, タグ数)
    """
    from src.infrastructure.repositories.file_xmp_repository import FileXmpRepository

    try:
        raw_image = RawImage(raw_image_path)
        xmp_path = raw_image_path.with_suffix(".xmp")
        xmp_repository = FileXmpRepository()

        # LOAD: 既存のXMPがあれば読み込む
        existing_xmp = xmp_repository.load(xmp_path) if xmp_path.exists() else None

        # UPDATE: 既存のXMPにタグを追加、なければ新規作成
        if existing_xmp:
            xmp_metadata = existing_xmp
            xmp_metadata.add_keywords_from_tags(tags)
        else:
            xmp_metadata = XmpMetadata(raw_image=raw_image)
            xmp_metadata.add_keywords_from_tags(tags)

        # SAVE: ドライランでなければ保存
        if not dry_run:
            xmp_repository.save(xmp_metadata)
            return (raw_image.filename, True, len(tags))
        else:
            return (raw_image.filename, False, len(tags))

    except Exception as e:
        return (str(raw_image_path), False, 0)


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
        """クラスタリング結果をXMPメタデータとして書き込む（並列処理）

        Args:
            directory: RAW画像が格納されているディレクトリ
            cluster_results: クラスタリング結果のリスト（詳細度1, 2など）
            dry_run: Trueの場合は実際には書き込まない

        Returns:
            更新したXMPファイルの数
        """
        import multiprocessing
        import os

        print(f"\nUpdating XMP metadata (next to RAW files)...")

        # RAW画像を取得
        raw_images = self._raw_repository.find_all(directory)

        # 画像IDからタグへのマッピングを統合
        image_to_tags: Dict[str, List[str]] = {}
        for result in cluster_results:
            for image_id, tags in result.image_to_tags.items():
                if image_id not in image_to_tags:
                    image_to_tags[image_id] = []
                image_to_tags[image_id].extend(tags)

        # 並列処理用のタスクリストを作成
        tasks = []
        for raw_image in raw_images:
            # 画像IDを取得（相対パスまたはstem）
            try:
                relative_path = raw_image.path.relative_to(directory)
                image_id = str(relative_path.with_suffix("")).replace("\\", "/")
            except ValueError:
                image_id = raw_image.stem

            tags = image_to_tags.get(image_id, [])
            if tags:
                tasks.append((raw_image.path, directory, tags, dry_run))

        if not tasks:
            print("\nNo files to update")
            return 0

        # CPU数に基づいてワーカー数を決定
        max_workers = min(multiprocessing.cpu_count(), len(tasks))

        # 並列処理でXMPファイルを更新
        updated_count = 0
        completed = 0
        total = len(tasks)

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # タスクを投入
            future_to_task = {
                executor.submit(_update_single_xmp, *task): task
                for task in tasks
            }

            # 完了したタスクから処理
            for future in as_completed(future_to_task):
                filename, success, tag_count = future.result()
                completed += 1

                if dry_run:
                    print(f"  [{completed}/{total}] {filename}: Would add {tag_count} tags")
                else:
                    if success:
                        updated_count += 1
                        print(f"  [{completed}/{total}] {filename}: Added {tag_count} tags")
                    else:
                        print(f"  [{completed}/{total}] {filename}: Failed to update")

        if not dry_run:
            print(f"\nUpdated {updated_count} XMP files")
        else:
            print(f"\nWould update {len(tasks)} XMP files")

        return updated_count
