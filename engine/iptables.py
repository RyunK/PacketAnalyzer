import subprocess


def add_black(ip):
    subprocess.run([
        "iptables",
        "-A", "INPUT",
        "-s", ip,
        "-j", "DROP"
    ], check=True)


def remove_black(ip):
    subprocess.run([
        "iptables",
        "-D", "INPUT",
        "-s", ip,
        "-j", "DROP"
    ], check=True)


def add_white(ip):
    subprocess.run([
        "iptables",
        "-I", "INPUT", "1",
        "-s", ip,
        "-j", "ACCEPT"
    ], check=True)


def remove_white(ip):
    subprocess.run([
        "iptables",
        "-D", "INPUT",
        "-s", ip,
        "-j", "ACCEPT"
    ], check=True)