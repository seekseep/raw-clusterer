"""XMP生成機能のテスト"""

from pathlib import Path

from src.application.use_cases.cluster_images import ClusterImages
from src.application.use_cases.extract_features import ExtractFeatures
from src.application.use_cases.generate_thumbnails import GenerateThumbnails
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

# パス設定（テストデータのコピーを使用）
SOURCE_DIR = Path("test_data/raw_images")
TEST_DIR = Path("outputs/test_xmp")
RAW_DIR = TEST_DIR / "raw_images"
THUMBNAIL_DIR = TEST_DIR / "thumbs"
EMBEDDING_DIR = TEST_DIR
CLUSTER_FILE_FINE = TEST_DIR / "clusters_fine.json"
CLUSTER_FILE_COARSE = TEST_DIR / "clusters_coarse.json"

print("=" * 70)
print("XMP生成機能テスト")
print("=" * 70)

# RAW画像をコピー
print("\n[Setup] RAW画像をテストディレクトリにコピー")
print("-" * 70)
import shutil

RAW_DIR.mkdir(parents=True, exist_ok=True)
for src_file in SOURCE_DIR.glob("*.ARW"):
    dest_file = RAW_DIR / src_file.name
    if not dest_file.exists():
        shutil.copy2(src_file, dest_file)

print(f"Copied RAW files to {RAW_DIR}")

# 1. サムネイル生成
print("\n[Step 1/5] サムネイル生成")
print("-" * 70)
raw_repository = FileRawImageRepository()
thumbnail_repository = FileThumbnailRepository()
converter = RawToJpegConverter(output_dir=THUMBNAIL_DIR, size=512, base_dir=RAW_DIR)

use_case_thumbnails = GenerateThumbnails(raw_repository, thumbnail_repository, converter)
thumbnails = use_case_thumbnails.execute(RAW_DIR)
print(f"✓ Generated {len(thumbnails)} thumbnails")

# 2. 特徴抽出
print("\n[Step 2/5] 特徴抽出")
print("-" * 70)
feature_extractor = ResNet50FeatureExtractor(device="cpu")
embedding_repository = NumpyEmbeddingRepository()

use_case_extract = ExtractFeatures(feature_extractor, embedding_repository)
embeddings = use_case_extract.execute(thumbnails, EMBEDDING_DIR, base_dir=RAW_DIR)
print(f"✓ Extracted {len(embeddings)} features")

# 3. クラスタリング（詳細度1 & 2）
print("\n[Step 3/5] クラスタリング")
print("-" * 70)

cluster_repository = JsonClusterRepository()

# 詳細度1: Fine（多クラスタ）
clusterer_fine = KMeansClusterer(n_clusters=8, random_state=42)
use_case_cluster_fine = ClusterImages(clusterer_fine, cluster_repository)
result_fine = use_case_cluster_fine.execute(
    embeddings, granularity=1, output_path=CLUSTER_FILE_FINE
)
print(f"✓ Fine clustering: {result_fine.num_clusters} clusters")

# 詳細度2: Coarse（少クラスタ）
clusterer_coarse = KMeansClusterer(n_clusters=4, random_state=42)
use_case_cluster_coarse = ClusterImages(clusterer_coarse, cluster_repository)
result_coarse = use_case_cluster_coarse.execute(
    embeddings, granularity=2, output_path=CLUSTER_FILE_COARSE
)
print(f"✓ Coarse clustering: {result_coarse.num_clusters} clusters")

# 4. XMP生成（Dry Run）
print("\n[Step 4/5] XMP生成（Dry Run）")
print("-" * 70)
xmp_repository = FileXmpRepository()
use_case_xmp = UpdateXmpMetadata(raw_repository, xmp_repository)

updated_dry = use_case_xmp.execute(
    RAW_DIR, cluster_results=[result_fine, result_coarse], dry_run=True
)

# 5. XMP生成（実際に書き込み）
print("\n[Step 5/5] XMP生成（実際に書き込み）")
print("-" * 70)
updated = use_case_xmp.execute(
    RAW_DIR, cluster_results=[result_fine, result_coarse], dry_run=False
)

# 結果確認
print("\n" + "=" * 70)
print("結果確認")
print("=" * 70)

xmp_files = list(RAW_DIR.glob("*.xmp"))
print(f"\n生成されたXMPファイル: {len(xmp_files)}個")

# 最初の3つのXMPファイルの内容を表示
print("\nサンプル（最初の3ファイル）:")
for xmp_file in sorted(xmp_files)[:3]:
    print(f"\n📄 {xmp_file.name}")
    print(f"   サイズ: {xmp_file.stat().st_size} bytes")

    # XMPの内容を読み込んで表示
    with open(xmp_file, "r") as f:
        content = f.read()
        # キーワード部分を抽出表示
        if "dc:subject" in content:
            print(f"   ✓ dc:subject (キーワード) 含まれています")
        if "lr:hierarchicalSubject" in content:
            print(f"   ✓ lr:hierarchicalSubject (階層キーワード) 含まれています")

print("\n" + "=" * 70)
print("テスト完了！")
print("=" * 70)
print(f"\n📊 統計:")
print(f"  RAW画像: {len(thumbnails)}枚")
print(f"  XMPファイル: {len(xmp_files)}個")
print(f"  詳細度1クラスタ: {result_fine.num_clusters}")
print(f"  詳細度2クラスタ: {result_coarse.num_clusters}")

print(f"\n📁 出力先:")
print(f"  RAW & XMP: {RAW_DIR}")
print(f"  サムネイル: {THUMBNAIL_DIR}")
print(f"  クラスタ: {CLUSTER_FILE_FINE}, {CLUSTER_FILE_COARSE}")
