import asyncio, pickle, math, os, shutil, stat, tempfile, time, warnings, numpy as np, pandas as pd
from datetime import datetime, timezone, timedelta
warnings.filterwarnings("ignore")
from polar_nexus.iceberg.core import *
from polar_nexus.iceberg.orchestrator import assess_iceberg
M='models/IMMUTABLE/'; U='models/original/'; HERE=os.path.dirname(os.path.abspath(__file__))
CONF = os.path.abspath(os.path.join(HERE, '../../configs'))
N=[0]
def ok(n): N[0]+=1; print("PASS", n)
UTC=timezone.utc
man={'4_dataset_model':'35335e9b01f6fdb9337f9998443804bbfcc32440dce28b19e5a13fc5420758e9','5_dataset_model':'ddf91b5d8484e6011ec2c42068c17008c054b8712eaf7fb9267213a066ee3879',
     '6_dataset_model.zip':'07c3c27199aa5026fe826d05e5ab229db05b334f07e33d99ca1afc8b1b4bbe08','8_dataset_model':'3f7ffeec8b6a3a4c01fbc25939df8dabb0eb21f11075d07ed065538e745f1baa'}
before={f:sha256_file(U+f) for f in man}

# ---- 15 immutability
assert verify_manifest(man,U); ok("15 originals match manifest")
t=tempfile.mkdtemp(); shutil.copy(U+'5_dataset_model',t+'/x'); os.chmod(t+'/x', stat.S_IWRITE | stat.S_IREAD); open(t+'/x','ab').write(b'!')
try: verify_manifest({'x':man['5_dataset_model']},t); raise SystemExit("tamper not caught")
except ArtifactMismatch: ok("15 tampered artifact rejected")
d=freeze_copy(U+'5_dataset_model',t+'/IMMUTABLE/m5.zip',man['5_dataset_model']); assert stat.S_IMODE(os.stat(d).st_mode)==0o444 and sha256_file(d)==man['5_dataset_model']; ok("15 freeze_copy byte-identical, mode 0444")

# ---- 11 config versioned + hashed
cfg=HazardCfg.load(CONF+'/hazard_config.v1.json'); s=cfg.stamp(); assert s['hazard_config_version']=='hazard-cfg-1.0.0' and len(s['hazard_config_sha256'])==64
import json; raw=json.load(open(CONF+'/hazard_config.v1.json')); raw['params']['r24_km']=3.0; json.dump(raw,open(t+'/c.json','w')); assert HazardCfg.load(t+'/c.json').sha256!=cfg.sha256
assert HazardCfg.load(CONF+'/hazard_config.v1.json').sha256==cfg.sha256; ok("11 config version+sha256; param change => new hash; stable otherwise")
assert cfg.r24_km==6.84 and cfg.provenance['r24_km'].startswith('D4'); ok("11 r24 sourced from measured D4 persistence P90, provenance stored")

# ---- 7 temporal semantics
now=datetime(2025,12,31,12,tzinfo=UTC); b=datetime(2025,12,31,0,tzinfo=UTC)
p=mk_point("P6","predicted","model_6","x","operational",0,0,b,24.0,now); assert p.valid_at-p.base_time==timedelta(hours=24)
for bad in (lambda: Point("P6","predicted","m","v","operational",0,0,0,0,b,b+timedelta(hours=5),24.0,now),
            lambda: Point("P4","observed","d","v","operational",0,0,0,0,b.replace(tzinfo=None),b,0.0,now),
            lambda: mk_point("P4","observed","d","v","operational",0,0,b,3.0,now)):
    try: bad(); raise SystemExit("semantics not enforced")
    except ValueError: pass
ok("7 every Point: base_time/valid_at/horizon/computed_at validated; naive tz, wrong horizon, observed@h>0 rejected")

# ---- 5/6 M5 units + scaler never loaded
pl=pickle.load(open(M+'5_dataset_model/V6_1_clean_final/V6_1_final_model.pkl','rb'))['model']; mean=dict(zip(M5_FEATURES,pl.named_steps['scaler'].mean_))
_,_,(dx,dy)=m5_predict(pl,dict(mean),1286.584e3,-43.844e3)
bad=pl.predict(np.array([[1286.584e3 if k=='x_t' else -43.844e3 if k=='y_t' else mean[k] for k in M5_FEATURES]]))[0]
assert max(abs(dx),abs(dy))<5 and max(abs(bad))>500; ok(f"5 km->m adapter: {dx:.2f},{dy:.2f} m (metre input would give {bad[0]:.0f},{bad[1]:.0f} m)")
import re; src=open(HERE+'/../../iceberg/core.py').read()+open(HERE+'/../../iceberg/orchestrator.py').read(); assert not re.search(r'(load|open)\([^)]*feature_scaler',src)
ok("6 no code path loads feature_scaler.pkl")

