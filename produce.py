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
        print(f"Warning: File {path} not found.")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 过滤注释、空行以及 chnroutes.txt 中可能存在的非 IP 行
                if not line or line.startswith(('#', '//', ';', 'USER-AGENT', 'payload:')):
                    continue
                
                # 兼容性清洗：
                # 1. 移除 SukkaW 格式的前缀
                # 2. 移除 yfgao/misakaio 可能带有的 define 前缀
                clean = line.replace('IP-CIDR,','').replace('IP-CIDR6,','').replace('define ','')
                # 3. 提取第一个逗号、分号或空格前的内容（适配各种纯文本或带注释格式）
                clean = clean.split(',')[0].split(';')[0].split()[0].strip()
                
                try:
                    nets.append(ip_network(clean))
                except:
                    continue
    except Exception as e:
        print(f"Error parsing {path}: {e}")
    return nets

def subtract(roots, excludes):
    """
    差集计算逻辑：全球地址空间减去中国 IP 段
    """
    for ex in excludes:
        new_roots = []
        for r in roots:
            if r.overlaps(ex):
                # 如果当前路由块 r 是要排除的 ex 的父集，则进行拆分
                if r.supernet_of(ex):
                    new_roots.extend(list(r.address_exclude(ex)))
                # 如果 ex 覆盖或等于 r，则直接舍弃 r (即不加入 new_roots)
                else:
                    continue
            else:
                # 无重叠，原样保留
                new_roots.append(r)
        roots = new_roots
    return roots

def main():
    # 1. 初始化
    # 拆分 0.0.0.0/0 为两个 /1 段以提高 GitHub Actions 的处理效率
    v4 = list(IPv4Network('0.0.0.0/0').subnets(new_prefix=1))
    v6 = [IPv6Network('::/0')]
    
    # 2. 解析文件
    c4 = parse_file('china_ip.conf')
    c6 = parse_file('china_ip_ipv6.conf')
    
    # 【安全检查】
    # 如果 chnroutes2 下载失败或为空，强制停止 Action，防止生成空路由表
    if len(c4) < 100:
        print("致命错误: IPv4 数据源解析结果过少，请检查下载链接是否失效。")
        sys.exit(1)

    # 3. 计算逻辑
    print(f"正在计算补集路由... (IPv4 排除项: {len(c4)} 条)")
    
    out4 = subtract(v4, [ip_network(i) for i in RES_V4] + c4)
    out6 = subtract(v6, [ip_network(i) for i in RES_V6] + c6)

    # 4. 写入文件
    with open("routes4.conf", "w", encoding='utf-8') as f:
        for n in sorted(out4):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
            
    with open("routes6.conf", "w", encoding='utf-8') as f:
        for n in sorted(out6):
            f.write(f'route {n} via "{NEXT_HOP}";\n')
    
    print(f"生成完毕: v4={len(out4)}, v6={len(out6)}")

if __name__ == "__main__":
    main()
