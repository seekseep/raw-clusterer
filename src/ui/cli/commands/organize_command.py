"""整理コマンド"""

import argparse
from pathlib import Path

from src.application.use_cases.cluster_images import ClusterImages
from src.application.use_cases.extract_features import ExtractFeatures
from src.application.use_cases.generate_thumbnails import GenerateThumbnails
from src.application.use_cases.organize_raw_images import OrganizeRawImages
from src.application.use_cases.update_xmp_metadata import UpdateXmpMetadata
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter
from src.infrastructure.ml.clustering.kmeans_clusterer import KMeansClusterer
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
        target_directory = Path(args.directory)

        # ディレクトリの検証
        if not target_directory.exists():
            ConsolePresenter.show_error(f"Directory does not exist: {target_directory}")
            return

        if not target_directory.is_dir():
            ConsolePresenter.show_error(f"Path is not a directory: {target_directory}")
            return

        # 出力ディレクトリの設定
        output_dir = Path(args.output) if hasattr(args, "output") and args.output else config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # サムネイル出力ディレクトリ
        thumbnail_dir = output_dir / "thumbs"

        # 依存性の構築
        # Repositories
        raw_repository = FileRawImageRepository()
        thumbnail_repository = FileThumbnailRepository()
        embedding_repository = NumpyEmbeddingRepository()
        cluster_repository = JsonClusterRepository()
        xmp_repository = FileXmpRepository()

        # Infrastructure
        converter = RawToJpegConverter(
            output_dir=thumbnail_dir,
            size=config.thumbnail_size,
            base_dir=target_directory,
        )
        feature_extractor = ResNet50FeatureExtractor(device="cpu")

        # クラスタ数の設定
        n_clusters_fine = getattr(args, "clusters_fine", config.num_clusters)
        n_clusters_coarse = getattr(args, "clusters_coarse", config.num_clusters // 2)

        clusterer_fine = KMeansClusterer(n_clusters=n_clusters_fine, random_state=42)
        clusterer_coarse = KMeansClusterer(n_clusters=n_clusters_coarse, random_state=42)

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
