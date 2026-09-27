import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'release'))
import experiment as e
def summary(complete=True,steps=10,cpu=100,wall=110,clear=3,hard=False):
    return dict(both_parked=complete,hard_safety_terminal=hard,executed_steps=steps,
                search_cpu_total_ms=cpu,search_wall_total_ms=wall,minimum_sampled_clearance_m=clear)
class PolicyMetrics(unittest.TestCase):
    def test_strict_joint(self):
        c=e.compare_pair(summary(),summary(steps=9,cpu=90,wall=100))
        self.assertTrue(c['strict_joint_improvement_observed_on_this_pair'])
    def test_cap_not_speed_gain(self):
        c=e.compare_pair(summary(),summary(complete=False,cpu=1,wall=1))
        self.assertFalse(c['strict_joint_improvement_observed_on_this_pair'])
        self.assertIsNone(c['candidate_total_search_cpu_lower'])
    def test_hard_failure_not_gain(self):
        self.assertFalse(e.compare_pair(summary(),summary(hard=True,cpu=1,wall=1))['strict_joint_improvement_observed_on_this_pair'])
    def test_longer_trip_not_joint_gain(self):
        self.assertFalse(e.compare_pair(summary(),summary(steps=11,cpu=90,wall=90))['strict_joint_improvement_observed_on_this_pair'])
    def test_clearance_regression_visible(self):
        self.assertFalse(e.compare_pair(summary(),summary(clear=2,cpu=90,wall=90))['strict_joint_improvement_observed_on_this_pair'])
    def test_cpu_only_is_not_wall_gain(self):
        self.assertFalse(e.compare_pair(summary(),summary(cpu=90,wall=120))['strict_joint_improvement_observed_on_this_pair'])
    def test_percentile(self):
        self.assertAlmostEqual(e.percentile([1,2,3,4],.95),3.85)
    def test_bad_time(self):
        self.assertRaises(RuntimeError,e.percentile,[float('nan')],.95)
    def test_no_samples(self):
        self.assertRaises(RuntimeError,e.percentile,[],.95)
    def test_native_parity_rejects_different_action(self):
        a={k:{} for k in ('before','after','detail','rng_before','rng_after')}
        a.update(action_id='0,0',reward=1,diagnostics={'iterations':64,'elapsed_ms':1})
        b=dict(a,action_id='1,1')
        self.assertRaises(RuntimeError,e.cold_parity,a,b)
    def test_native_parity_ignores_only_timing_and_reuse(self):
        a={k:{} for k in ('before','after','detail','rng_before','rng_after')}
        a.update(action_id='0,0',reward=1,diagnostics={'iterations':64,'elapsed_ms':1})
        b=dict(a,diagnostics={'iterations':64,'elapsed_ms':99,'reuse_accounting':{}})
        e.cold_parity(a,b)
if __name__=='__main__':unittest.main(verbosity=2)
