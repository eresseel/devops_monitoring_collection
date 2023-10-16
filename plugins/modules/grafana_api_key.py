#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from ansible.module_utils.basic import AnsibleModule

class GrafanaAPIKeysManager:
    def __init__(self, api_url, auth, org_name):
        self.api_url = api_url
        self.auth = auth
        self.api_endpoint = f"{api_url}/api/auth/keys"
        self.org_name = org_name
        self._set_organization_as_default()

    def _get_organization_id_by_name(self):
        org_endpoint = f"{self.api_url}/api/orgs"
        response = requests.get(org_endpoint, auth=self.auth)
        response.raise_for_status()
        orgs = response.json()
        for org in orgs:
            if org.get("name") == self.org_name:
                return org["id"]
        return None

    def _set_organization_as_default(self):
        organization_id = self._get_organization_id_by_name()
        if organization_id is not None:
            endpoint = f"{self.api_url}/api/user/using/{organization_id}"
            response = requests.post(endpoint, auth=self.auth)
            response.raise_for_status()

    def get_api_keys(self):
        response = requests.get(self.api_endpoint, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def add_api_key_to_org_folder(self, name, role, seconds_to_live=None):
        payload = {
            "name": name,
            "role": role,
            "secondsToLive": seconds_to_live
        }
        response = requests.post(self.api_endpoint, auth=self.auth, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_api_key_from_org_folder(self, key_id):
        response = requests.delete(f"{self.api_endpoint}/{key_id}", auth=self.auth)
        response.raise_for_status()

def main():
    module_args = {
        "url": {"type": "str", "required": True},
        "grafana_user": {"type": "str", "required": False, "default": None},
        "grafana_password": {"type": "str", "required": False, "default": None, "no_log": True},
        "grafana_api_key": {"type": "str", "required": False, "default": None, "no_log": True},
        "name": {"type": "str", "required": True},
        "role": {"type": "str", "required": True},
        "seconds_to_live": {"type": "int", "required": False, "default": None},
        "org_name": {"type": "str", "required": True},
        "state": {"type": "str", "required": False, "default": "present", "choices": ["present", "absent"]},
    }

    module = AnsibleModule(argument_spec=module_args)

    url = module.params["url"]
    grafana_user = module.params["grafana_user"]
    grafana_password = module.params["grafana_password"]
    grafana_api_key = module.params["grafana_api_key"]
    name = module.params["name"]
    role = module.params["role"]
    seconds_to_live = module.params["seconds_to_live"]
    org_name = module.params["org_name"]
    state = module.params["state"]

    if grafana_api_key:
        auth = (grafana_api_key, "")
    elif grafana_user and grafana_password:
        auth = (grafana_user, grafana_password)
    else:
        module.fail_json(msg="Either grafana_api_key or both grafana_user and grafana_password must be provided")

    api_keys_manager = GrafanaAPIKeysManager(url, auth, org_name)

    try:
        api_keys = api_keys_manager.get_api_keys()

        if state == "present":
            if not api_keys or name not in [api_key["name"] for api_key in api_keys]:
                response = api_keys_manager.add_api_key_to_org_folder(name, role, seconds_to_live)
                module.exit_json(changed=True, msg="API keys retrieved and added", api_keys=response)
            else:
                module.exit_json(changed=False, msg="API keys already exist")

        elif state == "absent":
            if api_keys:
                key_to_delete = next((api_key for api_key in api_keys if api_key["name"] == name), None)

                if key_to_delete:
                    api_keys_manager.delete_api_key_from_org_folder(key_to_delete['id'])
                    module.exit_json(changed=True, msg="API key deleted")
                else:
                    module.exit_json(changed=False, msg="API key does not exist")
            else:
                module.exit_json(changed=False, msg="No API keys exist")

        else:
            module.fail_json(msg=f"Invalid state: {state}")

    except requests.exceptions.RequestException as err:
        module.fail_json(msg=f"Failed to retrieve or delete API keys: {err}")

if __name__ == '__main__':
    main()