# ---- 2/3 advisory only
adv=m5_advisory(pl,dict(mean),1286.584e3,-43.844e3,b,now); assert adv.role_in_hazard=='advisory' and adv.horizon_h==8760
class F:  # fake M8 parts
    def __init__(s,v): s.v=v
    def predict(s,X): return np.array([s.v])
    def transform(s,X): return np.nan_to_num(X)
fm={'xgb_e':F(.2),'et_e':F(.1),'xgb_n':F(-.3),'et_n':F(-.2),'imputer':F(0)}; names=[f"f{i}" for i in range(87)]
a8=m8_advisory(fm,names,{n:1.0 for n in names},0,0,b,now,0.15); assert abs(a8.quality['east_km']-(0.8*.2+0.2*.1))<1e-12 and a8.quality['parity']=='UNVERIFIED'
try: m8_advisory(fm,names,{n:1.0 for n in names[:40]},0,0,b,now,0.15); raise SystemExit("imputation cap")
except ValueError: pass
ok("3 M8 advisory: 0.8/0.2 blend, heavy imputation refused, parity flagged UNVERIFIED")
p4x=mk_point("P4","observed","dataset_4","D4","operational",0,0,b,0.0,now); pkx=mk_point("P_kin24","derived","persistence_baseline","k","baseline",1000,0,b,24.0,now)
for a in (adv,a8):
    try: build_route_hazard([p4x,pkx,a],cfg); raise SystemExit("advisory leaked")
    except ForbiddenHazardInput: pass
ok("2,3 build_route_hazard rejects M5/M8 points structurally")

# ---- data
d4=pd.read_pickle(U+'4_dataset_model'); wm=d4.datetime_utc.max().to_pydatetime()
live=[i for i in d4.iceberg_id.unique() if d4[d4.iceberg_id==i].datetime_utc.max()>=d4.datetime_utc.max()]
ice=live[0]; asof=datetime(2025,12,31,12,tzinfo=UTC)
def run(now,mode,ad,wmk=wm,i=None): return asyncio.run(assess_iceberg(i or ice,d4,wmk,now,cfg,ad,load_m6_limitations(M+'6_dataset_model/metadata_final.json'),mode=mode))

def fake_m6(tr,delay=0.0,dev=(1200.,-800.)):
    time.sleep(delay); vx,vy=kinematic_velocity(tr['t_h'],tr['x'],tr['y']); base=tr['base_time']
    return mk_point("P6","predicted","model_6","fake","operational",tr['x'][-1]+vx*24+dev[0],tr['y'][-1]+vy*24+dev[1],base,24.0,datetime.now(UTC),{"stand_in":True})
# ---- 4/13 freshness + live ingest
r=run(datetime(2026,9,28,12,tzinfo=UTC),"operational",{}); assert r['status']==INSUFFICIENT and "INGEST_NOT_LIVE" in r['reason']; ok("13 operational mode + stale store => INSUFFICIENT_DATA (INGEST_NOT_LIVE)")
r=run(datetime(2026,9,28,12,tzinfo=UTC),"replay",{}); assert r['status']==INSUFFICIENT and "P4_STALE" in r['reason']; ok("4 stale P4 => INSUFFICIENT_DATA even in replay")
r=run(asof+timedelta(days=3),"operational",{},wmk=asof+timedelta(days=3)); assert r['status']==INSUFFICIENT and "P4_STALE" in r['reason']; ok("4 fresh store but iceberg fix 3 d old => INSUFFICIENT_DATA")
r=run(asof,"operational",{'m6':lambda tr:fake_m6(tr)}); assert r['status']==OK, r; ok(f"4/13 live store + fresh P4 (age {r['points'][0]['quality']['age_h']:.0f} h) => {r['status']}")
r_rep=run(asof,"replay",{'m6':lambda tr:fake_m6(tr)}); assert r_rep['status']==REPLAY; ok("13 replay is labelled REPLAY_NOT_OPERATIONAL, never OPERATIONAL_OK")

