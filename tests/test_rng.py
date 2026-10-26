import numpy as np
import pytest
from core.rng import make_draws

@pytest.mark.parametrize("seed",[0,1,42,999])
def test_same_seed_same_fingerprint(seed):
    assert make_draws(seed,8,12).fingerprint()==make_draws(seed,8,12).fingerprint()

def test_different_seed_changes_draws():
    assert make_draws(42,8,12).fingerprint()!=make_draws(43,8,12).fingerprint()

def test_head_is_prefix():
    d=make_draws(42,20,12); h=d.head(7)
    assert h.n_sims==7
    assert np.array_equal(h.market_z,d.market_z[:7])
    assert np.array_equal(h.unplanned_u,d.unplanned_u[:7])

def test_head_clamps_to_sim_count(): assert make_draws(1,4,4).head(100).n_sims==4

@pytest.mark.parametrize("n,m",[(0,1),(1,0),(-1,2)])
def test_invalid_draw_dimensions(n,m):
    with pytest.raises(ValueError): make_draws(1,n,m)
