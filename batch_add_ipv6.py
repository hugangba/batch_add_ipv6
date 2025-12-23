#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import ipaddress

def run_cmd(cmd):
    """执行 shell 命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {cmd}\n错误: {result.stderr.strip()}")
        return False
    return True

def get_existing_ipv6(interface):
    """获取接口上的 global IPv6 地址"""
    cmd = f"ip -6 addr show dev {interface} scope global"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    existing = set()
    for line in result.stdout.splitlines():
        if "inet6" in line:
            addr = line.strip().split()[1].split('/')[0]
            existing.add(addr)
    return existing

def add_ipv6_addresses(interface, prefix, start_host, count, dry_run=False):
    """批量添加 IPv6 地址"""
    # 使用 strict=False 自动规范网络地址（主机位清零）
    network = ipaddress.IPv6Network(prefix, strict=False)
    
    if network.prefixlen != 64:
        print(f"警告: 前缀不是 /64，当前: /{network.prefixlen}（推荐 /64）")

    # 显示规范后的网络地址
    normalized_prefix = f"{network.network_address}/{network.prefixlen}"
    if normalized_prefix != prefix.rstrip('/64') + '/64':  # 粗略比较
        print(f"注意: 你的前缀被规范化为 {normalized_prefix}（原前缀主机位非零）")

    existing = get_existing_ipv6(interface)
    added_count = 0

    print(f"开始向接口 {interface} 添加 IPv6 地址（使用规范前缀 {normalized_prefix}）...")
    for i in range(start_host, start_host + count):
        addr_int = network.network_address + i
        addr_str = addr_int.compressed  # 使用 compressed 格式，确保标准（如 ::1）

        if addr_str in existing:
            print(f"跳过已存在: {addr_str}")
            continue

        full_addr = f"{addr_str}/64"
        cmd = f"ip -6 addr add {full_addr} dev {interface}"

        if dry_run:
            print(f"[干跑] {cmd}")
        else:
            print(f"添加: {addr_str}")
            if not run_cmd(cmd):
                print(f"添加失败: {addr_str}")
                continue
        added_count += 1

    print(f"完成！本次新增 {added_count} 个地址。")

def remove_ipv6_by_prefix(interface, prefix):
    """删除属于该前缀的地址（使用规范网络）"""
    network = ipaddress.IPv6Network(prefix, strict=False)
    existing = get_existing_ipv6(interface)
    removed_count = 0

    print(f"正在删除接口 {interface} 上属于 {network} 的 IPv6 地址...")
    for addr in existing:
        try:
            ip = ipaddress.IPv6Address(addr)
            if ip in network:
                cmd = f"ip -6 addr del {addr}/64 dev {interface}"
                print(f"删除: {addr}")
                if not run_cmd(cmd):
                    print(f"删除失败: {addr}")
                else:
                    removed_count += 1
        except:
            continue

    print(f"清理完成！共删除 {removed_count} 个地址。")

def main():
    parser = argparse.ArgumentParser(description="批量添加 IPv6 地址到网络接口（支持非标准前缀）")
    parser.add_argument("--interface", "-i", default="eth0", help="网络接口名 (默认: eth0)")
    parser.add_argument("--prefix", "-p", required=True, help="IPv6 前缀，例如: 2001:470:8935:3:3::/64")
    parser.add_argument("--start", "-s", type=int, default=1, help="起始主机号 (默认: 1)")
    parser.add_argument("--count", "-c", type=int, default=100, help="添加数量 (默认: 100)")
    parser.add_argument("--dry-run", action="store_true", help="仅显示命令，不执行")
    parser.add_argument("--remove", action="store_true", help="删除该前缀下所有地址")

    args = parser.parse_args()

    if not args.dry_run and not args.remove and os.geteuid() != 0:
        print("错误: 添加地址需要 root 权限（--remove 也需要，或用 --dry-run 测试）")
        sys.exit(1)

    if args.remove:
        remove_ipv6_by_prefix(args.interface, args.prefix)
    else:
        add_ipv6_addresses(args.interface, args.prefix, args.start, args.count, args.dry_run)

if __name__ == "__main__":
    main()
