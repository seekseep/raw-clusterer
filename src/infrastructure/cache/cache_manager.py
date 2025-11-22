"""キャッシュ管理"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class CacheManager:
    """実行時のキャッシュを管理するクラス

    .cache/
    ├── mapping.json    # RAW画像とサムネイルの対応
    └── thumbnails/     # サムネイル画像
    """

    MAPPING_FILE_NAME = "mapping.json"
    THUMBNAILS_DIR_NAME = "thumbnails"

    def __init__(self, base_dir: Path, cache_dir: Optional[Path] = None) -> None:
        """キャッシュマネージャーを初期化

        Args:
            base_dir: 実行時のベースディレクトリ（絶対パス）
            cache_dir: キャッシュディレクトリ（指定しない場合はbase_dir/.cache）
        """
        self._base_dir = base_dir.resolve()
        self._cache_dir = cache_dir.resolve() if cache_dir else self._base_dir / ".cache"
        self._mapping_path = self._cache_dir / self.MAPPING_FILE_NAME
        self._thumbnails_dir = self._cache_dir / self.THUMBNAILS_DIR_NAME

    @property
    def cache_dir(self) -> Path:
        """キャッシュディレクトリのパスを取得"""
        return self._cache_dir

    @property
    def thumbnails_dir(self) -> Path:
        """サムネイルディレクトリのパスを取得"""
        return self._thumbnails_dir

    @property
    def mapping_path(self) -> Path:
        """マッピングファイルのパスを取得"""
        return self._mapping_path

    @property
    def base_dir(self) -> Path:
        """ベースディレクトリのパスを取得"""
        return self._base_dir

    def initialize(self) -> None:
        """キャッシュディレクトリを初期化"""
        # キャッシュディレクトリを作成
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._thumbnails_dir.mkdir(parents=True, exist_ok=True)

        # マッピングファイルが存在しない場合のみ作成
        if not self._mapping_path.exists():
            mapping = {}
            self._save_mapping(mapping)

    def load_mapping(self) -> Dict[str, str]:
        """マッピングを読み込み

        Returns:
            RAW相対パス → サムネイル相対パスのマッピング
        """
        if not self._mapping_path.exists():
            return {}

        try:
            with open(self._mapping_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # マッピングファイルが壊れている場合は削除して空のマッピングを返す
            if self._mapping_path.exists():
                self._mapping_path.unlink()
            return {}

    def _save_mapping(self, mapping: Dict[str, str]) -> None:
        """マッピングを保存

        Args:
            mapping: RAW相対パス → サムネイル相対パスのマッピング
        """
        try:
            with open(self._mapping_path, "w", encoding="utf-8") as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save mapping: {self._mapping_path}") from e

    def add_raw_thumbnail_mapping(
        self, raw_path: Path, thumbnail_path: Path
    ) -> None:
        """RAW画像とサムネイルの対応を追加

        Args:
            raw_path: RAW画像の絶対パス
            thumbnail_path: サムネイルの絶対パス
        """
        import fcntl
        import time

        # ファイルロックを使用して競合を回避
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # ロックファイルを使用
                lock_path = self._mapping_path.with_suffix(".lock")
                with open(lock_path, "w") as lock_file:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                    try:
                        mapping = self.load_mapping()

                        # ベースディレクトリからの相対パスを取得
                        try:
                            raw_relative = raw_path.relative_to(self._base_dir)
                            thumbnail_relative = thumbnail_path.relative_to(self._cache_dir)
                        except ValueError as e:
                            return

                        # マッピングを追加
                        mapping[str(raw_relative)] = str(thumbnail_relative)
                        self._save_mapping(mapping)
                        break
                    finally:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    raise Exception(f"Failed to update mapping after {max_retries} attempts") from e

    def get_thumbnail_path(self, raw_path: Path) -> Optional[Path]:
        """RAW画像に対応するサムネイルパスを取得

        Args:
            raw_path: RAW画像の絶対パス

        Returns:
            サムネイルの絶対パス、存在しない場合はNone
        """
        mapping = self.load_mapping()

        try:
            raw_relative = str(raw_path.relative_to(self._base_dir))
        except ValueError:
            return None

        thumbnail_relative = mapping.get(raw_relative)
        if thumbnail_relative is None:
            return None

        return self._cache_dir / thumbnail_relative

    def exists(self) -> bool:
        """キャッシュディレクトリが存在するか確認

        Returns:
            存在する場合True
        """
        return self._cache_dir.exists() and self._mapping_path.exists()

    def clear(self) -> None:
        """キャッシュディレクトリを削除"""
        if self._cache_dir.exists():
            try:
                shutil.rmtree(self._cache_dir)
            except Exception as e:
                raise Exception(f"Failed to clear cache: {self._cache_dir}") from e

    def get_all_mappings(self) -> Dict[str, str]:
        """全てのRAW→サムネイルマッピングを取得

        Returns:
            RAW相対パス → サムネイル相対パスのマッピング
        """
        return self.load_mapping()
