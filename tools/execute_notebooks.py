"""Execute the three trusted project notebooks without requiring a Jupyter server."""
from contextlib import redirect_stdout
import argparse
import io
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NOTEBOOKS=['01_data_cleaning.ipynb','02_career_analysis.ipynb','03_map_analysis.ipynb']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    original=Path.cwd()
    try:
        os.chdir(ROOT)
        for name in NOTEBOOKS:
            path=ROOT/'analysis'/name;notebook=json.loads(path.read_text(encoding='utf-8'));scope={};execution=0
            for cell in notebook['cells']:
                if cell['cell_type']!='code':continue
                execution+=1;outputs=[];stream=io.StringIO()
                def display(value):
                    data={'text/plain':repr(value)}
                    if hasattr(value,'_repr_html_'):data['text/html']=value._repr_html_()
                    outputs.append({'output_type':'display_data','metadata':{},'data':data})
                scope['display']=display
                source=cell['source'] if isinstance(cell['source'],str) else ''.join(cell['source'])
                with redirect_stdout(stream):exec(compile(source,name,'exec'),scope)
                if stream.getvalue():outputs.insert(0,{'output_type':'stream','name':'stdout','text':stream.getvalue()})
                cell['execution_count']=execution;cell['outputs']=outputs
            if not args.check:path.write_text(json.dumps(notebook,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(name,'executed')
    finally:os.chdir(original)


if __name__=='__main__':main()
