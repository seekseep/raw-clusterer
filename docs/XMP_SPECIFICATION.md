# XMP (Extensible Metadata Platform) 仕様書

## 概要

XMP（Extensible Metadata Platform）は、Adobe Systems Inc.が開発し、現在はISO標準（ISO 16684-1:2019）として定められているメタデータ管理の標準規格です。デジタルドキュメントやデータセットに対する標準化されたメタデータの作成、処理、交換を可能にします。

## XMPの3つの基本要素

XMP仕様は以下の3つの基本的な側面から構成されています：

### 1. データモデル (Data Model)
- XMPメタデータ項目の形式を定義する抽象モデル
- リソースに対して記述できる情報の構造を規定

### 2. シリアライゼーション形式 (Serialization Format)
- W3C RDF/XML構文のサブセットを使用
- RDF（Resource Description Framework）グラフをXML形式で表現

### 3. コアプロパティ (Core Properties)
- 幅広いファイル形式や利用領域に適用可能なメタデータ項目の集合
- 標準的な名前空間とプロパティを定義

## XMPファイルの基本構造

### XMPパケットの完全な構造

```xml
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
      xmlns:dc="http://purl.org/dc/elements/1.1/"
      xmlns:xmp="http://ns.adobe.com/xap/1.0/"
      xmlns:exif="http://ns.adobe.com/exif/1.0/"
      xmlns:tiff="http://ns.adobe.com/tiff/1.0/">

      <!-- メタデータプロパティをここに記述 -->

    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>
```

### 構造の各要素

#### 1. XMPパケットヘッダー
```xml
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
```
- `begin`属性：BOM（Byte Order Mark: U+FEFF）を含むことができる
- `id`属性：固定値（パケット識別子）

#### 2. xmpmeta要素
```xml
<x:xmpmeta xmlns:x="adobe:ns:meta/">
```
- メタデータブロックのラッパー要素
- 名前空間：`adobe:ns:meta/`

#### 3. RDF要素
```xml
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
```
- RDFグラフのルート要素
- RDF構文の名前空間を宣言

#### 4. Description要素
```xml
<rdf:Description rdf:about="" ...>
```
- リソースのプロパティを記述
- `rdf:about`属性：リソースを識別（空文字列は現在のファイルを示す）
- 複数の名前空間を宣言して使用可能

#### 5. XMPパケットトレイラー
```xml
<?xpacket end="w"?>
```
- `end="w"`：書き込み可能（writable）なパケット
- `end="r"`：読み取り専用（read-only）なパケット

## 主要な名前空間（Namespaces）

XMPでは、プロパティ名の衝突を避けるために名前空間URIを使用します。

### 1. Dublin Core (dc:)
**名前空間URI:** `http://purl.org/dc/elements/1.1/`

一般的な記述メタデータの標準。

主要なプロパティ：
- `dc:title` - タイトル（lang-alt型）
- `dc:creator` - 作成者（seq配列）
- `dc:description` - 説明（lang-alt型）
- `dc:subject` - キーワード/タグ（bag配列）
- `dc:format` - MIMEタイプ
- `dc:rights` - 著作権情報（lang-alt型）

### 2. XMP Basic (xmp:)
**名前空間URI:** `http://ns.adobe.com/xap/1.0/`

Adobeのコアメタデータ。

主要なプロパティ：
- `xmp:CreateDate` - 作成日時
- `xmp:ModifyDate` - 更新日時
- `xmp:MetadataDate` - メタデータ更新日時
- `xmp:CreatorTool` - 作成ツール名
- `xmp:Rating` - 評価（1-5の整数）
- `xmp:Label` - ラベル（文字列）

### 3. EXIF (exif:)
**名前空間URI:** `http://ns.adobe.com/exif/1.0/`

画像の技術的メタデータ。

主要なプロパティ：
- `exif:DateTimeOriginal` - 撮影日時
- `exif:ExposureTime` - 露出時間
- `exif:FNumber` - F値
- `exif:ISO` - ISO感度
- `exif:FocalLength` - 焦点距離
- `exif:Flash` - フラッシュ使用

