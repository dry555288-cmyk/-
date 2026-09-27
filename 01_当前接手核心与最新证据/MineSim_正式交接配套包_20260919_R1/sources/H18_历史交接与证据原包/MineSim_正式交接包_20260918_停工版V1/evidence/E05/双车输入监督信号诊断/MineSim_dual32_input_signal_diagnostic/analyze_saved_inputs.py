"""Descriptive analysis of frozen MineSim input/return records, not a model trial.
Reads only packaged JSON; no MineSim imports, fitting, forward, simulation, or network.
Usage for reproduction: python analyze_saved_inputs.py --inputs inputs --out new_output_dir
All thresholds below are descriptive display bins, never label or exclusion rules.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, statistics, struct
from pathlib import Path
import numpy as np

DATA_SHA = '9abe28a904c3be43d68c0e5973d6bfa6d84e3cf7882c9d74d6b5b4b41471bbc1'
ACTIONS = ('0,3', '3,0')
PARKED = 'BOTH_PARKED_AT_OWN_DESTINATIONS'
CAP = 'EVALUATION_CAP_NOT_TASK_TERMINAL'
NAMES13 = ['route_fraction','remaining_to_goal_lower_fraction','remaining_to_goal_upper_fraction',
           'speed_div15','command_accel_div3','target_speed_div15','braking_margin_fraction',
           'goal_reached','prev_none','prev_brake','prev_decel','prev_keep','prev_accel']

def require(condition, message):
    if not condition: raise ValueError(message)

def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()

def sha(b): return hashlib.sha256(b).hexdigest()

def load(path): return json.loads(path.read_bytes())

def write(path, value):
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False); out.write('\n')

def feature26(state):
    values=[]
    for token in ('A','B'):
        c=state['vehicles'][token]; lo,hi=c['goal_window_m']; s=c['route_s']; v=c['speed_mps']; p=c['prev_action']
        values += [s/hi,(lo-s)/hi,(hi-s)/hi,v/15,c['accel_mps2']/3,c['target_speed_mps']/15,
                   (hi-s-v*v/6)/hi,float(c['goal_reached'])]+[float(p==a) for a in (None,0,1,2,3)]
    return list(struct.unpack('<26f',struct.pack('<26f',*values)))

def four_direction(a,b):
    require(len(a)==len(b)==4, 'FOUR_PER_BLOCK')
    tolerance=1e-9*max(1.0,*(abs(x) for x in a+b))
    return 1 if min(a)>max(b)+tolerance else -1 if min(b)>max(a)+tolerance else None

def stats(values):
    return {'count':len(values), 'mean':math.fsum(values)/len(values) if values else None,
            'sample_sd':statistics.stdev(values) if len(values)>1 else None,
            'min':min(values) if values else None,'max':max(values) if values else None}

def analyze(inputs, out):
    require(not out.exists(),'OUTPUT_EXISTS_NO_OVERWRITE')
    identity=load(inputs/'SOURCE_IDENTITY.json')
    for entry in identity['files']:
        b=(inputs/entry['copy']).read_bytes()
        require(len(b)==entry['size'] and sha(b)==entry['sha256'],'SOURCE_CHANGED:'+entry['copy'])
    raw=(inputs/'DATASET32.json').read_bytes(); require(sha(raw)==DATA_SHA,'DATASET_SHA')
    d=json.loads(raw); rows=d['rows']; combined=load(inputs/'COMBINED32_INPUTS.json')
    cmap={r['root_id']:r for r in combined}
    require(len(rows)==len(cmap)==32 and sum(len(r['records']) for r in rows)==512,'COUNTS')
    X=np.asarray([r['x'] for r in rows],dtype=float)
    y=np.asarray([r['empirical_mean_gap03_minus30'] for r in rows],dtype=float)
    groups=collections.Counter(r['source_run'] for r in rows)
    require(len(groups)==8 and set(groups.values())=={4},'SOURCE_GROUPS')
    require(len({r['feature_sha256'] for r in rows})==32,'EXACT_FEATURE_ALIAS')
    contexts={ep:load(inputs/(ep+'.json')) for ep in {r['condition'] for r in rows}}
    details=[]; ids=[]; seeds=[]; masks_before=sha(canonical([[r['root_id'],r['original_training_mask'],r['hard_label_originally_unknown'],r['repeated_order_sign']] for r in rows]))
    for r in rows:
        state=r['full_state']; c=cmap[r['root_id']]; ep=r['condition']; ctx=contexts[ep]
        require(feature26(state)==r['x'],'FEATURE_RECONSTRUCTION')
        require(sha(struct.pack('<26f',*r['x']))==r['feature_sha256'],'FEATURE_HASH')
        require(sha(canonical(state))==r['state_sha256']==c['exact_before_state_sha256'],'STATE_HASH')
        require(state==c['state'] and c['task']['task_id']==r['source_run'],'COMBINED_STATE_BINDING')
        require(sha((inputs/(ep+'.json')).read_bytes())==c['task']['context_sha256'],'CONTEXT_HASH')
        require(all(r['mask16']) and c['step_index']>0,'ADMISSION_AND_PREVIOUS_TRANSITION')
        require(len(r['records'])==16,'RECORDS_PER_STATE')
        parts={}; signs=[]; bg=[]
        for block in ('block0','block1'):
            ba={a:[t['window_return'] for t in r['records'] if t['action_id']==a and t['block']==block] for a in ACTIONS}
            require(all(sorted(ba[a])==sorted(r['blocks'][block][a]) for a in ACTIONS),'BLOCKS')
            signs.append(four_direction(ba[ACTIONS[0]],ba[ACTIONS[1]]))
            bg.append(math.fsum(ba[ACTIONS[0]])/4-math.fsum(ba[ACTIONS[1]])/4)
        repeat=signs[0] if signs[0] is not None and signs[0]==signs[1] else None
        require(repeat==r['repeated_order_sign'],'STORED_REPEATED_SIGN')
        require(all(abs(a-b)<1e-9 for a,b in zip(bg,r['block_mean_gaps'])),'BLOCK_MEAN')
        for a in ACTIONS:
            rec=[t for t in r['records'] if t['action_id']==a]; values=[t['window_return'] for t in rec]
            require(len(values)==8,'EIGHT_PER_ACTION')
            require(abs(math.fsum(values)/8-r['mean_returns'][a])<1e-9,'SAVED_MEAN')
            by={k:stats([t['window_return'] for t in rec if t['task_outcome']==k]) for k in (PARKED,CAP)}
            require(sum(v['count'] for v in by.values())==8,'OUTCOME_DOMAIN')
            parts[a]={**stats(values),'outcome_mixture':by}
            for t in rec:
                require(t['window_target_observed'] and math.isfinite(t['window_return']),'OBSERVED_WINDOW')
                if t['task_outcome']==CAP:
                    require(t['executed_steps']==t['maximum_outer_steps']==128 and
                            t['old_full_task_return'] is None and t['old_full_task_tail_censored'],'CAP_TAIL')
                ids.append(t['cell_id']); seeds.append(t['rng_seed'])
        delta=parts[ACTIONS[0]]['mean']-parts[ACTIONS[1]]['mean']
        require(abs(delta-r['empirical_mean_gap03_minus30'])<1e-9,'GAP')
        variance=math.fsum(parts[a]['sample_sd']**2/8 for a in ACTIONS)
        vs=state['vehicles']; dist={t:ctx['conflict_route_s'][t]-vs[t]['route_s'] for t in ('A','B')}
        times={t:dist[t]/vs[t]['speed_mps'] if dist[t]>0 and vs[t]['speed_mps']>0 else None for t in ('A','B')}
        valid=all(times[t] is not None for t in ('A','B'))
        details.append({'root_id':r['root_id'],'source_run':r['source_run'],'condition':ep,
          'new_state':c['role']=='NEW_INPUT_ONLY_NOT_TEACHER_LABEL','empirical_mean_gap':delta,
          'block_mean_gaps':bg,'absolute_block_difference':abs(bg[0]-bg[1]),
          'block_mean_sign_changed':bg[0]*bg[1]<0,'stored_repeated_order_sign_unchanged':repeat,
          'original_training_mask_unchanged':r['original_training_mask'],
          'descriptive_independent_repeat_gap_SE':math.sqrt(variance),
          'SE_scope':'Plug-in summary assuming independent repeats within this fixed model; n=8 each; not a confidence bound, label, safety threshold, or proven noise floor.',
          'actions':parts,
          'has_CAP_observation':any(parts[a]['outcome_mixture'][CAP]['count']>0 for a in ACTIONS),
          'prior_transition_sampled_min_clearance_m':state['minimum_internal_clearance_m'],
          'source_conflict_reference_s_m':ctx['conflict_route_s'],
          'signed_distance_to_source_reference_m':dist,
          'speed_mps':{t:vs[t]['speed_mps'] for t in ('A','B')},
          'both_upstream_of_source_reference':all(dist[t]>0 for t in ('A','B')),
          'constant_current_speed_time_to_reference_s':times,
          'time_difference_A_minus_B_s':times['A']-times['B'] if valid else None,
          'reference_scope':'Saved C11 route reference, not recomputed collision region. d/v ignores acceleration, vehicle length, interaction and uncertainty; not TTC, safety permission or a tested policy.'})
    require(len(set(ids))==len(set(seeds))==512,'RECORD_SEED_IDENTITIES')
    f=[]
    for j,name in enumerate([f'{t}_{n}' for t in ('A','B') for n in NAMES13]):
        f.append({'index':j,'name':name,'unique_values':len(set(X[:,j])),'min':float(X[:,j].min()),
                  'max':float(X[:,j].max()),'constant_in_this_dataset':bool(np.ptp(X[:,j])==0)})
    svals=np.linalg.svd(X-X.mean(axis=0),compute_uv=False)
    groups_stats={}
    baseline=np.array([np.mean([y[j] for j in range(32) if rows[j]['source_run']!=r['source_run']]) for r in rows])
    ae=np.abs(y-baseline); sq=(y-baseline)**2
    for label,mask in [('old16',np.array([not t['new_state'] for t in details])),
                       ('new16',np.array([t['new_state'] for t in details])),('all32',np.ones(32,dtype=bool)),
                       ('any_CAP',np.array([t['has_CAP_observation'] for t in details])),
                       ('no_CAP',np.array([not t['has_CAP_observation'] for t in details])),
                       ('both_upstream',np.array([t['both_upstream_of_source_reference'] for t in details])),
                       ('not_both_upstream',np.array([not t['both_upstream_of_source_reference'] for t in details]))]:
        yy=y[mask]; groups_stats[label]={'count':len(yy),'gap_min':float(yy.min()),'gap_max':float(yy.max()),
          'abs_gap_le1_count':int((abs(yy)<=1).sum()),'abs_gap_le2_count':int((abs(yy)<=2).sum()),
          'abs_gap_gt10_count':int((abs(yy)>10).sum()),'constant_baseline_absolute_error_fraction':float(ae[mask].sum()/ae.sum()),
          'constant_baseline_squared_error_fraction':float(sq[mask].sum()/sq.sum())}
    neighbours=[]
    for i,r in enumerate(rows):
        candidates=[j for j,q in enumerate(rows) if q['source_run']!=r['source_run']]
        j=min(candidates,key=lambda j:(float(np.linalg.norm(X[i]-X[j])),rows[j]['root_id']))
        neighbours.append({'root_id':r['root_id'],'other_source_nearest_root':rows[j]['root_id'],
         'physical_normalized26_Euclidean_distance':float(np.linalg.norm(X[i]-X[j])),
         'gap':float(y[i]),'other_gap':float(y[j]),'scope':'Descriptive nearest neighbour chosen using input only; not fitted model or prospective evaluation.'})
    summary={'status':'COMPLETE_FIXED512_INPUT_SIGNAL_DIAGNOSTIC_NOT_MODEL_VALIDATION',
      'scope':'Post-outcome descriptive analysis; no new labels, data exclusions, training or online decisions.',
      'source_identity_files_checked':len(identity['files']), 'dataset_sha256':DATA_SHA,
      'states':32,'source_groups':dict(groups),'observations':512,'all_feature26_reconstruction_exact':True,
      'all_state_feature_context_bindings_match':True,'exact_feature_aliases':0,
      'constant_feature_columns':[v['name'] for v in f if v['constant_in_this_dataset']],
      'centered_feature_singular_values':svals.tolist(),'centered_rank_at_descriptive_absolute_tol_1e_minus6':int((svals>1e-6).sum()),
      'rank_scope':'Tolerance is for describing float32 rounding and column redundancy, not feature selection or effective sample count.',
      'groups':groups_stats,'repeated_signs_unchanged':dict(collections.Counter(str(t['stored_repeated_order_sign_unchanged']) for t in details)),
      'block_mean_direction_flips':sum(t['block_mean_sign_changed'] for t in details),
      'block_difference_gt10_count':sum(t['absolute_block_difference']>10 for t in details),
      'largest_block_difference':max(details,key=lambda t:t['absolute_block_difference'])['root_id'],
      'max_absolute_block_difference':max(t['absolute_block_difference'] for t in details),
      'all_state_masks_snapshot_sha256':masks_before,
      'no_new_fits':True,'new_fits':0,'saved_model_forwards':0,'MCTS_calls':0,'new_samples':0,
      'remote_connection':False,'source_files_modified':False,
      'next_scope':'Propose root-only explicit interaction features; no current authorization to fit, collect, prune, deploy or change rewards.',
      'interpretation_boundaries':['Dataset integrity and model usefulness are distinct.',
       'Small empirical gaps and CAP groupings are retrospective descriptions, never live input fields or filters.',
       'CAP is observed Y64 with unknown full-task tail; do not relabel as collision or missing data.',
       'Missing explicit geometry is not proof of information-theoretic insufficiency on one fixed route.',
       'Saved minimum_internal_clearance_m is preceding transition sampled minimum for these noninitial roots, not instantaneous point clearance.',
       'Signed distance and d/v features come from bound route references and current state only; d/v is not a collision probability or TTC.',
       'Old and new state sets differ; comparisons are descriptive, not a randomized single-factor experiment.']}
    out.mkdir(parents=True,exist_ok=False)
    write(out/'SUMMARY.json',summary);write(out/'PER_STATE_SIGNAL.json',details)
    write(out/'FEATURE_COLUMNS.json',f);write(out/'NEAREST_OTHER_SOURCE.json',neighbours)
    table=['# 双车输入与监督信号逐状态诊断','',
           '只读、事后描述；无新增训练、仿真或标签。参考点时间为当前速度近似，不是TTC。','',
           '|状态|均值回报差|前4次差|后4次差|CAP 03/30|上一转换最小净距m|到参考点时间 A/B s|',
           '|---|---:|---:|---:|---:|---:|---:|']
    for t in details:
        times=t['constant_current_speed_time_to_reference_s']; ts='/'.join('不适用' if times[a] is None else f'{times[a]:.3f}' for a in ('A','B'))
        cap='/'.join(str(t['actions'][a]['outcome_mixture'][CAP]['count']) for a in ACTIONS)
        table.append(f"|{t['root_id']}|{t['empirical_mean_gap']:.3f}|{t['block_mean_gaps'][0]:.3f}|{t['block_mean_gaps'][1]:.3f}|{cap}|{t['prior_transition_sampled_min_clearance_m']:.3f}|{ts}|")
    (out/'STATE_TABLE.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['status','states','observations','new_fits','MCTS_calls','new_samples']},ensure_ascii=False))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); analyze(a.inputs,a.out)
