#!/usr/bin/env python3
import sys
import os
from ipaddress import IPv4Network, IPv6Network, ip_network

# --- 配置区 ---
NEXT_HOP = "eth0"
# 保留地址列表 (RFC私有地址及保留地址)
RES_V4 = [
    '0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', 
    '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', 
    '198.18.0.0/15', '198.51.100.0/24', '203.0.113.0/24',
    '224.0.0.0/4', '240.0.0.0/4', '255.255.255.255/32'
]
RES_V6 = [
    '::/128', '::1/128', 'fc00::/7', 'fe80::/10', 'ff00::/8'
]

def parse_file(path):
    """
    高度兼容解析器：
    支持格式:
    1. IP-CIDR,1.0.1.0/24,no-resolve (SukkaW)
    2. 1.0.1.0/24 (yfgao / txt)
    3. define 1.0.1.0/24 (其他格式)
    """
    nets = []
    if not os.path.exists(path):
        print(f"警告: 找不到文件 {path}")
        return []

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 安全校验：防止下载到空文件或 404 导致全量路由泄露
    if len(lines) < 100:
        print(f"致命错误: {path} 数据量异常 ({len(lines)}行)，下载可能已失败。脚本停止。")
        sys.exit(1)

    for line in lines:
        line = line.strip()
        # 过滤注释、空行、User-Agent等头信息
        if not line or any(line.startswith(s) for s in ['#', '//', 'USER-AGENT', 'payload:', ';']):
            continue
        
        # 清洗逻辑：
        # 1. 移除常见前缀
        clean = line.replace('IP-CIDR,', '').replace('IP-CIDR6,', '').replace('define ', '')
        # 2. 移除后缀（如 ,no-resolve 或分号注释）
        clean = clean.split(',')[0].split(';')[0].strip()
        
        try:
            nets.append(ip_network(clean))
        except ValueError:
            continue
    return nets

def subtract(roots, excludes):
    """高效差集算法"""
    for ex in excludes:
        new_roots = []
        for r in roots:
            if r.overlaps(ex):
                if r.supernet_of(ex):
                    # 只有父网段包含子网段时才进行拆分
                    new_roots.extend(list(r.address_exclude(ex)))
                # 如果 ex 包含 r，则直接丢弃 r，不加入 new_roots
            else:
                new_roots.append(r)
        roots = new_roots
    return roots

def main():
    # 1. 初始化全量空间 (IPv4 分两段 0.0.0.0/1 和 128.0.0.0/1 提高计算速度)
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 2. 解析文件
    print("正在解析中国 IP 数据源...")
    c4 = parse_file('china_ip.conf')
    c6 = parse_file('china_ip_ipv6.conf')
    
    # 3. 计算补集
    print(f"正在计算取反路由... (已导入 v4:{len(c4)}, v6:{len(c6)})")
    
    # 合并保留地址和中国地址进行剔除
    excludes_v4 = [ip_network(i) for i in RES_V4] + c4
    excludes_v6 = [ip_network(i) for i in RES_V6] + c6
    
    out4 = subtract(v4, excludes_v4)
    out6 = subtract(v6, excludes_v6)

    # 4. 写入 BIRD 格式文件
    with open("routes4.conf", "w", encoding='utf-8') as f:
        for n in sorted(out4):
            f.write(f'route {n} via "{NEXT_HOP}";\n')

    with open("routes6.conf", "w", encoding='utf-8') as f:
        for n in sorted(out6):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
    
    print(f"成功完成！生成路由条目: v4={len(out4)}, v6={len(out6)}")

if __name__ == "__main__":
    main()
