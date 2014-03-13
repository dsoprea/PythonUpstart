import dbus


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

