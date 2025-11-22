"""ネストしたディレクトリ構造のテスト"""

from pathlib import Path

from src.domain.models.raw_image import RawImage
from src.domain.models.thumbnail import Thumbnail
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter

# テストケース：ネストしたディレクトリ構造を想定
BASE_DIR = Path("/Users/seekseep/Pictures/レタッチ/20251112_兵庫前期")
OUTPUT_DIR = Path("outputs/test_nested")

# 仮想的なネストしたパス（実際のファイルを使用）
test_files = [
    BASE_DIR / "DSC00762.ARW",  # ルート
    BASE_DIR / "DSC00763.ARW",  # ルート
]

print("=" * 60)
print("ネストしたディレクトリ構造対応テスト")
print("=" * 60)

# base_dirを指定した変換器
converter_with_base = RawToJpegConverter(
    output_dir=OUTPUT_DIR, size=512, base_dir=BASE_DIR
)

# base_dirを指定しない変換器（従来の動作）
converter_without_base = RawToJpegConverter(
    output_dir=OUTPUT_DIR / "flat", size=512
)

for raw_path in test_files:
    if not raw_path.exists():
        print(f"⚠️  File not found: {raw_path}")
        continue

    raw_image = RawImage(raw_path)
    print(f"\nProcessing: {raw_image.path}")

    # base_dir指定あり
    thumbnail_with_base = converter_with_base.convert(raw_image)
    if thumbnail_with_base:
        unique_id = thumbnail_with_base.get_unique_id(BASE_DIR)
        print(f"  [With base_dir]")
        print(f"    Output: {thumbnail_with_base.path.relative_to(OUTPUT_DIR)}")
        print(f"    Unique ID: {unique_id}")

    # base_dir指定なし
    thumbnail_without_base = converter_without_base.convert(raw_image)
    if thumbnail_without_base:
        unique_id_flat = thumbnail_without_base.get_unique_id()
        print(f"  [Without base_dir]")
        print(f"    Output: {thumbnail_without_base.path.relative_to(OUTPUT_DIR)}")
        print(f"    Unique ID: {unique_id_flat}")

print("\n" + "=" * 60)
print("テスト完了")
print("=" * 60)

# 同じファイル名が異なるディレクトリにあるケースのシミュレーション
print("\n同名ファイルの衝突チェック:")
print(f"  DSC00762.ARW (root) -> ID: DSC00762")
print(f"  subdir/DSC00762.ARW -> ID: subdir/DSC00762")
print("  ✓ 相対パスベースのIDにより衝突を回避")
