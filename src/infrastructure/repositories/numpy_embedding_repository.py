"""Numpy形式の埋め込みベクトルリポジトリ"""

import json
from pathlib import Path
from typing import List

import numpy as np

from src.domain.models.embedding import Embedding
from src.domain.repositories.embedding_repository import EmbeddingRepository


class NumpyEmbeddingRepository(EmbeddingRepository):
    """Numpy形式で埋め込みベクトルを保存・読み込むリポジトリ"""

    def save_all(self, embeddings: List[Embedding], output_path: Path) -> None:
        """埋め込みベクトルを一括保存

        Args:
            embeddings: 保存する埋め込みベクトルのリスト
            output_path: 出力先ディレクトリパス
        """
        output_path.mkdir(parents=True, exist_ok=True)

        # ベクトルをnumpy配列として保存
        vectors = np.array([emb.vector for emb in embeddings])
        np.save(output_path / "embeddings.npy", vectors)

        # メタデータ（画像ID、モデル名）をJSON形式で保存
        metadata = {
            "image_ids": [emb.image_id for emb in embeddings],
            "model_name": embeddings[0].model_name if embeddings else None,
            "dimension": embeddings[0].dimension if embeddings else 0,
            "count": len(embeddings),
        }

        with open(output_path / "meta.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def load_all(self, input_path: Path) -> List[Embedding]:
        """埋め込みベクトルを一括読み込み

        Args:
            input_path: 読み込み元ディレクトリパス

        Returns:
            埋め込みベクトルのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
        """
        embeddings_file = input_path / "embeddings.npy"
        metadata_file = input_path / "meta.json"

        if not embeddings_file.exists():
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")

        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        # ベクトルを読み込み
        vectors = np.load(embeddings_file)

        # メタデータを読み込み
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Embeddingオブジェクトのリストを構築
        embeddings: List[Embedding] = []
        for i, image_id in enumerate(metadata["image_ids"]):
            embedding = Embedding(
                image_id=image_id,
                vector=vectors[i],
                model_name=metadata.get("model_name"),
            )
            embeddings.append(embedding)

        return embeddings

    def exists(self, path: Path) -> bool:
        """埋め込みベクトルファイルが存在するか確認

        Args:
            path: 確認するディレクトリパス

        Returns:
            存在する場合True
        """
        embeddings_file = path / "embeddings.npy"
        metadata_file = path / "meta.json"
        return embeddings_file.exists() and metadata_file.exists()
