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

#### pre_start(command)

- Stanza: 'pre-start'

#### post_start(command)

- Stanza: 'post-start'

#### pre_stop(command)

- Stanza: 'pre-stop'

#### post_stop(command)

- Stanza: 'post-stop'

#### start_on(events, conjunct=None)

- Stanza: 'start_on'

#### start_on_runlevel(runlevels=[2,3,4,5])

- Stanza: 'start on runlevel'

#### start_on_before_started(service)

- Stanza: 'start on starting'

#### start_on_after_started(service)

- Stanza: 'start on started'

#### stop_on(events, conjunct=None)

- Stanza: 'stop on'

#### stop_on_runlevel(runlevels=[0,1,6])

- Stanza: 'stop on runlevel'

#### stop_on_before_stopped(service)

- Stanza: 'stop on stopping'

#### stop_on_after_stopped(service)

- Stanza: 'stop on stopped'

#### description(description)

- Stanza: 'description'

#### author(author)

- Stanza: 'author'

#### version(version)

- Stanza: 'version'

#### emits(emits):

- Stanza: 'emits'

#### expect(type_='daemon')

- Stanza: 'expect fork', 'expect daemon', 'expect stop'

#### respawn()

- Stanza: 'respawn'

#### respawn_limit(count, timeout_s)

- Stanza: 'respawn limit'

#### kill_timeout(timeout_s)

- Stanza: 'kill timeout'

#### normal_exist(normal_codes=[], normal_signals=[])

- Stanza: 'normal timeout'

#### console(target)

- Stanza: 'console'

#### env(key, value)

- Stanza: 'env'

#### env_kv(dict_)

- Stanza: 'env'

#### export(env_name)

- Stanza: 'export'

#### nice(priority)

- Stanza: 'nice'

#### limit(resource, soft_limit, hard_limit)

- Stanza: 'nproc'

#### chdir(path)

- Stanza: 'chdir'

#### chroot(path)

- Stanza: 'chroot'

#### nice(priority)

- Stanza: 'nice'
    
#### apparmor_load(profile_path)

- Stanza: 'apparmor load'
    
#### apparmor_switch(profile)

- Stanza: 'apparmor switch'

#### instance(var_name)

- Stanza: 'instance'

#### kill_signal(signal)

- Stanza: 'kill signal'

#### manual()

- Stanza: 'manual'

#### oom_score(score)

- Stanza: 'oom score'

#### reload_signal(signal)

- Stanza: 'reload signal'

#### setgid(group_name)

- Stanza: 'setgid'

#### setuid(user_name)

- Stanza: 'setuid'

#### task()

- Stanza: 'task'

#### umask(value)

- Stanza: 'umask'

#### usage(text)

- Stanza: 'usage'

