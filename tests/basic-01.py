def check_delivered_messages(results):
    """Check number of delivered messages."""
    assert results["metrics"]["Delivered messages"] == 10


def check_states(results):
    """Check final device states."""
    assert results["states"]["device0"] == {"counter": 10}
    assert results["states"]["device1"] == {"counter": 10}


def check_exit_code(results):
    """Check exit code is zero."""
    assert results["metrics"]["Exit code"] == 0