#!/usr/bin/env python3
from ipaddress import IPv4Network, IPv6Network, ip_network

# 配置
NEXT_HOP = "eth0"
RES_V4 = ['0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', '224.0.0.0/4', '240.0.0.0/4', '255.255.255.255/32']
RES_V6 = ['::/128', '::1/128', 'fc00::/7', 'fe80::/10', 'ff00::/8']

def parse_file(path):
    nets = []
    try:
        with open(path, 'r') as f:
            for line in f:
                if line.startswith(('#','//')) or not line.strip(): continue
                # 兼容 List 格式
                clean = line.replace('IP-CIDR,','').replace('IP-CIDR6,','').split(',')[0].strip()
                try: nets.append(ip_network(clean))
                except: continue
    except: pass
    return nets

def subtract(roots, excludes):
    for ex in excludes:
        new_roots = []
        for r in roots:
            if r.overlaps(ex):
                if r.supernet_of(ex): new_roots.extend(list(r.address_exclude(ex)))
            else: new_roots.append(r)
        roots = new_roots
    return roots

def main():
    # 初始化
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 转换逻辑
    c4 = parse_file('china_ip.conf')
    c6 = parse_file('china_ip_ipv6.conf')
    
    out4 = subtract(v4, [ip_network(i) for i in RES_V4] + c4)
    out6 = subtract(v6, [ip_network(i) for i in RES_V6] + c6)

    # 写入文件
    with open("routes4.conf", "w") as f:
        for n in sorted(out4): f.write(f'route {n} via "{NEXT_HOP}";\n')
    with open("routes6.conf", "w") as f:
        for n in sorted(out6): f.write(f'route {n} via "{NEXT_HOP}";\n')
    
    print(f"Produced: v4={len(out4)}, v6={len(out6)}")

if __name__ == "__main__":
    main()
