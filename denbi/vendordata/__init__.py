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

log = logging.getLogger("nova_dynamic_vendordata")
log.setLevel(logging.INFO)

class JsonSerDe:
    """ Implements a (en-)coding safe (de-)serializer for Json objects.
        Implementation can be used as ser[ialize]de[serialize]er for
        pymemcache client.
        See https://pymemcache.readthedocs.io/en/latest/getting_started.html#serialization
    """

    def serialize(self, key, value): # pylint: disable=W0613
        """ Serialize value."""
        if isinstance(value, str):
            return value.encode('utf-8'), 1
        return json.dumps(value).encode('utf-8'), 2

    def deserialize(self, key, value, flags): # pylint: disable=W0613
        """ Deserialize value."""
        if flags == 1:
            return value.decode('utf-8')
        if flags == 2:
            return json.loads(value.decode('utf-8'))
        raise Exception("Unknown serialization format")

def check_configuration():
    """ Check validity of given configuration and set meaningful defaults."""
    global config
    if "cache" in config:
        log.debug(f"Found option 'cache' !")
        if "expires" in config["cache"]:
            log.debug("Found option cache.expires")
            if not isinstance(config["cache"]["expires"],int):
                log.error("Option 'cache.expires' must be of type int.")
                return False
        else:
            config["cache"]["expire"] = 300
        if "host" in config["cache"]:
            if not(isinstance(config["cache"]["expires"],str) and \
                   re.match(r'(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'
                            r'([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9]):\d{1,5}',
                            config["cache"]["expires"])):
                log.error("Option 'cache.host' must be of form <host>:<port>.")
        else:
            config["cache"]["host"] = "localhost:11211"

    if "cloud" in config:
        log.debug("Found option cloud.")
    for units in ("domains","projects"):
        if units in config:
            log.debug("Found option domains.")
            for listtype in ("blocklist","allowlist"):
                if listtype in config[units]:
                    if isinstance(config[units][listtype],list):
                        log.debug(f"Found option {units}->{listtype} ({','.join(config[units][listtype])})")
                    else:
                        log.error(f"Option {units}->{listtype} is must be of type list.")
                        return False
    return True

# check for configuration file locations ...
configpath = None
if os.path.isfile("nova_dynamic_vendordata.yaml"):
    configpath = "nova_dynamic_vendordata.yaml"
elif os.path.isfile("/etc/nova_dynamic_vendordata.yaml"):
    configpath = "/etc/nova_dynamic_vendordata.yaml"

# check if configuration file available, load and check it
if configpath:
    log.info(f"Read configuration file {configpath}")
    try:
        with open(configpath,encoding="UTF-8") as f:
            config = yaml.load(f, Loader=SafeLoader)
            if not check_configuration():
                sys.exit(1)
    except OSError as e:
        log.error(e)
        sys.exit(1)
else:
    config = {}

# make use of clouds.yaml if set
if "cloud" in config:
    identity = os_client_config.make_rest_client("identity", cloud=config["cloud"])
    sdk = os_client_config.make_sdk(cloud=config["cloud"])
else:
    identity = os_client_config.make_rest_client("identity")
    sdk = os_client_config.make_sdk()

# initialize memcached client if cache is used
if "cache" in config:
    memcachedclient = MemCachedClient(config["cache"]["host"],serde=JsonSerDe)
else:
    memcachedclient = None