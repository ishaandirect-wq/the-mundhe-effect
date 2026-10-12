"""Load and save the directory manifest and reviewable bulk-data files."""
import json
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEST=ROOT/'data/establishments.json'

def load_directory(path=DEST):
    data=json.loads(path.read_text());records=list(data['establishments']);seen=set()
    for name in data.get('additional_data',[]):
        relative=pathlib.PurePosixPath(name)
        if relative.parts[:2]!=('data','establishments') or '..' in relative.parts or name in seen:
            raise ValueError('Invalid or duplicate directory data path')
        seen.add(name);records.extend(json.loads((path.parents[1]/relative).read_text())['establishments'])
    data['establishments']=records
    return data

def save_directory(data,path=DEST):
    # Keep media entries and all original entries in the original file. Bulk official
    # records remain small enough to review individually through the GitHub API.
    media=[p for p in data['establishments'] if not p['id'].startswith('fssai-')]
    official=[p for p in data['establishments'] if p['id'].startswith('fssai-')]
    manifest={**data,'establishments':media,'additional_data':[]}
    for i in range(0,len(official),50):
        name=f'data/establishments/fssai-{i//50+1:02}.json';manifest['additional_data'].append(name)
        dest=path.parents[1]/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps({'establishments':official[i:i+50]},ensure_ascii=False,indent=2)+'\n')
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
