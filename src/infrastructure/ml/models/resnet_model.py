"""ResNet50特徴抽出モデル"""

from pathlib import Path

import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

from src.domain.services.feature_extraction_service import FeatureExtractionService


class ResNet50FeatureExtractor(FeatureExtractionService):
    """ResNet50を使用した特徴抽出サービス"""

    def __init__(self, device: str = "cpu") -> None:
        """ResNet50特徴抽出器を初期化

        Args:
            device: 使用するデバイス（"cpu" or "cuda"）
        """
        self.device = torch.device(device)

        # ResNet50の事前学習済みモデルをロード
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

        # 最終層（分類層）を削除して特徴抽出のみ行う
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.to(self.device)
        self.model.eval()

        # 画像の前処理
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def extract(self, image_path: Path) -> np.ndarray:
        """画像から特徴ベクトルを抽出

        Args:
            image_path: 画像ファイルのパス

        Returns:
            特徴ベクトル（2048次元の1次元numpy配列）

        Raises:
            FileNotFoundError: 画像ファイルが存在しない場合
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # 画像を読み込んで前処理
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 特徴抽出
        with torch.no_grad():
            features = self.model(image_tensor)

        # (1, 2048, 1, 1) -> (2048,) に変換
        feature_vector = features.squeeze().cpu().numpy()

        return feature_vector

    def get_model_name(self) -> str:
        """使用しているモデル名を取得

        Returns:
            モデル名
        """
        return "resnet50"
