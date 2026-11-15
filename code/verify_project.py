"""Check saved notebooks, derived artifacts and the verified CSV after execution."""
from pathlib import Path
import hashlib,json
import nbformat
from PIL import Image
from kickstarter import ROOT,FIGURES,load_cleaned

notebooks={}
for name in ['01_data_prep.ipynb','02_analysis_and_prediction.ipynb']:
    n=nbformat.read(ROOT/'code'/name,as_version=4)
    code=[c for c in n.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in code),f'Unexecuted cells: {name}'
    assert not any(o.output_type=='error' for c in code for o in c.outputs),f'Saved errors: {name}'
    assert not any('%pip' in c.source for c in code)
    assert all(c.source.strip() for c in n.cells)
    images=sum('image/png' in o.get('data',{}) for c in code for o in c.outputs)
    notebooks[name]={'executed_code_cells':len(code),'inline_figures':images,'saved_errors':0}
assert notebooks['02_analysis_and_prediction.ipynb']['inline_figures']==6
assert sorted(p.name for p in (ROOT/'visualizations').iterdir())==sorted(FIGURES)
for name in FIGURES:
    with Image.open(ROOT/'visualizations'/name) as image:
        image.verify()
c=load_cleaned()
audit=json.loads((ROOT/'data/cohort_audit.json').read_text())
assert audit['cohort_rows']==len(c)==63075
csv_sha256=hashlib.sha256((ROOT/'data/kickstarter_cleaned_2024_2026.csv').read_bytes()).hexdigest()
assert audit['cleaned_csv_sha256']==csv_sha256=='b6c852abfce2d0dced78816e348edc59b3b919485f0401e123d7764a77fb3e2e'
assert audit['raw_observations']==2258203
assert audit['csv_parts']==721
assert audit['calendar_boundaries'][1]['deadline_on_or_after_next_jan1']==1506
metrics=json.loads((ROOT/'data/model_evaluation.json').read_text())
for model,expected in [('Always success',[76.3,0,0,0]),('Logistic Regression',[80.5,65.4,37.8,47.9]),('Decision Tree',[80.0,63.2,37.6,47.1])]:
    result=metrics['evaluation_2026'][model]
    actual=[round(100*result[k],1) for k in ['accuracy','failure_precision','failure_recall','failure_f1']]
    assert actual==expected,(model,actual,expected)
checks=json.loads((ROOT/'data/prediction_smoke_checks.json').read_text())
assert checks[0]['prediction']=='Reaches funding goal'
assert checks[1]['prediction']=='Misses funding goal'
assert checks[2]['rejected'] is True
assert len(checks[3]['cautions'])==2
# Ignore notebook bytes here: execution timing metadata can change on reruns.
paths=[ROOT/'data/kickstarter_cleaned_2024_2026.csv',*(ROOT/'visualizations'/name for name in FIGURES)]
verification={'cohort_unchanged':True,'raw_rebuild_matches_baseline':True,'notebooks':notebooks,'figure_count':6,
              'metrics_match_prior_review':True,'prediction_cases_passed':4,
              'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(ROOT/'data/verification.json').write_text(json.dumps(verification,indent=2)+chr(10))
print(json.dumps(verification,indent=2))