### 4. TIFF (tiff:)
**名前空間URI:** `http://ns.adobe.com/tiff/1.0/`

画像ファイル形式メタデータ。

主要なプロパティ：
- `tiff:Make` - カメラメーカー
- `tiff:Model` - カメラモデル
- `tiff:Orientation` - 画像の向き
- `tiff:XResolution` - 横解像度
- `tiff:YResolution` - 縦解像度

### 5. Lightroom (lr:)
**名前空間URI:** `http://ns.adobe.com/lightroom/1.0/`

Adobe Lightroom固有のメタデータ。

主要なプロパティ：
- `lr:hierarchicalSubject` - 階層的キーワード（bag配列）

### 6. IPTC Core (Iptc4xmpCore:)
**名前空間URI:** `http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/`

ニュース・メディア向けメタデータ。

主要なプロパティ：
- `Iptc4xmpCore:Location` - 場所
- `Iptc4xmpCore:CountryCode` - 国コード
- `Iptc4xmpCore:CreatorContactInfo` - 作成者連絡先

## データ型

XMPプロパティは以下のデータ型を持ちます：

### 単純型（Simple Types）
- **string**: 文字列
- **integer**: 整数
- **real**: 浮動小数点数
- **boolean**: true/false
- **date**: ISO 8601形式の日時（例：`2025-11-22T10:30:00+09:00`）

### 配列型（Array Types）
- **Bag（無順序配列）**: 順序が重要でない値の集合
- **Seq（順序付き配列）**: 順序が重要な値の集合
- **Alt（代替配列）**: 代替値の集合（通常は言語別）

### 構造型（Structure Types）
- 複数のフィールドを持つ複合データ

## プロパティの記述方法

### 1. 単純プロパティ
```xml
<xmp:CreatorTool>Adobe Photoshop CC 2024</xmp:CreatorTool>
<xmp:Rating>5</xmp:Rating>
```

または属性形式：
```xml
<rdf:Description
  xmp:CreatorTool="Adobe Photoshop CC 2024"
  xmp:Rating="5">
```

### 2. 言語代替配列（lang-alt）
複数言語のテキストを記述する場合：

```xml
<dc:title>
  <rdf:Alt>
    <rdf:li xml:lang="x-default">My Photo Title</rdf:li>
    <rdf:li xml:lang="ja-JP">私の写真タイトル</rdf:li>
    <rdf:li xml:lang="en-US">My Photo Title</rdf:li>
  </rdf:Alt>
</dc:title>
```

### 3. Bag配列（無順序）
キーワード/タグの記述：

```xml
<dc:subject>
  <rdf:Bag>
    <rdf:li>ai_cluster_001</rdf:li>
    <rdf:li>ai_cluster_level1</rdf:li>
    <rdf:li>landscape</rdf:li>
    <rdf:li>nature</rdf:li>
  </rdf:Bag>
</dc:subject>
```

### 4. Seq配列（順序付き）
作成者リスト：

```xml
<dc:creator>
  <rdf:Seq>
    <rdf:li>John Doe</rdf:li>
    <rdf:li>Jane Smith</rdf:li>
  </rdf:Seq>
</dc:creator>
```

### 5. 階層的キーワード（Lightroom用）
```xml
<lr:hierarchicalSubject>
  <rdf:Bag>
    <rdf:li>AI|cluster|001</rdf:li>
    <rdf:li>AI|cluster|level1|001</rdf:li>
    <rdf:li>Location|Japan|Tokyo</rdf:li>
  </rdf:Bag>
</lr:hierarchicalSubject>
```

## このプロジェクトでの使用タグ

本プロジェクト（RAW画像自動分類ツール）では、以下のXMPタグを使用します：

### 1. フラットキーワード（dc:subject）
クラスタリング結果をフラットなキーワードとして記述：

