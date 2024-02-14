# ansible_role_pve_exporter
An Ansible role that installs Prometheus Monitoring server on Ubuntu-based machines with systemd.

## 1. Requirements
All needed packages will be installed with this role. Minimal Ansible version - 2.0.

## 2. Role Variables
Available main variables are listed below, along with default values:
```yaml
proxmox_is_enterprise: false
pve_exporter_is_install: true
prometheus_pve_exporter_version: 3.2.1

prometheus_pve_exporter_user: prometheus
prometheus_pve_exporter_group: prometheus

prometheus_pve_exporter_root_dir: /opt/prometheus-pve-exporter
prometheus_pve_exporter_config_dir: /etc/prometheus

pve_exporter_config:
  user: root@pve
  password: "root123"
  verify_ssl: false
```

## 3. Dependencies
This role doesn't have dependencies.
