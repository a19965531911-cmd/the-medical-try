"""Append platform transport without modifying frozen candidates."""
import base64
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.b5_experiments import build_variant
from scripts.build_b_submission import submission_sanity_check,load_rows


def build(variant):
    bundle=build_variant('B5'+variant[-1])
    transport=(ROOT/'src/b_board/b6_transport.py').read_text(encoding='utf8')
    for entry in bundle['entry'][1:]:
        r=entry['resource']
        source=base64.b64decode(r['content'][0]['data']).decode('utf8')
        source+='\nB6_CONFIG='+repr(dict(endpoint='http://127.0.0.1:1213/v1/chat/completions',max_tokens=2048))+'\n'
        source+='B5_CONFIG.update(variant='+repr(variant)+',total_model_budget_seconds=8,request_timeout_seconds=8)\n'
        source+=transport
        compile(source,r['name'],'exec')
        r['content'][0]['data']=base64.b64encode(source.encode()).decode()
    submission_sanity_check(bundle,load_rows())
    return bundle


if __name__=='__main__':
    dest=ROOT/'experiment/b6';dest.mkdir(exist_ok=True)
    for variant in ('B6R','B6H','B6L'):
        name='B6H_platform_candidate' if variant=='B6H' else variant
        (dest/(name+'.json')).write_text(json.dumps(build(variant),ensure_ascii=False,indent=2),encoding='utf8')
    print('Built B6R/B6H/B6L; platform inference unverified; publication blocked')
