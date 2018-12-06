#!/usr/bin/env python
#
# This little helper exists to decrypt KMS keys on-the-fly when running
# Terraform.  This will prevent the plaintext of a KMS key from being put into
# the state file, which is a longstanding problem infamous in Terraform. 
#
# Only a user which has access to KMS on the environment will be able to
# decode these keys.
#
# With my deepest sympathies for how bad Terraform is at times...
#    Love,
#         Farley Farley <farley@neonsurge.com>
#######################

# Imports
from __future__ import print_function
import sys
import json
import shlex
from subprocess import Popen, PIPE

# Get our input from stdin
def get_stdin_input():
  output = ""
  for line in sys.stdin:
      output = output + line.strip() + "\n"
  output = output.strip()
  return output

# Shell execute helper
def get_exitcode_stdout_stderr(cmd, shell=False):
    """
    Execute the external command and get its exitcode, stdout and stderr.  The
    shell option is necessary to perform piping and other advanced features
    """
    if not shell:
      args = shlex.split(cmd)
      proc = Popen(args, stdout=PIPE, stderr=PIPE)
    else:
      proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    exitcode = proc.returncode
    return exitcode, out, err

# Helper to print to stderr which is what TF needs on failure to show anything
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Get our STDIN from Terraform
input = get_stdin_input()
parsed = json.loads(input)

# This is the GCloud CLI command to decrypt some input ciphertext
command = "echo -n \"{}\"".format(parsed['ciphertext'])
command = command + " | base64 --decode"
command = command + " | gcloud kms decrypt"
command = command + " --project {}".format(parsed['project'])
command = command + " --location {}".format(parsed['region'])
command = command + " --keyring {}".format(parsed['keyring'])
command = command + " --key {}".format(parsed['keyring'])
command = command + " --plaintext-file -"
command = command + " --ciphertext-file -"

# Run our command and capture the stdout/err/exitcode
exitcode, out, err = get_exitcode_stdout_stderr(command, True)

# If we succeeded running, return as a json blob (that is what Terraform needs)
if exitcode == 0:
  output = {'output': out}
  print(json.dumps(output))
  exit(0)

# If we failed, print the error and bail
eprint('Error: {}'.format(command))
eprint(err)
eprint(out)
exit(1)
