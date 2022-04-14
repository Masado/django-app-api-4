#!/usr/bin/env python3

import subprocess as sp

command = ['docker', 'version']
print("starting docker_in_py")
process = sp.run(command,
                 stdout=sp.PIPE,
                 stderr=sp.PIPE,
                 shell=False,
                 universal_newlines=True)

if process.returncode == 0:
    print("docker_in_py finished successfully!")
print(process.stdout)
print(process.stderr)

