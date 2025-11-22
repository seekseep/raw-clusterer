# TODO リスト

## 進行中のタスク

なし

## 未着手のタスク

### 1. RAWファイルをJPGに変換する機能

- [ ] 1.1 Domain層の実装
  - [ ] 1.1.1 `RawImage`エンティティの作成 (`src/domain/models/raw_image.py`)
  - [ ] 1.1.2 `Thumbnail`エンティティの作成 (`src/domain/models/thumbnail.py`)
  - [ ] 1.1.3 `RawImageRepository`インターフェースの作成 (`src/domain/repositories/raw_image_repository.py`)
  - [ ] 1.1.4 `ThumbnailRepository`インターフェースの作成 (`src/domain/repositories/thumbnail_repository.py`)

- [ ] 1.2 Infrastructure層の実装
  - [ ] 1.2.1 `DirectoryScanner`の実装 (`src/infrastructure/file_system/directory_scanner.py`)
  - [ ] 1.2.2 `RawToJpegConverter`の実装 (`src/infrastructure/converters/raw_to_jpeg_converter.py`)
  - [ ] 1.2.3 `FileRawImageRepository`の実装 (`src/infrastructure/repositories/file_raw_image_repository.py`)
  - [ ] 1.2.4 `FileThumbnailRepository`の実装 (`src/infrastructure/repositories/file_thumbnail_repository.py`)

- [ ] 1.3 Application層の実装
  - [ ] 1.3.1 `GenerateThumbnails`ユースケースの実装 (`src/application/use_cases/generate_thumbnails.py`)

- [ ] 1.4 UI層の実装
  - [ ] 1.4.1 CLI設定の実装 (`src/ui/config/app_config.py`)
  - [ ] 1.4.2 `ConsolePresenter`の実装 (`src/ui/cli/presenters/console_presenter.py`)

- [ ] 1.5 テストとコミット
  - [ ] 1.5.1 単体テストの作成
  - [ ] 1.5.2 動作確認
  - [ ] 1.5.3 コミット（メッセージ: `feat: RAWファイルをJPEGサムネイルに変換する機能を実装`）

### 2. 詳細度レベル1: とても近い写真（ほぼ同じ被写体）を判定する機能

- [ ] 2.1 Domain層の実装
  - [ ] 2.1.1 `Embedding`値オブジェクトの作成 (`src/domain/models/embedding.py`)
  - [ ] 2.1.2 `Cluster`エンティティの作成 (`src/domain/models/cluster.py`)
  - [ ] 2.1.3 `EmbeddingRepository`インターフェースの作成 (`src/domain/repositories/embedding_repository.py`)
  - [ ] 2.1.4 `ClusterRepository`インターフェースの作成 (`src/domain/repositories/cluster_repository.py`)
  - [ ] 2.1.5 `FeatureExtractionService`ドメインサービスの作成 (`src/domain/services/feature_extraction_service.py`)
  - [ ] 2.1.6 `ClusteringService`ドメインサービスの作成（詳細度1用） (`src/domain/services/clustering_service.py`)

- [ ] 2.2 Infrastructure層の実装
  - [ ] 2.2.1 ResNet50モデルラッパーの実装 (`src/infrastructure/ml/models/resnet_model.py`)
  - [ ] 2.2.2 MiniBatchKMeansクラスタラーの実装（詳細度1: 多クラスタ） (`src/infrastructure/ml/clustering/kmeans_clusterer.py`)
  - [ ] 2.2.3 `NumpyEmbeddingRepository`の実装 (`src/infrastructure/repositories/numpy_embedding_repository.py`)
  - [ ] 2.2.4 `JsonClusterRepository`の実装 (`src/infrastructure/repositories/json_cluster_repository.py`)

- [ ] 2.3 Application層の実装
  - [ ] 2.3.1 `ExtractFeatures`ユースケースの実装 (`src/application/use_cases/extract_features.py`)
  - [ ] 2.3.2 `ClusterImages`ユースケースの実装（詳細度1） (`src/application/use_cases/cluster_images.py`)
  - [ ] 2.3.3 `ClusterResult` DTOの作成 (`src/application/dto/cluster_result.py`)

- [ ] 2.4 UI層の実装
  - [ ] 2.4.1 クラスタリング結果の標準出力フォーマッターを`ConsolePresenter`に追加

- [ ] 2.5 テストとコミット
  - [ ] 2.5.1 単体テストの作成
  - [ ] 2.5.2 動作確認
  - [ ] 2.5.3 コミット（メッセージ: `feat: 詳細度レベル1（ほぼ同じ被写体）のクラスタリング機能を実装`）

