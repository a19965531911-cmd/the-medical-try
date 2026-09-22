"""Experiment H1: align criterion-485 retrieval vocabulary with H clinical matcher."""

EXPH1_SOURCE = r'''
_exph1_original_retrieve_evidence = retrieve_evidence
_EXPH1_485_ALIASES = ("子宫脱垂", "盆底器官脱垂", "阴道前壁脱垂", "阴道后壁脱垂", "阴道穹隆脱垂")

class _EXPH1Metrics(dict):
    @property
    def metrics(self):
        return self

def retrieve_evidence(reports, spec):
    if str(TITLE) != "485":
        return _exph1_original_retrieve_evidence(reports, spec)
    aligned = dict(spec)
    aliases = list(spec.get("aliases", ()))
    groups = [list(group) for group in spec.get("groups", ())]
    if not groups:
        groups = [list(aliases)]
    for alias in _EXPH1_485_ALIASES:
        if alias not in aliases:
            aliases.append(alias)
        if alias not in groups[0]:
            groups[0].append(alias)
    aligned["aliases"] = aliases
    aligned["groups"] = groups
    windows = _exph1_original_retrieve_evidence(reports, aligned)
    windows.metrics = _EXPH1Metrics(windows.metrics)
    return windows
'''
