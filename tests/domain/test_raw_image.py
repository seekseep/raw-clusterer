"""RAW画像エンティティのテスト"""

import tempfile
from pathlib import Path

import pytest

from src.domain.models.raw_image import RawImage


def test_raw_image_valid_file():
    """有効なRAWファイルでRawImageを作成できる"""
    with tempfile.NamedTemporaryFile(suffix=".cr2", delete=False) as f:
        temp_path = Path(f.name)

    try:
        raw_image = RawImage(temp_path)
        assert raw_image.path == temp_path
        assert raw_image.format == ".cr2"
        assert raw_image.filename == temp_path.name
        assert raw_image.stem == temp_path.stem
    finally:
        temp_path.unlink()


def test_raw_image_file_not_exists():
    """存在しないファイルパスでValueErrorが発生"""
    non_existent = Path("/non/existent/file.cr2")
    with pytest.raises(ValueError, match="does not exist"):
        RawImage(non_existent)


def test_raw_image_unsupported_format():
    """サポート外の形式でValueErrorが発生"""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Unsupported RAW format"):
            RawImage(temp_path)
    finally:
        temp_path.unlink()


def test_raw_image_equality():
    """RawImageの等価性テスト"""
    with tempfile.NamedTemporaryFile(suffix=".nef", delete=False) as f:
        temp_path = Path(f.name)

    try:
        raw1 = RawImage(temp_path)
        raw2 = RawImage(temp_path)
        assert raw1 == raw2
        assert hash(raw1) == hash(raw2)
    finally:
        temp_path.unlink()
