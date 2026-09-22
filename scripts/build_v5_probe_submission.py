"""Replace only the generator boot block in the independently checked artifact."""
import base64
import hashlib
import json

from build_v5_submission import BOOT, ROOT

SOURCE = ROOT / 'submission/a_test_message_bundle_v5a_transportfix_candidate.json'
OUT = ROOT / 'submission/a_test_message_bundle_v5a_probe_candidate.json'


def main():
    bundle = json.loads(SOURCE.read_text(encoding='utf-8'))
    count = 0
    for entry in bundle['entry']:
        resource = entry['resource']
        if resource.get('resourceType') != 'Library':
            continue
        content = resource['content'][0]
        old = base64.b64decode(content['data'], validate=True).decode('utf-8')
        prefix, marker, boot = old.partition('ENGINE_VERSION=')
        if not marker or not boot.rstrip().endswith('for r in result.resources]}'):
            raise ValueError('Unexpected generator boundary')
        source = prefix + BOOT.lstrip('\n')
        compile(source, resource['name'], 'exec')
        content['data'] = base64.b64encode(source.encode('utf-8')).decode('ascii')
        count += 1
    assert count == 16
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding='utf-8')
    print(OUT, OUT.stat().st_size, hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
