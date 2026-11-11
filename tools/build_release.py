"""Build a deterministic, curated v1 source archive."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    version=(ROOT/'VERSION').read_text().strip()
    files=[ROOT/name for name in ['README.md','VERSION','CHANGELOG.md','LICENSE','DATA_LICENSES.md','requirements.txt','requirements.lock','.gitignore','index.html']]
    for folder in ['analysis','dashboard','reports','checks','data/provenance','.github','docs/images']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.db','.sqlite','.pyc'} and p.name!='04_weapon_analysis.ipynb')
    files.extend(ROOT/'tools'/name for name in ['build_portfolio.py','build_release.py','integrate_cs2.py','verify_release.py','execute_notebooks.py'])
    files.extend(ROOT/'docs'/name for name in ['sources.md','github_release.md','data_dictionary_v1.md','validation.md'])
    files.extend(ROOT/'data/processed'/name for name in ['niko_maps.csv','hltv_recent_rows.json','niko_external_csgo_2021_2023.csv','niko_ektarr_cs2_v10.csv','niko_maps_before_cs2.csv'])
    payload={str(p.relative_to(ROOT).as_posix()):p.read_bytes() for p in sorted(set(files))}
    manifest={'version':version,'files':{name:hashlib.sha256(data).hexdigest() for name,data in payload.items()},'snapshot_sha256':hashlib.sha256(payload['data/processed/niko_maps.csv']).hexdigest()}
    payload['RELEASE_MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    target=ROOT/f'dist/niko-career-analysis-v{version}.zip';target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(payload.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,11,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            archive.writestr(info,data)
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='utf-8')
    print(f'{target}: {len(payload)} files, {target.stat().st_size:,} bytes; SHA-256 {digest}')


if __name__=='__main__':main()
