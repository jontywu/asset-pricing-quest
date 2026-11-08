"""从干净内核执行指定课程本，并保存内嵌输出、HTML核验预览和运行清单。"""
from pathlib import Path
import argparse
import base64
import json
import time

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('patterns', nargs='*', default=['*.ipynb'])
    args = parser.parse_args()
    paths = sorted({path for pattern in args.patterns for path in (ROOT/'notebooks').glob(pattern)})
    qa = ROOT / '.qa'
    qa.mkdir(exist_ok=True)
    records = []
    for path in paths:
        started = time.monotonic()
        notebook = nbformat.read(path, as_version=4)
        notebook.metadata.kernelspec = {'name':'asset-pricing-quest','display_name':'Python (Asset Pricing Quest)','language':'python'}
        client = NotebookClient(notebook, timeout=180, kernel_name='asset-pricing-quest', resources={'metadata':{'path':str(ROOT)}})
        client.execute()
        nbformat.validate(notebook)
        nbformat.write(notebook,path)
        html,_ = HTMLExporter().from_notebook_node(notebook)
        (qa/(path.stem+'.html')).write_text(html,encoding='utf-8')
        images = 0
        for cell in notebook.cells:
            for output in cell.get('outputs',[]):
                if output.get('output_type')=='error':
                    raise RuntimeError(f'Notebook error in {path.name}')
                png = output.get('data',{}).get('image/png')
                if png:
                    images += 1
                    (qa/f'{path.stem}_figure{images}.png').write_bytes(base64.b64decode(png))
        record = {'notebook':path.name,'code_cells':sum(c.cell_type=='code' for c in notebook.cells),
                  'figures':images,'executed':True,'seconds':round(time.monotonic()-started,2)}
        records.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
    (qa/'execution_latest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
