import re
import os
import sys
import subprocess
import argparse
import uuid
import pylogx

from . import log

from .settings import Settings

pylogx.enable_colors()


def main():
    """ invoke a test run """

    parser = argparse.ArgumentParser(description="radish-run <arguments>", usage=__doc__)
    parser.add_argument('--upgrade',
                        help="update dependencies according to the project's etc/requirements.txt",
                        action="store_true")
    parser.add_argument('--debug', help="enable debug logging", action="store_true")
    parser.add_argument('--trid', help="use the given trid (uuid4) as testrun-id",
                        default=os.environ.get('TRID', str(uuid.uuid4())))
    parser.add_argument('-S', '--setting', help="read setting file to environment",
                        nargs="+", default=[])
    (myargs, options) = parser.parse_known_args()

    if myargs.debug:
        pylogx.log.setLevel(pylogx.Level.DEBUG)
    log.debug(f"arguments: {options}")
    log.debug(f"options: {options}")

    userdata = _read_userdata()
    Settings.read(myargs.setting)

    artifacts = os.path.join("artifacts", myargs.trid)
    os.makedirs(artifacts)

    if myargs.upgrade:
        log.info("upgrading project requirements")
        cmd = "sudo pip3 install --upgrade -r etc/requirements.txt"
        ec = subprocess.run(cmd, shell=True).returncode
        if ec != 0:
            log.error("upgrading requirements failed")
            return 3

    result_xml = os.path.join(artifacts, f"{myargs.trid}.xml")

    os.environ['ARTIFACTS'] = artifacts
    os.environ['TRID'] = myargs.trid
    os.environ['DISPLAY'] = ":99.0"
    pp = []
    if 'PYTHONPATH' in os.environ:
        pp.extend(os.environ['PYTHONPATH'].split(":"))
    pp.append("src/")

    env = ""
    arguments = f"-t --bdd-xml {result_xml} {env} -b ./steps"
    cmd = f'PYTHONPATH={":".join(pp)} radish {arguments}  {userdata} {" ".join(options)}'
    log.trace(f"{cmd} [{myargs.trid}]")
    # monitor = open("monitor.log", "w")
    # radish = subprocess.Popen(cmd, shell=True, stdout=monitor, stderr=monitor)
    radish = subprocess.Popen(cmd, shell=True)
    # mon = subprocess.Popen("tail -f /tmp/monitor2.log", shell=True)
    radish.wait()
    # mon.terminate()
    # mon.wait()


def _read_userdata():
    if not os.path.exists("etc/user.data"):
        return ""

    userdata = []
    for line in open("etc/user.data", "r").readlines():
        if not re.match(r"\w+=.*", line):
            log.bailout(f'invalid user data: {line}', 3)
        userdata.append(f'-u "{line.strip()}"')
    return " ".join(userdata)


if __name__ == "__main__":
    ec = main()
    sys.exit(ec)
