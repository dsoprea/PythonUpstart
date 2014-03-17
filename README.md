##Introduction

This is a Python-based management interface for Upstart (Canonical's service 
layer). This library provides two main areas of functionality:

1. Management commands (using D-Bus) to query jobs, start/stop jobs, emit 
   events, etc...
2. Writing and updating job files.

##Dependencies

- *python-dbus* (under Apt), or equivalent.

##Installation

```
sudo pip install upstart
```

##Tools

The upstart module also comes packaged with two command-line utilities to help 
create new jobs. This is a value-added convenience for the end-user, as such
utilities don't come packages with Upstart, itself.

###upstart-create

Create boilerplate jobs using standard choices.

```
$ upstart-create test-job /bin/sh -j -d "some description" -a "some author <some@author>"
description "some description"
author "some author <some@author>"
exec /bin/sh
start on runlevel [2345]
stop on runlevel [016]
respawn 
```

We specified the "-j" option to just print to the screen rather than write a 
job file.

###upstart-reload

Force Upstart to reload jobs. Generally, Upstart uses inotify to sense changes, 
but sometimes it may need help.

```
$ upstart-reload
```

##Upstart Management API

The management commands usually return D-Bus types. However, they can generally 
be treated like the corresponding standard Python types.

###System-Level Functions

Do the import and create the *system* object:

```python
from upstart.system import UpstartSystem

s = UpstartSystem()
```

Get version:

```
>>> s.get_version()
init (upstart 1.10)
```

Get log priority:

```
>>> s.get_log_priority()
message
```

Set log priority:

```
>>> s.set_log_priority('debug')
```

Get a list of all defined (and parsable) jobs (list has been truncated):

```
>>> list(s.get_all_jobs())
['avahi_2ddaemon', 'cgroup_2dlite', 'mountnfs_2dbootclean_2esh', ...]
```

Emit event (only the event-name is required):

```
>>> s.emit('event_name', {'env_test_key': 'env_val'})
```

###Job-Level Functions

Do the import and create the *job* object:

```python
from upstart.job import UpstartJob

j = UpstartJob('smbd')
```

Get job status (displayed with formatting):

```
>>> j.get_status()
dbus.Dictionary({
            dbus.String(u'processes'): 
                dbus.Array(
                    [dbus.Struct(
                        (dbus.String(u'main'), dbus.Int32(24825)), 
                        signature=None)], 
                    signature=dbus.Signature('(si)'), 
                    variant_level=1), 

            dbus.String(u'state'): 
                dbus.String(u'running', variant_level=1), 
            
            dbus.String(u'name'): 
                dbus.String(u'', variant_level=1), 
            
            dbus.String(u'goal'): 
                dbus.String(u'start', variant_level=1)
        }, 
        signature=dbus.Signature('sv')
    )
```

Get the *start-on* conditions (displayed with formatting):

```
>>> j.get_start_on_condition()
dbus.Array([
        dbus.Array([dbus.String(u'local-filesystems')], signature=dbus.Signature('s')), 
        dbus.Array([dbus.String(u'net-device-up')], signature=dbus.Signature('s')), 
        dbus.Array([dbus.String(u'/AND')], signature=dbus.Signature('s'))], 
    signature=dbus.Signature('as'), 
    variant_level=1)
```

Get the *stop-on* conditions (displayed with formatting):

```
>>> j.get_stop_on_condition()
dbus.Array([
        dbus.Array([dbus.String(u'runlevel'), 
                    dbus.String(u'[!2345]')], 
                   signature=dbus.Signature('s'))], 
    signature=dbus.Signature('as'), 
    variant_level=1)
```

Send the *start* event to the job:

```
>>> j.start()
```

Send the *stop* event to the job:

```
>>> j.stop()
```

##Job-Building API

###Examples

####Example 1

```python
from upstart.job_builder import JobBuilder

jb = JobBuilder()

# Build the job to start/stop with default runlevels to call a command.
jb.description('Job description').\
   author('Iam Admin <admin@corp.com>').\
   start_on_runlevel().\
   stop_on_runlevel().\
   run('/usr/bin/my_daemon')

with open('/etc/init/my_daemon.conf', 'w') as f:
    f.write(str(jb))
```

Job config:

```
description "Job description"
author "Iam Admin <admin@corp.com>"
start on runlevel [2345]
stop on runlevel [016]
exec /usr/bin/my_daemon
```

####Example 2

```python
from upstart.job_builder import JobBuilder, JobPythonScript

s = JobPythonScript("""
import time
while 1:
    time.sleep(1)
""")

jb = JobBuilder()

# Build the job to start/stop with default runlevels to call a script 
# fragment.
jb.description('Test description').\
   author('Iam Admin <admin@corp.com>').\
   start_on_runlevel().\
   stop_on_runlevel().\
   run(s)

with open('/etc/init/my_daemon_2.conf', 'w') as f:
    f.write(str(jb))
```

Job config:

```
description "Test description"
author "Iam Admin <admin@corp.com>"
start on runlevel [2345]
stop on runlevel [016]
script 
python - <<END
import time
while 1:
    time.sleep(1)
END
end script
```

### Methods

#### run(command)

- Stanza: 'exec', 'script'
- The command to run. Can be a string or a script object.

#### pre_start(command)

