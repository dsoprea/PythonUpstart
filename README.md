##Introduction

This is a Python-based management interface for Upstart (Canonical's service 
layer). This library provides two bodies of functionality (in terms of 
development priority):

1. DBus-based communication with Upstart to query jobs, start/stop jobs, emit 
  events, etc...
2. Writing and updating job files.

**(2) is currently in development.**

##Dependencies

- python-dbus (via apt)

##Installation

```
sudo pip install upstart
```

##Usage

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

Send the *start* event to the job.

```
>>> j.start()
```

Send the *stop* event to the job.

```
>>> j.stop()
```

