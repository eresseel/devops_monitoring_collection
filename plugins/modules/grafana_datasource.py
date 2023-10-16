#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from ansible.module_utils.basic import AnsibleModule

class GrafanaDatasourceManager:
    def __init__(self, api_url, auth, org_id):
        self.api_url = api_url
        self.auth = auth
        self.api_endpoint = f"{api_url}/api/datasources"
        self._set_organization_as_default(org_id)

    def _set_organization_as_default(self, org_id):
        endpoint = f"{self.api_url}/api/user/using/{org_id}"
        response = requests.post(endpoint, auth=self.auth)
        response.raise_for_status()

    def get_datasource(self):
        response = requests.get(self.api_endpoint, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def add_datasource_to_org_folder(self, org_id, name, ds_type, access, ds_url,
            password=None, user=None, database=None, basic_auth_user=None,
            basic_auth_password=None, is_default=False, tls_skip_verify=None):
        basic_auth = bool(basic_auth_user and basic_auth_password)
        json_data = {}

        if tls_skip_verify:
            json_data["tlsSkipVerify"] = True

        payload = {
            "orgId": org_id,
            "name": name,
            "type": ds_type,
            "access": access,
            "url": ds_url,
            "password": password,
            "user": user,
            "database": database,
            "basicAuth": basic_auth,
            "basicAuthUser": basic_auth_user,
            "basicAuthPassword": basic_auth_password,
            "isDefault": is_default,
            "jsonData": json_data
        }

        response = requests.post(self.api_endpoint, auth=self.auth, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_datasource_from_org_folder(self, key_id):
        response = requests.delete(f"{self.api_endpoint}/{key_id}", auth=self.auth)
        response.raise_for_status()

def main():
    module_args = {
        "url": {"type": "str", "required": True},
        "grafana_user": {"type": "str", "required": False, "default": None},
        "grafana_password": {"type": "str", "required": False, "default": None, "no_log": True},
        "grafana_api_key": {"type": "str", "required": False, "default": None, "no_log": True},
        "name": {"type": "str", "required": True},
        "ds_url": {"type": "str", "required": True},
        "ds_type": {"type": "str", "required": True},
        "access": {"type": "str", "required": False},
        "is_default": {"type": "bool", "required": False},
        "basic_auth_user": {"type": "str", "required": False},
        "basic_auth_password": {"type": "str", "required": False, "no_log": True},
        "database": {"type": "str", "required": False},
        "user": {"type": "str", "required": False},
        "password": {"type": "str", "required": False, "no_log": True},
        "tls_skip_verify": {"type": "bool", "required": False},
        "org_id": {"type": "int", "required": True},
        "state": {"type": "str", "required": True, "choices": ["present", "absent"]},
    }

    module = AnsibleModule(argument_spec=module_args)

    url = module.params["url"]
    grafana_user = module.params["grafana_user"]
    grafana_password = module.params["grafana_password"]
    grafana_api_key = module.params["grafana_api_key"]
    name = module.params["name"]
    ds_url = module.params["ds_url"]
    ds_type = module.params["ds_type"]
    access = module.params["access"]
    is_default = module.params["is_default"]
    basic_auth_user = module.params["basic_auth_user"]
    basic_auth_password = module.params["basic_auth_password"]
    database = module.params["database"]
    user = module.params["user"]
    password = module.params["password"]
    tls_skip_verify = module.params["tls_skip_verify"]
    org_id = module.params["org_id"]
    state = module.params["state"]

    if grafana_api_key:
        auth = (grafana_api_key, "")
    elif grafana_user and grafana_password:
        auth = (grafana_user, grafana_password)
    else:
        module.fail_json(msg="Either grafana_api_key or both grafana_user and grafana_password must be provided")

    datasource_manager = GrafanaDatasourceManager(url, auth, org_id)

    try:
        datasources = datasource_manager.get_datasource()

        if state == "present":
            if not datasources or name not in [ds["name"] for ds in datasources]:
                response = datasource_manager.add_datasource_to_org_folder(
                    org_id, name, ds_type, access, ds_url, password, user, database, basic_auth_user, basic_auth_password, is_default, tls_skip_verify)
                module.exit_json(changed=True, msg="Datasources retrieved and added", datasources=response)
            else:
                module.exit_json(changed=False, msg="Datasources already exist")

        elif state == "absent":
            if datasources:
                key_to_delete = next((api_key for api_key in datasources if api_key["name"] == name), None)

                if key_to_delete:
                    datasource_manager.delete_datasource_from_org_folder(key_to_delete['id'])
                    module.exit_json(changed=True, msg="Datasource deleted")
                else:
                    module.exit_json(changed=False, msg="Datasource does not exist")
            else:
                module.exit_json(changed=False, msg="No Datasources exist")

        else:
            module.fail_json(msg=f"Invalid state: {state}")

    except requests.exceptions.RequestException as err:
        module.fail_json(msg=f"Failed to retrieve or delete Datasources: {err}")

if __name__ == '__main__':
    main()