```xml
<dc:subject>
  <rdf:Bag>
    <rdf:li>ai_cluster_level1_001</rdf:li>
    <rdf:li>ai_cluster_level2_003</rdf:li>
  </rdf:Bag>
</dc:subject>
```

### 2. 階層的キーワード（lr:hierarchicalSubject）
Lightroomで階層表示されるキーワード：

```xml
<lr:hierarchicalSubject>
  <rdf:Bag>
    <rdf:li>AI|clustering|level1|001</rdf:li>
    <rdf:li>AI|clustering|level2|003</rdf:li>
  </rdf:Bag>
</lr:hierarchicalSubject>
```

### タグ付与の詳細

#### 詳細度レベル1（ほぼ同じ被写体）
- クラスタID例：`001`, `002`, `003`...
- フラットキーワード：`ai_cluster_level1_001`
- 階層キーワード：`AI|clustering|level1|001`

#### 詳細度レベル2（同じ場所・似た被写体）
- クラスタID例：`001`, `002`, `003`...
- フラットキーワード：`ai_cluster_level2_001`
- 階層キーワード：`AI|clustering|level2|001`

## XMPサイドカーファイル

### ファイル命名規則
RAW画像ファイルに対するXMPサイドカーファイルの命名：

**パターン1（推奨）:**
```
image001.arw → image001.xmp
image002.cr3 → image002.xmp
```

**パターン2（代替）:**
```
image001.arw → image001.arw.xmp
image002.cr3 → image002.cr3.xmp
```

Lightroomやその他の商用ソフトウェアとの互換性のため、**パターン1（拡張子を置換）** を推奨します。

### ファイルサイズ
- RAW画像：10-30 MB
- XMPサイドカー：約10 KB（メタデータ量に依存）

### XMPファイルの利点
1. **非破壊編集**: オリジナルRAWファイルを変更しない
2. **可搬性**: メタデータを個別ファイルとして管理
3. **互換性**: 複数のソフトウェア間でメタデータを共有
4. **バックアップ**: メタデータのみを独立してバックアップ可能

## Lightroomでの使用方法

### XMPメタデータの読み込み
1. Lightroomでカタログを開く
2. 対象画像を選択
3. メニュー：「メタデータ → メタデータをファイルから読み込み」を実行
4. XMPサイドカーファイルからメタデータが読み込まれる

### キーワードの確認
- 右パネルの「キーワード」セクションで確認
- `lr:hierarchicalSubject`は階層構造で表示される
- `dc:subject`はフラットリストで表示される

## 完全なXMPファイル例

本プロジェクトで生成するXMPサイドカーファイルの例：

```xml
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
      xmlns:dc="http://purl.org/dc/elements/1.1/"
      xmlns:xmp="http://ns.adobe.com/xap/1.0/"
      xmlns:lr="http://ns.adobe.com/lightroom/1.0/">

      <!-- メタデータ更新日時 -->
      <xmp:MetadataDate>2025-11-22T10:30:00+09:00</xmp:MetadataDate>

      <!-- フラットキーワード -->
      <dc:subject>
        <rdf:Bag>
          <rdf:li>ai_cluster_level1_001</rdf:li>
          <rdf:li>ai_cluster_level2_003</rdf:li>
        </rdf:Bag>
      </dc:subject>

      <!-- 階層的キーワード（Lightroom用） -->
      <lr:hierarchicalSubject>
        <rdf:Bag>
          <rdf:li>AI|clustering|level1|001</rdf:li>
          <rdf:li>AI|clustering|level2|003</rdf:li>
        </rdf:Bag>
      </lr:hierarchicalSubject>

    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>
```

## 既存XMPファイルの更新

既にXMPファイルが存在する場合は、以下のルールで更新します：

### 1. キーワードの追加
- 既存の`dc:subject`と`lr:hierarchicalSubject`を読み込み
- 新しいクラスタタグを追加
- **重複チェック**: 同じキーワードは追加しない

### 2. メタデータ日時の更新
- `xmp:MetadataDate`を現在日時に更新

