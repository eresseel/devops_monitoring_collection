# ansible_role_prometheus
An Ansible role that installs Prometheus Monitoring server on Ubuntu-based machines with systemd.

## 1. Requirements
All needed packages will be installed with this role. Minimal Ansible version - 2.0.

## 2. Role Variables
Available main variables are listed below, along with default values:
```yaml
prometheus_is_install: false
prometheus_version: 2.47.2
prometheus_release_name: "prometheus-{{ prometheus_version }}.linux-amd64"
prometheus_gomaxprocs: "{{ ansible_processor_vcpus|default(ansible_processor_count) }}"

prometheus_user: prometheus
prometheus_group: prometheus

prometheus_global_scrape_interval: 15s
prometheus_global_evaluation_interval: 15s
prometheus_global_scrape_timeout: 10s

prometheus_root_dir: /opt/prometheus
prometheus_config_dir: /etc/prometheus
prometheus_log_dir: /var/log/prometheus
prometheus_db_dir: /var/lib/prometheus
prometheus_dist_dir: "{{ prometheus_root_dir }}/dist"
prometheus_bin_dir: "{{ prometheus_root_dir }}/current"
prometheus_rules_dir: "{{ prometheus_config_dir }}/rules"
prometheus_file_sd_config_dir: "{{ prometheus_config_dir }}/tgroups"

prometheus_rules_src_dir: "{{ playbook_dir }}/files/rules"
prometheus_config_parts_src_dir: "{{ playbook_dir }}/files/config_parts"
prometheus_tgroups_src_dir: "{{ playbook_dir }}/files/tgroups"

prometheus_rules_files: []

prometheus_web_listen_address: ":9090"
prometheus_web_external_url: 'http://localhost:9090/'

prometheus_config_flags:
  'config.file': '{{ prometheus_config_dir }}/prometheus.yml'
  'storage.tsdb.path': '{{ prometheus_db_dir }}'
  'web.listen-address': '{{ prometheus_web_listen_address }}'
  'web.external-url': '{{ prometheus_web_external_url }}'
  'web.console.templates': '/etc/prometheus/consoles'
  'web.console.libraries': '/etc/prometheus/console_libraries'

prometheus_config_flags_extra: {}
prometheus_pam_domain: "prometheus"
prometheus_pam_nofile_value: "1024"
```

## 3. Dependencies
This role doesn't have dependencies.

## 4. Example Playbook
```yaml
- hosts: monitoring
  roles:
    - { role: UnderGreen.prometheus }
```
You should create another config parts of main file inside `{{ playbook_dir }}/files/config_parts`.
I use Ansible [assembly](http://docs.ansible.com/ansible/assemble_module.html) and config parts should have alphabethical order. For example `2-static_sd.yml`:
```yaml
scrape_configs:
  - job_name: "files_sd"
    scrape_interval: 15s
    file_sd_configs:
      - files:
        - '/etc/prometheus/tgroups/*.json'
        - '/etc/prometheus/tgroups/*.yml'
        - '/etc/prometheus/tgroups/*.yaml'
        refresh_interval: '5m'
```

Example 03-alertmanager.yml:
```yaml
alerting:
  alertmanagers:
  - scheme: http
    static_configs:
      - targets:
        - '127.0.0.1:9093'
```
