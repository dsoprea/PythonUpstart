##Introduction

This is a Python-based management interface for Upstart (Canonical's service 
layer). This library provides two bodies of functionality (in terms of 
development priority):

1. Management commands (using D-Bus) to query jobs, start/stop jobs, emit 
   events, etc...
2. Writing and updating job files.

##Dependencies

- *python-dbus* (under Ubuntu), or equivalent.

##Installation

```
sudo pip install upstart
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

### run(command)

- 'exec'
- 'script'

### pre_start(command)

- 'pre-start'

### post_start(command)

- 'post-start'

### pre_stop(command)

- 'pre-stop'

### post_stop(command)

- 'post-stop'

### start_on(events, conjunct=None)

- 'start_on'

### start_on_runlevel(runlevels=[2,3,4,5])

- 'start on runlevel'

### start_on_before_started(service)

- 'start on starting'

### start_on_after_started(service)

- 'start on started'

### stop_on(events, conjunct=None)

- 'stop on'

### stop_on_runlevel(runlevels=[0,1,6])

- 'stop on runlevel'

### stop_on_before_stopped(service)

- 'stop on stopping'

### stop_on_after_stopped(service)

- 'stop on stopped'

### description(description)

- 'description'

### author(author)

- 'author'

### version(version)

- 'version'

### emits(emits):

- 'emits'

### expect(type_='daemon')

- 'expect fork'
- 'expect daemon'
- 'expect stop'

### respawn()

- 'respawn'

### respawn_limit(count, timeout_s)

- 'respawn limit'

### kill_timeout(timeout_s)

- 'kill timeout'

### normal_exist(normal_codes=[], normal_signals=[])

- 'normal timeout'

### console(target)

- 'console'

### env(key, value)

- 'env'

### env_kv(dict_)

- 'env'

### export(env_name)

- 'export'

### nice(priority)

- 'nice'

### limit(resource, soft_limit, hard_limit)

- 'nproc'

### chdir(path)

- 'chdir'

### chroot(path)

- 'chroot'

### nice(priority)

- 'nice'
    
### apparmor_load(profile_path)

- 'apparmor load'
    
### apparmor_switch(profile)

- 'apparmor switch'

### instance(var_name)

- 'instance'

### kill_signal(signal)

- 'kill signal'

### manual()

- 'manual'

# oom_score(score)

- 'oom score'

### reload_signal(signal)

- 'reload signal'

### setgid(group_name)

- 'setgid'

### setuid(user_name)

- 'setuid'

### task()

- 'task'

### umask(value)

- 'umask'

### usage(text)

- 'usage'

