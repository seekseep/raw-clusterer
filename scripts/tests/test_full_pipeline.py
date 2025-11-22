"""フルパイプライン統合テスト（32枚のテストデータ使用）"""

from pathlib import Path

from src.application.use_cases.cluster_images import ClusterImages
from src.application.use_cases.extract_features import ExtractFeatures
from src.application.use_cases.generate_thumbnails import GenerateThumbnails
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter
from src.infrastructure.ml.clustering.kmeans_clusterer import KMeansClusterer
from src.infrastructure.ml.models.resnet_model import ResNet50FeatureExtractor
from src.infrastructure.repositories.file_raw_image_repository import (
    FileRawImageRepository,
)
from src.infrastructure.repositories.file_thumbnail_repository import (
    FileThumbnailRepository,
)
from src.infrastructure.repositories.json_cluster_repository import (
    JsonClusterRepository,
)
from src.infrastructure.repositories.numpy_embedding_repository import (
    NumpyEmbeddingRepository,
)
from src.ui.cli.presenters.console_presenter import ConsolePresenter

# パス設定
RAW_DIR = Path("test_data/raw_images")
OUTPUT_BASE = Path("outputs/test_full_pipeline")
THUMBNAIL_DIR = OUTPUT_BASE / "thumbs"
EMBEDDING_DIR = OUTPUT_BASE
CLUSTER_FILE_FINE = OUTPUT_BASE / "clusters_fine.json"
CLUSTER_FILE_COARSE = OUTPUT_BASE / "clusters_coarse.json"

print("=" * 70)
print("フルパイプライン統合テスト（32枚のテストデータ）")
print("=" * 70)

# 1. サムネイル生成
print("\n[Step 1/5] サムネイル生成")
print("-" * 70)
raw_repository = FileRawImageRepository()
thumbnail_repository = FileThumbnailRepository()
converter = RawToJpegConverter(
    output_dir=THUMBNAIL_DIR, size=512, base_dir=RAW_DIR
)

use_case_thumbnails = GenerateThumbnails(
    raw_repository, thumbnail_repository, converter
)
thumbnails = use_case_thumbnails.execute(RAW_DIR)

ConsolePresenter.show_info(f"Generated {len(thumbnails)} thumbnails")

# 2. 特徴抽出
print("\n[Step 2/5] 特徴抽出（ResNet50）")
print("-" * 70)
feature_extractor = ResNet50FeatureExtractor(device="cpu")
embedding_repository = NumpyEmbeddingRepository()

use_case_extract = ExtractFeatures(feature_extractor, embedding_repository)
embeddings = use_case_extract.execute(thumbnails, EMBEDDING_DIR, base_dir=RAW_DIR)

ConsolePresenter.show_info(f"Extracted {len(embeddings)} feature vectors")

# 3. クラスタリング（詳細度1: Fine - 多クラスタ）
print("\n[Step 3/5] クラスタリング - 詳細度1（Fine: ほぼ同じ被写体）")
print("-" * 70)
clusterer_fine = KMeansClusterer(n_clusters=8, random_state=42)
cluster_repository = JsonClusterRepository()

use_case_cluster_fine = ClusterImages(clusterer_fine, cluster_repository)
result_fine = use_case_cluster_fine.execute(
    embeddings, granularity=1, output_path=CLUSTER_FILE_FINE
)

ConsolePresenter.show_cluster_result(result_fine)

# 4. クラスタリング（詳細度2: Coarse - 少クラスタ）
print("\n[Step 4/5] クラスタリング - 詳細度2（Coarse: 同じ場所・似た被写体）")
print("-" * 70)
clusterer_coarse = KMeansClusterer(n_clusters=4, random_state=42)

use_case_cluster_coarse = ClusterImages(clusterer_coarse, cluster_repository)
result_coarse = use_case_cluster_coarse.execute(
    embeddings, granularity=2, output_path=CLUSTER_FILE_COARSE
)

ConsolePresenter.show_cluster_result(result_coarse)

# 5. タグ表示
print("\n[Step 5/5] 生成されたタグ")
print("-" * 70)

print("\n【詳細度1: Fine】")
ConsolePresenter.show_image_tags(result_fine.image_to_tags, max_display=10)

print("\n【詳細度2: Coarse】")
ConsolePresenter.show_image_tags(result_coarse.image_to_tags, max_display=10)

# サマリー
print("\n" + "=" * 70)
print("テスト完了！")
print("=" * 70)
print(f"\n📊 統計情報:")
print(f"  入力画像: {len(thumbnails)}枚")
print(f"  特徴ベクトル: {embeddings[0].dimension}次元")
print(f"  詳細度1クラスタ数: {result_fine.num_clusters}")
print(f"  詳細度2クラスタ数: {result_coarse.num_clusters}")

print(f"\n📁 出力ファイル:")
print(f"  サムネイル: {THUMBNAIL_DIR}")
print(f"  埋め込みベクトル: {EMBEDDING_DIR}/embeddings.npy")
print(f"  クラスタ（Fine）: {CLUSTER_FILE_FINE}")
print(f"  クラスタ（Coarse）: {CLUSTER_FILE_COARSE}")
