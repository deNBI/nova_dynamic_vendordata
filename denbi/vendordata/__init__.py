"""
Module that uses the Openstack API to create project specific user data (elixir id, elixir_name, ssh keys, ...).
"""

import logging
import os_client_config
import os.path
import sys
import yaml
from yaml.loader import SafeLoader

# cloud="openstack-dev"
#
# if cloud:
#     identity = os_client_config.make_rest_client("identity",cloud=cloud)
#     sdk = os_client_config.make_sdk(cloud=cloud)
# else:
#    identity = os_client_config.make_rest_client("identity")
#    sdk = os_client_config.make_sdk()



identity = os_client_config.make_rest_client("identity")
sdk = os_client_config.make_sdk()
log = logging.getLogger("nova_dynamic_vendordata")

def check_configuration():
    """ Check validity of given configuration."""
    if config["cache"]:
        log.debug(f"Found option 'cache' {config['cache']}")
        if isinstance(config["cache"],int):
            log.error("Option 'cache' must be of type int.")
            return False
    else:
        config["cache"] = 300
    if config["cloud"]:
        log.debug("Found option cloud.")
    for units in ("domains","projects"):
        if config[units]:
            log.debug("Found option domains.")
            for listtype in ("blocklist","allowlist"):
                if config[units][listtype] and isinstance(config[units][listtype],list):
                    log.debug(f"Found option {units}->{listtype} ({','.join(config[units][listtype])})")
                else:
                    log.error(f"Option {units}->{listtype} is must be of type list.")
                    return False
    return True


# check if configuration file available
if os.path.isfile("/etc/nova_dynamic_vendordata.yaml"):
    try:
        with open('/etc/nova_dynamic_vendordata.yaml',encoding="UTF-8") as f:
            config = yaml.load(f, Loader=SafeLoader)
            if not check_configuration():
                sys.exit(1)
    except OSError as e:
        log.error(e)
        sys.exit(1)
else:
    config = {'cache':300}
