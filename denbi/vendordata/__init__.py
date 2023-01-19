"""
Module that uses the Openstack API to create project specific user data (elixir id, elixir_name, ssh keys, ...).
"""

import json
import logging
import os_client_config
import os.path
from pymemcache.client.base import Client as MemCachedClient
import re
import sys
import yaml
from yaml.loader import SafeLoader

# configure logger
log = logging.getLogger("ndv")
log.setLevel(logging.INFO)
# create console handler and set level to debug
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s')
# add formatter to ch
consolehandler.setFormatter(formatter)
# add ch to logger
log.addHandler(consolehandler)

# configuration
CONFIG = {}
# memcached client
MEMCACHEDCLIENT = None

class JsonSerDe:
    """ Implements a (en-)coding safe (de-)serializer for Json objects.
        Implementation can be used as ser[ialize]de[serialize]er for
        pymemcache client.
        See https://pymemcache.readthedocs.io/en/latest/getting_started.html#serialization
    """

    def serialize(self, key, value):  # pylint: disable=W0613
        """ Serialize value."""
        if isinstance(value, str):
            return value.encode('utf-8'), 1
        return json.dumps(value).encode('utf-8'), 2

    def deserialize(self, key, value, flags):  # pylint: disable=W0613
        """ Deserialize value."""
        if flags == 1:
            return value.decode('utf-8')
        if flags == 2:
            return json.loads(value.decode('utf-8'))
        raise Exception("Unknown serialization format")


def load_configuration(path):
    """Load configuration"""
    global CONFIG # pylint: disable=global-statement
    log.info(f"Read configuration file {path}")
    try:
        with open(path, encoding="UTF-8") as f:
            CONFIG = yaml.load(f, Loader=SafeLoader)
            if not check_configuration():
                sys.exit(1)
    except OSError as error:
        log.error(error)
        sys.exit(1)

def check_configuration(): # pylint: disable=too-many-branches
    """ Check validity of given configuration and set meaningful defaults."""
    if "cache" in CONFIG:
        if CONFIG["cache"] is None:
            CONFIG["cache"] = {}
        if "expires" in CONFIG["cache"]:
            if not isinstance(CONFIG["cache"]["expires"], int):
                log.error("Option 'cache.expires' must be of type int.")
                return False
        else:
            log.info("Cache expire time is 300 seconds.")
            CONFIG["cache"]["expire"] = 300
        if "host" in CONFIG["cache"]:
            if not (isinstance(CONFIG["cache"]["host"], str) and \
                    re.match(r'(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'
                             r'([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9]):\d{1,5}',
                             CONFIG["cache"]["host"])):
                log.error("Option 'cache.host' must be of form <host>:<port>.")
        else:
            log.info("Use 'localhost:11211' as memcached host address.")
            CONFIG["cache"]["host"] = "localhost:11211"

    for units in ("domains", "projects"):
        if units in CONFIG:
            for listtype in ("blocklist", "allowlist"):
                if listtype in CONFIG[units]:
                    if CONFIG[units][listtype] is None:
                        CONFIG[units][listtype] = []
                    elif not isinstance(CONFIG[units][listtype], list):
                        log.error(f"Option {units}->{listtype} is must be of type list (or None).")
                        return False
    return True


# check for configuration file locations ...
if os.path.isfile("nova_dynamic_vendordata.yaml"):
    load_configuration("nova_dynamic_vendordata.yaml")
elif os.path.isfile("/etc/nova_dynamic_vendordata.yaml"):
    load_configuration("/etc/nova_dynamic_vendordata.yaml")

# make use of clouds.yaml if set
if "cloud" in CONFIG:
    identity = os_client_config.make_rest_client("identity", cloud=CONFIG["cloud"])
    sdk = os_client_config.make_sdk(cloud=CONFIG["cloud"])
else:
    identity = os_client_config.make_rest_client("identity")
    sdk = os_client_config.make_sdk()

# initialize memcached client if cache is used
if "cache" in CONFIG:
    MEMCACHEDCLIENT = MemCachedClient(CONFIG["cache"]["host"], serde=JsonSerDe())
