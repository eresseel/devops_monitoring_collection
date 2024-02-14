# ansible_grafana_role

## 1. Role Variables
### 1.1. defaults/main.yml

```yaml
grafana_version: grafana=10.0.1
grafana_apt_key: 'https://apt.grafana.com/gpg.key'
grafana_repository: 'deb https://apt.grafana.com stable main'
grafana_retries: 60
grafana_delay: 30
grafana_is_install: false
grafana_is_write_api_keys_in_file: false
grafana_instance: "{{ ansible_fqdn | default(ansible_host) | default(inventory_hostname) }}"
grafana_logs_dir: '/var/log/grafana'
grafana_data_dir: '/var/lib/grafana'
grafana_address: '0.0.0.0'
grafana_port: 3000
grafana_url: "http://{{ grafana_address }}:{{ grafana_port }}"
grafana_api_url: "{{ grafana_url }}"
grafana_domain: "{{ ansible_fqdn | default(ansible_host) | default('localhost') }}"
grafana_server:
  protocol: http
  enforce_domain: false
  socket: ''
  cert_key: ''
  cert_file: ''
  enable_gzip: false
  static_root_path: public
  router_logging: false
  serve_from_sub_path: false
grafana_security:
  admin_user: admin
  admin_password: password
grafana_database:
  type: sqlite3
grafana_remote_cache: {}
grafana_welcome_email_on_sign_up: false
grafana_users:
  allow_sign_up: false
  auto_assign_org_role: Viewer
  default_theme: dark
grafana_auth: {}
grafana_ldap: {}
grafana_session: {}
grafana_analytics: {}
grafana_smtp: {}
grafana_alerting:
  execute_alerts: true
grafana_log: []
grafana_metrics: {}
grafana_tracing: {}
grafana_snapshots: {}
grafana_image_storage: {}
grafana_plugins: []
grafana_dashboards: []
grafana_alert_notifications: []
grafana_datasources: []
grafana_api_keys: []
grafana_api_keys_dir: "{{ lookup('env', 'HOME') }}/grafana/keys"
grafana_panels: {}
grafana_folders: []
grafana_user_list: []
grafana_organization: []
grafana_teams: []
contact_points: []
notification_policies: []
```

