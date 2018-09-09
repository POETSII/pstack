def check_log(results):
    """Check number of log messages."""
    return len(results["log"]) == 20


def check_delivered_messages(results):
    """Check number of delivered messages."""
    return results["metrics"]["Delivered messages"] == 10


def check_log_order(results):
    """Check order of log messages."""
    device_names = [log_entry[0] for log_entry in results["log"]]
    return device_names == ["device0", "device1"] * 10


def check_states(results):
    """Check final device states."""

    if results["states"]["device0"] != {"counter": 10}:
        return False

    if results["states"]["device1"] != {"counter": 10}:
        return False

    return True


def check_exit_code(results):
    """Check exit code is zero."""

    return results["metrics"]["Exit code"] == 0