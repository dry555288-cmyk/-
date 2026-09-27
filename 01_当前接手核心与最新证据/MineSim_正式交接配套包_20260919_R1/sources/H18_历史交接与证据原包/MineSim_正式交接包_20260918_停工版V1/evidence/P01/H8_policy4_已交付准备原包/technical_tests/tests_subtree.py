from dataclasses import dataclass,asdict,replace
import importlib.util,json,math,sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent
RT=BASE/'minesim_dual_subtree_h8_smoke_v1'/'parent_sources/parent_sources/parent_sources/parent_sources/parent_sources/runtime'
sys.path[:0]=[str(BASE/'release'),str(RT)]
from candidate_mcts.fleet_search import FleetMCTSSearch
from candidate_mcts.joint_action import JointAction
from candidate_mcts.action_space import MCTSAction
from subtree_reuse import HorizonRebasedSearch,discounted
from verify_audit import verify,verify_rebase

@dataclass(frozen=True)
class ToyState:
    t:int=0
    x:int=1
    stop:int=100
    hard_safety_violation:bool=False
    @property
    def all_goals_reached(self):return self.t>=self.stop
    @property
    def minimum_clearance_m(self):return 1.0
    @property
    def controlled_tokens(self):return ('A','B')
class Transition:
    calls=0
    def step(self,s,a):
        self.calls+=1
        return replace(s,t=s.t+1,x=s.x+int(a.actions[0])*2+int(a.actions[1]))
class Reward:
    def evaluate(self,s,n):return 100.+s.t*7. + (n.x-s.x)*.11 - (n.x%7)*.5
    def is_terminal(self,s,d,h):return s.hard_safety_violation or s.all_goals_reached or d>=h

def actions(s):
    if s.hard_safety_violation or s.all_goals_reached:return []
    return [JointAction.from_pairs((('A',MCTSAction(i)),('B',MCTSAction(j)))) for i in range(4) for j in range(4)]
def new(seed=1,h=8,b=64):
    t=Transition();r=Reward();tag={'v':'same'}
    kw=dict(transition_model=t,reward_model=r,action_provider=actions,budget=b,max_depth=h,seed=seed)
    native=FleetMCTSSearch(**kw)
    reuse=HorizonRebasedSearch(**kw,state_encode=lambda s:asdict(s),binding=lambda:tag['v'])
    return t,native,reuse,tag

def clean(d):return {k:v for k,v in d.items() if k not in ('elapsed_ms','reuse_accounting')}
def normalized(a):return json.loads(json.dumps(a))

