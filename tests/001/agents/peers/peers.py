#!/usr/bin/env python
    
from magi.util.agent import DispatchAgent, agentmethod
from magi.util.execl import run, pipeIn
from magi.util.processAgent import initializeProcessAgent

import errno
import logging
import os
import glob
import stat
import time
import re
import StringIO
import sys
import subprocess
import tempfile
import threading


logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# the getAgent() method must be defined somewhere for all agents.
# The Magi daemon invokes this mehod to get a reference to an
# agent. It uses this reference to run and interact with an agent
# instance.
def getAgent(**kwargs):
    agent = peers()
    agent.setConfiguration(None, **kwargs)
    return agent


class peers(DispatchAgent):
    def __init__(self):
        DispatchAgent.__init__(self)

    @agentmethod()
    def start_iperf(self, msg):
        log.info("Starting iperf")
        cmd = MyCommand("iperf -s -D")
        cmd.run()

    @agentmethod()
    def stop_iperf(self, msg):
        log.info("Stopping iperf")
        cmd = MyCommand("killall iperf")
        cmd.run()


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


