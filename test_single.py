"""単一ファイルテスト"""

from pathlib import Path

from src.domain.models.raw_image import RawImage
from src.infrastructure.converters.raw_to_jpeg_converter import RawToJpegConverter

# テスト用RAW画像
raw_path = Path("/Users/seekseep/Pictures/レタッチ/20251112_兵庫前期/DSC00762.ARW")
output_dir = Path("outputs/test_single")

print(f"Testing with: {raw_path}")

# RAW画像エンティティ作成
raw_image = RawImage(raw_path)
print(f"Created RawImage: {raw_image}")

# 変換器作成
converter = RawToJpegConverter(output_dir=output_dir, size=512)
print(f"Output directory: {output_dir}")

# 変換実行
print("Converting...")
thumbnail = converter.convert(raw_image)

if thumbnail:
    print(f"✓ Success! Thumbnail saved to: {thumbnail.path}")
    print(f"  Size: {thumbnail.size}px")
    print(f"  Exists: {thumbnail.exists}")
else:
    print("✗ Failed to convert")