class SubtreeTests(unittest.TestCase):
    def test_cold_equivalence_seed1(self):self.cold(1)
    def test_cold_equivalence_seed0(self):self.cold(0)
    def test_cold_equivalence_seed9(self):self.cold(9)
    def cold(self,seed):
        t,b,c,_=new(seed);s=ToyState();a,d=b.search(s);aa,dd=c.search(s)
        self.assertEqual(a,aa);self.assertEqual(clean(d),clean(dd));self.assertEqual(b.rng.getstate(),c.rng.getstate());verify(c.audit(),64)
    def test_promote_horizon_and_count(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);old=normalized(c.audit());ns=t.step(s,a);c.search(ns)
        m=c.last_meta;self.assertGreater(m['inherited_samples'],0);self.assertEqual(m['inherited_samples']+m['new_iterations'],64)
        self.assertEqual(m['tail_transitions'],m['inherited_samples']);verify(c.audit(),64)
        verify_rebase(old,normalized(c.promotion_snapshot))
    def test_old_reward_excluded(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);old=normalized(c.audit());c.search(t.step(s,a))
        audit=normalized(c.promotion_snapshot);verify(audit)
        for r in audit['samples']:
            o=next(x for x in old['samples'] if x['uid']==r['uid'])
            self.assertEqual(r['rewards'][:7],o['rewards'][1:])
    def test_nonterminal_length_eight(self):
        t,b,c,_=new();s=ToyState()
        for k in range(3):
            a,_=c.search(s);self.assertTrue(all(len(x.rewards)==8 for x in c.samples));verify(c.audit(),64);s=t.step(s,a)
    def test_terminal_suffix_no_fictitious_tail(self):
        t,b,c,_=new();s=ToyState(stop=3);a,_=c.search(s);c.search(t.step(s,a));self.assertEqual(c.last_meta['tail_transitions'],0)
        self.assertTrue(all(len(x.actions)==2 for x in c.samples));verify(c.audit(),64)
    def test_mismatch_fresh_rng_not_reset(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);n=replace(t.step(s,a),x=999)
        b.rng.setstate(c.rng.getstate());aa,d=b.search(n);ca,cd=c.search(n)
        self.assertEqual(c.last_meta['reason'],'EXECUTED_STATE_MISMATCH');self.assertEqual(aa,ca);self.assertEqual(clean(d),clean(cd))
    def test_config_change_fallback(self):
        t,b,c,tag=new();s=ToyState();a,_=c.search(s);tag['v']='new';c.search(t.step(s,a));self.assertEqual(c.last_meta['reason'],'MODEL_ROUTE_CONFIG_CHANGED')
    def test_budget_change_fallback(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);c.budget=32;c.search(t.step(s,a));self.assertEqual(c.last_meta['inherited_samples'],0)
    def test_gamma_change_fallback(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);c.gamma=.9;c.search(t.step(s,a));self.assertEqual(c.last_meta['inherited_samples'],0)
    def test_children_zero_reconstructed(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);child=c.last_root.children[a]
        child.value_sum=9e8;c.search(t.step(s,a));verify(c.promotion_snapshot);verify(c.audit(),64)
    def test_duplicate_history_is_error(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);kept=[x for x in c.samples if x.nodes[1] is c.last_root.children[a]]
        c.samples.append(kept[0]);self.assertRaisesRegex(RuntimeError,'SUPPORT_COUNT',c.search,t.step(s,a))
    def test_terminal_root_not_searched(self):
        t,b,c,_=new();self.assertRaisesRegex(RuntimeError,'NO_SEARCH_AFTER',c.search,ToyState(stop=0))
    def test_hard_root_not_searched(self):
        t,b,c,_=new();self.assertRaisesRegex(RuntimeError,'NO_SEARCH_AFTER',c.search,ToyState(hard_safety_violation=True))
    def test_no_trace_means_error(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);c.samples=[];self.assertRaisesRegex(RuntimeError,'SUPPORT_COUNT',c.search,t.step(s,a))
    def test_audit_detects_q_corruption(self):
        t,b,c,_=new();c.search(ToyState());x=c.audit();x['nodes'][0]['q']+=1;self.assertRaisesRegex(RuntimeError,'Q_FROM',verify,x)
    def test_audit_detects_depth_corruption(self):
        t,b,c,_=new();c.search(ToyState());x=c.audit();x['nodes'][1]['depth']+=1;self.assertRaisesRegex(RuntimeError,'RELATIVE_DEPTH',verify,x)
    def test_audit_detects_duplicate(self):
        t,b,c,_=new();c.search(ToyState());x=c.audit();x['samples'][1]['uid']=x['samples'][0]['uid'];self.assertRaisesRegex(RuntimeError,'DUPLICATE',verify,x)
    def test_bad_gamma(self):self.assertRaisesRegex(RuntimeError,'BAD_GAMMA',HorizonRebasedSearch,Transition(),Reward(),actions,state_encode=asdict,binding=lambda:1,gamma=0)
    def test_discount_formula(self):self.assertAlmostEqual(discounted([1,2,3],.5),2.75)
    def test_three_promotions(self):
        t,b,c,_=new();s=ToyState();prev=None
        for i in range(4):
            a,_=c.search(s);verify(c.audit(),64)
            if prev:verify_rebase(prev,normalized(c.promotion_snapshot))
            prev=normalized(c.audit());s=t.step(s,a)
    def test_kept_states_no_mutation(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);old=[asdict(v) for x in c.samples for v in x.states];states=[v for x in c.samples for v in x.states]
        c.search(t.step(s,a));self.assertEqual([asdict(v) for v in states],old)
    def test_actual_search_iterations_count(self):
        t,b,c,_=new();s=ToyState();a,_=c.search(s);aa,d=c.search(t.step(s,a));self.assertEqual(d['iterations'],64-c.last_meta['inherited_samples'])


    def test_thirty_two_successive_decisions(self):
        t,b,c,_=new();s=ToyState(stop=100);prev=None
        for i in range(32):
            a,d=c.search(s)
            verify(c.audit(),64)
            self.assertEqual(d['iterations']+c.last_meta['inherited_samples'],64)
            if prev is not None:
                verify_rebase(prev,normalized(c.promotion_snapshot))
            prev=normalized(c.audit()); s=t.step(s,a)
    def test_continue_until_parked_no_extra_search(self):
        t,b,c,_=new();s=ToyState(stop=11);cnt=0
        while not s.all_goals_reached:
            a,_=c.search(s);verify(c.audit(),64);s=t.step(s,a);cnt+=1
        self.assertEqual(cnt,11)

if __name__=='__main__':unittest.main(verbosity=2)