###  1.2. playbook configuration
```yaml
---
grafana_version: grafana=10.0.1
grafana_apt_key: 'https://apt.grafana.com/gpg.key'
grafana_repository: 'deb https://apt.grafana.com stable main'
grafana_retries: 60
grafana_delay: 30
grafana_is_install: true
grafana_is_write_api_keys_in_file: false

grafana_instance: "{{ ansible_fqdn | default(ansible_host) | default(inventory_hostname) }}"
grafana_logs_dir: '/var/log/grafana'
grafana_data_dir: '/var/lib/grafana'

grafana_address: '0.0.0.0'
grafana_port: 3000
grafana_url: "http://{{ grafana_address }}:{{ grafana_port }}"
grafana_api_url: "{{ grafana_url }}"
grafana_domain: "{{ ansible_fqdn | default(ansible_host) | default('localhost') }}"

# Additional options for grafana 'server' section
# This section WILL omit options for: http_addr, http_port, domain, and root_url, as those settings are set by variables listed before
grafana_server:
  protocol: http
  enforce_domain: false
  socket: ''
  cert_key: ''
  cert_file: ''
  enable_gzip: false
  static_root_path: public
  router_logging: false
  serve_from_sub_path: false

# Variables correspond to ones in grafana.ini configuration file
# Security
grafana_security:
  admin_user: admin
  admin_password: password
  secret_key: ''
  login_remember_days: 7
  cookie_username: grafana_user
  cookie_remember_name: grafana_remember
  disable_gravatar: true
  data_source_proxy_whitelist:

# Database setup
grafana_database:
  type: sqlite3
  host: 127.0.0.1:3306
  name: grafana
  user: root
  password: ''
  url: ''
  ssl_mode: disable
  path: grafana.db
  max_idle_conn: 2
  max_open_conn: ''
  log_queries: ''

# Remote cache
grafana_remote_cache: {}

# User management and registration
grafana_welcome_email_on_sign_up: false
grafana_users:
  allow_sign_up: false
  allow_org_create: true
  auto_assign_org: true
  auto_assign_org_role: Viewer
  login_hint: 'email or username'
  default_theme: dark
  external_manage_link_url: ''
  external_manage_link_name: ''
  external_manage_info: ''

# grafana authentication mechanisms
grafana_auth:
  disable_login_form: false
  oauth_auto_login: false
  disable_signout_menu: false
  signout_redirect_url: ''
  anonymous:
    org_name: 'Main Organization'
    org_role: Viewer
  ldap:
    config_file: '/etc/grafana/ldap.toml'
    allow_sign_up: false
  basic:
    enabled: true

grafana_ldap:
  verbose_logging: false
  servers:
    host: 127.0.0.1
    port: 389 # 636 for SSL
    use_ssl: false
    start_tls: false
    ssl_skip_verify: false
    root_ca_cert: /path/to/certificate.crt
    bind_dn: 'cn=admin,dc=grafana,dc=org'
    bind_password: grafana
    search_filter: '(cn=%s)' # '(sAMAccountName=%s)' on AD
    search_base_dns:
      - 'dc=grafana,dc=org'
    group_search_filter: '(&(objectClass=posixGroup)(memberUid=%s))'
    group_search_base_dns:
      - 'ou=groups,dc=grafana,dc=org'
    attributes:
      name: givenName
      surname: sn
      username: sAMAccountName
      member_of: memberOf
      email: mail
  group_mappings:
    - name: Main Org.
      id: 1
      groups:
        - group_dn: 'cn=admins,ou=groups,dc=grafana,dc=org'
          org_role: Admin
        - group_dn: 'cn=editors,ou=groups,dc=grafana,dc=org'
          org_role: Editor
        - group_dn: '*'
          org_role: Viewer
    - name: Alternative Org
      id: 2
      groups:
        - group_dn: 'cn=alternative_admins,ou=groups,dc=grafana,dc=org'
          org_role: Admin

grafana_session:
  provider: file
  provider_config: 'sessions'

grafana_analytics:
  reporting_enabled: true
  google_analytics_ua_id: ''

# Set this for mail notifications
grafana_smtp:
  host:
  user:
  password:
  from_address:

# Enable grafana alerting mechanism
grafana_alerting:
  execute_alerts: true
  error_or_timeout: 'alerting'
  nodata_or_nullvalues: 'no_data'
  concurrent_render_limit: 5

# Grafana logging configuration
grafana_log:
  mode: 'console file'
  level: info

# Internal grafana metrics system
grafana_metrics:
  interval_seconds: 10
  graphite:
    address: 'localhost:2003'
    prefix: 'prod.grafana.%(instance_name)s'

# Distributed tracing options
grafana_tracing:
  address: 'localhost:6831'
  always_included_tag: 'tag1:value1,tag2:value2'
  sampler_type: const
  sampler_param: 1

grafana_snapshots:
  external_enabled: true
  external_snapshot_url: 'https://snapshots-origin.raintank.io'
  external_snapshot_name: 'Publish to snapshot.raintank.io'
  snapshot_remove_expired: true
  snapshot_TTL_days: 90

# External image store
grafana_image_storage:
  provider: gcs
  key_file:
  bucket:
  path:


#######
# Plugins from https://grafana.com/plugins
grafana_plugins:
  - name: 'macropower-analytics-panel'
    version: '2.1.0'
  - name: 'blackcowmoo-googleanalytics-datasource'
    version: '0.2.0'

# Dashboards from https://grafana.com/dashboards
grafana_dashboards:
  - dashboard_id: '6098'
    dashbord_revision: 1
    commit_message: 'Zabbix'
    folder: 'General'
    org_name: 'Main Org.'
    datasource_name: 'Prometheus'
  - commit_message: 'Jenkins'
    folder: 'Jenkins'
    folder_path: 'files/jenkins'
    org_name: 'Main Org.'
    file: 'jenkins.json'
    datasource_name:
      - name: 'DS_PROMETHEUS'
      - name: 'TEMPO'

# Alert notification channels to configure
grafana_alert_notifications:
  - name: 'Email Alert'
    type: 'email'
    uid: channel1
    is_default: true
    settings:
      addresses: 'example@example.com'

# Datasources to configure
grafana_datasources:
  - name: 'Prometheus'
    type: 'prometheus'
    access: 'proxy'
    url: 'https://prometheus.mycorp.com'
    is_default: true
    tls_skip_verify: true
    org_name: 'Main Org.'

# API keys to configure
grafana_api_keys:
- name: 'admin'
  role: 'Admin'
  org_name: 'Main Org.'
- name: 'foobar'
  role: 'Viewer'
  org_name: 'Main Org.'
  seconds_to_live: 86400
- name: 'dummy'
  role: 'Editor'
  org_name: 'Main Org.'
  seconds_to_live: 86400

# The location where the keys should be stored.
grafana_api_keys_dir: "{{ lookup('env', 'HOME') }}/grafana/keys"

# Panels configurations
grafana_panels:
  disable_sanitize_html: false
  enable_alpha: false

grafana_folders:
  - title: 'Jenkins'
    org_name: 'Main Org.'
  - title: 'grafana_working_group'
    org_name: 'foobar'
grafana_user_list:
  - name: 'Bruce Wayne'
    email: 'batman@gotham.city'
    login: 'batman'
    password: 'robin'
    is_admin: true
  - name: 'Foo Bar'
    email: 'foo@gotham.city'
    login: 'foo'
    password: 'foobar'
    is_admin: false
  - name: 'Jenkins'
    email: 'jenkins@gotham.city'
    login: 'jenkins'
    password: 'jenkins'
    is_admin: false
grafana_organization:
  - name: 'orgtest'
  - name: 'foobar'
grafana_teams:
  - name: 'grafana_working_group'
    email: 'foo.bar@example.com'
    org_name: 'Main Org.'
    members:
      - batman@gotham.city
      - foo@gotham.city
  - name: 'jenkins'
    org_name: 'Main Org.'
    email: 'foo.bar@example.com'
contact_points:
  - name: 'Pipeline status mail'
    disableResolveMessage: true
    org_name: 'foobar'
    settings:
      addresses: 'foobar@email.com'
    type: 'email'
    uid: 'foobar'
  - name: 'Dummy'
    disableResolveMessage: true
    org_name: 'Main Org.'
    settings:
      addresses: 'dummy@email.com'
    type: 'email'
    uid: 'dummy'
notification_policies:
  - receiver: 'Pipeline status mail'
    org_name: 'foobar'
    group_wait: '30s'
    group_interval: '5m'
  - receiver: 'Dummy'
    org_name: 'Main Org.'
    group_wait: '30s'
    group_interval: '5m'
```
