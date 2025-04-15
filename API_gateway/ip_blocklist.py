
blocked_ips = set()

def is_blocked(ip):
    return ip in blocked_ips

def block_ip(ip):
    blocked_ips.add(ip)