# ---- 9/10/7 baseline + M6 limits + roles
roles={p['role']:p for p in r['points']}; assert set(roles)=={'P4','P_kin24','P6'}
assert roles['P_kin24']['role_in_hazard']=='baseline' and roles['P_kin24']['kind']=='derived' and 'not truth' in roles['P_kin24']['limitations'][0]; ok("9 persistence vertex tagged baseline/derived with limitation text")
ml=r['model_limitations']['model_6']; assert ml['beats_persistence'] is False and abs(ml['improvement_over_persistence_pct']+11.7528)<1e-3 and len(ml['caveats'])==4 and 'unseen-iceberg' in ml['caveats'][3]; ok("10 M6 limits in every response: -11.75% vs persistence, 46.9 km tail, interpolated-data validation, no unseen-iceberg holdout")
for p_ in r['points']: assert p_['valid_at'] and p_['base_time'] and 'horizon_h' in p_
assert roles['P4']['horizon_h']==0 and roles['P6']['horizon_h']==24 and roles['P_kin24']['horizon_h']==24; assert r['envelope']['temporal']['semantics']=='swept_envelope_not_same_instant'; ok("7 P4@t0, P_kin24@t0+24h, P6@t0+24h; envelope labelled swept, not same-instant")

# ---- 2/3 advisory separate & 14 parallel
def slow(k,pt=None):
    def f(tr): time.sleep(0.3); return pt(tr) if pt else {"k":k}
    return f
ad={'m6':lambda tr:fake_m6(tr,0.3),'m1':slow('sic'),'m5':lambda tr:(time.sleep(0.3),adv)[1],'m8':lambda tr:(time.sleep(0.3),a8)[1]}
t0=time.perf_counter(); r=run(asof,"operational",ad); wall=time.perf_counter()-t0
assert wall<0.3*4*0.6 and r['wall_ms']<600, (wall,r['timings_ms']); ok(f"14 4 independent stages 0.3 s each ran concurrently: wall {r['wall_ms']:.0f} ms (sequential would be ~1200)")
assert {a['role'] for a in r['advisories']}=={'M5_ADV','M8_ADV'} and all(p['role'] in ('P4','P_kin24','P6') for p in r['points']); assert all(p.role_in_hazard!='advisory' for p in r['route_hazard'].hazard.points); ok("2,3 M5/M8 returned as advisories, absent from hazard points")
# failure handling
def boom(tr): raise RuntimeError("x")
r=run(asof,"operational",{'m6':lambda tr:fake_m6(tr),'m8':boom}); assert r['status']==DEGRADED and r['missing']==['m8'] and r['envelope']['kind'] in('buffered_triangle',); ok("14 M8 failure => DEGRADED, hazard unaffected")
r=run(asof,"operational",{'m6':boom}); assert r['status']==DEGRADED and r['envelope']['kind']=='buffered_linestring' and r['envelope']['metrics']['triangle_available'] is False and r['route_hazard'].degraded; ok("14 M6 failure => DEGRADED kinematic-only (no triangle claimed, labelled)")
assert run(asof,"operational",{'m6':lambda tr:fake_m6(tr)})['cache_key']==run(asof,"operational",{'m6':lambda tr:fake_m6(tr)})['cache_key'] and cfg.sha256 in r['cache_key']; ok("cache key = (iceberg, base_time, cfg hash)")