### 3. その他のメタデータは保持
- タイトル、説明、評価など既存のメタデータは変更しない

## 実装時の注意事項

### 1. XML構文の正確性
- XML宣言、名前空間、要素の入れ子構造を正確に記述
- UTF-8エンコーディングを使用
- 特殊文字はエスケープ（`&`, `<`, `>`, `"`, `'`）

### 2. ファイル操作
- 既存XMPファイルを上書きする前にバックアップ推奨
- ファイル書き込み権限の確認
- 原子性（atomic write）の確保（一時ファイル経由で書き込み）

### 3. Lightroom互換性
- 名前空間URIを正確に記述
- `lr:hierarchicalSubject`の区切り文字は`|`（パイプ）
- Lightroomが認識できる最小構造を維持

### 4. パフォーマンス
- 大量のファイル処理時はバッチ処理を検討
- XMLパーサー（`xml.etree.ElementTree`など）を使用
- メモリ効率を考慮

## Pythonでの実装例

### XMLパーサーの使用
```python
import xml.etree.ElementTree as ET
from datetime import datetime

# 名前空間定義
NAMESPACES = {
    'x': 'adobe:ns:meta/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xmp': 'http://ns.adobe.com/xap/1.0/',
    'lr': 'http://ns.adobe.com/lightroom/1.0/'
}

# 名前空間を登録
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)
```

### 新規XMPファイルの生成
```python
def create_new_xmp(keywords: list[str], hierarchical_keywords: list[str]) -> str:
    """新規XMPファイルのXML文字列を生成"""

    # ルート要素
    xmpmeta = ET.Element('{adobe:ns:meta/}xmpmeta')
    rdf = ET.SubElement(xmpmeta, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')

    # Description要素
    desc = ET.SubElement(rdf, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
    desc.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')

    # メタデータ日時
    metadata_date = ET.SubElement(desc, '{http://ns.adobe.com/xap/1.0/}MetadataDate')
    metadata_date.text = datetime.now().isoformat()

    # dc:subject (フラットキーワード)
    if keywords:
        subject = ET.SubElement(desc, '{http://purl.org/dc/elements/1.1/}subject')
        bag = ET.SubElement(subject, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag')
        for keyword in keywords:
            li = ET.SubElement(bag, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li')
            li.text = keyword

    # lr:hierarchicalSubject (階層キーワード)
    if hierarchical_keywords:
        hier_subject = ET.SubElement(desc, '{http://ns.adobe.com/lightroom/1.0/}hierarchicalSubject')
        bag = ET.SubElement(hier_subject, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag')
        for keyword in hierarchical_keywords:
            li = ET.SubElement(bag, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li')
            li.text = keyword

    # XML文字列化
    xml_str = ET.tostring(xmpmeta, encoding='unicode')

    # XMPパケットヘッダー・トレイラーを追加
    return f'''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
{xml_str}
<?xpacket end="w"?>'''
```

## 参考資料

### 公式仕様
- **ISO 16684-1:2019**: Graphic technology — Extensible metadata platform (XMP) — Part 1: Data model, serialization and core properties
- **Adobe XMP Specifications**: https://developer.adobe.com/xmp/docs/XMPSpecifications/
- **XMP Documentation (GitHub)**: https://github.com/adobe/xmp-docs

### 技術リファレンス
- **ExifTool XMP Tags**: https://exiftool.org/TagNames/XMP.html
- **W3C RDF/XML Syntax**: https://www.w3.org/TR/rdf-syntax-grammar/
- **Dublin Core Metadata Initiative**: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/

### ツール
- **ExifTool**: コマンドラインからXMPメタデータを読み書きできる強力なツール
- **Adobe Lightroom**: XMPメタデータの視覚的な管理が可能
- **Python libraries**: `xml.etree.ElementTree`, `lxml`, `python-xmp-toolkit`

---

**最終更新**: 2025-11-22
**バージョン**: 1.0
**プロジェクト**: RAW画像自動分類ツール
