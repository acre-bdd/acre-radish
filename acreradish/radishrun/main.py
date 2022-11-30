import re
import os
import sys
import subprocess
import argparse
import uuid
import logging as log

from acre.path import AcrePath


def main():
    """ invoke a test run """

    parser = argparse.ArgumentParser(description="radish-run <arguments>", usage=__doc__)
    parser.add_argument('--upgrade',
                        help="update dependencies according to the project's etc/requirements.txt",
                        action="store_true")
    parser.add_argument('--trid', help="use the given trid (uuid4) as testrun-id",
                        default=os.environ.get('ACRE_TRID', str(uuid.uuid4())))
    (myargs, options) = parser.parse_known_args()

    log.basicConfig(level=log.DEBUG)
    log.debug(f"arguments: {options}")

    userdata = _read_userdata()

    artifacts = os.path.join("artifacts", myargs.trid)
    os.makedirs(artifacts)

    if myargs.upgrade:
        cmd = "sudo pip3 install --upgrade -r etc/requirements.txt"
        ec = subprocess.run(cmd, shell=True).returncode
        if ec != 0:
            log.error("upgrading requirements failed")
            return 3

    result_xml = os.path.join(artifacts, f"{myargs.trid}.xml")
    os.environ['ARTIFACTS'] = artifacts
    os.environ['TRID'] = myargs.trid
    env = f"-u TRID={myargs.trid} -u ARTIFACTS={artifacts}"
    arguments = f"-t --bdd-xml {result_xml} {env} -b ./steps -b {AcrePath.steps()}"
    cmd = f'PYTHONPATH=src/ radish {arguments}  {userdata} {" ".join(options)}'
    log.info(f"running: {cmd} [{myargs.trid}]")
    os.environ['DISPLAY'] = ":99.0"
    return subprocess.run(cmd, shell=True).returncode


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
