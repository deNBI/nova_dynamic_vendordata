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


## Dynamic Vendor data

tbw.

## Usage

tbw.

## Docker container

tbw.
