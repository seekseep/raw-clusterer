"""RAW画像整理ユースケース（全体orchestration）"""

from pathlib import Path
from typing import List, Optional

from src.application.dto.cluster_result import ClusterResult
from src.application.use_cases.cluster_images import ClusterImages
from src.application.use_cases.extract_features import ExtractFeatures
from src.application.use_cases.generate_thumbnails import GenerateThumbnails
from src.application.use_cases.update_xmp_metadata import UpdateXmpMetadata
from src.infrastructure.cache.cache_manager import CacheManager
from src.ui.cli.presenters.console_presenter import ConsolePresenter


class OrganizeRawImages:
    """RAW画像を整理する全体ユースケース

    以下の処理を順番に実行:
    1. サムネイル生成
    2. 特徴抽出
    3. クラスタリング（詳細度1: Fine）
    4. クラスタリング（詳細度2: Coarse）
    5. XMPメタデータ更新
    6. キャッシュクリーンアップ
    """

    def __init__(
        self,
        generate_thumbnails: GenerateThumbnails,
        extract_features: ExtractFeatures,
        cluster_images_fine: ClusterImages,
        cluster_images_coarse: ClusterImages,
        update_xmp: UpdateXmpMetadata,
        cache_manager: Optional[CacheManager] = None,
    ) -> None:
        """RAW画像整理ユースケースを初期化

        Args:
            generate_thumbnails: サムネイル生成ユースケース
            extract_features: 特徴抽出ユースケース
            cluster_images_fine: クラスタリングユースケース（詳細度1: Fine）
            cluster_images_coarse: クラスタリングユースケース（詳細度2: Coarse）
            update_xmp: XMP更新ユースケース
            cache_manager: キャッシュマネージャー
        """
        self._generate_thumbnails = generate_thumbnails
        self._extract_features = extract_features
        self._cluster_images_fine = cluster_images_fine
        self._cluster_images_coarse = cluster_images_coarse
        self._update_xmp = update_xmp
        self._cache_manager = cache_manager

    def execute(
        self,
        directory: Path,
        output_dir: Path,
        dry_run: bool = False,
    ) -> List[ClusterResult]:
        """RAW画像を整理

        Args:
            directory: RAW画像が格納されているディレクトリ
            output_dir: 出力先ディレクトリ
            dry_run: Trueの場合はXMP書き込みを行わない

        Returns:
            クラスタリング結果のリスト
        """
        print("=" * 70)
        print("RAW画像自動分類ツール")
        print("=" * 70)

        # 1. サムネイル生成
        print("\n[Step 1/5] サムネイル生成")
        print("-" * 70)
        thumbnails = self._generate_thumbnails.execute(directory)
        ConsolePresenter.show_info(f"Generated {len(thumbnails)} thumbnails")

        if len(thumbnails) == 0:
            ConsolePresenter.show_error("No RAW images found")
            return []

        # 2. 特徴抽出
        print("\n[Step 2/5] 特徴抽出（ResNet50）")
        print("-" * 70)
        embeddings = self._extract_features.execute(
            thumbnails, output_dir, base_dir=directory
        )
        ConsolePresenter.show_info(
            f"Extracted {len(embeddings)} feature vectors ({embeddings[0].dimension}D)"
        )

        # 3. クラスタリング（詳細度1: Fine）
        print("\n[Step 3/5] クラスタリング - 詳細度1（Fine: ほぼ同じ被写体）")
        print("-" * 70)
        cluster_file_fine = output_dir / "clusters_fine.json"
        result_fine = self._cluster_images_fine.execute(
            embeddings, granularity=1, output_path=cluster_file_fine
        )
        ConsolePresenter.show_cluster_result(result_fine)

        # 4. クラスタリング（詳細度2: Coarse）
        print("\n[Step 4/5] クラスタリング - 詳細度2（Coarse: 同じ場所・似た被写体）")
        print("-" * 70)
        cluster_file_coarse = output_dir / "clusters_coarse.json"
        result_coarse = self._cluster_images_coarse.execute(
            embeddings, granularity=2, output_path=cluster_file_coarse
        )
        ConsolePresenter.show_cluster_result(result_coarse)

        # 5. XMPメタデータ更新
        print("\n[Step 5/5] XMPメタデータ更新")
        print("-" * 70)
        updated_count = self._update_xmp.execute(
            directory, cluster_results=[result_fine, result_coarse], dry_run=dry_run
        )

        if dry_run:
            ConsolePresenter.show_info(
                f"Would update {updated_count} XMP files (dry run mode)"
            )
        else:
            ConsolePresenter.show_info(f"Updated {updated_count} XMP files")

        # サマリー表示
        print("\n" + "=" * 70)
        print("完了！")
        print("=" * 70)
        print(f"\n📊 統計情報:")
        print(f"  処理画像数: {len(thumbnails)}枚")
        print(f"  詳細度1クラスタ数: {result_fine.num_clusters}")
        print(f"  詳細度2クラスタ数: {result_coarse.num_clusters}")
        print(f"  XMPファイル: {updated_count}個")

        return [result_fine, result_coarse]
