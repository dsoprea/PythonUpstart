from collections import OrderedDict
from cStringIO import StringIO


class _JobScriptBase(object):
    def __init__(self, code):
        code = code.lstrip()

        if code[-1] != "\n":
            code += "\n"

        self.code = code

    def __str__(self):
        return self.render()

    def render(self, add_prefix=True):
        raise NotImplementedError()


class JobBashScript(_JobScriptBase):
    def __init__(self, code, shell=None, *args, **kwargs):
        super(JobBashScript, self).__init__(code)
        self.__shell = shell

    def render(self, add_prefix=True):
        if self.__shell is None:
            template = """%(code)send script
"""
        else:
            template = """%(shell)s <<EOT
%(code)sEOT
end script
"""

        rendered = template % { 'code': self.code, 
                                'shell': self.__shell }

        if add_prefix is True:
            return "script\n" + rendered
        else:
            return rendered


class JobPerlScript(_JobScriptBase):
    def render(self, add_prefix=True):
        template = """perl - <<END
%sEND
end script""" 

        rendered = (template % (self.code))

        if add_prefix is True:
            return "script\n" + rendered
        else:
            return rendered


class JobPythonScript(_JobScriptBase):
    def render(self, add_prefix=True):
        template = """python - <<END
%sEND
end script""" 

        rendered = (template % (self.code))

        if add_prefix is True:
            return "script\n" + rendered
        else:
            return rendered


class JobBuilder(object):
    def __init__(self):
        self.__stanzas = OrderedDict()

    def __str__(self):
        self.__validate()

        s = StringIO()
        for k, values in self.__stanzas.iteritems():
            for value in values:
                s.write(k)
                s.write(' ')
                s.write(value)
                s.write("\n")

        return s.getvalue()

    def __validate(self):
        if 'exec' not in self.__stanzas and \
           'script' not in self.__stanzas:
            raise ValueError("Please set exec/script before rendering.")

    def __add(self, stanza_type, raw):
        """Add a stanza that might appear more than once."""

        try:
            self.__stanzas[stanza_type].append(raw)
        except KeyError:
            self.__stanzas[stanza_type] = [raw]

        return self

    def __set(self, stanza_type, raw=''):
        """Add a stanza that may only appear once."""

        self.__stanzas[stanza_type] = [raw]
        return self

    def __script_or_exec_string(self, value, add_prefix=True):
        if issubclass(value.__class__, _JobScriptBase) is True:
            value = value.render(add_prefix)

        return value

    def run(self, command):
        assert issubclass(command.__class__, (basestring, _JobScriptBase))

        distilled = self.__script_or_exec_string(command, add_prefix=False)

        if issubclass(command.__class__, basestring) is True:
            return self.__set('exec', distilled)
        else:
            return self.__set('script', "\n" + distilled)

    def pre_start(self, command):
        assert issubclass(command.__class__, (basestring, _JobScriptBase))

        return self.__set('pre-start', self.__script_or_exec_string(command))

    def post_start(self, command):
        assert issubclass(command.__class__, (basestring, _JobScriptBase))

        return self.__set('post-start', self.__script_or_exec_string(command))

    def pre_stop(self, command):
        assert issubclass(command.__class__, (basestring, _JobScriptBase))

        return self.__set('pre-stop', self.__script_or_exec_string(command))

    def post_stop(self, command):
        assert issubclass(command.__class__, (basestring, _JobScriptBase))

        return self.__set('post-stop', self.__script_or_exec_string(command))

    def __stringify(self, dict_):