# ---- 1/8/12 geometry, time dependence, metrics
o=to_xy(-71,0); P4=mk_point("P4","observed","d","D","operational",*o,b,0,now)
def at(dxm,dym,role,kind="derived",src="persistence_baseline",rih="baseline"): return mk_point(role,kind if role!="P6" else "predicted",src if role!="P6" else "model_6","v",rih if role!="P6" else "operational",o[0]+dxm,o[1]+dym,b,24.0,now)
hz=build_route_hazard([P4,at(0,10000,"P_kin24"),at(10000,0,"P6")],cfg).hazard; m=hz.metrics()
assert abs(m['triangle_area_km2']-50)<0.1 and abs(m['disagreement_km']-14.142)<0.02 and abs(m['heading_diff_deg']-90)<0.05 and abs(m['disagreement_ratio']-14.142/6.84)<0.01 and abs(m['speed_ratio_m6_over_kin']-1)<1e-3; ok(f"12 metrics exact: area {m['triangle_area_km2']:.1f} km2, disagreement {m['disagreement_km']:.2f} km ({m['disagreement_ratio']:.2f}x r24), heading diff {m['heading_diff_deg']:.0f} deg")
assert hz.envelope()['kind']=='buffered_triangle' and abs(hz.envelope()['buffer_km']-6.84)<1e-9; ok("1 triangle P4+P_kin24+P6 buffered by configured r24")
hzc=build_route_hazard([P4,at(0,10000,"P_kin24"),at(0,25000,"P6")],cfg).hazard; assert hzc.envelope()['kind']=='buffered_linestring'; ok("1 collinear => buffered linestring")
hzd=build_route_hazard([P4,at(0,0,"P_kin24"),at(0,0,"P6")],cfg).hazard; assert hzd.envelope()['metrics']['triangle_area_km2']==0; ok("1 duplicate points handled")
a0,b0=hz.centres(0); a12,b12=hz.centres(12); assert np.hypot(*(a12-a0))>0 and np.hypot(*(b12-b0))>0 and hz.radius_km(0)<hz.radius_km(24)<hz.radius_km(48); ok(f"8 time-dependent: centres move, r(0)={hz.radius_km(0):.1f}, r(24)={hz.radius_km(24):.1f}, r(48)={hz.radius_km(48):.1f} km")
f=hz.field(range(0,145,12)); assert len(f)==13 and f[0]['h']==0 and f[-1]['unbounded'] and not f[6]['unbounded'] and f[-1]['h']==144; ok("8 HazardField slices with valid_at + unbounded flag once r>60 km (~124 h)")
c12=hz.centres(12)[1]; hit=np.array([[c12[0],c12[1],11.9],[c12[0]+100,c12[1],12.1]]); r1=cpa_tcpa(hit,hz)
early=hit.copy(); early[:,2]=[0.0,0.2]; r2=cpa_tcpa(early,hz)
assert r1['min_clearance_grid_m']<0 and 11.9<=r1['tcpa_h']<=12.1 and r2['min_clearance_grid_m']>1000; ok(f"8 same waypoint: hit at h=12 (clearance {r1['min_clearance_grid_m']/1e3:.1f} km), clear at h=0 (+{r2['min_clearance_grid_m']/1e3:.1f} km) => a static polygon would misjudge")
hzl=build_route_hazard([P4,at(0,10000,"P_kin24"),at(1000,10000,"P6")],cfg).hazard; assert hz.risk_level(-1)=="HIGH" and hz.risk_level(1e9)=="MEDIUM" and hzl.risk_level(1e9)=="LOW"; hzx=build_route_hazard([P4,at(0,10000,"P_kin24"),at(30000,0,"P6")],cfg).hazard; assert hzx.risk_level(1e9)=="HIGH"; ok("12 disagreement ratio drives risk level (2.1x => MEDIUM, 4.6x => HIGH even with clear route; 0.15x => LOW)")

assert {f_:sha256_file(U+f_) for f_ in man}==before; ok("15 all four original artifacts byte-identical after full run")

# ---- Regression Tests (A, B)
def test_regression_d4_jump_filter():
    df = pd.DataFrame({'iceberg_id':['j']*5,'datetime_utc':pd.date_range('2025-1-1',periods=5,freq='1h',tz='UTC'),'latitude':[-60]*5,'longitude':[-40,-50,-50.01,-50.02,-50.03],'source_quality':[0]*5})
    tr = d4_clean_track(df, 'j', datetime(2025,1,1,10,tzinfo=UTC), cfg)
    assert tr['n_clean'] == 4; ok("A. D4 jump-filter recovers from bad first fix")

def test_regression_d4_source_quality():
    df = pd.DataFrame({'iceberg_id':['q']*3,'datetime_utc':pd.date_range('2025-1-1',periods=3,freq='1h',tz='UTC'),'latitude':[-60]*3,'longitude':[-50,-50.01,-50.02],'source_quality':[0, 1, 0]})
    tr = d4_clean_track(df, 'q', datetime(2025,1,1,10,tzinfo=UTC), cfg)
    assert tr['n_clean'] == 3 and tr['q_dist'] == {0: 2, 1: 1} and tr['n_raw'] == 3; ok("B. D4 source quality=0 is kept, distribution reported")

test_regression_d4_jump_filter()
test_regression_d4_source_quality()

print(f"ALL {N[0]} CHECKS PASSED")
