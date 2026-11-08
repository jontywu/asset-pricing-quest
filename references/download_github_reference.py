"""保存固定版本的公开实现参考；不导入、不执行下载的第三方代码。"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

REPOSITORY = "OpenSourceAP/CrossSection"
COMMIT = "9f053398c4995651d822e90d81526d0644c6f3e5"
DESTINATION = Path(__file__).resolve().parent / "github" / "OpenSourceAP_CrossSection"
FILES = [
    "README.md",
    "LICENSE",
    "Signals/pyCode/Predictors/Size.py",
    "Signals/pyCode/Predictors/BMdec.py",
    "Signals/pyCode/Predictors/OperProf.py",
    "Signals/pyCode/Predictors/AssetGrowth.py",
    "Portfolios/Code/01_PortfolioFunction.R",
    "Portfolios/Code/32_Predictor2x3Ports.R",
]


def save_reference(path):
    url = f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/{path}"
    target = DESTINATION / path
    if target.exists():
        content = target.read_bytes()
    else:
        with urlopen(Request(url, headers={"User-Agent": "AssetPricingQuest-reference/1.0"}), timeout=60) as response:
            content = response.read()
        if not content or content.lstrip().lower().startswith(b"<!doctype html"):
            raise ValueError(f"下载内容不是预期源码：{url}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return {
        "path": path,
        "source_url": f"https://github.com/{REPOSITORY}/blob/{COMMIT}/{path}",
        "download_url": url,
        "bytes": len(content),
        "sha256": sha256(content).hexdigest(),
    }


def main():
    manifest_path = DESTINATION / "SOURCE_MANIFEST.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in previous["files"]:
            content = (DESTINATION / record["path"]).read_bytes()
            if sha256(content).hexdigest() != record["sha256"]:
                raise ValueError(f"本地参考文件已变化：{record['path']}")
        print("参考包校验通过，保留原始来源记录。")
        return
    with ThreadPoolExecutor(max_workers=4) as executor:
        records = list(executor.map(save_reference, FILES))
    manifest = {
        "repository": REPOSITORY,
        "repository_url": f"https://github.com/{REPOSITORY}",
        "commit": COMMIT,
        "commit_url": f"https://github.com/{REPOSITORY}/commit/{COMMIT}",
        "commit_date_utc": "2026-10-27T20:27:06Z",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "license": "GPL-2.0",
        "selection": "Reading-only subset, original file contents retained. No third-party code executed.",
        "verification": "Repository, README, commit and selected code inspected using the GitHub connector before download.",
        "files": records,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"保存 {len(records)} 份参考源码/文档，共 {sum(item['bytes'] for item in records):,} 字节。")
    print(manifest_path)


if __name__ == "__main__":
    main()
