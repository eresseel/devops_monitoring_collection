"""
Testing Grafana Configurations
"""
import os
import json
import requests
import testinfra
from pytest import mark
from requests.auth import HTTPBasicAuth

from testinfra.utils.ansible_runner import AnsibleRunner


testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('grafana')


def grafana_ip():
    host = testinfra.\
        get_host('docker://root@ubuntu-focal-grafana', sudo=True)
    grafana_address = host.\
        addr('ubuntu-focal-grafana').ipv4_addresses
    return grafana_address[0]


def grafana_get_request(url):
    request = requests.get('http://%s:3000%s' %
                           (grafana_ip(), url),
                           auth=HTTPBasicAuth(username='admin',
                                              password='admin123'))
    return request


def grafana_get_orgs():
    request = requests.get('http://%s:3000/api/orgs' %
                           (grafana_ip()),
                           auth=HTTPBasicAuth(username='admin',
                                              password='admin123'))
    return request.json()


def grafana_set_orgs(org_name):
    data = grafana_get_orgs()
    org_id = next(
                 (item["id"] for item in data if item["name"] == org_name),
                  None)

    requests.post('http://%s:3000/api/user/using/%s' %
                  (grafana_ip(), org_id),
                  auth=HTTPBasicAuth(username='admin',
                                     password='admin123'))


def test_grafana_service(host):
    grafana = host.service('grafana-server')
    assert grafana.is_running


@mark.parametrize('name, role', [(u'admin', u'Admin')])
def test_api_keys_setup(name, role):
    grafana_set_orgs("Main Org.")
    request = grafana_get_request('/api/auth/keys')
    data = json.loads(request.content)

    assert request.status_code == 200
    assert any(item['name'] == name for item in data)
    assert any(item['role'] == role for item in data)


@mark.parametrize('id', [
    (u'macropower-analytics-panel')
])
def test_plugin_setup(id):
    grafana_set_orgs("Main Org.")
    request = grafana_get_request('/api/plugins')
    data = json.loads(request.content)
    results = list(map(lambda item: item["id"], data))

    assert request.status_code == 200
    assert id in results


@mark.parametrize('name, type, access, url', [
    (u'Prometheus', u'prometheus', u'proxy', u'https://prometheus.mycorp.com')
])
def test_datasource_setup(name, type, access, url):
    grafana_set_orgs("Main Org.")
    request = grafana_get_request('/api/datasources')
    data = json.loads(request.content)

    assert request.status_code == 200
    assert any(item['name'] == name for item in data)
    assert any(item['type'] == type for item in data)
    assert any(item['access'] == access for item in data)
    assert any(item['url'] == url for item in data)


@mark.parametrize('name, login, email, is_admin', [
    (u'Bruce Wayne', u'batman', u'batman@gotham.city', True)
])
def test_user_setup(name, login, email, is_admin):
    grafana_set_orgs("Main Org.")
    request = grafana_get_request('/api/users')
    data = json.loads(request.content)
    results = [item["name"] for item in data]
    user = next(item for item in data if item["name"] == name)

    assert request.status_code == 200
    assert name in results
    assert user["login"] == login
    assert user["email"] == email
    assert user["isAdmin"] == is_admin


@mark.parametrize('name', [(u'orgtest')])
def test_organization_setup(name):
    grafana_set_orgs("Main Org.")
    request = grafana_get_request('/api/orgs/')
    data = json.loads(request.content)
    results = list(map(lambda item: item["name"], data))

    assert request.status_code == 200
    assert name in results


@mark.parametrize('name, member_name', [
    (u'grafana_working_group', u'Foo Bar')
])
def test_team_setup(name, member_name):
    grafana_set_orgs("foobar")
    request = grafana_get_request(
        f'/api/teams/search?perpage=10&page=1&query={name}')
    data = json.loads(request.content)
    id = next((
        item['id'] for item in data['teams'] if item['name'] == name), None)

    assert request.status_code == 200
    assert any(item['name'] == name for item in data['teams'])

    request = grafana_get_request(f'/api/teams/{id}/members')
    data = json.loads(request.content)
    results = list(map(lambda item: item["name"], data))

    assert request.status_code == 200
    assert member_name in results


@mark.parametrize('title', [
    (u'Jenkins')
])
def test_folder_setup(title):
    grafana_set_orgs("foobar")
    request = grafana_get_request('/api/folders')
    data = json.loads(request.content)

    assert request.status_code == 200
    assert any(item['title'] == title for item in data)


@mark.parametrize('title1, title2', [
    (u'Jenkins / Node / Resources', u'Jenkins / Node / Jobs')])
def test_dashboard_setup(title1, title2):
    grafana_set_orgs("foobar")
    request = grafana_get_request('/api/search?query=&type=dash-db')
    data = json.loads(request.content)

    assert request.status_code == 200
    assert any(item['title'] == title1 for item in data)
    assert any(item['title'] == title2 for item in data)


@mark.parametrize('name, disable_resolve_message, addresses, type, uid', [
    (u'Pipeline status mail', True, u'foobar@email.com', u'email', u'foobar')
])
def test_contact_points_setup(name, disable_resolve_message,
                              addresses, type, uid):
    grafana_set_orgs("foobar")
    request = grafana_get_request('/api/v1/provisioning/contact-points')
    data = json.loads(request.content)
    results = [item["name"] for item in data]
    contact_points = next(item for item in data if item["name"] == name)

    assert request.status_code == 200
    assert name in results
    assert contact_points["disableResolveMessage"] == disable_resolve_message
    assert contact_points["settings"]["addresses"] == addresses
    assert contact_points["type"] == type
    assert contact_points["uid"] == uid


@mark.parametrize('receiver, group_wait, group_interval', [
    ('Pipeline status mail', '30s', '5m')
])
def test_notification_policies_setup(receiver, group_wait, group_interval):
    grafana_set_orgs("foobar")
    request = grafana_get_request('/api/v1/provisioning/policies')
    data = json.loads(request.content)

    assert request.status_code == 200
    assert data["receiver"] == receiver
    assert data["group_wait"] == group_wait
    assert data["group_interval"] == group_interval
