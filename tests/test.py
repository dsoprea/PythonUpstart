#!/usr/bin/env python2.7

import sys
sys.path.insert(0, '..')

from pprint import pprint
from sys import stdout

def test_system():
    from upstart.system import UpstartSystem

    s = UpstartSystem()

    print("Version: %s" % (s.get_version()))

    current_priority = s.get_log_priority()
    print("Current priority: %s" % (current_priority))

    new_priority = 'debug'
    s.set_log_priority(new_priority)

    updated_priority = s.get_log_priority()
    print("Updated priority: %s" % (updated_priority))

    s.set_log_priority(current_priority)

    restored_priority = s.get_log_priority()
    print("Restored priority: %s" % (restored_priority))

#    print(list(s.get_all_jobs()))
    s.emit('foo', { 'aa': 55 })

def test_jobs():
    from upstart.job import UpstartJob, JobBuilder

#    j = UpstartJob('smbd')
#    j = UpstartJob('dustin2')
#    pprint(j.get_status().keys())
#
#    c = j.get_start_on_condition()
#    c = j.get_stop_on_condition()
#    print(c)
#
#    j.stop()
#    j.start()

    jb = JobBuilder()
    jb.description('Test description').author('Dustin Oprea').run('my_daemon')

    job_raw = str(jb)

    print("================")
    stdout.write(job_raw)
    print("================")


test_system()
#test_jobs()

