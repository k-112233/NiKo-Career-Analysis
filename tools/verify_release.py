"""Verify archive hashes, exclusions, notebooks and a clean offline rebuild."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    version=(ROOT/'VERSION').read_text().strip()
    target=ROOT/f'dist/niko-career-analysis-v{version}.zip'
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    assert target.with_suffix('.zip.sha256').read_text().split()[0]==digest
    commands=[[sys.executable,'-m','tools.build_portfolio'],[sys.executable,'-m','unittest','discover','-s','checks','-v'],[sys.executable,'-m','tools.execute_notebooks','--check']]
    if shutil.which('node'):commands.append(['node','checks/dashboard.cjs'])
    with zipfile.ZipFile(target) as archive:
        names=archive.namelist();manifest=json.loads(archive.read('RELEASE_MANIFEST.json'))
        assert set(names)==set(manifest['files'])|{'RELEASE_MANIFEST.json'}
        assert not any(name.startswith(('data/raw/','crawler/','pipeline/','tests/','.build/','.git/')) or name.endswith(('.db','.sqlite','.pyc','.env')) for name in names)
        assert not any('04_weapon' in name for name in names)
        for name,expected in manifest['files'].items():
            assert '..' not in Path(name).parts and not Path(name).is_absolute()
            assert hashlib.sha256(archive.read(name)).hexdigest()==expected,name
        with tempfile.TemporaryDirectory(prefix='niko-v1-') as tmp:
            archive.extractall(tmp)
            snapshot=Path(tmp)/'data/processed/niko_maps.csv'
            before=hashlib.sha256(snapshot.read_bytes()).hexdigest()
            for command in commands:
                result=subprocess.run(command,cwd=tmp,capture_output=True,text=True,encoding='utf-8',errors='replace')
                if result.returncode:raise RuntimeError(str(command)+'\n'+result.stdout+result.stderr)
                print('Passed:', ' '.join(command[1:]))
            assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==before==manifest['snapshot_sha256']
    result={'version':version,'status':'passed','archive_sha256':digest,'files':len(names),'clean_rebuild':True,'snapshot_unchanged':True,'python':sys.version.split()[0]}
    (ROOT/'dist/v1-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
