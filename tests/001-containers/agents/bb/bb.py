#!/usr/bin/env python
    
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
import xmlrunner
try:
    import unittest2 as unittest
except ImportError:
    import unittest


# allow the test to be run by hand for development
if __name__ != '__main__':
    from magi.util.agent import DispatchAgent, agentmethod
    from magi.util.execl import run, pipeIn
    from magi.util.processAgent import initializeProcessAgent

    # the getAgent() method must be defined somewhere for all agents.
    # The Magi daemon invokes this mehod to get a reference to an
    # agent. It uses this reference to run and interact with an agent
    # instance.
    def getAgent(**kwargs):
        agent = bb()
        agent.setConfiguration(None, **kwargs)
        return agent
    
    
    class bb(DispatchAgent):
        def __init__(self):
            DispatchAgent.__init__(self)
            # usually replaced by an "arg" from the agent
            self.report_dir = "/tmp"
    
        @agentmethod()
        def test001containers(self, msg):
            log.info("About to start unit tests...")
            log.info(" ... writing test results to: " + self.report_dir)
            print("Testing stdout!")
            try:
                stream = StringIO.StringIO()
                suite = unittest.TestLoader().loadTestsFromTestCase(Test001Containers)
                xmlrunner.XMLTestRunner(stream=stream, output=self.report_dir).run(suite)
                stream.seek(0)
                log.info(stream.read())
            except Exception, err:
                log.exception(err)
            log.info("Done with the unit tests")


logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Test001Containers(unittest.TestCase):


    def test_reachability_aa(self):
        rc, msg, loss = ping("aa", count=200)
        # link should have 10% packet loss
        if rc != 0 or loss < 5 or loss > 25:
            self.fail(msg)
        pass


    def test_reachability_bb(self):
        rc, msg, loss = ping("bb")
        if rc != 0 or loss > 0:
            self.fail(msg)
        pass


    def test_reachability_cc(self):
        rc, msg, loss = ping("cc")
        if rc != 0 or loss > 0:
            self.fail(msg)
        pass


    def test_reachability_dd(self):
        rc, msg, loss = ping("dd")
        if rc != 0 or loss > 0:
            self.fail(msg)
        pass

    
    def test_reachability_outside(self):
        rc, msg, loss = ping("128.9.128.127")
        if re.search("Destination Host Unreachable", msg, re.MULTILINE) is None:
            self.fail(msg)
        pass
   
    
    def test_bw_aa_30MbExpected(self):
        rc, msg, bw_mb = bw("aa")
        # the link has packet loss, so a lower bw is expected
        if rc != 0 or bw_mb < 0.1 or bw_mb > 40:
            self.fail(msg)
        pass


    def test_bw_cc_100MbExpected(self):
        rc, msg, bw_mb = bw("cc")
        if rc != 0 or bw_mb < 80 or bw_mb > 110:
            self.fail(msg)
        pass


    def test_bw_dd_MbExpected(self):
        rc, msg, bw_mb = bw("dd")
        if rc != 0 or bw_mb < 80 or bw_mb > 110:
            self.fail(msg)
        pass


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


def ping(host, count=30):
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


def bw(host):
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


# allow the test to be run by hand for development
if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(Test001Containers)
    unittest.TextTestRunner(verbosity=2).run(suite)

