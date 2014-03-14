import dbus

from collections import OrderedDict
from cStringIO import StringIO


class UpstartJob(object):
    def __init__(self, job_name):
        if job_name[0] == '/':
            raise ValueError("Expected simple, short job name: %s" % 
                             (job_name))

        self.__system = dbus.SystemBus()
        self.__job_name = job_name

        self.__o = self.__system.get_object(
                'com.ubuntu.Upstart', 
                '/com/ubuntu/Upstart/jobs/%s' % (self.__job_name))

        self.__job_i = dbus.Interface(
                        self.__o, 
                        'com.ubuntu.Upstart0_6.Job')

    def get_status(self):
        o = self.__system.get_object(
                'com.ubuntu.Upstart', 
                '/com/ubuntu/Upstart/jobs/%s/_' % (self.__job_name))

        properties_i = dbus.Interface(
                        o, 
                        'org.freedesktop.DBus.Properties')

        return properties_i.GetAll('')

    def __get_conditions(self, type_):
        properties_i = dbus.Interface(
                        self.__o, 
                        'org.freedesktop.DBus.Properties')

        return properties_i.Get('com.ubuntu.Upstart0_6.Job', type_)

    def get_start_on_condition(self):
        return self.__get_conditions('start_on')

    def get_stop_on_condition(self):
        return self.__get_conditions('stop_on')

    def start(self):
        self.__job_i.Start('', True)

    def stop(self):
        self.__job_i.Stop('', True)

    def restart(self):
        self.__job_i.Restart('', True)


class _JobScriptBase(object):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        raise NotImplementedError()


class JobBashScript(_JobScriptBase):
    def __init__(self, shell=None):
        self.__shell = shell

    def __str__(self):
        if self.__shell is None:
            template = """script
%(code)s
end script
"""
        else:
            template = """script
%(shell)s <<EOT
%(code)s
EOT
end script
"""

        return template % { 'code': self.code, 
                            'shell': self.__shell }


class JobPerlScript(_JobScriptBase):
    def __str__(self):
        template = """script

perl - <<END
%s
END

end script""" 

        return (template % (self.code))


class JobPythonScript(_JobScriptBase):
    def __str__(self):
        template = """script

python - <<END
%s
END

end script""" 

        return (template % (self.code))


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

    def __script_or_exec_string(self, value):
        if issubclass(value.__class__, _JobScriptBase) is True:
            value = str(value)

        return value

    def run(self, text):
        distilled = self.__script_or_exec_string(text)

        if issubclass(text.__class__, basestring) is True:
            return self.__set('exec', distilled)
        else:
            return self.__set('script', distilled)

    def pre_start(self, command):
        return self.__add('pre-start', self.__script_or_exec_string(command))

    def post_start(self, command):
        return self.__add('post-start', self.__script_or_exec_string(command))

    def pre_stop(self, command):
        return self.__add('pre-stop', self.__script_or_exec_string(command))

    def post_stop(self, command):
        return self.__add('post-stop', self.__script_or_exec_string(command))

    def start_on(self, command):
        return self.__add('start on', self.__script_or_exec_string(command))

    def stop_on(self, command):
        return self.__add('stop on', self.__script_or_exec_string(command))

    def __escape(self, value):
        return value.replace('\\', '\\\\').\
                     replace('"', '\\"').\
                     replace('\'', '\\\'')

    def description(self, description):
        return self.__set('description', "\"%s\"" % (self.__escape(description)))

    def author(self, author):
        return self.__set('author', "\"%s\"" % (self.__escape(author)))

    def version(self, version):
        return self.__set('version', version)

    def emits(self, emits):
        return self.__set('emits', emits)

    def respawn(self):
        return self.__set('respawn')

    def respawn_limit(self, count, timeout_s):
        return self.__set('respawn limit', ('%d %d' % (count, timeout_s)))

# TODO(dustin): Implement *instance*.

    def kill_timeout(self, timeout_s):
        return self.__set('kill timeout', timeout_s)

    def normal_exist(self, normal_codes=[], normal_signals=[]):
        if not normal_codes and not normal_signals:
            raise ValueError("Please provide at least one code/signal for a normal exit.")

        normal_codes = [str(c) for c in normal_codes]

        return self.__set('normal timeout', ' '.join(normal_codes + normal_signals))

    def console(self, target):
        if target not in ('logged', 'output', 'owner', None):
            raise ValueError("Console target is not valid: %s" % (target))

        return self.__set('console', target)

    def env(self, key, value):
# TODO(dustin): How do we escape/quote the key/value?
        return self.__add('env', ('%s=%s' % (key, value)))

    def env_kv(self, dict_):
# TODO(dustin): How do we escape/quote the key/value?
        for k, v in dict_.iteritems():
            self.env_kv(k, v)

        return self

    def nice(self, priority):
        return self.__set('nice', priority)

    def limit(self, resource, soft_limit, hard_limit):
        if resource not in ['as', 'core', 'cpu', 'data', 'fsize', 'memlock', 
                            'msgqueue', 'nice', 'nofile', 'nproc', 'rss', 
                            'rtprio', 'sigpending', 'stack']:
            raise ValueError("Invalid resource for limit: %s" % (resource))

        return self.__set('nproc', ('%s %d %d' % (resource, soft_limit, hard_limit)))

    def chroot(self, path):
        return self.__set('chroot', path)

    def nice(self, path):
        return self.__set('chdir', path)
