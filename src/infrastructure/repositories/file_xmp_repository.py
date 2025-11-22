"""ファイルシステムベースのXMPリポジトリ実装"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Set

from src.domain.models.raw_image import RawImage
from src.domain.models.xmp_metadata import XmpMetadata
from src.domain.repositories.xmp_repository import XmpRepository


class FileXmpRepository(XmpRepository):
    """ファイルシステムを使用したXMPリポジトリの実装"""

    # XMP名前空間
    NAMESPACES = {
        "x": "adobe:ns:meta/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "dc": "http://purl.org/dc/elements/1.1/",
        "lr": "http://ns.adobe.com/lightroom/1.0/",
    }

    def __init__(self) -> None:
        """ファイルベースXMPリポジトリを初期化"""
        # XML名前空間をElementTreeに登録
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)

    def load(self, xmp_path: Path) -> Optional[XmpMetadata]:
        """XMPファイルを読み込み

        Args:
            xmp_path: XMPファイルのパス

        Returns:
            XMPメタデータ、ファイルが存在しない場合はNone
        """
        if not xmp_path.exists():
            return None

        try:
            tree = ET.parse(xmp_path)
            root = tree.getroot()

            # RAW画像パスを取得
            raw_path = xmp_path.with_suffix(".ARW")  # 拡張子は動的に判定すべきだが簡易実装
            if not raw_path.exists():
                # 他の拡張子も試す
                for ext in [".CR2", ".CR3", ".NEF", ".RAF", ".DNG"]:
                    raw_path = xmp_path.with_suffix(ext)
                    if raw_path.exists():
                        break

            raw_image = RawImage(raw_path)

            # キーワードを抽出
            keywords = self._extract_keywords(root)
            hierarchical_keywords = self._extract_hierarchical_keywords(root)

            return XmpMetadata(
                raw_image=raw_image,
                keywords=keywords,
                hierarchical_keywords=hierarchical_keywords,
            )

        except Exception as e:
            print(f"Failed to load XMP: {xmp_path}, error: {e}")
            return None

    def save(self, xmp_metadata: XmpMetadata) -> None:
        """XMPメタデータを保存

        Args:
            xmp_metadata: 保存するXMPメタデータ
        """
        xmp_path = xmp_metadata.xmp_path

        # 新しいXMPファイルを作成
        root = self._create_xmp_root(xmp_metadata)
        tree = ET.ElementTree(root)

        # XMLファイルとして保存
        tree.write(
            xmp_path, encoding="utf-8", xml_declaration=True, method="xml"
        )

    def exists(self, xmp_path: Path) -> bool:
        """XMPファイルが存在するか確認

        Args:
            xmp_path: XMPファイルのパス

        Returns:
            存在する場合True
        """
        return xmp_path.exists()

    def merge_and_save(self, xmp_metadata: XmpMetadata) -> None:
        """既存のXMPファイルとマージして保存

        Args:
            xmp_metadata: マージするXMPメタデータ
        """
        xmp_path = xmp_metadata.xmp_path

        if self.exists(xmp_path):
            # 既存のXMPを読み込んでマージ
            existing = self.load(xmp_path)
            if existing:
                # キーワードをマージ
                xmp_metadata.keywords.update(existing.keywords)
                xmp_metadata.hierarchical_keywords.update(
                    existing.hierarchical_keywords
                )

        # 保存
        self.save(xmp_metadata)

    def _extract_keywords(self, root: ET.Element) -> Set[str]:
        """XMPからキーワードを抽出

        Args:
            root: XMPのルート要素

        Returns:
            キーワードのセット
        """
        keywords: Set[str] = set()

        # dc:subject配下のrdf:Bag/rdf:liを探す
        for bag in root.findall(".//dc:subject/rdf:Bag", self.NAMESPACES):
            for li in bag.findall("rdf:li", self.NAMESPACES):
                if li.text:
                    keywords.add(li.text)

        return keywords

    def _extract_hierarchical_keywords(self, root: ET.Element) -> Set[str]:
        """XMPから階層キーワードを抽出

        Args:
            root: XMPのルート要素

        Returns:
            階層キーワードのセット
        """
        hierarchical_keywords: Set[str] = set()

        # lr:hierarchicalSubject配下のrdf:Bag/rdf:liを探す
        for bag in root.findall(".//lr:hierarchicalSubject/rdf:Bag", self.NAMESPACES):
            for li in bag.findall("rdf:li", self.NAMESPACES):
                if li.text:
                    hierarchical_keywords.add(li.text)

        return hierarchical_keywords

    def _create_xmp_root(self, xmp_metadata: XmpMetadata) -> ET.Element:
        """XMPのルート要素を作成

        Args:
            xmp_metadata: XMPメタデータ

        Returns:
            XMPのルート要素
        """
        # XMPルート要素
        root = ET.Element(
            f"{{{self.NAMESPACES['x']}}}xmpmeta",
            attrib={f"{{{self.NAMESPACES['x']}}}xmptk": "Claude RAW Clusterer 1.0"},
        )

        # RDF要素
        rdf = ET.SubElement(
            root, f"{{{self.NAMESPACES['rdf']}}}RDF"
        )

        # Description要素
        desc = ET.SubElement(
            rdf,
            f"{{{self.NAMESPACES['rdf']}}}Description",
            attrib={f"{{{self.NAMESPACES['rdf']}}}about": ""},
        )

        # dc:subject（キーワード）
        if xmp_metadata.keywords:
            subject = ET.SubElement(
                desc, f"{{{self.NAMESPACES['dc']}}}subject"
            )
            bag = ET.SubElement(
                subject, f"{{{self.NAMESPACES['rdf']}}}Bag"
            )
            for keyword in sorted(xmp_metadata.keywords):
                li = ET.SubElement(
                    bag, f"{{{self.NAMESPACES['rdf']}}}li"
                )
                li.text = keyword

        # lr:hierarchicalSubject（階層キーワード）
        if xmp_metadata.hierarchical_keywords:
            hierarchical = ET.SubElement(
                desc, f"{{{self.NAMESPACES['lr']}}}hierarchicalSubject"
            )
            bag = ET.SubElement(
                hierarchical, f"{{{self.NAMESPACES['rdf']}}}Bag"
            )
            for h_keyword in sorted(xmp_metadata.hierarchical_keywords):
                li = ET.SubElement(
                    bag, f"{{{self.NAMESPACES['rdf']}}}li"
                )
                li.text = h_keyword

        return root
