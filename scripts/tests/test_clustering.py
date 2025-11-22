"""クラスタリング機能のテスト"""

from pathlib import Path

from src.application.dto.cluster_result import ClusterResult
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

# 検証用ディレクトリ（最初の10枚のみテスト）
RAW_DIR = Path("/Users/seekseep/Pictures/レタッチ/20251112_兵庫前期")
OUTPUT_BASE = Path("outputs/test_clustering")
THUMBNAIL_DIR = OUTPUT_BASE / "thumbs"
EMBEDDING_DIR = OUTPUT_BASE
CLUSTER_FILE = OUTPUT_BASE / "clusters_fine.json"

# サンプル数を制限
MAX_SAMPLES = 10

print("=" * 60)
print("クラスタリング機能テスト")
print("=" * 60)

# 1. サムネイル生成（最初の10枚のみ）
print("\n[1/4] サムネイル生成中...")
raw_repository = FileRawImageRepository()
thumbnail_repository = FileThumbnailRepository()
converter = RawToJpegConverter(output_dir=THUMBNAIL_DIR, size=512)

use_case_thumbnails = GenerateThumbnails(raw_repository, thumbnail_repository, converter)
raw_images = raw_repository.find_all(RAW_DIR)[:MAX_SAMPLES]  # 最初の10枚のみ

thumbnails = []
for raw_image in raw_images:
    print(f"  Converting: {raw_image.filename}")
    thumbnail = converter.convert(raw_image)
    if thumbnail:
        thumbnails.append(thumbnail)

print(f"✓ {len(thumbnails)}枚のサムネイルを生成しました")

# 2. 特徴抽出
print("\n[2/4] 特徴抽出中...")
feature_extractor = ResNet50FeatureExtractor(device="cpu")
embedding_repository = NumpyEmbeddingRepository()

use_case_extract = ExtractFeatures(feature_extractor, embedding_repository)
embeddings = use_case_extract.execute(thumbnails, EMBEDDING_DIR)

print(f"✓ {len(embeddings)}個の特徴ベクトルを抽出しました")

# 3. クラスタリング（詳細度1: 細かい分類）
print("\n[3/4] クラスタリング中...")
# サンプル数が少ないのでクラスタ数を3に設定
clusterer = KMeansClusterer(n_clusters=3, random_state=42)
cluster_repository = JsonClusterRepository()

use_case_cluster = ClusterImages(clusterer, cluster_repository)
result = use_case_cluster.execute(embeddings, granularity=1, output_path=CLUSTER_FILE)

print(f"✓ {result.num_clusters}個のクラスタを生成しました")

# 4. 結果表示
print("\n[4/4] 結果表示")
ConsolePresenter.show_cluster_result(result)
ConsolePresenter.show_image_tags(result.image_to_tags, max_display=20)

print("\n" + "=" * 60)
print("テスト完了！")
print("=" * 60)
print(f"\n出力ファイル:")
print(f"  - サムネイル: {THUMBNAIL_DIR}")
print(f"  - 埋め込みベクトル: {EMBEDDING_DIR}/embeddings.npy")
print(f"  - メタデータ: {EMBEDDING_DIR}/meta.json")
print(f"  - クラスタ結果: {CLUSTER_FILE}")