### 3. 詳細度レベル2: 近い写真（同じ場所、似た被写体）を判定する機能

- [ ] 3.1 Domain層の実装
  - [ ] 3.1.1 `ClusteringService`に詳細度2用のロジックを追加

- [ ] 3.2 Infrastructure層の実装
  - [ ] 3.2.1 HDBSCANクラスタラーの実装（詳細度2: 少クラスタ） (`src/infrastructure/ml/clustering/hdbscan_clusterer.py`)
  - [ ] 3.2.2 または KMeans で少ないクラスタ数での実装

- [ ] 3.3 Application層の実装
  - [ ] 3.3.1 `ClusterImages`ユースケースに詳細度2のロジックを追加

- [ ] 3.4 UI層の実装
  - [ ] 3.4.1 詳細度2の結果出力フォーマッターを追加

- [ ] 3.5 テストとコミット
  - [ ] 3.5.1 単体テストの作成
  - [ ] 3.5.2 動作確認
  - [ ] 3.5.3 コミット（メッセージ: `feat: 詳細度レベル2（同じ場所・似た被写体）のクラスタリング機能を実装`）

### 4. 各ファイルに生成するタグを標準出力に出力する機能

- [ ] 4.1 Application層の実装
  - [ ] 4.1.1 タグ生成ロジックを`ClusterImages`ユースケースに追加
  - [ ] 4.1.2 詳細度1と詳細度2の両方のタグを生成

- [ ] 4.2 UI層の実装
  - [ ] 4.2.1 タグ出力フォーマッターを`ConsolePresenter`に追加
  - [ ] 4.2.2 ファイル名とタグのマッピングを表形式で出力

- [ ] 4.3 テストとコミット
  - [ ] 4.3.1 単体テストの作成
  - [ ] 4.3.2 動作確認
  - [ ] 4.3.3 コミット（メッセージ: `feat: クラスタリング結果に基づくタグを標準出力に表示する機能を実装`）

### 5. XMPファイルを生成する機能

- [ ] 5.1 Domain層の実装
  - [ ] 5.1.1 `XmpMetadata`エンティティの作成 (`src/domain/models/xmp_metadata.py`)
  - [ ] 5.1.2 `XmpRepository`インターフェースの作成 (`src/domain/repositories/xmp_repository.py`)

- [ ] 5.2 Infrastructure層の実装
  - [ ] 5.2.1 `FileXmpRepository`の実装 (`src/infrastructure/repositories/file_xmp_repository.py`)
  - [ ] 5.2.2 XMPファイルの読み込み・書き込み・マージ処理の実装

- [ ] 5.3 Application層の実装
  - [ ] 5.3.1 `UpdateXmpMetadata`ユースケースの実装 (`src/application/use_cases/update_xmp_metadata.py`)
  - [ ] 5.3.2 詳細度1と詳細度2の両方のタグをXMPに書き込み

- [ ] 5.4 テストとコミット
  - [ ] 5.4.1 単体テストの作成
  - [ ] 5.4.2 動作確認
  - [ ] 5.4.3 コミット（メッセージ: `feat: クラスタリング結果をXMPメタデータとして書き込む機能を実装`）

### 6. 全体統合とCLI完成

- [ ] 6.1 Application層の実装
  - [ ] 6.1.1 `OrganizeRawImages`ユースケースの実装（全体orchestration） (`src/application/use_cases/organize_raw_images.py`)

- [ ] 6.2 UI層の実装
  - [ ] 6.2.1 `OrganizeCommand`の実装 (`src/ui/cli/commands/organize_command.py`)
  - [ ] 6.2.2 `main.py`エントリーポイントの実装 (`src/ui/cli/main.py`)
  - [ ] 6.2.3 CLIオプション（--size, --clusters, --model, --dry-run）の実装

- [ ] 6.3 テストとコミット
  - [ ] 6.3.1 統合テストの作成
  - [ ] 6.3.2 E2Eテストの実施
  - [ ] 6.3.3 コミット（メッセージ: `feat: 全ユースケースを統合したCLIコマンドを実装`）

### 7. ドキュメント整備

- [ ] 7.1 README.mdに使用方法を追記
- [ ] 7.2 各層のアーキテクチャ説明を追記
- [ ] 7.3 コミット（メッセージ: `docs: 使用方法とアーキテクチャ説明をREADMEに追加`）

## 完了したタスク

なし

---

## 注意事項

- このTODOリストは常に最新の状態に保つこと
- 各タスク完了時に進捗を更新すること
- コミット単位で作業を区切り、適切なコミットメッセージを付与すること
