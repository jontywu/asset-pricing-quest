"""下载课程所需的公开因子与组合；复用第 0 关的冻结与校验逻辑。"""
from pathlib import Path
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'level00'))
import download_data as downloader

FILES = {
    'ff3': 'F-F_Research_Data_Factors_CSV.zip',
    'ff5': 'F-F_Research_Data_5_Factors_2x3_CSV.zip',
    'bm6': '6_Portfolios_2x3_CSV.zip',
    'op6': '6_Portfolios_ME_OP_2x3_CSV.zip',
    'inv6': '6_Portfolios_ME_INV_2x3_CSV.zip',
    'bm25': '25_Portfolios_5x5_CSV.zip',
    'op25': '25_Portfolios_ME_OP_5x5_CSV.zip',
    'inv25': '25_Portfolios_ME_INV_5x5_CSV.zip',
    'bm_op32': '32_Portfolios_ME_BEME_OP_2x4x4_CSV.zip',
    'bm_inv32': '32_Portfolios_ME_BEME_INV_2x4x4_CSV.zip',
    'op_inv32': '32_Portfolios_ME_OP_INV_2x4x4_CSV.zip',
    'industry30': '30_Industry_Portfolios_CSV.zip',
    'mom': 'F-F_Momentum_Factor_CSV.zip',
    'mom25': '25_Portfolios_ME_Prior_12_2_CSV.zip',
}


def main():
    downloader.ROOT = ROOT
    downloader.RAW = ROOT / 'data' / 'raw'
    downloader.MANIFEST = downloader.RAW / 'manifest.json'
    downloader.SOURCES = {key: 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/' + name for key, name in FILES.items()}
    downloader.RAW.mkdir(parents=True, exist_ok=True)
    old_raw = ROOT / 'level00' / 'data' / 'raw'
    # 沿用已冻结的两份快照及其真实下载时间，不覆盖原学习目录。
    if not downloader.MANIFEST.exists() and (old_raw / 'manifest.json').exists():
        old = json.loads((old_raw / 'manifest.json').read_text(encoding='utf-8'))
        records = {}
        for old_key, new_key in [('ff3', 'ff3'), ('size_bm_25', 'bm25')]:
            record = old['datasets'][old_key]
            for field in ('zip_file', 'csv_file'):
                target = downloader.RAW / record[field]
                if not target.exists():
                    shutil.copy2(old_raw / record[field], target)
            records[new_key] = record
        downloader.save_manifest({'source_page': downloader.SOURCE_PAGE, 'datasets': records})
    downloader.main()


if __name__ == '__main__':
    main()
