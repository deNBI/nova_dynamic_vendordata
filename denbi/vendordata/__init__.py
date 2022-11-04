import os_client_config

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