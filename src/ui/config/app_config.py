"""アプリケーション設定"""

from pathlib import Path


class AppConfig:
    """アプリケーション設定を管理するクラス"""

    DEFAULT_THUMBNAIL_SIZE = 512
    DEFAULT_OUTPUT_DIR = Path("outputs/thumbs")
    DEFAULT_NUM_CLUSTERS = 50

    def __init__(
        self,
        thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        num_clusters: int = DEFAULT_NUM_CLUSTERS,
    ) -> None:
        """アプリケーション設定を初期化

        Args:
            thumbnail_size: サムネイルの長辺サイズ
            output_dir: 出力先ディレクトリ
            num_clusters: クラスタ数
        """
        self.thumbnail_size = thumbnail_size
        self.output_dir = output_dir
        self.num_clusters = num_clusters

    @classmethod
    def from_args(cls, args) -> "AppConfig":
        """コマンドライン引数から設定を作成

        Args:
            args: argparseのNamespaceオブジェクト

        Returns:
            アプリケーション設定
        """
        output = getattr(args, "output", None)
        return cls(
            thumbnail_size=getattr(args, "size", cls.DEFAULT_THUMBNAIL_SIZE),
            output_dir=Path(output) if output else cls.DEFAULT_OUTPUT_DIR,
            num_clusters=getattr(args, "clusters", cls.DEFAULT_NUM_CLUSTERS),
        )
