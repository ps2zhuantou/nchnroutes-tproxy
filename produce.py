#!/usr/bin/env python3
import sys
import os
from ipaddress import IPv4Network, IPv6Network, ip_network

# 配置
NEXT_HOP = "eth0"
RES_V4 = ['0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', '224.0.0.0/4', '240.0.0.0/4', '255.255.255.255/32']
RES_V6 = ['::/128', '::1/128', 'fc00::/7', 'fe80::/10', 'ff00::/8']

def parse_file(path):
    nets = []
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(('#','//',';','USER-AGENT','payload:')) or not line:
                    continue
                # 核心兼容逻辑：清洗 SukkaW 的 IP-CIDR, 前缀和 yfgao 的纯文本格式
                clean = line.replace('IP-CIDR,','').replace('IP-CIDR6,','').replace('define ','')
                # 提取第一个逗号或分号前的内容
                clean = clean.split(',')[0].split(';')[0].strip()
                try:
                    nets.append(ip_network(clean))
                except:
                    continue
    except:
        pass
    return nets

def subtract(roots, excludes):
    """
    修正后的差集计算：确保所有重叠情况都被处理
    """
    for ex in excludes:
        new_roots = []
        for r in roots:
            if r.overlaps(ex):
                # 情况 A：当前块 r 包含排除块 ex -> 拆分 r 并保留剩余部分
                if r.supernet_of(ex):
                    new_roots.extend(list(r.address_exclude(ex)))
                # 情况 B：排除块 ex 包含或等于当前块 r -> 彻底丢弃 r (即不加到 new_roots)
                else:
                    continue
            else:
                # 情况 C：完全没重叠 -> 原样保留
                new_roots.append(r)
        roots = new_roots
    return roots

def main():
    # 1. 初始化 (IPv4 分段初始化可提升计算性能)
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 2. 解析 (文件名对应 Makefile 中的 -o 参数)
    c4 = parse_file('china_ip.conf')
    c6 = parse_file('china_ip_ipv6.conf')
    
    # 安全校验：如果 GitHub Action 下载失败得到空文件，直接报错退出防止覆盖旧路由
    if len(c4) < 100:
        print("Error: IPv4 source list is too short or empty.")
        sys.exit(1)

    # 3. 转换逻辑
    print(f"Processing: v4_excludes={len(c4)}, v6_excludes={len(c6)}")
    
    out4 = subtract(v4, [ip_network(i) for i in RES_V4] + c4)
    out6 = subtract(v6, [ip_network(i) for i in RES_V6] + c6)

    # 4. 写入文件
    with open("routes4.conf", "w", encoding='utf-8') as f:
        for n in sorted(out4):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
            
    with open("routes6.conf", "w", encoding='utf-8') as f:
        for n in sorted(out6):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
    
    print(f"Produced: v4={len(out4)}, v6={len(out6)}")

if __name__ == "__main__":
    main()
