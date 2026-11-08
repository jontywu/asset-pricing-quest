"""只读解析作者 XLSX，导出原始字段值并记录核验结果；不推断收益单位。"""

from csv import writer
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd

ROOT = Path(__file__).resolve().parent
XLSX = ROOT / "LTW_3factor.xlsx"
CSV = ROOT / "LTW_3factor_raw_values.csv"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def main():
    with ZipFile(XLSX) as archive:
        if archive.testzip() is not None:
            raise ValueError("XLSX 压缩结构校验失败。")
        strings = ["".join(item.itertext()) for item in ET.fromstring(
            archive.read("xl/sharedStrings.xml")).findall("s:si", NS)]
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        values = {}
        for row in sheet.findall("s:sheetData/s:row", NS):
            for cell in row.findall("s:c", NS):
                value_node = cell.find("s:v", NS)
                text = value_node.text if value_node is not None else ""
                if cell.get("t") == "s":
                    text = strings[int(text)]
                values[cell.attrib["r"]] = text
        core = ET.fromstring(archive.read("docProps/core.xml"))
        modified = core.find("{http://purl.org/dc/terms/}modified").text

    header = [values[f"{column}6"] for column in "ABCD"]
    assert header == ["yyww", "cmkt", "csize", "cmom"]
    row_numbers = sorted(int(key[1:]) for key in values if key.startswith("A") and key[1:].isdigit() and int(key[1:]) >= 7)
    rows = [[values.get(f"{column}{number}", "") for column in "ABCD"] for number in row_numbers]
    with CSV.open("w", newline="", encoding="utf-8") as stream:
        output = writer(stream)
        output.writerow(header)
        output.writerows(rows)

    # 分析结构而不改变收益口径。输出 CSV 保留 XLSX XML 中的数字字符串。
    frame = pd.read_csv(CSV)
    week_codes = frame["yyww"].astype(int)
    years = week_codes // 100
    weeks = week_codes % 100
    valid_weeks = bool(weeks.between(1, 52).all())
    ordinals = years * 52 + weeks - 1
    contiguous = bool(ordinals.diff().iloc[1:].eq(1).all())
    assert valid_weeks and contiguous and week_codes.is_unique
    assert frame.shape == (479, 4)

    download = json.loads((ROOT / "download_record.json").read_text(encoding="utf-8"))
    manifest = {
        "paper": {
            "title": "Common Risk Factors in Cryptocurrency",
            "authors": ["Yukun Liu", "Aleh Tsyvinski", "Xi Wu"],
            "journal_reference": "The Journal of Finance 77(2), 2022, 1133-1177",
            "doi": "10.1111/jofi.13119",
            "author_source_page": "https://www.yukunliu.com/research/",
        },
        "original_workbook": download,
        "workbook_metadata": {
            "sheet": "Sheet1",
            "header_excel_row": 6,
            "data_excel_rows": [min(row_numbers), max(row_numbers)],
            "original_columns": header,
            "author_notes": [values[f"A{number}"] for number in (1, 2, 3)],
            "embedded_modified_utc": modified,
            "release_identifier": "No explicit release identifier; frozen by download timestamp and SHA-256",
        },
        "verified_structure": {
            "rows": len(frame),
            "columns": len(frame.columns),
            "first_yyww": int(week_codes.iloc[0]),
            "last_yyww": int(week_codes.iloc[-1]),
            "duplicate_week_codes": int(week_codes.duplicated().sum()),
            "missing_values_by_column": {name: int(count) for name, count in frame.isna().sum().items()},
            "frequency": "Author-defined weekly: 52 weeks per year, last week longer than 7 days",
            "frequency_documentation": "Workbook Sheet1!A2",
            "week_number_range_valid": valid_weeks,
            "contiguous_in_author_52_week_calendar": contiguous,
            "calendar_dates_assigned": False,
        },
        "scope_and_unit_notes": {
            "coverage_discrepancy": "Sheet1!A3 says updated through 2022, but the actual observations end at week code 202314. Preserve both facts.",
            "data_source_change": "Sheet1!A3 says data are from CoinGecko since mid-2020.",
            "raw_factor_labels": {"cmkt": "cryptocurrency market factor", "csize": "cryptocurrency size factor", "cmom": "cryptocurrency momentum factor"},
            "unit_status": "UNVERIFIED: workbook does not explicitly identify decimal versus percentage units",
            "unit_conversion_applied": False,
            "analysis_use": "Read and inspect raw values only until the units and exact factor-return convention are documented. Do not treat the factors themselves as independent test assets.",
        },
        "derived_csv": {
            "filename": CSV.name,
            "sha256": sha256(CSV.read_bytes()).hexdigest(),
            "bytes": CSV.stat().st_size,
            "derived_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_filename": XLSX.name,
            "source_sha256": sha256(XLSX.read_bytes()).hexdigest(),
            "transformation": "Sheet1 A6:D485 exported with original headers and exact numeric XML strings; no scaling, date conversion, filling or model estimation",
        },
        "paper_download": {
            "local_relative_path": "../../papers/crypto/LTW_working_paper_20190415.pdf",
            "version": "Author working paper dated 2019-04-15, 47 PDF pages; NOT the 2022 journal version",
            "formal_pdf_and_replication_zip": "Public endpoints returned HTTP 403; see papers/crypto/download_attempts.json. No restricted material bypass attempted.",
        },
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["verified_structure"], ensure_ascii=False, indent=2))
    print("Raw values exported. Units remain explicitly unverified.")


if __name__ == "__main__":
    main()
