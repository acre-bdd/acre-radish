import re
import os
import sys
import argparse
import logging as log

from acre.path import AcrePath


def main():
    """ invoke a test run """

    parser = argparse.ArgumentParser(description="radish-run <arguments>", usage=__doc__)
    parser.add_argument('--upgrade',
                        help="update dependencies according to the project's etc/requirements.txt",
                        action="store_true")
    (myargs, options) = parser.parse_known_args()

    log.basicConfig(level=log.DEBUG)
    log.debug(f"arguments: {options}")

    userdata = _read_userdata()

    if myargs.upgrade:
        cmd = "pip3 install --upgrade -r etc/requirements.txt"
        os.system(cmd)

    cmd = f'PYTHONPATH=src/ radish -t -b ./steps -b {AcrePath.steps()} {userdata} {" ".join(options)}'
    log.info(f"running: {cmd}")
    os.environ['DISPLAY'] = ":99.0"
    return os.system(cmd)


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
