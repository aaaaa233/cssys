#!/usr/bin/env python3
"""Run a command on the lab server, or upload/download files.

Usage:
  python _tools/rsh.py run  "<command>"        [--timeout N]
  python _tools/rsh.py put  <local> <remote>
  python _tools/rsh.py get  <remote> <local>
  python _tools/rsh.py putdir <localdir> <remotedir>

Credentials come from server.txt (host / user / password, one per line).
"""
import os
import posixpath
import stat
import sys

import paramiko

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def creds():
    with open(os.path.join(ROOT, "server.txt"), encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    return lines[0], lines[1], lines[2]


def connect():
    host, user, password = creds()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)
    return client


def do_run(command, timeout):
    client = connect()
    try:
        chan = client.get_transport().open_session()
        chan.settimeout(timeout)
        chan.exec_command(command)
        chan.shutdown_write()
        out = chan.makefile("rb", -1)
        err = chan.makefile_stderr("rb", -1)
        sys.stdout.write(out.read().decode("utf-8", "replace"))
        sys.stderr.write(err.read().decode("utf-8", "replace"))
        return chan.recv_exit_status()
    finally:
        client.close()


def _mkdirs(sftp, remote_dir):
    parts, cur = [p for p in remote_dir.split("/") if p], ""
    if remote_dir.startswith("/"):
        cur = ""
    for part in parts:
        cur = cur + "/" + part if remote_dir.startswith("/") else posixpath.join(cur, part)
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)


def do_put(local, remote):
    client = connect()
    try:
        sftp = client.open_sftp()
        _mkdirs(sftp, posixpath.dirname(remote))
        sftp.put(local, remote)
        sftp.close()
    finally:
        client.close()
    return 0


def do_putdir(localdir, remotedir):
    client = connect()
    count = 0
    try:
        sftp = client.open_sftp()
        for dirpath, _dirnames, filenames in os.walk(localdir):
            rel = os.path.relpath(dirpath, localdir).replace("\\", "/")
            rdir = remotedir if rel == "." else posixpath.join(remotedir, rel)
            _mkdirs(sftp, rdir)
            for name in filenames:
                sftp.put(os.path.join(dirpath, name), posixpath.join(rdir, name))
                count += 1
        sftp.close()
    finally:
        client.close()
    print(f"uploaded {count} files -> {remotedir}")
    return 0


def do_get(remote, local):
    client = connect()
    try:
        sftp = client.open_sftp()
        os.makedirs(os.path.dirname(os.path.abspath(local)), exist_ok=True)
        sftp.get(remote, local)
        sftp.close()
    finally:
        client.close()
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    mode = sys.argv[1]
    if mode == "run":
        timeout = 300
        args = sys.argv[2:]
        if "--timeout" in args:
            i = args.index("--timeout")
            timeout = float(args[i + 1])
            args = args[:i] + args[i + 2:]
        return do_run(args[0], timeout)
    if mode == "put":
        return do_put(sys.argv[2], sys.argv[3])
    if mode == "putdir":
        return do_putdir(sys.argv[2], sys.argv[3])
    if mode == "get":
        return do_get(sys.argv[2], sys.argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
