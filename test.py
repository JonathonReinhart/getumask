#!/usr/bin/env python
import sys
import os
from subprocess import Popen, PIPE

class Sync(object):
    def __init__(self):
        self.rp, self.wp = os.pipe()

    def notify(self):
        os.write(self.wp, '1')

    def wait(self):
        os.read(self.rp, 1)

    def close(self):
        for fd in (self.rp, self.wp):
            os.close(fd)


def do_test(umask):
    print 'Testing with umask 0{0:03o}'.format(umask)

    umask_set = Sync()
    finished = Sync()

    pid = os.fork()
    if pid == 0:
        ### child
        # set umask
        os.umask(umask)

        # tell parent we've set umask
        #print 'child: notifying parent'
        umask_set.notify()

        #print 'child: waiting to die'
        finished.wait()

        #print 'child: finished'

        sys.exit(0)

    ### parent
    # Wait for child to set umask
    umask_set.wait()

    # Invoke 'getumask'
    getumask = Popen(['./getumask', str(pid)], stdout=PIPE, stderr=PIPE)
    out, err = getumask.communicate()

    # Tell child to die
    finished.notify()

    umask_set.close()
    finished.close()

    # Verify getumask returned success
    assert(getumask.returncode == 0)

    # Verify the determined umask is correct
    result = int(out.strip())
    assert(result == umask)


def test_nosuchproc():
    print 'Testing invalid process'

    # Get the system pid_max. This value is one higher than the
    # highest PID which will be allocated. We know that this
    # process will not be running
    pid = int(open('/proc/sys/kernel/pid_max', 'r').read())

    # Invoke 'getumask'
    getumask = Popen(['./getumask', str(pid)], stdout=PIPE, stderr=PIPE)
    out, err = getumask.communicate()

    # Verify getumask returned failure
    assert(getumask.returncode == 2)

    # Verify the output indicated why
    assert('no such process' in err.lower())

def test_noperm():
    print 'Testing not permitted process'

    # First, make sure we're not running as root
    assert(os.geteuid() != 0)

    # As long as we're not root, we won't be able to
    # attach to init
    pid = 1

    # Invoke 'getumask'
    getumask = Popen(['./getumask', str(pid)], stdout=PIPE, stderr=PIPE)
    out, err = getumask.communicate()

    # Verify getumask returned failure
    assert(getumask.returncode == 2)

    # Verify the output indicated why
    assert('operation not permitted' in err.lower())


if __name__ == '__main__':
    if os.geteuid() == 0:
        print 'Cannot be run as root.'
        sys.exit(1)

    do_test(0)
    do_test(0345)

    test_nosuchproc()

    test_noperm()

    print '\nSuccess!'
