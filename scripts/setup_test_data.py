"""テストデータのセットアップスクリプト"""

import shutil
from pathlib import Path

# ソースディレクトリ
SOURCE_DIR = Path("/Users/seekseep/Pictures/レタッチ/20251112_兵庫前期")
# テストデータディレクトリ
TEST_DATA_DIR = Path("test_data/raw_images")

# 32枚のファイルをコピー
TARGET_COUNT = 32
FILE_START = 762

print(f"Setting up test data...")
print(f"Source: {SOURCE_DIR}")
print(f"Destination: {TEST_DATA_DIR}")

# ディレクトリ作成
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ファイルをコピー
copied_count = 0
for i in range(FILE_START, FILE_START + TARGET_COUNT):
    source_file = SOURCE_DIR / f"DSC00{i}.ARW"

    if source_file.exists():
        dest_file = TEST_DATA_DIR / source_file.name
        shutil.copy2(source_file, dest_file)
        copied_count += 1
        print(f"  ✓ Copied: {source_file.name}")
    else:
        print(f"  ⚠️  Not found: {source_file.name}")

print(f"\nCopied {copied_count} files to {TEST_DATA_DIR}")

# 確認
files = sorted(TEST_DATA_DIR.glob("*.ARW"))
print(f"\nTotal files in test_data: {len(files)}")
