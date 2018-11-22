from fabric.api import run
from fabric.api import cd
from fabric.api import env
from fabric.contrib.files import exists
from fabric.context_managers import prefix


env.use_ssh_config = True
PSTACK_DIR         = "~/psim"

def install():
    """Pull latest master commit.

    Clones the repository if it doesn't exist.
    """

    if not exists(PSTACK_DIR):
        with cd("~"):
            run("git clone git@github.com:poetsii/pstack")
        return

    run("killall -q python || true")  # terminate any existing daemons

    with cd(PSTACK_DIR):
        run("git fetch --all >/dev/null")
        run("git reset --hard origin/master >/dev/null")


def setup():
    """Setup virtualenv and install dependencies."""

    if not exists(PSTACK_DIR):
        raise Exception("pstack is not installed")

    run("killall -q python || true")  # terminate any existing daemons

    with cd(PSTACK_DIR):
        run("virtualenv env")
        run("source env/bin/activate && pip install -q -r requirements.txt")


def daemon(host):
    """Run POETS daemon."""

    daemon_command = "python pd.py --name '%s' --host '%s'" % (env.host, host)
    nohup_wrapper = "(nohup %s &> /dev/null &) && true"

    with cd(PSTACK_DIR), prefix("source env/bin/activate"):
        run("killall -q python || true")  # terminate any existing daemons
        run(nohup_wrapper % daemon_command, pty=False)


def stop():
    """Terminate POETS daemon."""
    run("killall -q python || true")
