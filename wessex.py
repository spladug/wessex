import hashlib
import hmac
import posixpath
import urllib
import urlparse

import requests


__all__ = ['Harold', 'connect_harold']
__version__ = '1.5.0'


class Harold(object):
    def __init__(self, url, secret, timeout=3):
        self.scheme, self.netloc, self.path, query, fragment = urlparse.urlsplit(url)
        assert not query, "harold url may not contain query parameters."
        assert not fragment, "harold url may not contain fragments."

        self.secret = secret
        self.timeout = timeout
        self.session = requests.Session()

    def _post_to_harold(self, path, data):
        combined_path = posixpath.join(self.path, "harold", path)
        url = urlparse.urlunsplit((
            self.scheme,
            self.netloc,
            combined_path,
            None,
            None,
        ))

        body = urllib.urlencode(data)
        hash = hmac.new(self.secret, body, hashlib.sha1)

        resp = self.session.post(
            url,
            data=body,
            timeout=self.timeout,
            headers={
                "User-Agent": "/".join((__name__, __version__)),
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Hub-Signature": "sha1=" + hash.hexdigest(),
            },
        )
        resp.raise_for_status()

    def alert(self, tag, message):
        self._post_to_harold("alert", {
            "tag": tag,
            "message": message,
        })

    def heartbeat(self, tag, interval):
        self._post_to_harold("heartbeat", {
            "tag": tag,
            "interval": interval,
        })

    def get_irc_channel(self, channel):
        return IrcChannel(self, channel)

    def get_deploy(self, id):
        return Deploy(self, id)


class IrcChannel(object):
    def __init__(self, harold, channel):
        self.harold = harold
        self.channel = channel

    def message(self, message):
        self.harold._post_to_harold("message", {
            "channel": self.channel,
            "message": message,
        })

    def set_topic(self, topic):
        self.harold._post_to_harold("topic/set", {
            "channel": self.channel,
            "topic": topic,
        })


class Deploy(object):
    def __init__(self, harold, id):
        self.harold = harold
        self.id = id

    def begin(self, who, args, log_path, host_count):
        self.harold._post_to_harold("deploy/begin", {
            "id": self.id.encode('utf-8'),
            "who": who,
            "args": args,
            "log_path": log_path.encode('utf-8'),
            "count": host_count
        })

    def end(self):
        self.harold._post_to_harold("deploy/end", {
            "id": self.id.encode('utf-8'),
        })

    def error(self, error):
        self.harold._post_to_harold("deploy/error", {
            "id": self.id.encode('utf-8'),
            "error": error,
        })

    def abort(self, reason):
        self.harold._post_to_harold("deploy/abort", {
            "id": self.id.encode('utf-8'),
            "reason": reason,
        })

    def progress(self, host, index):
        self.harold._post_to_harold("deploy/progress", {
            "id": self.id.encode('utf-8'),
            "host": host,
            "index": index,
        })


def connect_harold(config="/etc/harold.ini"):
    """Creates a Harold object based on configuration in the given
    configuration file"""
    import ConfigParser

    parser = ConfigParser.RawConfigParser({
        "timeout": 3,
    })
    files_read = parser.read(config)
    if not files_read:
        raise IOError("No config file found in: %r" % config)

    url = parser.get("harold", "url")
    secret = parser.get("harold", "hmac_secret")
    timeout = parser.getint("harold", "timeout")

    return Harold(url, secret, timeout)


def harold_irc():
    import os
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Send a message to an IRC channel via Harold.")
    parser.add_argument("channel", nargs=1, help="IRC channel to send message to")
    parser.add_argument("message", nargs="*", help="Message to send.")
    args = parser.parse_args()

    try:
        harold = connect_harold()
        channel = harold.get_irc_channel(args.channel[0])

        if args.message:
            channel.message(" ".join(args.message))
        else:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                channel.message(line)
    except Exception, e:
        print "%s: %s" % (os.path.basename(sys.argv[0]), e)
        return 1

    return 0
