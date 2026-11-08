"""第 0 关：下载并冻结两份 Kenneth French 官方数据。只使用标准库。"""

from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.json"
SOURCE_PAGE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html"
SOURCES = {
    "ff3": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip",
    "size_bm_25": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/25_Portfolios_5x5_CSV.zip",
}


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def save_manifest(manifest: dict) -> None:
    temporary = MANIFEST.with_suffix(".json.part")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(MANIFEST)


def validate_archive(content: bytes) -> tuple[str, bytes]:
    """校验压缩包，并取出唯一 CSV；不使用 extractall。"""
    with ZipFile(io.BytesIO(content)) as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ValueError(f"ZIP CRC 校验失败：{bad_member}")
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"预期一个 CSV，实际为：{members}")
        member = members[0]
        csv_bytes = archive.read(member)
        if not csv_bytes:
            raise ValueError("下载的 CSV 为空。")
        return member, csv_bytes


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        manifest = {"source_page": SOURCE_PAGE, "datasets": {}}

    for name, url in SOURCES.items():
        archive_path = RAW / url.rsplit("/", 1)[-1]
        existing = manifest["datasets"].get(name)

        # 已有快照只核验，不重新下载，也不改写下载时间。
        if existing is not None:
            csv_path = RAW / existing["csv_file"]
            if not archive_path.exists():
                raise FileNotFoundError(f"快照缺少 ZIP：{archive_path}")
            content = archive_path.read_bytes()
            if sha256(content) != existing["zip_sha256"]:
                raise ValueError(f"本地 ZIP 与记录不符：{archive_path}")
            member, csv_bytes = validate_archive(content)
            if sha256(csv_bytes) != existing["csv_sha256"]:
                raise ValueError(f"ZIP 中 CSV 与记录不符：{member}")
            if not csv_path.exists():
                csv_path.write_bytes(csv_bytes)
            if sha256(csv_path.read_bytes()) != existing["csv_sha256"]:
                raise ValueError(f"本地 CSV 与记录不符：{csv_path}")
            print(f"已核验快照：{name} / {archive_path.name}")
            continue

        if archive_path.exists():
            raise FileExistsError(f"发现没有来源记录的同名 ZIP，请先检查：{archive_path}")

        request = Request(url, headers={"User-Agent": "AssetPricingQuest/1.0 (educational replication)"})
        with urlopen(request, timeout=60) as response:
            content = response.read()
            response_metadata = {
                "resolved_url": response.geturl(),
                "http_last_modified": response.headers.get("Last-Modified"),
                "http_etag": response.headers.get("ETag"),
            }
        downloaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        member, csv_bytes = validate_archive(content)
        csv_path = RAW / Path(member).name
        if csv_path.exists():
            raise FileExistsError(f"不覆盖没有快照记录的 CSV：{csv_path}")

        archive_path.write_bytes(content)
        csv_path.write_bytes(csv_bytes)
        manifest["datasets"][name] = {
            "url": url,
            "downloaded_at_utc": downloaded_at,
            "zip_file": archive_path.name,
            "zip_bytes": len(content),
            "zip_sha256": sha256(content),
            "zip_member": member,
            "csv_file": csv_path.name,
            "csv_bytes": len(csv_bytes),
            "csv_sha256": sha256(csv_bytes),
            "source_header": csv_bytes.decode("utf-8-sig").splitlines()[0],
            **response_metadata,
        }
        save_manifest(manifest)
        print(f"已下载并校验：{archive_path.name} ({len(content):,} bytes)")

    print(f"来源记录：{MANIFEST}")


if __name__ == "__main__":
    main()
