import dbus


class UpstartSystem(object):
    def __init__(self):
        self.__system = dbus.SystemBus()
        self.__o = self.__system.get_object('com.ubuntu.Upstart', '/com/ubuntu/Upstart')

    def get_version(self):
        i = dbus.Interface(self.__o, 'org.freedesktop.DBus.Properties')
        raw = i.Get('com.ubuntu.Upstart0_6', 'version')

        return str(raw)

