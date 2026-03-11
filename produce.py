#!/usr/bin/env python3
import sys
from ipaddress import IPv4Network, IPv6Network, ip_network

# 配置
NEXT_HOP = "eth0"
RES_V4 = ['0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', '224.0.0.0/4', '240.0.0.0/4', '255.255.255.255/32']
RES_V6 = ['::/128', '::1/128', 'fc00::/7', 'fe80::/10', 'ff00::/8']

def parse_file(path):
    """
    通用解析器：
    1. 支持 misakaio 的纯 IP 段格式 (1.0.1.0/24)
    2. 支持 SukkaW 的 List 格式 (IP-CIDR,1.0.1.0/24)
    """
    nets = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or any(line.startswith(s) for s in ['#', '//', 'define']):
                    continue
                
                # 清洗数据：移除前缀、后缀、空格
                # 处理 'IP-CIDR,1.0.1.0/24,no-resolve' -> '1.0.1.0/24'
                # 处理 '1.0.1.0/24' -> '1.0.1.0/24'
                clean = line.replace('IP-CIDR6,', '').replace('IP-CIDR,', '').split(',')[0].strip()
                
                try:
                    nets.append(ip_network(clean))
                except ValueError:
                    continue
    except Exception as e:
        print(f"Warning: Failed to read {path}: {e}")
    return nets

def subtract(roots, excludes):
    """计算差集逻辑"""
    current_roots = roots
    for ex in excludes:
        new_roots = []
        for r in current_roots:
            if r.overlaps(ex):
                if r.supernet_of(ex):
                    new_roots.extend(list(r.address_exclude(ex)))
                elif ex.supernet_of(r):
                    continue
            else:
                new_roots.append(r)
        current_roots = new_roots
    return current_roots

def main():
    # 初始化全量空间 (IPv4 拆分为 2 个 /1 块提高计算效率)
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 解析文件
    print("Parsing input files...")
    c4 = parse_file('china_ip.conf')      # misakaio 数据
    c6 = parse_file('china_ip_ipv6.conf') # SukkaW 数据
    
    # 准备排除列表
    r4 = [ip_network(i) for i in RES_V4]
    r6 = [ip_network(i) for i in RES_V6]

    # 计算取反路由
    print("Calculating non-China IPv4 routes...")
    out4 = subtract(v4, r4 + c4)
    
    print("Calculating non-China IPv6 routes...")
    out6 = subtract(v6, r6 + c6)

    # 导出 BIRD 配置文件
    print(f"Writing results: v4={len(out4)}, v6={len(out6)}")
    with open("routes4.conf", "w") as f:
        for n in sorted(out4):
            f.write(f'route {n} via "{NEXT_HOP}";\n')

    with open("routes6.conf", "w") as f:
        for n in sorted(out6):
            f.write(f'route {n} via "{NEXT_HOP}";\n')

if __name__ == "__main__":
    main()
