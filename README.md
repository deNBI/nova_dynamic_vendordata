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

``
curl http://169.254.269.254/latest
``

## Configure Dynamic Vendor data

Dynamic Vendor data can be enabled and configured in the Nova API configuration. It is possible to configure more
than one endpoint. Different endpoints are distinguished by a unique prefix. The configuration example below configure
two endpoints which delivers data when dynamic vendor is requested. 
```
tbw. Example nova configuration which two dynamic vendor data service defined.
```
Information like the project id the current instance
is started in is provided to each dynamic enpoint.

```
tbw. Example information (in JSON) which is provided inside the POST request to a configured dynamic vendor data service.
```


## Usage

The nova_dynamic_vendordata service needs access to the Openstack API, therefor valid credentials must be past to 
the service (using environment or clouds.yaml).

## Docker/Podman container

A simple container based on latest alpine/python3 can be build using the Dockerfile ...

```
docker build -t denbi/nova_dynamic_vendordata .
```

and be can run as follows ...

```
docker run --rm --env-file env.file --network host nova_dynamic_vendordata
```
using host network or ...

```
docker run --rm --env-file env.file -p 9000:9000 nova_dynamic_vendordata
```
using a separate network layer.

## Requirements and known issues.
nova_dynamic_vendordata is tested on Ubuntu 20.04 and newer (Python 3.8 or newer). Older python version might work, but
Ubuntu 18.04 with default python 3 version (3.6) is known not to be working.

As defined in the requirements.txt the project is based on:

- Flask
- os_client_config
- gunicorn