# TODO(dustin): Verify that we can use quotes.
        return ' '.join([('%s="%s"' % (k, self.__escape(v))) 
                         for (k, v) 
                         in dict_.iteritems()])

    def __stringify_events(self, events, conjunct=None):
        def distill(event):
            if issubclass(event.__class__, (tuple, list)):
                if len(event) == 1:
                    event = event[0]
                else:
                    event = ('%s %s' % (event[0], 
                                        self.__stringify(event[1])))

            return event

        if conjunct is not None:
            if issubclass(events.__class__, list) is False:
                events = [events]

            distilled = [distill(event) for event in events]
            conjunct_phrase = (' %s ' % (conjunct))
            events = conjunct_phrase.join(distilled)
        else:
            events = distill(events)

        return events

    def start_on(self, events, conjunct=None):
        """Specifies which events to start on.
        
        Examples:

        "start_on abc"
            start_on('abc')

        "start_on abc aa=1 bb=2"
            start_on(('abc', {'aa': 1, 'bb': 2}))
         
        "start_on abc and def"
            start_on(['abc', 'def'], conjunct='and')

        "start_on abc aa=1 bb=2 and def cc=3 dd=4"
            start_on([('abc', {'aa': 1, 'bb': 2}), 
                      ('def', {'cc': 3, 'dd': 4})], 
                     conjunct='and')

            start_on('abc aa=1 bb=2 and def cc=3 dd=4')
        """

        assert issubclass(events.__class__, (basestring, list))
        assert issubclass(conjunct.__class__, (None, basestring))

        events = self.__stringify_events(events, conjunct)
        return self.__set('start on', events)

    def start_on_runlevel(self, runlevels='2345'):
        assert issubclass(runlevels.__class__, (list, str))

        if issubclass(runlevels.__class__, list) is True:
            runlevels = [str(r) for r in runlevels]
            runlevel_phrase = ''.join(runlevels)
        else:
            runlevel_phrase = runlevels
        
        return self.__set('start on', ('runlevel [%s]' % (runlevel_phrase)))

    def start_on_before_started(self, service):
        assert issubclass(service.__class__, basestring)

        return self.__set('start on', ('starting %s' % (service)))

    def start_on_after_started(self, service):
        assert issubclass(service.__class__, basestring)

        return self.__set('start on', ('started %s' % (service)))

    def stop_on(self, events, conjunct=None):
        """Specifies which events to stop on. Similar syntax as "start on"."""

        assert issubclass(events.__class__, (basestring, list))
        assert issubclass(conjunct.__class__, (None, basestring))

        events = self.__stringify_events(events, conjunct)
        return self.__set('stop on', events)

    def stop_on_runlevel(self, runlevels='!2345'):
        assert issubclass(runlevels.__class__, (list, str))

        if issubclass(runlevels.__class__, list) is True:
            runlevels = [str(r) for r in runlevels]
            runlevel_phrase = ''.join(runlevels)
        else:
            runlevel_phrase = runlevels
        
        return self.__set('stop on', ('runlevel [%s]' % (runlevel_phrase)))

    def stop_on_before_stopped(self, service):
        assert issubclass(service.__class__, basestring)

        return self.__set('stop on', ('stopping %s' % (service)))

    def stop_on_after_stopped(self, service):
        assert issubclass(service.__class__, basestring)

        return self.__set('stop on', ('stopped %s' % (service)))

    def __escape(self, value):
        return value.replace('\\', '\\\\').\
                     replace('"', '\\"').\
                     replace('\'', '\\\'')

    def __quote(self, text):
        return "\"%s\"" % (self.__escape(text))

    def description(self, description):
        assert issubclass(description.__class__, basestring)

        return self.__set('description', self.__quote(description))

    def author(self, author):
        assert issubclass(author.__class__, basestring)

        return self.__set('author', self.__quote(author))

    def version(self, version):
        assert issubclass(version.__class__, basestring)

        return self.__set('version', self.__quote(version))

    def emits(self, emits):
        assert issubclass(emits.__class__, [basestring, list])

        if issubclass(emits.__class__, list) is True:
            emits = ' '.join(emits)

        return self.__add('emits', emits)

    def expect(self, type_='daemon'):
        if type_ not in ['fork', 'daemon', 'stop']:
            raise ValueError("Expect type is not valid: %s" % (type_))

        return self.__set('expect %s' % (type_))

    def respawn(self):
        return self.__set('respawn')

    def respawn_limit(self, count, timeout_s):
        assert issubclass(count.__class__, int)
        assert issubclass(timeout_s.__class__, int)

        return self.__set('respawn limit', ('%d %d' % (count, timeout_s)))

    def kill_timeout(self, timeout_s):
        assert issubclass(timeout_s.__class__, int)

        return self.__set('kill timeout', timeout_s)

    def normal_exit(self, normal_codes=[], normal_signals=[]):
        """Define what to expect for a successful exist. "codes" are integers, 
        and "signals" are name strings (and, possibly, signal integers).
        """

        if not normal_codes and not normal_signals:
            raise ValueError("Please provide at least one code/signal for a "
                             "normal exit.")

        normal_codes = [str(c) for c in normal_codes]

        return self.__set('normal exit', ' '.join(normal_codes + normal_signals))

    def console(self, target):
        if target not in ('log', 'output', 'owner', None):
            raise ValueError("Console target is not valid: %s" % (target))
        elif target is None:
            target = 'none'

        return self.__set('console', target)

    def env(self, key, value):
        assert issubclass(key.__class__, basestring)
        assert issubclass(value.__class__, basestring)

