import urllib
import urllib2
import urlparse

__all__ = ['Harold']
__version__ = '1.1.0'

class Harold(object):
    def __init__(self, host, secret, port=80, timeout=3):
        self.host = host
        self.port = port
        self.secret = secret
        self.timeout = timeout

    def _post_to_harold(self, path, data):
        path_components = ['harold'] + path + [self.secret]
        combined_path = '/'.join(path_components)
        netloc = "%s:%d" % (self.host, self.port)
        url = urlparse.urlunsplit(("http", netloc, combined_path, None, None))
        encoded_data = urllib.urlencode(data)
        urllib2.urlopen(url, data=encoded_data, timeout=self.timeout)

    def alert(self, tag, message):
        self._post_to_harold(
            ["alert"],
            {
                "tag": tag,
                "message": message,
            }
        )

    def heartbeat(self, tag, interval):
        self._post_to_harold(
            ["heartbeat"],
            {
                "tag": tag,
                "interval": interval,
            }
        )

    def get_irc_channel(self, channel):
        return IrcChannel(self, channel)

    def get_deploy(self, id):
        return Deploy(self, id)


class IrcChannel(object):
    def __init__(self, harold, channel):
        self.harold = harold
        self.channel = channel

    def message(self, message):
        self.harold._post_to_harold(
            ["message"],
            {
                "channel": self.channel,
                "message": message,
            }
        )

    def set_topic(self, topic):
        self.harold._post_to_harold(
            ["topic", "set"],
            {
                "channel": self.channel,
                "topic": topic,
            }
        )


class Deploy(object):
    def __init__(self, harold, id):
        self.harold = harold
        self.id = id

    def begin(self, who, args, log_path, host_count):
        self.harold._post_to_harold(
            ["deploy", "begin"],
            {
                "id": self.id,
                "who": who,
                "args": args,
                "log_path": log_path,
                "count": host_count
            }
        )

    def end(self):
        self.harold._post_to_harold(
            ["deploy", "end"],
            {
                "id": self.id,
            }
        )

    def abort(self, reason):
        self.harold._post_to_harold(
            ["deploy", "abort"],
            {
                "id": self.id,
                "reason": reason,
            }
        )

    def progress(self, host, index):
        self.harold._post_to_harold(
            ["deploy", "progress"],
            {
                "id": self.id,
                "host": host,
                "index": index,
            }
        )
