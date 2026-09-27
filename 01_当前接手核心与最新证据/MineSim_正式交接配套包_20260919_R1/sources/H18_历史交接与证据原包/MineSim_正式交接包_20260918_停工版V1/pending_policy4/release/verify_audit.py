"""Independent arithmetic checks on saved sample-level evidence. Never searches."""
import math


def check(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def verify(audit, expected=None):
    nodes={n['id']:n for n in audit['nodes']}
    totals={i:[] for i in nodes}
    samples=audit['samples']; gamma=audit['gamma']; horizon=audit['horizon']
    check(len({tuple(s['uid']) for s in samples})==len(samples), 'DUPLICATE_SAMPLE_UID')
    for s in samples:
        r=s['rewards']; ids=s['path_nodes']; actions=s['action_ids'];states=s['states']
        check(0<=len(r)<=horizon and (len(r)==horizon or s['true_terminal']), 'WRONG_SAMPLE_HORIZON')
        check(len(r)==len(actions) and ids and ids[0]==0,'PATH_SHAPE')
        if states is not None:
            check(len(states)==len(r)+1,'STATE_SEQUENCE_LENGTH')
        for j,i in enumerate(ids):
            n=nodes[i]
            check(n['depth']==j,'RELATIVE_DEPTH')
            check(n['parent']==(None if j==0 else ids[j-1]),'PARENT_LINK')
            if j:
                check(n['action_from_parent']==actions[j-1],'ACTION_PATH')
            if states is not None and n['state'] is not None:
                check(n['state']==states[j],'EXPLICIT_STATE_TRACE')
            offset=max(j-1,0)
            # Algebraic discounted sum; different accumulation order to native backup.
            value=math.fsum((gamma**(k-offset))*r[k] for k in range(offset,len(r)))
            totals[i].append(value)
    max_error=0.0
    for i,n in nodes.items():
        check(n['visits']==len(totals[i]),'COUNT_FROM_TRACE')
        val=math.fsum(totals[i]); error=abs(val-n['value_sum']);max_error=max(max_error,error)
        check(math.isclose(val,n['value_sum'],abs_tol=1e-9,rel_tol=1e-11),'VALUE_FROM_FULL_HORIZON')
        q=val/len(totals[i]) if totals[i] else 0.0
        check(math.isclose(q,n['q'],abs_tol=1e-9,rel_tol=1e-11),'Q_FROM_TRACE')
        check(len(set(n['children']).intersection(n['untried']))==0,'TRIED_UNTRIED_OVERLAP')
        check(all(math.isfinite(v) for v in (n['q'],n['value_sum'])),'FINITE_STATS')
    check(nodes[0]['visits']==audit['root_visits']==len(samples),'ROOT_ACCOUNTING')
    if expected is not None:check(len(samples)==expected,'TOTAL_SUPPORT')
    return {'status':'PASS_SAMPLE_REBASED_STATS', 'samples':len(samples),'nodes':len(nodes),
            'maximum_absolute_sum_difference':max_error,'independent_mc_samples_claimed':False}


def verify_rebase(previous, promotion):
    old={tuple(s['uid']):s for s in previous['samples']}
    count=0;tail=0
    for s in promotion['samples']:
        o=old[tuple(s['uid'])]; meta=s['inherited_from']
        check(meta['removed_first_reward']==o['rewards'][0],'REMOVED_REWARD')
        prefix=o['rewards'][1:]; prefix_actions=o['action_ids'][1:]
        check(s['rewards'][:len(prefix)]==prefix,'REWARD_SUFFIX_CHANGED')
        check(s['action_ids'][:len(prefix_actions)]==prefix_actions,'ACTION_SUFFIX_CHANGED')
        check(s['tail_actions_added']==len(s['rewards'])-len(prefix) in (0,1),'TAIL_COUNT')
        check(meta['old_rewards']==o['rewards'] and meta['old_action_ids']==o['action_ids'],'OLD_TRACE_SOURCE')
        count+=1;tail+=s['tail_actions_added']
    return {'status':'PASS_REMOVE_FIRST_REWARD_AND_COMPLETE_HORIZON', 'inherited_samples':count,
            'tail_transitions':tail, 'old_q_copied':False}
