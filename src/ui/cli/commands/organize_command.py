"""整理コマンド"""

import argparse
from pathlib import Path

from src.application.use_cases.cluster_images import ClusterImages
from src.application.use_cases.extract_features import ExtractFeatures
from src.application.use_cases.generate_thumbnails import GenerateThumbnails
from src.application.use_cases.organize_raw_images import OrganizeRawImages
from src.application.use_cases.update_xmp_metadata import UpdateXmpMetadata
from src.infrastructure.cache.cache_manager import CacheManager
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter
from src.infrastructure.ml.clustering.kmeans_clusterer import KMeansClusterer
from src.infrastructure.ml.clustering.hdbscan_clusterer import HDBSCANClusterer
from src.infrastructure.ml.models.resnet_model import ResNet50FeatureExtractor
from src.infrastructure.repositories.file_raw_image_repository import (
    FileRawImageRepository,
)
from src.infrastructure.repositories.file_thumbnail_repository import (
    FileThumbnailRepository,
)
from src.infrastructure.repositories.file_xmp_repository import FileXmpRepository
from src.infrastructure.repositories.json_cluster_repository import (
    JsonClusterRepository,
)
from src.infrastructure.repositories.numpy_embedding_repository import (
    NumpyEmbeddingRepository,
)
from src.ui.cli.presenters.console_presenter import ConsolePresenter
from src.ui.config.app_config import AppConfig


class OrganizeCommand:
    """RAW画像を整理するコマンド"""

    def __init__(self) -> None:
        """整理コマンドを初期化"""
        pass

    def execute(self, args: argparse.Namespace) -> None:
        """コマンドを実行

        Args:
            args: コマンドライン引数
        """
        # 設定を作成
        config = AppConfig.from_args(args)
        target_directory = Path(args.directory).resolve()

        # ディレクトリの検証
        if not target_directory.exists():
            ConsolePresenter.show_error(f"Directory does not exist: {target_directory}")
            return

        if not target_directory.is_dir():
            ConsolePresenter.show_error(f"Path is not a directory: {target_directory}")
            return

        # キャッシュディレクトリの設定
        cache_dir = Path(args.output) if hasattr(args, "output") and args.output else target_directory / ".cache"

        # キャッシュマネージャーの初期化
        cache_manager = CacheManager(base_dir=target_directory, cache_dir=cache_dir)
        cache_manager.initialize()

        # 出力ディレクトリはキャッシュディレクトリと同じ
        output_dir = cache_dir

        # 依存性の構築
        # Repositories
        raw_repository = FileRawImageRepository()
        thumbnail_repository = FileThumbnailRepository()
        embedding_repository = NumpyEmbeddingRepository()
        cluster_repository = JsonClusterRepository()
        xmp_repository = FileXmpRepository()

        # Infrastructure
        converter = RawToJpegConverter(
            size=config.thumbnail_size,
            cache_manager=cache_manager,
        )
        feature_extractor = ResNet50FeatureExtractor(device="cpu")

        # クラスタリングアルゴリズムの選択
        algorithm = getattr(args, "algorithm", "hdbscan")

        if algorithm == "kmeans":
            # KMeans: クラスタ数を指定
            n_clusters_fine = getattr(args, "clusters_fine", config.num_clusters)
            n_clusters_coarse = getattr(args, "clusters_coarse", config.num_clusters // 2)
            clusterer_fine = KMeansClusterer(n_clusters=n_clusters_fine, random_state=42)
            clusterer_coarse = KMeansClusterer(n_clusters=n_clusters_coarse, random_state=42)
        else:
            # HDBSCAN: 自動的にクラスタ数を決定
            min_cluster_size = getattr(args, "min_cluster_size", 5)
            min_samples = getattr(args, "min_samples", 3)
            # Fine: より小さいクラスタサイズで詳細に分割
            clusterer_fine = HDBSCANClusterer(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
            )
            # Coarse: より大きいクラスタサイズで粗く分割
            clusterer_coarse = HDBSCANClusterer(
                min_cluster_size=min_cluster_size * 2,
                min_samples=min_samples,
            )

        # Use Cases
        generate_thumbnails = GenerateThumbnails(
            raw_repository, thumbnail_repository, converter
        )
        extract_features = ExtractFeatures(feature_extractor, embedding_repository)
        cluster_images_fine = ClusterImages(clusterer_fine, cluster_repository)
        cluster_images_coarse = ClusterImages(clusterer_coarse, cluster_repository)
        update_xmp = UpdateXmpMetadata(raw_repository, xmp_repository)

        # 全体ユースケース
        organize = OrganizeRawImages(
            generate_thumbnails,
            extract_features,
            cluster_images_fine,
            cluster_images_coarse,
            update_xmp,
            cache_manager=cache_manager,
        )

        # 実行
        try:
            dry_run = getattr(args, "dry_run", False)
            organize.execute(
                directory=target_directory,
                output_dir=output_dir,
                dry_run=dry_run,
            )
        except Exception as e:
            ConsolePresenter.show_error(f"Failed to organize RAW images: {e}")
            import traceback
            traceback.print_exc()
