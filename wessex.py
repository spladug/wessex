import urllib
import urllib2
import urlparse

__all__ = ['Harold']

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

    def restore_topic(self):
        self.harold._post_to_harold(
            ["topic", "restore"],
            {
                "channel": self.channel,
            }
        )

