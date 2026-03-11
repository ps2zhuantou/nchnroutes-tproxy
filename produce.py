#!/usr/bin/env python3
import sys
import os
from ipaddress import IPv4Network, IPv6Network, ip_network

# --- 配置 ---
NEXT_HOP = "eth0"
RES_V4 = ['0.0.0.0/8', '10.0.0.0/8', '20.254.0.0/16', '20.253.0.0/16', '100.64.0.0/10', '127.0.0.0/8', '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', '224.0.0.0/4', '240.0.0.0/4', '255.255.255.255/32']
RES_V6 = ['::/128', '::1/128', 'fc00::/7', 'fe80::/10', 'ff00::/8']

def parse_file(path):
    nets = []
    if not os.path.exists(path):
        print(f"Error: 文件 {path} 不存在")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(('#','//',';','USER-AGENT','payload:')):
                    continue
                # 兼容清洗：处理 IP-CIDR, 前缀及纯文本格式
                clean = line.replace('IP-CIDR,','').replace('IP-CIDR6,','').replace('define ','')
                clean = clean.split(',')[0].split(';')[0].split()[0].strip()
                try:
                    nets.append(ip_network(clean))
                except:
                    continue
        return nets
    except:
        return []

def subtract(roots, excludes):
    for ex in excludes:
        new_roots = []
        for r in roots:
            if r.overlaps(ex):
                if r.supernet_of(ex):
                    new_roots.extend(list(r.address_exclude(ex)))
                else:
                    continue # ex 覆盖了 r
            else:
                new_roots.append(r)
        roots = new_roots
    return roots

def main():
    # 1. 初始化
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 2. 解析 (文件名需与 Makefile 下载的文件名一致)
    c4 = parse_file('china_ip.conf')
    c6 = parse_file('china_ip_ipv6.conf')
    
    # 【核心修复】安全阀门：如果解析出的条目数量太少，说明下载失败或格式有误
    # 绝不执行后续操作，保护现有文件不被 1 字节文件覆盖
    if len(c4) < 1000 or len(c6) < 10:
        print(f"致命错误: 解析到的 IP 数量不足 (v4:{len(c4)}, v6:{len(c6)})，停止运行。")
        sys.exit(1)

    # 3. 计算补集
    print(f"正在计算补集... IPv4 排除项: {len(c4)}")
    out4 = subtract(v4, [ip_network(i) for i in RES_V4] + c4)
    out6 = subtract(v6, [ip_network(i) for i in RES_V6] + c6)

    # 4. 写入前二次检查
    if not out4 or not out6:
        print("错误: 计算生成的路由列表为空，取消写入。")
        sys.exit(1)

    # 5. 写入文件
    with open("routes4.conf", "w", encoding='utf-8') as f:
        for n in sorted(out4):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
            
    with open("routes6.conf", "w", encoding='utf-8') as f:
        for n in sorted(out6):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
    
    print(f"成功！v4={len(out4)} 条, v6={len(out6)} 条")

if __name__ == "__main__":
    main()
