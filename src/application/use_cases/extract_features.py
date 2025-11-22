"""特徴抽出ユースケース"""

from pathlib import Path
from typing import List, Optional

from src.domain.models.embedding import Embedding
from src.domain.models.thumbnail import Thumbnail
from src.domain.repositories.embedding_repository import EmbeddingRepository
from src.domain.services.feature_extraction_service import FeatureExtractionService


class ExtractFeatures:
    """サムネイル画像から特徴ベクトルを抽出するユースケース"""

    def __init__(
        self,
        feature_extractor: FeatureExtractionService,
        embedding_repository: EmbeddingRepository,
    ) -> None:
        """特徴抽出ユースケースを初期化

        Args:
            feature_extractor: 特徴抽出サービス
            embedding_repository: 埋め込みベクトルリポジトリ
        """
        self._feature_extractor = feature_extractor
        self._embedding_repository = embedding_repository

    def execute(
        self, thumbnails: List[Thumbnail], output_dir: Path, base_dir: Optional[Path] = None
    ) -> List[Embedding]:
        """サムネイル画像から特徴ベクトルを抽出

        Args:
            thumbnails: サムネイルのリスト
            output_dir: 埋め込みベクトルの出力先ディレクトリ
            base_dir: RAW画像のベースディレクトリ（相対パス計算用）

        Returns:
            埋め込みベクトルのリスト
        """
        print(f"\nExtracting features from {len(thumbnails)} thumbnails...")
        print(f"Model: {self._feature_extractor.get_model_name()}")

        embeddings: List[Embedding] = []

        for i, thumbnail in enumerate(thumbnails, 1):
            if i % 10 == 0 or i == len(thumbnails):
                print(f"  Progress: {i}/{len(thumbnails)}")

            # 特徴ベクトルを抽出
            vector = self._feature_extractor.extract(thumbnail.path)

            # 一意のIDを取得（ネストしたディレクトリ構造に対応）
            image_id = thumbnail.get_unique_id(base_dir)

            # Embeddingオブジェクトを作成
            embedding = Embedding(
                image_id=image_id,
                vector=vector,
                model_name=self._feature_extractor.get_model_name(),
            )
            embeddings.append(embedding)

        # 埋め込みベクトルを保存
        self._embedding_repository.save_all(embeddings, output_dir)
        print(f"Saved {len(embeddings)} embeddings to {output_dir}")

        return embeddings
