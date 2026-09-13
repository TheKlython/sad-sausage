#!/usr/bin/env python3
"""
tests/test_build_pages.py
=========================
AI-Agent Context & Test Suite Documentation:
--------------------------------------------
This test suite verifies the static site generation and SEO discovery pipeline
implemented in `scripts/build_pages.py`.

It ensures that:
1. All required HTML documents, manifest files, and web standard endpoints are generated.
2. The generated XML Sitemap (sitemap.xml) is valid XML conforming to Sitemaps.org standards.
3. The robots.txt explicitly declares the Sitemap directive for Googlebot and other indexers.
4. Google SEO tags (canonical link, robots meta, JSON-LD schema referencing the GitHub repo)
   are present and strictly valid.
5. Security by Design rules are upheld (strict CSP headers, `rel="noopener noreferrer"` on
   all outbound external links, and `.nojekyll` present).
"""

import json
import re
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

# Import the build script under test
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import build_pages


class TestBuildPages(unittest.TestCase):
    """
    Test suite for the static site build pipeline and SEO discovery assets.
    """

    @classmethod
    def setUpClass(cls):
        """
        Execute the build pipeline once to create the `_site/` directory for inspection.
        """
        cls.output_dir = build_pages.build_site()

    def test_01_all_required_files_generated(self):
        """
        Verify that all core HTML pages, machine-readable manifests,
        and configuration files exist in the output directory.
        """
        expected_files = [
            "index.html",
            "architecture.html",
            "security.html",
            "donations.html",
            "sitemap.xml",
            "robots.txt",
            "llms.txt",
            "llms-full.txt",
            "agent_manifest.json",
            ".nojekyll",
            ".well-known/ai-agent.json",
        ]
        for rel_path in expected_files:
            target = self.output_dir / rel_path
            self.assertTrue(target.exists(), f"Expected artifact '{rel_path}' is missing in _site/")
            if rel_path != ".nojekyll":
                self.assertGreater(target.stat().st_size, 0, f"Artifact '{rel_path}' should not be empty")

    def test_02_sitemap_xml_validity(self):
        """
        Verify that `sitemap.xml` is well-formed XML and conforms to the Sitemaps protocol.
        """
        sitemap_path = self.output_dir / "sitemap.xml"
        self.assertTrue(sitemap_path.exists())

        # Parse XML with standard parser
        tree = ET.parse(sitemap_path)
        root = tree.getroot()

        # Namespace is http://www.sitemaps.org/schemas/sitemap/0.9
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall("sm:url", ns)
        self.assertGreaterEqual(len(urls), 5, "Sitemap should contain at least 5 indexed URLs")

        # Check loc elements
        locs = [u.find("sm:loc", ns).text for u in urls if u.find("sm:loc", ns) is not None]
        
        # Verify base URL and important subpages are present
        self.assertIn("https://theklython.github.io/sad-sausage/", locs)
        self.assertIn("https://theklython.github.io/sad-sausage/architecture.html", locs)
        self.assertIn("https://theklython.github.io/sad-sausage/security.html", locs)
        self.assertIn("https://theklython.github.io/sad-sausage/donations.html", locs)
        self.assertIn("https://theklython.github.io/sad-sausage/llms.txt", locs)

    def test_03_robots_txt_sitemap_directive(self):
        """
        Verify that `robots.txt` declares the canonical Sitemap URL and permits crawling.
        """
        robots_path = self.output_dir / "robots.txt"
        content = robots_path.read_text(encoding="utf-8")

        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn(
            "Sitemap: https://theklython.github.io/sad-sausage/sitemap.xml",
            content,
            "robots.txt must contain the absolute Sitemap URL for search engine bots",
        )

    def test_04_index_html_seo_and_schema(self):
        """
        Verify that `index.html` contains canonical links, robots meta, and
        valid Schema.org JSON-LD pointing to the primary GitHub repository.
        """
        index_path = self.output_dir / "index.html"
        html_text = index_path.read_text(encoding="utf-8")

        # 1. Canonical link
        self.assertIn(
            '<link rel="canonical" href="https://theklython.github.io/sad-sausage/">',
            html_text,
            "index.html must include the canonical link for Googlebot",
        )

        # 2. Robots meta tag
        self.assertIn(
            '<meta name="robots" content="index, follow',
            html_text,
            "index.html must explicitly allow indexing and following",
        )

        # 3. Schema.org JSON-LD extraction and validation
        m_schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_text, re.DOTALL)
        self.assertIsNotNone(m_schema, "index.html must contain a Schema.org JSON-LD script block")

        schema_data = json.loads(m_schema.group(1).strip())
        self.assertEqual(schema_data.get("@context"), "https://schema.org")
        self.assertEqual(schema_data.get("@type"), "SoftwareSourceCode")
        self.assertEqual(
            schema_data.get("codeRepository"),
            "https://github.com/TheKlython/sad-sausage",
            "Schema.org codeRepository must point to the GitHub repository",
        )

    def test_05_security_by_design_hygiene(self):
        """
        Verify that security principles are implemented across generated HTML:
        - Content Security Policy (CSP) meta tag exists.
        - Every external anchor with target="_blank" has rel="noopener noreferrer".
        """
        for html_file in self.output_dir.glob("*.html"):
            content = html_file.read_text(encoding="utf-8")

            # Check CSP
            self.assertIn(
                "Content-Security-Policy",
                content,
                f"{html_file.name} must declare a Content-Security-Policy",
            )

            # Check outbound links for target="_blank" without rel="noopener noreferrer"
            # Find all <a ...> tags
            for a_tag in re.findall(r'<a\s+[^>]+>', content):
                if 'target="_blank"' in a_tag:
                    self.assertIn(
                        'rel="noopener noreferrer"',
                        a_tag,
                        f"Unsafe external target='_blank' found without rel='noopener noreferrer' in {html_file.name}: {a_tag}",
                    )


if __name__ == "__main__":
    unittest.main()