- Stanza: 'pre-start'
- A pre-start command to run. Can be a string or a script object.

#### post_start(command)

- Stanza: 'post-start'
- A post-start command to run. Can be a string or a script object.

#### pre_stop(command)

- Stanza: 'pre-stop'
- A pre-stop command to run. Can be a string or a script object.

#### post_stop(command)

- Stanza: 'post-stop'
- A post-stop command to run. Can be a string or a script object.

#### start_on(events, conjunct=None)

- Stanza: 'start_on'
- One or more start conditions, best expressed via example:
  - start_on('abc')
  - start_on(('abc', {'aa': 1, 'bb': 2}))
  - start_on(['abc', 'def'], conjunct='and')
  - start_on([('abc', {'aa': 1, 'bb': 2}), 
              ('def', {'cc': 3, 'dd': 4})], 
             conjunct='and')
  - start_on('abc aa=1 bb=2 and def cc=3 dd=4')

  Depending on the complexity of your conditions, you may prefer passing a
  string, directly (as in the last example).

#### start_on_runlevel(runlevels=[2,3,4,5])

- Stanza: 'start on runlevel'
- One or more runlevels to start on. Can be a list of integers, or a string.

#### start_on_before_started(service)

- Stanza: 'start on starting'
- Start the job whenever another job is started (before it starts).

#### start_on_after_started(service)

- Stanza: 'start on started'
- Start the job whenever another job has started (after it starts).

#### stop_on(events, conjunct=None)

- Stanza: 'stop on'
- One or more stop conditions, using the same syntax as [start on](#start_onevents-conjunctnone).

#### stop_on_runlevel(runlevels='!2345')

- Stanza: 'stop on runlevel'
- One or more runlevels to stop on. Can be a list of integers, or a string.

#### stop_on_before_stopped(service)

- Stanza: 'stop on stopping'
- Stop the job whenever another job has stopped (before it stops).

#### stop_on_after_stopped(service)

- Stanza: 'stop on stopped'
- Stop the job whenever another job has stopped (after it stops).

#### description(description)

- Stanza: 'description'
- A description of the job.

#### author(author)

- Stanza: 'author'
- The author of the job. Should look like "FirstName LastName <email@address>".

#### version(version)

- Stanza: 'version'
- The version of the job.

#### emits(emits):

- Stanza: 'emits'
- The Upstart events that the process (or one of its children) might emit 
  (presumably via D-Bus).

#### expect(type_='daemon')

- Stanza: 'expect fork', 'expect daemon', 'expect stop'
- The type of forking that the process will do, so that Upstart can track the 
  PID properly.

#### respawn()

- Stanza: 'respawn'
- Whether to restart the process when it comes down (with an exit-code of (0)).

#### respawn_limit(count, timeout_s)

- Stanza: 'respawn limit'
- The maximum number of times to allow a processes to be respawned.

#### kill_timeout(timeout_s)

- Stanza: 'kill timeout'
- How long to wait for a process to come down before killing it.

#### normal_exit(normal_codes=[], normal_signals=[])

- Stanza: 'normal exit'
- What exit-codes and/or signals to consider as a normal exit.

#### console(target)

- Stanza: 'console'
- Where to send process output:
  - 'logged'
  - 'output'
  - 'owner'
  - None

#### env(key, value)

- Stanza: 'env'
- A key-value to set into the environment.

#### env_kv(env)

- Stanza: 'env'
- Sets N number of environment key values from a dictionary.

#### export(env_name)

- Stanza: 'export'
- Set the given environment value into all events emitted from this job.

#### nice(priority)

- Stanza: 'nice'
- Process priority.

#### limit(resource, soft_limit, hard_limit)

- Stanza: 'nproc'
- Set resource limits.

#### chdir(path)

- Stanza: 'chdir'
- Set the working-directory.

#### chroot(path)

- Stanza: 'chroot'
- Set a chroot path.
    
#### apparmor_load(profile_path)

- Stanza: 'apparmor load'
- The AppArmor profile to load into the kernel and impose onto the process.
    
#### apparmor_switch(profile)

- Stanza: 'apparmor switch'
- Impose an already-loaded AppArmor profile.

#### instance(var_name)

- Stanza: 'instance'
- Indicate the variable to describe the randomized name of one specific 
  instance of a multi-instance job.

#### kill_signal(signal)

- Stanza: 'kill signal'
- Describe the signal to be sent to the process to kill it (when a normal stop
  times out).

#### manual()

- Stanza: 'manual'
- Set to ignore any "start on" or "stop on" stanzas (perhaps for debugging).

#### oom_score(score)

- Stanza: 'oom score'
- OOM bias for likelihood of being killed.

#### reload_signal(signal)

- Stanza: 'reload signal'
- The signal to emit to tell the process to reload.

#### setgid(group_name)

- Stanza: 'setgid'
- User group to run as.

#### setuid(user_name)

- Stanza: 'setuid'
- User name to run as.

#### task()

- Stanza: 'task'
- Indicates that any jobs that are triggered by us should wait until this job 
  comes down (because we're a non-respawnable task that does some prerequisite 
  task).

#### umask(value)

- Stanza: 'umask'
- Set the file-mode creation mask.

#### usage(text)

- Stanza: 'usage'
- Usage/help string for the job, such as might be queried by initctl.

