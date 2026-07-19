import csv,json
from collections import Counter
from itertools import combinations
from pathlib import Path
R=Path(__file__).resolve().parents[1]; M=R/'data/master'; D='2026-04-01'; S='src_pl_jogger_price_my26_20260401'
G={'ecog120-manual':'_ecog120_manual','ecog120-automatic':'_ecog120_automatic','tce110-manual':'_tce110_manual','hybrid155-automatic':'_hybrid155_automatic'}
def rows(n):
 with (M/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
c=[r for r in rows('configurations.csv') if r['status']=='active' and r['code'].startswith('jogger_')]; v=rows('configuration_attribute_values.csv'); q=rows('configuration_attribute_value_ranges.csv'); a=rows('configuration_attribute_availability.csv'); p=rows('configuration_prices.csv'); out={}
for name,tok in G.items():
 sel=sorted(r['code'] for r in c if tok in r['code']); sets={}
 for code in sel:
  x={(r['attribute_code'],r['fuel_type_code'],'scalar') for r in v if r['configuration_code']==code and r['observation_date']==D and r['source_code']==S}
  x|={(r['attribute_code'],r['fuel_type_code'],'range') for r in q if r['configuration_code']==code and r['observation_date']==D and r['source_code']==S}; sets[code]=x
 ss=list(sets.values()); inter=set.intersection(*ss); union=set.union(*ss); ec={code:sum(r['configuration_code']==code and r['observation_date']==D and r['source_code']==S for r in a) for code in sel}; pc={code:sum(r['configuration_code']==code and r['observation_date']==D and r['source_code']==S for r in p) for code in sel}; st=Counter(r['availability_status'] for r in a if r['configuration_code'] in sel and r['observation_date']==D and r['source_code']==S)
 out[name]={'configurations':sel,'configuration_count':len(sel),'pair_count':len(list(combinations(sel,2))),'technical_slot_counts':{k:len(x) for k,x in sets.items()},'technical_sets_identical':len({tuple(sorted(x)) for x in ss})==1,'technical_intersection_count':len(inter),'technical_union_count':len(union),'scalar_slot_count':sum(k=='scalar' for _,_,k in inter),'range_slot_count':sum(k=='range' for _,_,k in inter),'technical_observation_count':len(inter)*len(sel),'technical_slots':[{'attribute_code':x,'fuel_type_code':f,'kind':k} for x,f,k in sorted(inter)],'equipment_counts':ec,'equipment_observation_count':sum(ec.values()),'equipment_status_counts':dict(sorted(st.items())),'price_counts':pc,'price_observation_count':sum(pc.values()),'complete':bool(sel) and inter==union and set(ec.values())=={53} and set(pc.values())=={1}}
o=R/'project/audits/jogger-reporting-groups.json';o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if len(c)!=22 or not all(x['complete'] for x in out.values()):raise SystemExit(1)
