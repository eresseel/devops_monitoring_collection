"""
Testing node-exporter Configurations
"""
import os
import requests
import testinfra

from testinfra.utils.ansible_runner import AnsibleRunner


testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('node-exporter')


def docker_ip(host_name):
    host = testinfra.\
        get_host(f'docker://root@{host_name}', sudo=True)
    ubuntu_address = host.\
        addr(host_name).ipv4_addresses
    return ubuntu_address[0]


def test_passwd_file(host):
    passwd = host.file("/etc/passwd")
    assert passwd.contains("prometheus")
    assert passwd.mode == 0o644


def test_process(host):
    args = "/opt/prometheus/exporters/node_exporter_current/node_exporter" \
        + " --web.listen-address=0.0.0.0:9100 --log.level=info"
    process = host.process.get(args=args)
    assert process.user == "root"
    assert process.args == args


def test_url_output():
    hostnames = ["ubuntu-focal-node-exporter", "debian-bullseye-node-exporter",
                 "redhat-8-node-exporter", "alpine-3-18-node-exporter"]
    expected_text = "process_open_fds"

    for hostname in hostnames:
        url = "http://%s:9100/metrics" % docker_ip(hostname)

        response = requests.get(url)
        assert response.status_code == 200
        assert expected_text in response.text
