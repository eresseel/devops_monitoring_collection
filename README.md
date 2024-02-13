# devops_monitoring_collection

## 1. Prepare developer environment
```bash
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r test-requirements.txt

molecule test (--all|-s <scenario name>)        // mind that there is no scenario named 'default'
```

## 2. Documentation
* [ansible_role_grafana](roles/ansible_role_grafana/README.md)
* [ansible_role_node_exporter](roles/ansible_role_node_exporter/README.md)
* [ansible_role_prometheus](roles/ansible_role_prometheus/README.md)
* [ansible_role_pve_exporter](roles/ansible_role_pve_exporter/README.md)
