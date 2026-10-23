"""
KB Retriever — loads and searches the ZentroMart knowledge-base Markdown files.
Preserves [SECTION-ID] tags for retrieval scoring.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


KB_DIR = Path(__file__).parent.parent / "kb"


class Section:
    """A single section chunk from a KB document."""
    def __init__(self, doc_id: str, section_id: str, title: str, content: str):
        self.doc_id = doc_id
        self.section_id = section_id  # e.g. "RET-2"
        self.title = title
        self.content = content

    def __repr__(self):
        return f"<Section [{self.section_id}] {self.title!r}>"


def _parse_kb_file(filepath: Path) -> Tuple[dict, List[Section]]:
    """Parse a KB Markdown file into metadata + list of sections."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Extract YAML-like header fields (lines before first ##)
    meta = {}
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            body_start = i
            break
        if ": " in line:
            key, _, val = line.partition(": ")
            meta[key.strip()] = val.strip()

    doc_id = meta.get("doc_id", filepath.stem)
    status = meta.get("status", "current")

    # Split into sections on ## headings
    sections = []
    current_id = None
    current_title = ""
    current_lines = []

    section_pattern = re.compile(r"^## \[([A-Z0-9\-]+)\]\s+(.*)")

    for line in lines[body_start:]:
        m = section_pattern.match(line)
        if m:
            if current_id and current_lines:
                sections.append(Section(
                    doc_id=doc_id,
                    section_id=current_id,
                    title=current_title,
                    content="\n".join(current_lines).strip(),
                ))
            current_id = m.group(1)
            current_title = m.group(2)
            current_lines = []
        else:
            current_lines.append(line)

    if current_id and current_lines:
        sections.append(Section(
            doc_id=doc_id,
            section_id=current_id,
            title=current_title,
            content="\n".join(current_lines).strip(),
        ))

    return meta, sections, status


class KBRetriever:
    """Simple keyword-based retriever. Replace with vector search for production."""

    def __init__(self, kb_dir: Path = KB_DIR):
        self.sections: List[Section] = []
        self._load(kb_dir)

    def _load(self, kb_dir: Path):
        for md_file in sorted(kb_dir.glob("*.md")):
            meta, sections, status = _parse_kb_file(md_file)
            # Skip superseded docs unless needed for time-based logic
            # (keep them but tag them)
            for sec in sections:
                sec.doc_status = status
                self.sections.append(sec)
        print(f"[KBRetriever] Loaded {len(self.sections)} sections from {kb_dir}")

    def search(self, query: str, top_k: int = 5) -> str:
        """
        Basic keyword search. Replace with embeddings + FAISS/ChromaDB.
        Returns a formatted string of matching sections for the LLM context.
        """
        query_lower = query.lower()
        scored = []
        for sec in self.sections:
            score = 0
            haystack = f"{sec.title} {sec.content}".lower()
            for word in re.split(r"\W+", query_lower):
                if word and word in haystack:
                    score += 1
            if score > 0:
                scored.append((score, sec))

        scored.sort(key=lambda x: -x[0])
        top = scored[:top_k]

        if not top:
            return "(No relevant KB sections found)"

        chunks = []
        for _, sec in top:
            chunks.append(
                f"### [{sec.section_id}] {sec.title}\n"
                f"*(doc: {sec.doc_id}, status: {sec.doc_status})*\n\n"
                f"{sec.content}"
            )
        return "\n\n---\n\n".join(chunks)
