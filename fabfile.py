from fabric.api import run
from fabric.api import cd
from fabric.api import env
from fabric.contrib.files import exists
from fabric.context_managers import prefix


env.use_ssh_config = True


def install():
    """Pull latest master commit.

    Clones the repository if it doesn't exist.
    """

    if not exists("~/psim"):
        with cd("~"):
            run("git clone git@github.com:poetsii/psim")
        return

    run("killall -q python || true")  # terminate any existing daemons

    with cd("~/psim"):
        run("git fetch --all")
        run("git reset --hard origin/master")


def setup():
    """Setup virtualenv and install dependencies."""

    if not exists("~/psim"):
        raise Exception("psim is not installed")

    run("killall -q python || true")  # terminate any existing daemons

    with cd("~/psim"):
        run("virtualenv env")
        run("source env/bin/activate && pip install -q -r requirements.txt")


def daemon(host):
    """Run POETS daemon."""

    daemon_command = "python pd.py --redis '%s' --name $(hostname) --workers $(nproc)" % host
    nohup_wrapper = "(nohup %s &> /dev/null &) && true"

    with cd("~/psim"), prefix("source env/bin/activate"):
        run("killall -q python || true")  # terminate any existing daemons
        run(nohup_wrapper % daemon_command, pty=False)
