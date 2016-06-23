#!/usr/bin/python

import logging
import os
import re
import subprocess
import sys
import tempfile
import time

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class DeterLabTesting():

    def __init__(self):
        pass


    def ping(self, host, count=30):
        cmd = MyCommand("ping -i 0.2 -c " + str(count) + " " + host)
        cmd.run()
        if cmd.get_exit_code() != 0:
            return cmd.get_exit_code(), cmd.get_outerr(), 0
    
        # make sure output looks ok
        r = re.search(str(count) + " packets transmitted", cmd.get_outerr(), re.MULTILINE)
        if not r:
            return 1, cmd.get_outerr(), 0
    
        # determine the package loss
        r = re.search(" ([0-9]+)% packet loss", cmd.get_outerr(), re.MULTILINE)
        loss = int(r.group(1))
        return cmd.get_exit_code(), cmd.get_outerr(), loss
    
    
    def bw(self, host):
        cmd = MyCommand("iperf -i 120 -t 60 -f m -c " + host)
        cmd.run()
        if cmd.get_exit_code() != 0:
            return cmd.get_exit_code(), cmd.get_outerr(), 0
    
        # extract the bw from the stdout
        r = re.search(" ([0-9\.]+) Mbits/sec", cmd.get_outerr(), re.MULTILINE)
        if r:
            bw = float(r.group(1))
            return cmd.get_exit_code(), cmd.get_outerr(), bw
        r = re.search(" ([0-9\.]+) Gbits/sec", cmd.get_outerr(), re.MULTILINE)
        if r:
            bw = float(r.group(1)) * 1024
            return cmd.get_exit_code(), cmd.get_outerr(), bw
    
        return 1, cmd.get_outerr(), 0


class MyCommand(object):
    """ Provides a shell callout """

    def __init__(self, cmd, log_cmd = True, log_outerr = True):
        self._cmd = cmd
        self._log_cmd = log_cmd
        self._log_outerr = log_outerr
        self._process = None
        self._out_file = None
        self._outerr = ""

        # used in exceptions
        self._cmd_for_exc = cmd

    def run(self):

        if self._log_cmd or log.isEnabledFor(logging.DEBUG):
            log.info(self._cmd)

        sys.stdout.flush()

        # temp file for the stdout/stderr
        self._out_file = tempfile.TemporaryFile(prefix="cmd-", suffix=".out")

        self._process = subprocess.Popen(self._cmd, shell=True, 
                                         stdout=self._out_file, 
                                         stderr=subprocess.STDOUT,
                                         preexec_fn=os.setpgrp)
        self._process.communicate()

        # log the output
        self._out_file.seek(0)
        self._outerr = str.strip(self._out_file.read())
        if self._log_outerr and len(self._outerr) > 0:
            log.info(self._outerr)
        self._out_file.close()


    def get_outerr(self):
        """
        returns the combined stdout and stderr from the command
        """
        return self._outerr


    def get_exit_code(self):
        """
        returns the exit code from the process
        """
        return self._process.returncode


