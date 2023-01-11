# Attention! 
**This repository is work in progress and shouldn't use in a production environment.**

# Nova Dynamic Vendor data

Openstack Nova presents configuration information to instances it starts via a mechanism called metadata. 
This metadata is made available via metadata service. Services like cloud-init make use of this metadata
to initialize and configure a started instance.

Beside  metadata information in AWS compatible format, Openstack additionally supports metadata in its
own style. There are three different kind of metadata which can be made available to the instance.

| Typ | Description                                                                                   |
|-----|-----------------------------------------------------------------------------------------------|
| Nova (Compute) data | Structured data containing information about network, hostname, public-key, ...               |
| User data | The user has the ability to pass unstructured data like shell scripts, ...  to the instance.  |
| Vendor data | Optional the cloud provider can make vendor specific information (static or dynamic) availabe |

_Vendor data can be static or dynamic or a mixture of both._

Query the vendor_data2.json returns all available vendor data static and dynamic in a single json file.

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

## Configure Dynamic Vendor data

Dynamic Vendor data can be enabled and configured in the Nova API configuration. It is possible to configure more
than one endpoint. Different endpoints are distinguished by a unique prefix. The configuration example below configure
two endpoints which delivers data when dynamic vendor is requested. 
```
[api]
vendordata_providers=DynamicJSON
vendordata_dynamic_targets=denbi@http://localhost:9898,nfdi@http://localhost
```
Information like the project id the current instance is started in is provided to each dynamic endpoint.

## Usage

### Configuration

The nova_dynamic_vendordata service can be configured using a configuration file in yaml syntax.

#### Openstack 

The nova_dynamic_vendordata service needs access to the Openstack API, therefor valid cloud credentials
must be past to the service (using environment or clouds.yaml).
If `cloud` option is set, a clouds.yaml configuration is used, the environment otherwise.

##### Environment

The [Openstack cli manpage](https://docs.openstack.org/python-openstackclient/latest/cli/man/openstack.html#manpage)
gives an overview about supported and used environment variables.

##### Configuration file

clouds.yaml is a configuration file that contains everything needed to connect to one or more clouds.
It may contain private information and is generally considered private to a user. OpenStack API looks
for a file called clouds.yaml in the following locations:

- `.` (current directory)
- `~/.config/openstack`
- `/etc/openstack`

The first file found wins.

### Allow- or Blocklisting

The nova_dynamic_vendordata service supports _Allow_- or _Blocklisting_ for domains and projects. 
In general, it is a good idea to use _allowlist_ to give only specific domains/projects full access
to service. 

**Attention! There is no restriction when `allowlist` or `blocklist` for domains and project
are not set.** 

### Caching

The nova_dynamic_vendordata service caches data to minimize Openstack API access. The Data is cached for
300 seconds (= 5 minutes) by default and can be set using the `cache` option. Setting `cache` to `0` or 
less disables the cache.

#### Example/Template
```yaml
cloud: <name of cloud configuration to be used>

cache: 300 

domains:
  allowlist:
    - default_domain
    - ...
  blocklist:
    - secret_domain
    - ...
projects:
  allowlist:
    - ...
  blocklist:
    - service
    

```


## Docker/Podman container

A simple container based on latest alpine/python3 can be build using the Dockerfile ...

```shell
docker build -t denbi/nova_dynamic_vendordata .
```

and be can run as follows ...

```shell
docker run --rm --env-file env.file --v config.yaml:/etc/nova_dynamic_vendordata.yaml --network host nova_dynamic_vendordata
```
using host network or ...

```shell
docker run --rm --env-file env.file --v config.yaml:/etc/nova_dynamic_vendordata.yaml -p 9898:9898 nova_dynamic_vendordata
```
using a separate network layer.

## Requirements and known issues.
nova_dynamic_vendordata is tested on Ubuntu 20.04 and newer (Python 3.8 or newer). Older python version might work, but
Ubuntu 18.04 with default python 3 version (3.6) is known not to be working.

As defined in the requirements.txt the project is based on:

- Flask
- os_client_config
- gunicorn
