"""URL fetcher for academic papers.

Fetches metadata and content from academic paper URLs while respecting paywalls.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Metadata extracted from paper URL."""
    title: Optional[str] = None
    authors: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    full_text: Optional[str] = None
    source_url: Optional[str] = None
    pdf_url: Optional[str] = None
    access_status: str = "unknown"  # "open", "restricted", "paywall", "unknown"


class URLFetcher:
    """Fetch academic paper metadata and content from URLs."""

    def __init__(self):
        """Initialize fetcher."""
        self.timeout = 30.0
        self.user_agent = "LARA/0.1.0 (Local Academic Research Assistant; mailto:research@localhost)"

    async def fetch_paper(self, url: str) -> PaperMetadata:
        """Fetch paper metadata and content from URL.
        
        Args:
            url: Paper URL (DOI, arXiv, PubMed, or direct link)
        
        Returns:
            Paper metadata
        """
        # Normalize URL
        url = url.strip()
        
        # Detect source type
        if "doi.org/" in url or self._is_doi(url):
            return await self._fetch_from_doi(url)
        elif "arxiv.org" in url:
            return await self._fetch_from_arxiv(url)
        elif "pubmed.ncbi.nlm.nih.gov" in url or "ncbi.nlm.nih.gov/pubmed" in url:
            return await self._fetch_from_pubmed(url)
        else:
            return await self._fetch_from_generic_url(url)

    def _is_doi(self, text: str) -> bool:
        """Check if text is a DOI."""
        # DOI pattern: 10.xxxx/xxxxx
        doi_pattern = r"10\.\d{4,}/[^\s]+"
        return bool(re.match(doi_pattern, text))

    def _extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from text."""
        # Handle different DOI formats
        if "doi.org/" in text:
            doi = text.split("doi.org/")[-1]
        elif self._is_doi(text):
            doi = text
        else:
            doi_pattern = r"10\.\d{4,}/[^\s]+"
            match = re.search(doi_pattern, text)
            doi = match.group(0) if match else None
        
        return doi.strip() if doi else None


    async def _fetch_from_doi(self, url: str) -> PaperMetadata:
        """Fetch paper from DOI or DOI URL using CrossRef API."""
        doi = self._extract_doi(url)
        if not doi:
            logger.warning(f"Could not extract DOI from: {url}")
            return PaperMetadata(source_url=url, access_status="unknown")

        logger.info(f"Fetching metadata for DOI: {doi}")
        crossref_url = f"https://api.crossref.org/works/{doi}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(crossref_url, headers={"User-Agent": self.user_agent})
                
                if response.status_code != 200:
                    logger.warning(f"CrossRef API returned {response.status_code}")
                    return PaperMetadata(doi=doi, source_url=f"https://doi.org/{doi}", access_status="unknown")
                
                data = response.json()
                message = data.get("message", {})
                
                # Extract metadata
                title = message.get("title", [None])[0]
                authors_list = message.get("author", [])
                authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list])
                journal = message.get("container-title", [None])[0]
                
                # Extract year
                year = None
                published = message.get("published-print") or message.get("published-online")
                if published and "date-parts" in published:
                    year_parts = published["date-parts"][0]
                    if year_parts:
                        year = year_parts[0]
                
                abstract = message.get("abstract")
                
                # Check for open access PDF
                links = message.get("link", [])
                pdf_url = None
                access_status = "restricted"
                for link in links:
                    if link.get("content-type") == "application/pdf":
                        pdf_url = link.get("URL")
                        access_status = "open"
                        break
                
                return PaperMetadata(
                    title=title, authors=authors or None, doi=doi, journal=journal,
                    year=year, abstract=abstract, source_url=f"https://doi.org/{doi}",
                    pdf_url=pdf_url, access_status=access_status
                )
        except Exception as e:
            logger.error(f"Failed to fetch DOI {doi}: {e}")

    async def _fetch_from_arxiv(self, url: str) -> PaperMetadata:
        """Fetch paper from arXiv (always open access)."""
        arxiv_id_match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)", url.lower())
        if not arxiv_id_match:
            logger.warning(f"Could not extract arXiv ID from: {url}")
            return PaperMetadata(source_url=url, access_status="unknown")
        
        arxiv_id = arxiv_id_match.group(1)
        logger.info(f"Fetching metadata for arXiv: {arxiv_id}")
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(api_url)
                
                if response.status_code != 200:
                    logger.warning(f"arXiv API returned {response.status_code}")
                    return PaperMetadata(source_url=url, access_status="unknown")
                
                # Parse XML
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entry = root.find("atom:entry", ns)
                
                if entry is None:
                    logger.warning(f"No entry found for arXiv ID: {arxiv_id}")
                    return PaperMetadata(source_url=url, access_status="unknown")
                
                # Extract metadata
                title_elem = entry.find("atom:title", ns)
                title = title_elem.text.strip() if title_elem is not None else None
                
                authors_elems = entry.findall("atom:author/atom:name", ns)
                authors = ", ".join([a.text for a in authors_elems if a.text])
                
                summary_elem = entry.find("atom:summary", ns)
                abstract = summary_elem.text.strip() if summary_elem is not None else None
                
                published_elem = entry.find("atom:published", ns)
                year = None
                if published_elem is not None:
                    try:
                        year = int(published_elem.text[:4])
                    except Exception:
                        pass
                
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                return PaperMetadata(
                    title=title, authors=authors or None, doi=None, journal="arXiv",
                    year=year, abstract=abstract, source_url=f"https://arxiv.org/abs/{arxiv_id}",
                    pdf_url=pdf_url, access_status="open"
                )
        except Exception as e:
            logger.error(f"Failed to fetch arXiv {arxiv_id}: {e}")

    async def _fetch_from_pubmed(self, url: str) -> PaperMetadata:
        """Fetch paper from PubMed (metadata only, usually restricted access)."""
        pmid_match = re.search(r"/(\d{7,})", url)
        if not pmid_match:
            logger.warning(f"Could not extract PMID from: {url}")
            return PaperMetadata(source_url=url, access_status="unknown")
        
        pmid = pmid_match.group(1)
        logger.info(f"Fetching metadata for PMID: {pmid}")
        api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(api_url)
                
                if response.status_code != 200:
                    logger.warning(f"PubMed API returned {response.status_code}")
                    return PaperMetadata(source_url=url, access_status="unknown")
                
                data = response.json()
                result = data.get("result", {}).get(pmid)
                
                if not result:
                    logger.warning(f"No result found for PMID: {pmid}")
                    return PaperMetadata(source_url=url, access_status="unknown")
                
                # Extract metadata
                title = result.get("title")
                authors_list = result.get("authors", [])
                authors = ", ".join([a.get("name", "") for a in authors_list])
                journal = result.get("fulljournalname") or result.get("source")
                
                # Extract year
                year = None
                pubdate = result.get("pubdate", "")
                if pubdate:
                    try:
                        year = int(pubdate.split()[0])
                    except Exception:
                        pass
                
                # Extract DOI
                doi = None
                article_ids = result.get("articleids", [])
                for aid in article_ids:
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value")
                        break
                
                return PaperMetadata(
                    title=title, authors=authors or None, doi=doi, journal=journal,
                    year=year, source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    access_status="restricted"
                )
        except Exception as e:
            logger.error(f"Failed to fetch PubMed {pmid}: {e}")

    async def _fetch_from_generic_url(self, url: str) -> PaperMetadata:
        """Fetch paper from generic URL (respects paywalls)."""
        logger.info(f"Fetching metadata from generic URL: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": self.user_agent})
                
                if response.status_code != 200:
                    logger.warning(f"URL returned {response.status_code}: {url}")
                    return PaperMetadata(source_url=url, access_status="unknown")
                
                html = response.text
                
                # Extract metadata from HTML meta tags
                title = self._extract_html_metadata(html, "title")
                authors = self._extract_html_metadata(html, "authors")
                doi = self._extract_html_metadata(html, "doi")
                
                # Check access status
                access_status = "unknown"
                html_lower = html.lower()
                if any(kw in html_lower for kw in ["paywall", "subscription", "purchase", "access denied"]):
                    access_status = "paywall"
                elif any(kw in html_lower for kw in ["open access", "free"]):
                    access_status = "open"
                
                return PaperMetadata(
                    title=title, authors=authors, doi=doi,
                    source_url=url, access_status=access_status
                )
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return PaperMetadata(source_url=url, access_status="unknown")

    def _extract_html_metadata(self, html: str, field: str) -> Optional[str]:
        """Extract metadata from HTML meta tags."""
        patterns = {
            "title": [
                r'<meta name="citation_title" content="([^"]+)"',
                r'<meta property="og:title" content="([^"]+)"',
                r"<title>([^<]+)</title>"
            ],
            "authors": [
                r'<meta name="citation_author" content="([^"]+)"',
                r'<meta name="author" content="([^"]+)"'
            ],
            "doi": [
                r'<meta name="citation_doi" content="([^"]+)"',
                r'<meta name="dc.identifier" content="doi:([^"]+)"'
            ]
        }
        
        for pattern in patterns.get(field, []):
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    async def download_pdf(self, pdf_url: str) -> Optional[bytes]:
        """Download PDF from URL if available."""
        logger.info(f"Downloading PDF from: {pdf_url}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                response = await client.get(pdf_url, headers={"User-Agent": self.user_agent})
                
                if response.status_code != 200:
                    logger.warning(f"PDF download returned {response.status_code}")
                    return None
                
                content_type = response.headers.get("content-type", "")
                if "pdf" not in content_type.lower():
                    logger.warning(f"Downloaded content is not PDF: {content_type}")
                    return None
                
                return response.content
        except Exception as e:
            logger.error(f"Failed to download PDF: {e}")
            return None

    def generate_content_hash(self, metadata: PaperMetadata) -> str:
        """Generate hash for metadata content (for deduplication)."""
        content = f"{metadata.title}|{metadata.authors}|{metadata.doi}|{metadata.abstract}"
        return hashlib.sha256(content.encode()).hexdigest()
