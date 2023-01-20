# Nova Dynamic Vendor data

OpenStack Nova presents configuration information to instances it starts via a mechanism called metadata. 
This metadata is made available via metadata service. Services like cloud-init make use of this metadata
to initialize and configure an instance on launch.

Beside  metadata information in AWS compatible format, OpenStack additionally supports metadata in its
own style. There are three different kinds of metadata which can be made available to the instance.

| Typ                 | Description                                                                                      |
|---------------------|--------------------------------------------------------------------------------------------------|
| Nova (Compute) data | Structured data containing information about network, hostname, public-key, etc.                 |
| User data           | The user has the ability to pass unstructured data like shell scripts, ...  to the instance.     |
| Vendor data         | (Optional) The cloud provider can make vendor specific information (static or dynamic) available |

_Vendor data can be static or dynamic or a mixture of both._

Querying the `vendor_data2.json` returns all available vendor data (static and dynamic) in a single json file.

```
> curl http://169.254.169.254/openstack/latest/vendor_data2.json | jq 
>{
  "denbi": [
    {
      "elixir_name": "XXXX",
      "id": "...",
      "name": "...",
      "perun_id": "...",
      "public_keys": [
        "ecdsa-sha2-nistp256 AAAA...",
      ]
    },
    ...
  ],
  "nfdi": ...
 }
```

## Configuration of dynamic vendor data

Dynamic vendor data can be enabled and configured in the Nova API configuration. It is possible to configure more
than one endpoint. Different endpoints are distinguished by a unique prefix. The configuration example below configures
the two endpoints `denbi` and `nfdi`.
```
[api]
vendordata_providers=DynamicJSON
vendordata_dynamic_targets=denbi@http://localhost:9898,nfdi@http://localhost
```
Information like the project ID of the current instance is provided to each dynamic endpoint.

## Usage

### Configuration

The `nova_dynamic_vendordata` service can be configured using a configuration file in yaml syntax. The configuration
is searched in `$(pwd)/nova_dynamic_vendordata.yaml` (preferred) and `/etc/nova_dynamic_vendordata.yaml` 

#### OpenStack 

The `nova_dynamic_vendordata` service needs access to the OpenStack API, therefore valid cloud credentials
must be passed to the service (using environment or `clouds.yaml`).
If the `cloud` option is set, the `clouds.yaml` configuration is used instead of environment variables.

##### Environment

The [OpenStack CLI manpage](https://docs.openstack.org/python-openstackclient/latest/cli/man/openstack.html#manpage)
gives an overview about supported and used environment variables.

##### Configuration file

`clouds.yaml` is a configuration file that contains everything needed to connect to one or more clouds.
It may contain private information and is generally considered private to a user. OpenStack API looks
for a file called clouds.yaml in the following locations:

- `$(pwd)` (current working directory)
- `~/.config/openstack`
- `/etc/openstack`

The first file found is used.

### Allow- or Blocklisting

The `nova_dynamic_vendordata` service supports _allow- or _blocklisting_ for domains and projects. 
In general, it is a good idea to use _allowlist_ to give only specific domains/projects full access
to the service by providing their UUIDs.

**Attention! The API is unprotected if neither `allowlist` nor `blocklist` are set.** 

### Caching

The `nova_dynamic_vendordata` service caches data to minimize OpenStack API access using 
[memcached](https://memcached.org/). The Data is cached for 300 seconds (= 5 minutes) 
by default and can be set using the `cache.expires` option. The memcached host url is
"localhost:11211" by default and can be set using the `cache.host` option.

#### Example/Template
```yaml
cloud: <name of cloud configuration to be used>

cache:
  host: "localhost:11211"
  expire: 300

domains:
  allowlist:
    - fcae49b0-acf8-4a67-83e0-9960bc5fb598
    - ...
  blocklist:
    - c111d409-2350-4a32-963b-e819cf6d61ec
    - ...
projects:
  allowlist:
    - ...
  blocklist:
    - 6550efc9-b930-4956-b9d7-8d8ab42eab3f
```


## Docker/Podman container

A simple container based on the latest `alpine/python3` can be built using the Dockerfile ...

```shell
docker build -t denbi/nova_dynamic_vendordata .
```

and be can run as follows ...

```shell
docker run --rm --env-file env.file -v $(pwd)/config.yaml:/etc/nova_dynamic_vendordata.yaml --network host nova_dynamic_vendordata
```
using host network or ...

```shell
docker run --rm --env-file env.file -v $(pwd)/config.yaml:/etc/nova_dynamic_vendordata.yaml -p 9898:9898 nova_dynamic_vendordata
```
using a separate network layer.

## Requirements and known issues.
`nova_dynamic_vendordata` has been tested on Ubuntu 20.04 and newer (Python 3.8 or newer). Older python versions might work, but
Ubuntu 18.04 with default python 3 version (3.6) is known NOT to be working.
