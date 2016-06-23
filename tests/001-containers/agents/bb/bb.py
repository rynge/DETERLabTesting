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

import DeterLabTesting


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
                xmlrunner.XMLTestRunner(stream=stream, verbosity=2, output=self.report_dir).run(suite)
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
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, loss = dtl.ping("aa", count=200)
        # link should have 10% packet loss
        if rc != 0 or loss < 5 or loss > 25:
            self.fail(msg)
        pass


    def test_reachability_bb(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, loss = dtl.ping("bb")
        if rc != 0 or loss > 0:
            self.fail(msg)
        pass


    def test_reachability_cc(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, loss = dtl.ping("cc")
        if rc != 0 or loss > 0:
            self.fail(msg)
        pass


    def test_reachability_dd(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, loss = dtl.ping("dd")
        if rc != 0 or loss > 0:
            self.fail(msg)
        pass

    
    def test_reachability_outside(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, loss = dtl.ping("128.9.128.127")
        if re.search("Destination Host Unreachable|Network is unreachable", msg, re.MULTILINE) is None:
            self.fail(msg)
        pass
   
    
    def test_bw_aa_30MbExpected(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, bw_mb = dtl.bw("aa")
        # the link has packet loss, so a lower bw is expected
        if rc != 0 or bw_mb < 0.1 or bw_mb > 40:
            self.fail(msg)
        pass


    def test_bw_cc_100MbExpected(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, bw_mb = dtl.bw("cc")
        if rc != 0 or bw_mb < 80 or bw_mb > 110:
            self.fail(msg)
        pass


    def test_bw_dd_100MbExpected(self):
        dtl = DeterLabTesting.DeterLabTesting()
        rc, msg, bw_mb = dtl.bw("dd")
        if rc != 0 or bw_mb < 80 or bw_mb > 110:
            self.fail(msg)
        pass


# allow the test to be run by hand for development
if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(Test001Containers)
    unittest.TextTestRunner(verbosity=2).run(suite)


