"""Pure NumPy dual-vehicle return-gap models; no simulator, files, or network I/O.
New method, not a byte-identical replay of the old unregularized models.
"""
from __future__ import annotations
import math
import time

MODELS = ['ridge26', 'mlp26_8_1_l2']
LAMBDAS = [0.01, 0.1, 1.0]
SCALE = 100.0
SEED = 78004
UPDATES = 2000
LR = 0.001


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def arrays(np, X, y):
    need(X.ndim == 2 and X.shape == (len(y), 26) and y.ndim == 1 and len(y) > 0,
         'MODEL_ARRAY_SHAPE')
    need(X.dtype == np.float64 and y.dtype == np.float64 and
         np.isfinite(X).all() and np.isfinite(y).all(), 'MODEL_ARRAY_FINITE_FLOAT64')


def init(np, model, seed=SEED):
    need(type(seed) is int and seed >= 0, 'SEED_TYPE')
    if model == MODELS[0]:
        return {'W0': np.zeros((26, 1)), 'b0': np.zeros(1)}
    need(model == MODELS[1], 'MODEL_ID')
    rng = np.random.RandomState(seed)
    return {'W0': rng.normal(0., math.sqrt(2. / 26), (26, 8)),
            'b0': np.zeros(8), 'W1': rng.normal(0., math.sqrt(1. / 8), (8, 1)),
            'b1': np.zeros(1)}


