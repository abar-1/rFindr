
import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

EMAIL_REGEX = re.compile(r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})")
WS_RE = re.compile(r"\s+")


def norm_ws(text: str) -> str:
    return WS_RE.sub(" ", text or "").strip()


def fetch_html(url: str, timeout: int = 20) -> Tuple[str, str]:
    """
    Fetch HTML from URL. Returns (final_url, text).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FacultyProfileScraper/1.0; +https://example.org/bot)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return (str(resp.url), resp.text)


def best_text(nodes: List[Tag], max_chars: int = 2000) -> str:
    chunks: List[str] = []
    for n in nodes:
        t = n.get_text(separator=" ", strip=True)
        if t:
            chunks.append(t)
    text = norm_ws(" ".join(chunks))
    if len(text) > max_chars:
        cut = text.rfind(".", 0, max_chars)
        if cut == -1:
            cut = max_chars
        text = text[:cut].strip()
    return text


def extract_name(soup: BeautifulSoup) -> Optional[str]:
    schema_person = soup.select('[itemtype*="schema.org/Person"] [itemprop="name"]')
    if schema_person:
        name = norm_ws(schema_person[0].get_text())
        if name:
            return name

    og = soup.select_one('meta[property="og:title"]')
    if og and og.get("content"):
        cand = norm_ws(og["content"])
        cand = re.split(r"[-–|•·]\s+", cand)[0].strip()
        if cand:
            return cand

    for selector in [
        "h1", "header h1", "article h1", ".page-title", ".title h1", ".person-name",
        "h1.person", "h1.profile", "h1.profname", "h2.person-name", "h2"
    ]:
        el = soup.select_one(selector)
        if el:
            cand = norm_ws(el.get_text())
            if cand and len(cand.split()) <= 8:
                return cand

    if soup.title and soup.title.string:
        cand = norm_ws(soup.title.string)
        cand = re.split(r"[-–|•·]\s+", cand)[0].strip()
        if cand:
            return cand

    return None


def extract_emails(soup: BeautifulSoup) -> List[str]:
    emails = set()
    for a in soup.select('a[href^="mailto:"]'):
        href = a.get("href", "")
        email = href.replace("mailto:", "").split("?")[0].strip()
        if EMAIL_REGEX.fullmatch(email):
            emails.add(email)

    text = soup.get_text(" ", strip=True)
    for m in EMAIL_REGEX.finditer(text):
        emails.add(m.group(1))

    def rank(e: str) -> Tuple[int, str]:
        domain = e.split("@")[-1].lower()
        priority = 2
        if domain.endswith((".edu", ".ac.uk", ".ac.in", ".ac.jp", ".ac.cn", ".ac.nz", ".ac.za", ".ac.au")):
            priority = 0
        elif ".ac." in domain:
            priority = 1
        return (priority, e)

    return sorted(emails, key=rank)


BIO_HEADINGS = (
    "biography", "bio", "about", "profile", "overview", "research summary"
)

PUB_HEADINGS = (
    "publications", "selected publications", "recent publications",
    "papers", "articles", "books"
)


def find_section_by_heading(soup: BeautifulSoup, keywords: Tuple[str, ...]) -> Optional[Tag]:
    headings = soup.select("h1, h2, h3, h4, h5, h6, .section-title, .subhead, .heading")
    for h in headings:
        text = norm_ws(h.get_text()).lower()
        if any(k in text for k in keywords):
            container = h.parent if h.parent else h
            sib = h.find_next_sibling()
            if sib and len(sib.get_text(strip=True)) > 20:
                return sib
            return container
    return None


def extract_biography(soup: BeautifulSoup) -> Optional[str]:
    sec = find_section_by_heading(soup, BIO_HEADINGS)
    if sec:
        paras = sec.find_all(["p"], recursive=True)
        if paras:
            text = best_text(paras[:6], max_chars=1500)
            if len(text) >= 80:
                return text
        txt = norm_ws(sec.get_text(" ", strip=True))
        if len(txt) >= 80:
            return txt

    meta = soup.select_one('meta[name="description"], meta[property="og:description"]')
    if meta and meta.get("content"):
        cand = norm_ws(meta["content"])
        if len(cand) >= 60:
            return cand

    all_paras = soup.find_all("p")
    blocks: List[List[Tag]] = []
    current: List[Tag] = []
    for p in all_paras:
        txt = norm_ws(p.get_text())
        if len(txt) < 30:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(p)
    if current:
        blocks.append(current)

    if blocks:
        best = max(blocks, key=lambda b: sum(len(norm_ws(p.get_text())) for p in b))
        text = best_text(best[:8], max_chars=1500)
        if len(text) >= 80:
            return text
    return None


def _split_list_items(container: Tag) -> List[str]:
    items: List[str] = []
    li_elems = container.find_all("li")
    for li in li_elems:
        t = norm_ws(li.get_text(" ", strip=True))
        if len(t) > 10:
            items.append(t)

    if not li_elems:
        parts: List[str] = []
        for child in container.descendants:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif isinstance(child, Tag) and child.name == "br":
                parts.append("\n")
        joined = norm_ws("".join(parts))
        for line in [l.strip() for l in joined.split("\n")]:
            if len(line) > 10:
                items.append(line)

    if not items:
        for p in container.find_all("p"):
            t = norm_ws(p.get_text(" ", strip=True))
            if len(t) > 10:
                items.append(t)

    seen = set()
    out: List[str] = []
    for it in items:
        if it not in seen:
            out.append(it)
            seen.add(it)
    return out


def extract_publications(soup: BeautifulSoup, limit: int = 50) -> List[str]:
    sec = find_section_by_heading(soup, PUB_HEADINGS)
    if sec:
        items = _split_list_items(sec)
        if items:
            return items[:limit]

    candidates = soup.select('[id*="pub"], [class*="pub"], [id*="Public"], [class*="Public"]')
    for c in candidates:
        items = _split_list_items(c)
        if items:
            return items[:limit]

    all_li = [norm_ws(li.get_text(" ", strip=True)) for li in soup.find_all("li")]
    pubs = [t for t in all_li if len(t) > 30 and any(ch in t for ch in (".", "—", "-"))]
    pubs = sorted(pubs, key=len, reverse=True)[:limit]
    return pubs


@dataclass
class ProfessorRecord:
    source_url: str
    name: Optional[str]
    emails: List[str]
    information: Optional[str]
    publications: List[str]


def scrape_professor_page(url: str) -> ProfessorRecord:
    final_url, html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    name = extract_name(soup)
    emails = extract_emails(soup)
    information = extract_biography(soup)
    publications = extract_publications(soup)

    return ProfessorRecord(
        source_url=final_url,
        name=name,
        emails=emails,
        information=information,
        publications=publications,
    )


# === New Function ===
def get_professor_info(url: str) -> Tuple[str, str, str]:
    """
    Fetch and return professor's name, email(s), and formatted bio + publications.
    Returns:
        (name, emails_str, bio_and_pubs_markdown)
    """
    record = scrape_professor_page(url)
    name = record.name or "N/A"
    emails_str = "; ".join(record.emails) if record.emails else "N/A"

    bio_md = f"\n\n{record.information or 'N/A'}\n"
    pubs_md = "\n" + "\n".join([f" {p}" for p in record.publications]) if record.publications else "\nN/A"

    return name, emails_str, bio_md + "\n\n" + pubs_md


def write_jsonl(records: List[ProfessorRecord], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


def write_csv(records: List[ProfessorRecord], path: str) -> None:
    fieldnames = ["source_url", "name", "emails", "information", "publications"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            w.writerow({
                "source_url": r.source_url,
                "name": r.name or "",
                "emails": "; ".join(r.emails),
                "information": r.information or "",
                "publications": " || ".join(r.publications),
            })


def read_urls(args) -> List[str]:
    urls: List[str] = []
    if args.url:
        urls.append(args.url.strip())
    if args.url_file:
        with open(args.url_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    return urls


def main():
    ap = argparse.ArgumentParser(description="Scrape faculty profile pages for core fields.")
    ap.add_argument("--url", help="Single URL to scrape.")
    ap.add_argument("--url-file", help="Path to a text file with one URL per line.")
    ap.add_argument("--jsonl", default="professors.jsonl", help="Output JSONL path.")
    ap.add_argument("--csv", default="professors.csv", help="Output CSV path.")
    args = ap.parse_args()

    urls = read_urls(args)
    if not urls:
        print("Provide --url or --url-file.", file=sys.stderr)
        sys.exit(2)

    records: List[ProfessorRecord] = []
    for u in urls:
        try:
            rec = scrape_professor_page(u)
            records.append(rec)
            print(f"[ok] {u}")
        except Exception as e:
            print(f"[error] {u} -> {e}", file=sys.stderr)

    write_jsonl(records, args.jsonl)
    write_csv(records, args.csv)
    print(f"Wrote {len(records)} records to: {args.jsonl} and {args.csv}")


if __name__ == "__main__":
    main()