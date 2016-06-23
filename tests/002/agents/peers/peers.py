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

import DeterLabTesting

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
        cmd = DeterLabTesting.MyCommand("iperf -s -D")
        cmd.run()

    @agentmethod()
    def stop_iperf(self, msg):
        log.info("Stopping iperf")
        cmd = DeterLabTesting.MyCommand("killall iperf")
        cmd.run()


