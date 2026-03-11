#!/usr/bin/env python3
import sys
import os
from ipaddress import IPv4Network, IPv6Network, ip_network

# --- 配置区 ---
NEXT_HOP = "eth0"
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
    高度兼容解析器
    """
    nets = []
    if not os.path.exists(path):
        print(f"警告: 找不到文件 {path}")
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if len(lines) < 10: # 基础安全线
            return []

        for line in lines:
            line = line.strip()
            # 过滤注释和空行
            if not line or line.startswith(('#', '//', ';', 'USER-AGENT', 'payload:')):
                continue
            
            # 清洗逻辑：兼容 SukkaW (IP-CIDR,1.1.1.0/24,no-resolve) 和 yfgao (1.1.1.0/24)
            # 先移除前缀
            clean = line.replace('IP-CIDR,', '').replace('IP-CIDR6,', '').replace('define ', '')
            # 再移除逗号或分号后面的后缀
            clean = clean.split(',')[0].split(';')[0].strip()
            
            try:
                nets.append(ip_network(clean))
            except ValueError:
                continue
        return nets
    except Exception as e:
        print(f"读取文件错误: {e}")
        return []

def subtract(roots, excludes):
    """
    修复后的差集算法：确保逻辑严密
    """
    for ex in excludes:
        new_roots = []
        for r in roots:
            if r.overlaps(ex):
                # 情况1：当前网段 r 是排除项 ex 的父集，则需要拆分 r
                if r.supernet_of(ex):
                    new_roots.extend(list(r.address_exclude(ex)))
                # 情况2：当前网段 r 被排除项 ex 完全覆盖，则直接舍弃 r (不加进 new_roots)
                else:
                    continue
            else:
                # 情况3：完全没有重叠，保留当前网段
                new_roots.append(r)
        roots = new_roots
    return roots

def main():
    # 1. 初始化全量空间
    # 使用 subnets(new_prefix=1) 将 0.0.0.0/0 拆分为 0.0.0.0/1 和 128.0.0.0/1 提高处理效率
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 2. 解析文件
    c4 = parse_file('china_ip.conf')
    c6 = parse_file('china_ip_ipv6.conf')
    
    # 如果解析出的中国 IP 为空，为了防止生成全量路由导致代理失效，强制报错
    if not c4 or not c6:
        print("致命错误: 解析出的中国 IP 列表为空，请检查下载地址或文件格式！")
        sys.exit(1)
    
    # 3. 转换逻辑
    print(f"正在处理: 导入 IPv4 中国段 {len(c4)} 条, IPv6 中国段 {len(c6)} 条")
    
    # 计算补集：全球 - (保留地址 + 中国地址)
    out4 = subtract(v4, [ip_network(i) for i in RES_V4] + c4)
    out6 = subtract(v6, [ip_network(i) for i in RES_V6] + c6)

    # 4. 写入文件
    print(f"正在生成结果: v4={len(out4)} 条, v6={len(out6)} 条")
    
    with open("routes4.conf", "w", encoding='utf-8') as f:
        for n in sorted(out4):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
            
    with open("routes6.conf", "w", encoding='utf-8') as f:
        for n in sorted(out6):
            f.write(f'route {n} via "{NEXT_HOP}";\n')

if __name__ == "__main__":
    main()
    
