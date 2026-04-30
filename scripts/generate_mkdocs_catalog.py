from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs"
SAMPLES_DIR = ROOT / "samples"
SITE_DOCS_DIR = ROOT / "docs"
DOC_CATALOG = SITE_DOCS_DIR / "documentation-catalog.md"
SAMPLES_CATALOG = SITE_DOCS_DIR / "samples-catalog.md"

REPO_BLOB_BASE = "https://github.com/Keayoub/pvw-cli/blob/main"


def normalize_rel(path: Path) -> str:
    return path.as_posix()


def github_blob_link(path: Path) -> str:
    encoded_path = quote(normalize_rel(path), safe="/")
    return f"{REPO_BLOB_BASE}/{encoded_path}"


def local_docs_link(path: Path) -> str:
    rel = path.relative_to(DOC_DIR)
    return normalize_rel(rel)


def build_section(title: str, root_dir: Path, link_mode: str = "github") -> list[str]:
    lines = [f"## {title}", ""]
    files = sorted([p for p in root_dir.rglob("*") if p.is_file()])
    if not files:
        lines.append("No files found.")
        lines.append("")
        return lines

    for file_path in files:
        rel = file_path.relative_to(ROOT)
        label = normalize_rel(rel)
        if link_mode == "local":
            lines.append(f"- [{label}]({local_docs_link(file_path)})")
        else:
            lines.append(f"- [{label}]({github_blob_link(rel)})")

    lines.append("")
    return lines


def write_doc_catalog() -> None:
    header = [
        "# Full Documentation Catalog",
        "",
        "This page is auto-generated from the `docs/` folder.",
        "All links point to pages in this documentation website.",
        "",
    ]
    lines = header + build_section("Files in docs/", DOC_DIR, link_mode="local")
    DOC_CATALOG.write_text("\n".join(lines), encoding="utf-8")


def write_samples_catalog() -> None:
    header = [
        "# Full Samples Catalog",
        "",
        "This page is auto-generated from the `samples/` folder.",
        "All links point to the source files in GitHub.",
        "",
    ]
    lines = header + build_section("Files in samples/", SAMPLES_DIR)
    SAMPLES_CATALOG.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    SITE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    write_doc_catalog()
    write_samples_catalog()
    print("OK Generated MkDocs catalog pages in docs/")


if __name__ == "__main__":
    main()
