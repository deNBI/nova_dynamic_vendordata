"""
Module that uses the Openstack API to create project specific user data (elixir id, elixir_name, ssh keys, ...).
"""

from flask import Flask, request
from denbi.vendordata import identity, sdk, config, log

app = Flask(__name__)




@app.post("/")
def vendordata():
    """ Return a list of users (with metadata) for given project id.
        If project_id is block listed or not in allow listed an empty
        json document is returned.
    """
    data = request.get_json()

    if "project-id" in data:
        project_id = data["project-id"]

        # allowlist is set and project id is not in allowlist
        if "allowlist" in config and project_id not in config["allowlist"]:
            log.info(f"Project id {project_id} is not in allowlist.")
            return None
        # blocklist is set and project id is in blocklist
        if "blocklist" in config and project_id in config["blocklist"]:
            log.info(f"Project id {project_id} is in blocklist.")
            return None

        return __userlist_by_project(project_id=project_id)

    return None

def __userlist_by_project(project_id):
    """
    Creates a user list for given project_id. Each user comes with information about
    id, name, elixir_name, perun_id and ssh-keys

    :param project_id: openstack project id
    :return: set of user information
    """

    # For some reason I didn't understand the endpoint url differs
    # depending on the used authentication method (environment via openrc or clouds.yml).
    # The following conditional checks this and set a prefix if necessary.

    identity_prefix = ""
    if not identity.get_endpoint().endswith("v3/"):
        identity_prefix = "s3/"

    # get a list of all users, luckily also non-standard metadata ist returned when using REST-API
    _userlist = {}
    for _user in identity.get(f"{identity_prefix}users").json()["users"]:
        # id and name are always present
        _tmp = {"id": _user["id"],
                "name": _user["name"]
                }
        # elixir_name and perun_id are optional meta data
        if "elixir_name" in _user:
            _tmp["elixir_name"] = _user["elixir_name"]
        if "perun_id" in _user:
            _tmp["perun_id"] = _user["perun_id"]

        _userlist[_user["id"]] = _tmp

    # get a list of all role assignments belonging to given project id and extract all user id's
    _userset = set()
    for _role_assignment in identity.get(f"{identity_prefix}role_assignments?scope.project.id={project_id}").\
                                     json()["role_assignments"]:
        if "user" in _role_assignment: # we are only interested in users not groups or roles
            _userset.add(_role_assignment["user"]["id"])

    result = []
    for _user_id in _userset:
        _tmp = _userlist[_user_id]
        # get list of key pairs for _user_id
        _kp_list = []
        for _kp in sdk.list_keypairs({"user_id": _user_id}):
            if _kp.type == "ssh":
                _kp_list.append(_kp.public_key)
        _tmp["public_keys"] = _kp_list
        result.append(_tmp)
    return result