def forward(np, p, X):
    H = X
    for i in range(len(p) // 2):
        H = H @ p['W' + str(i)] + p['b' + str(i)]
        if i < len(p) // 2 - 1:
            H = np.maximum(H, 0.)
    return H[:, 0]


def objective_gradient(np, p, X, y, lam):
    need(math.isfinite(lam) and lam >= 0., 'LAMBDA_NONNEGATIVE')
    acts = [X]; pre = []
    for i in range(len(p) // 2):
        z = acts[-1] @ p['W' + str(i)] + p['b' + str(i)]
        pre.append(z)
        acts.append(np.maximum(z, 0.) if i < len(p) // 2 - 1 else z)
    residual = acts[-1][:, 0] - y
    data_loss = float(0.5 * np.mean(residual ** 2))
    penalty = float(0.5 * lam * math.fsum(float(np.sum(v * v)) for k, v in p.items() if k.startswith('W')))
    delta = residual[:, None] / len(y); grad = {}
    for i in reversed(range(len(p) // 2)):
        w, b = 'W' + str(i), 'b' + str(i)
        grad[w] = acts[i].T @ delta + lam * p[w]
        grad[b] = delta.sum(axis=0)
        if i:
            delta = (delta @ p[w].T) * (pre[i-1] > 0.)
    details = {'data_loss': data_loss, 'l2_penalty': penalty,
               'objective': data_loss + penalty,
               'train_mae_reward_units': float(np.mean(np.abs(residual)) * SCALE),
               'gradient_l2_norm': math.sqrt(math.fsum(float(np.sum(g*g)) for g in grad.values()))}
    return details, grad


class InterruptedFit(RuntimeError):
    def __init__(self, message, params, completed_updates, history, solve_completed=False):
        super().__init__(message)
        self.params = params
        self.completed_updates = completed_updates
        self.history = history
        self.solve_completed = solve_completed


def fit(np, model, p, X, y, lam, updates=UPDATES, lr=LR, progress=None, deadline=None):
    arrays(np, X, y)
    need(model in MODELS and math.isfinite(lam) and lam > 0., 'FIXED_MODEL_LAMBDA')
    need(type(updates) is int and updates > 0 and math.isfinite(lr) and lr > 0., 'OPTIMIZER_SETTINGS')
    history = []; done = 0; solved = False
    initial = objective_gradient(np, p, X, y, lam)[0]
    try:
        if deadline is not None and time.monotonic() > deadline:
            raise RuntimeError('METHOD_TIME_LIMIT')
        if model == MODELS[0]:
            # Exact ridge objective: ||Xw+b-y||^2/(2n) + lambda*||w||^2/2.
            # Means depend ONLY on the training rows supplied to this function.
            xm = X.mean(axis=0); ym = float(y.mean())
            Xc, yc = X - xm, y - ym
            w = np.linalg.solve(Xc.T @ Xc + len(y) * lam * np.eye(X.shape[1]), Xc.T @ yc)
            p = {'W0': w[:, None], 'b0': np.asarray([ym - xm @ w])}
            solved = True
            details = objective_gradient(np, p, X, y, lam)[0]
            need(details['gradient_l2_norm'] < 1e-9 * max(1., float(np.linalg.norm(y))),
                 'RIDGE_STATIONARITY_RESIDUAL')
            history.append(dict(details, update=0, closed_form_solve_completed=True))
            if progress is not None:
                progress(history[-1])
        else:
            m = {k: np.zeros_like(v) for k, v in p.items()}
            v = {k: np.zeros_like(a) for k, a in p.items()}
            for t in range(1, updates+1):
                if deadline is not None and time.monotonic() > deadline:
                    raise RuntimeError('METHOD_TIME_LIMIT')
                details, g = objective_gradient(np, p, X, y, lam)
                need(all(math.isfinite(a) for a in details.values()) and
                     all(np.isfinite(a).all() for a in g.values()), 'NONFINITE_TRAIN_GRADIENT')
                for k in sorted(p):
                    m[k] *= .9; m[k] += .1 * g[k]
                    v[k] *= .999; v[k] += .001 * g[k] * g[k]
                    p[k] -= lr * (m[k] / (1.-.9**t)) / (np.sqrt(v[k] / (1.-.999**t)) + 1e-8)
                done = t
                need(all(np.isfinite(a).all() for a in p.values()), 'NONFINITE_PARAMETERS')
                if t == 1 or t % 100 == 0 or t == updates:
                    details = objective_gradient(np, p, X, y, lam)[0]
                    history.append(dict(details, update=t))
                    if progress is not None:
                        progress(history[-1])
    except (Exception, KeyboardInterrupt) as e:
        raise InterruptedFit(type(e).__name__ + ':' + str(e), p, done, history, solved) from e
    return p, {'initial': initial, 'final': history[-1], 'completed_updates': done,
               'closed_form_solve_completed': solved, 'history': history,
               'final_iteration_only': True, 'early_stopping': False}


def dump_model(p, model, lam, complete, completed_updates, solve_completed):
    return {'model': model, 'lambda': lam,
            'parameters': {k: v.tolist() for k, v in p.items()},
            'architecture': [26, 1] if model == MODELS[0] else [26, 8, 1],
            'target_scale': SCALE, 'seed': SEED if model == MODELS[1] else None,
            'output_semantics': 'empirical mean Y64(forced03)-Y64(forced30), divided by100',
            'complete_fit': complete, 'completed_updates': completed_updates,
            'closed_form_solve_completed': solve_completed,
            'regularizer': 'lambda/2 * sum(weight_matrix_squared); biases unpenalized',
            'feature_processing': 'original physical-normalized float32 features promoted to float64; no new normalization',
            'deployable': False, 'pruning_authorized': False, 'full16_action_values': False}


def select_lambda(scores, candidates=LAMBDAS, expected_folds=7):
    """Scores contain ONLY validation groups within the outer training set."""
    records = []
    for lam in candidates:
        rows = [r for r in scores if r['lambda'] == lam]
        need(len(rows) == expected_folds and len({r['inner_group'] for r in rows}) == expected_folds,
             'INNER_SELECTION_INCOMPLETE')
        need(all(math.isfinite(r['mae_reward_units']) for r in rows), 'INNER_METRIC_NONFINITE')
        records.append({'lambda': lam, 'group_macro_mae_reward_units':
                        math.fsum(r['mae_reward_units'] for r in rows)/expected_folds})
    # No tolerance-based tie tweaking; exact equal scores prefer stronger regularization.
    chosen = min(records, key=lambda r: (r['group_macro_mae_reward_units'], -r['lambda']))
    return {'selected_lambda': chosen['lambda'], 'candidate_scores': records,
            'criterion': 'minimum inner source-group macro MAE; exact ties choose largest lambda',
            'outer_held_out_used': False}
