"""ディレクトリスキャナー"""

from pathlib import Path
from typing import List, Set


class DirectoryScanner:
    """ディレクトリを再帰的にスキャンするクラス"""

    def __init__(self, extensions: Set[str]) -> None:
        """ディレクトリスキャナーを初期化

        Args:
            extensions: 対象とする拡張子のセット（小文字、ドット含む）
        """
        self._extensions = {ext.lower() for ext in extensions}

    def scan(self, directory: Path) -> List[Path]:
        """指定ディレクトリ以下のファイルを再帰的にスキャン

        Args:
            directory: スキャン対象のディレクトリパス

        Returns:
            マッチしたファイルパスのリスト

        Raises:
            ValueError: ディレクトリが存在しない、またはディレクトリではない場合
        """
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        matched_files: List[Path] = []

        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in self._extensions:
                matched_files.append(path)

        return sorted(matched_files)
