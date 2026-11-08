"""按既有来源清单下载本地论文；校验冻结版本，不覆盖已有文件。

使用：python scripts/download_papers.py
查看来源而不下载：python scripts/download_papers.py --list
仅使用 Python 标准库；不会修改 Notebook、manifest 或论文版本。
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True)
class Paper:
    label: str
    url: str
    destination: Path
    sha256: str


def _paper(label: str, record: dict, folder: Path, filename_key: str, url_key: str) -> Paper:
    filename = record[filename_key]
    if Path(filename).name != filename or not filename.lower().endswith('.pdf'):
        raise ValueError(f'清单中的 PDF 文件名无效：{label}')
    url = record[url_key]
    if urlsplit(url).scheme != 'https':
        raise ValueError(f'论文来源必须是 HTTPS：{label}')
    digest = record['sha256'].lower()
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError(f'清单中的 SHA-256 无效：{label}')
    return Paper(label, url, folder / filename, digest)


def load_papers() -> list[Paper]:
    papers = ROOT / 'papers'
    primary = json.loads((papers / 'paper_map.json').read_text(encoding='utf-8'))
    records = [_paper(key, record, papers, 'pdf_file', 'pdf_url')
               for key, record in primary['papers'].items()]
    crypto = json.loads((papers / 'crypto' / 'manifest.json').read_text(encoding='utf-8'))
    records.extend(_paper(record['file'], record, papers / 'crypto', 'file', 'url')
                   for record in crypto['files'] if record.get('status') == 'downloaded')
    return records


def verify_pdf(content: bytes, paper: Paper) -> None:
    if not content.startswith(b'%PDF-'):
        raise ValueError(f'{paper.label}：来源未返回 PDF，可能是网站错误页。')
    if hashlib.sha256(content).hexdigest() != paper.sha256:
        raise ValueError(f'{paper.label}：SHA-256 与既有清单不符；未保存，也未自动更换版本。')


def download_one(paper: Paper) -> str:
    if paper.destination.exists():
        verify_pdf(paper.destination.read_bytes(), paper)
        return '已存在，校验通过，跳过下载'
    paper.destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(paper.url, headers={'User-Agent': 'AssetPricingQuest/1.0 (educational replication)'})
    with urlopen(request, timeout=45) as response:
        content = response.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError(f'{paper.label}：响应超过 25 MiB，未保存。')
    verify_pdf(content, paper)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=paper.destination.parent, suffix='.part', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        if paper.destination.exists():
            raise FileExistsError(f'{paper.destination.name} 下载期间已出现，未覆盖。')
        temporary.replace(paper.destination)
        return '下载完成，SHA-256 校验通过'
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='仅列出既有清单中的公开来源')
    args = parser.parse_args()
    failed = False
    for paper in load_papers():
        if args.list:
            print(f'{paper.destination.relative_to(ROOT)}\n  {paper.url}')
            continue
        try:
            print(f'{paper.destination.name}：{download_one(paper)}')
        except (OSError, ValueError) as exc:
            failed = True
            print(f'{paper.destination.name}：获取失败：{exc}')
    if failed:
        print('已有文件和来源清单保持原样。可根据 --list 显示的来源自行获取；不要以不同论文版本冒充原件。')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
