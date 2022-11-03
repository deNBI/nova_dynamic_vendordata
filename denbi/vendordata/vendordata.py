from flask import Flask, request

from denbi.vendordata import identity,sdk

app = Flask(__name__)


@app.post("/")
def vendordata():

    data = request.get_json()


    users = identity.get("v3/users")

    if "project-id" in data:
        id = data["project-id"]
        # check for blacklisted project
        return __userlist_by_project(project_id=id)


def __userlist_by_project(project_id):
    """
    Creates an userlist for given project_id. Each user comes with information about

    :param project_id: openstack project id
    :return: set of user information
    """

    # get a list of all users, luckily also non-standard metadata ist returned when using REST-API
    _userlist = dict()
    for _user in identity.get("v3/users").json()["users"]:
        # id and name are always present
        _tmp = {"id" : _user["id"],
                "name" :  _user["name"]
                }
        # elixir_name and perun_id are optional meta data
        if "elixir_name" in _user:
            _tmp["elixir_name"] = _user["elixir_name"]
        if "perun_id" in _user:
            _tmp["perun_id"] = _user["perun_id"]

        _userlist[_user["id"]] = _tmp

    # get a list of all role assignments belonging to given project id and extract all user id's
    _userset = set()
    for _role_assignment in identity.get(f"v3/role_assignments?scope.project.id={project_id}").json()["role_assignments"]:
        _userset.add(_role_assignment["user"]["id"])

    result = list()
    for _user_id in _userset:
        _tmp = _userlist[_user_id]
        # get list of key pairs for _user_id
        _kp_list = list()
        sdk.list_users
        for _kp in sdk.list_keypairs({"user_id": _user_id}):
            if _kp.type == "ssh":
                _kp_list.append(_kp.public_key)
        _tmp["public_keys"] = _kp_list
        result.append(_tmp)
    return result
