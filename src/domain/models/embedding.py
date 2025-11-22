"""画像埋め込みベクトル値オブジェクト"""

from typing import Optional

import numpy as np


class Embedding:
    """画像の特徴ベクトルを表す値オブジェクト

    Attributes:
        image_id: 画像の識別子（ファイル名など）
        vector: 特徴ベクトル（numpy配列）
        model_name: 使用したモデル名
    """

    def __init__(
        self, image_id: str, vector: np.ndarray, model_name: Optional[str] = None
    ) -> None:
        """埋め込みベクトルを初期化

        Args:
            image_id: 画像の識別子
            vector: 特徴ベクトル（1次元のnumpy配列）
            model_name: 使用したモデル名

        Raises:
            ValueError: ベクトルが1次元でない、または空の場合
        """
        if vector.ndim != 1:
            raise ValueError(f"Vector must be 1-dimensional, got {vector.ndim}")

        if len(vector) == 0:
            raise ValueError("Vector cannot be empty")

        self.image_id = image_id
        self.vector = vector.astype(np.float32)
        self.model_name = model_name

    @property
    def dimension(self) -> int:
        """ベクトルの次元数を取得"""
        return len(self.vector)

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, Embedding):
            return False
        return (
            self.image_id == other.image_id
            and np.array_equal(self.vector, other.vector)
            and self.model_name == other.model_name
        )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"Embedding(image_id={self.image_id}, "
            f"dimension={self.dimension}, model={self.model_name})"
        )