# TODO(dustin): Can we escape/quote the key/value?
        return self.__add('env', ('%s=%s' % (key, value)))

    def env_kv(self, env):
# TODO(dustin): How do we escape/quote the key/value?
        for k, v in env.iteritems():
            self.env_kv(k, v)

        return self

    def export(self, env_name):
        assert issubclass(env_name.__class__, basestring)

        return self.__add('export', env_name)

    def nice(self, priority):
        assert issubclass(priority.__class__, int)

        return self.__set('nice', priority)

    def limit(self, resource, soft_limit, hard_limit):
        assert issubclass(resource.__class__, basestring)
        assert soft_limit == 'unlimited' or issubclass(soft_limit, int)
        assert hard_limit == 'unlimited' or issubclass(hard_limit, int)

        if resource not in ['as', 'core', 'cpu', 'data', 'fsize', 'memlock', 
                            'msgqueue', 'nice', 'nofile', 'nproc', 'rss', 
                            'rtprio', 'sigpending', 'stack']:
            raise ValueError("Invalid resource for limit: %s" % (resource))

        return self.__set('nproc', ('%s %d %d' % (resource, soft_limit, hard_limit)))

    def chdir(self, path):
        assert issubclass(path.__class__, basestring)

        return self.__set('chdir', path)

    def chroot(self, path):
        assert issubclass(path.__class__, basestring)

        return self.__set('chroot', path)

    def apparmor_load(self, profile_path):
        assert issubclass(profile_path.__class__, basestring)

        return self.__set('apparmor load', profile_path)
    
    def apparmor_switch(self, profile):
        assert issubclass(profile.__class__, basestring)

        return self.__set('apparmor switch', profile)

    def instance(self, var_name):
        assert issubclass(instance.__class__, basestring)

        return self.__set('instance', ('$%s' % (var_name)))

    def kill_signal(self, signal):
        assert issubclass(signal__class__, (basestring, int))

        return self.__add('kill signal', signal)

    def manual(self):
        return self.__set('manual')

    def oom_score(self, score):
        assert issubclass(score.__class__, int)

        return self.__set('oom score', score)

    def reload_signal(self, signal):
        assert issubclass(signal.__class__, (basestring, int))

        return self.__add('reload signal', signal)

    def setgid(self, group_name):
        assert issubclass(group_name.__class__, basestring)

        return self.__set('setgid', group_name)

    def setuid(self, user_name):
        assert issubclass(user_name.__class__, basestring)

        return self.__set('setuid', user_name)

    def task(self):
        return self.__set('task')

    def umask(self, value):
        assert issubclass(value.__class__, int)

        return self.__set('umask', value)

    def usage(self, text):
        assert issubclass(text.__class__, basestring)

        return self.__set('usage', self.__quote(text))

