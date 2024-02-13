"""
Testing pve-exporter
"""

def test_passwd_file(host):
    passwd = host.file("/etc/passwd")
    assert passwd.contains("prometheus")
    assert passwd.mode == 0o644


def test_exists_file(host):
    pve_exporter = host.file("/etc/systemd/system/prometheus-pve-exporter.service")
    assert pve_exporter.exists


def test_port_open(host):
    assert host.socket("tcp://0.0.0.0:9221").is_listening
