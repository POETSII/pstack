def check_delivered_messages(results):
    """Check number of delivered messages."""
    assert results["metrics"]["Delivered messages"] == 40


def check_states(results):
    """Check final device states."""
    for state in results["states"].values():
        assert state == {"state": 0, "counter": 10 ,"toggle_buffer_ptr": 0}


def check_exit_code(results):
    """Check exit code is zero."""
    assert results["metrics"]["Exit code"] == 0
