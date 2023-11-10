"""
Testing prometheus Configurations
"""
import os
import time
import json
import requests
import testinfra

from pytest import mark
from testinfra.utils.ansible_runner import AnsibleRunner


testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('prometheus')


def prometheus_ip():
    host = testinfra.\
        get_host('docker://root@ubuntu-focal-prometheus', sudo=True)
    prometheus_address = host.\
        addr('ubuntu-focal-prometheus').ipv4_addresses
    return prometheus_address[0]


def prometheus_get_request(url):
    max_retries = 10
    retries = 0
    request = None

    while retries < max_retries and (request is None or not request.content):
        request = requests.get('http://%s:9090%s' % (prometheus_ip(), url))
        retries += 1
        time.sleep(5)

    return request


def test_passwd_file(host):
    passwd = host.file("/etc/passwd")
    assert passwd.contains("prometheus")
    assert passwd.mode == 0o644


def test_process(host):
    args = "/opt/prometheus/current/prometheus" \
         + " --config.file=/etc/prometheus/prometheus.yml" \
         + " --storage.tsdb.path=/var/lib/prometheus" \
         + " --web.listen-address=:9090" \
         + " --web.external-url=http://localhost:9090/" \
         + " --web.console.templates=/etc/prometheus/consoles" \
         + " --web.console.libraries=/etc/prometheus/console_libraries" \
         + " --web.enable-lifecycle"
    process = host.process.get(args=args)
    assert process.user == "root"
    assert process.args == args


def test_healthy():
    request = prometheus_get_request('/-/healthy')
    data = request.content.decode('utf-8').rstrip('\n')

    assert request.status_code == 200
    assert "Prometheus Server is Healthy." == data


@mark.parametrize('job, address, scrapeUrl', [
    (u'prometheus', u'localhost:9090', u'http://localhost:9090/metrics')
])
def test_get_target(job, address, scrapeUrl):
    request = prometheus_get_request('/api/v1/targets')
    data = json.loads(request.content).get('data', {})
    active_targets = data.get('activeTargets', [])

    assert request.status_code == 200
    assert any(item['discoveredLabels']['job'] ==
           job for item in active_targets)
    assert any(item['discoveredLabels']['__address__'] ==
           address for item in active_targets)
    assert any(item['scrapeUrl'] == scrapeUrl for item in active_targets)


@mark.parametrize('name, file, rule_name, rule_query', [
    (u'Deployment', u'/etc/prometheus/rules/alert.rules',
     u'Deployment at 0 Replicas',
     u'sum by (deployment, namespace) \
(kube_deployment_status_replicas{pod_template_hash=\"\"}) < 1')
])
def test_get_rules(name, file, rule_name, rule_query):
    request = prometheus_get_request('/api/v1/rules')
    data = json.loads(request.content).get('data', {})
    groups = data.get('groups', [])

    assert request.status_code == 200
    assert any(item['name'] == name for item in groups)
    assert any(item['file'] == file for item in groups)
    assert any(rule['name'] ==
           rule_name for item in groups for rule in item['rules'])
    assert any(rule['query'] ==
           rule_query for item in
           groups for rule in item['rules'])


@mark.parametrize('name, instance, job', [
    (u'up', u'localhost:9090', u'prometheus')
])
def test_get_query(name, instance, job):
    request = prometheus_get_request('/api/v1/query?query=up')
    data = json.loads(request.content).get('data', {})
    result = data.get('result', [])

    assert request.status_code == 200
    assert any(item['metric']['__name__'] == name for item in result)
    assert any(item['metric']['instance'] == instance for item in result)
    assert any(item['metric']['job'] == job for item in result)
