# batch_add_ipv6.py

一个用于在 Linux 网络接口上**批量添加 IPv6 地址**的 Python 脚本。  
特别适用于拥有一个 `/64` IPv6 子网的服务器（如 VPS、LXC 容器、WireGuard 等场景），快速添加大量 IPv6 地址，用于 rinetd、nginx、haproxy 等需要绑定多个公网 IPv6 的端口转发或反向代理服务。

### 特性

- 支持任意 `/64` 前缀（即使输入的前缀主机部分非零，也会自动规范化为正确网络地址）
- 自动跳过已存在的地址
- 支持干跑模式（`--dry-run`）预览命令
- 支持清理功能（`--remove`）删除该前缀下所有已添加地址
- 生成标准压缩格式的 IPv6 地址（如 `2001:db8::1`）
- 需要 root 权限执行添加/删除操作

### 依赖

- Python 3.6+
- 系统命令：`ip`（Linux 标准 net-tools，通常已预装）
- 无需额外 Python 包

### 使用方法

1. 保存脚本为 `batch_add_ipv6.py` 并赋予执行权限：

   ```bash
   chmod +x batch_add_ipv6.py

# 基本用法：向默认接口 eth0 添加 100 个地址（从 ::1 开始）
sudo python3 batch_add_ipv6.py -p 2001:db8:abcd:1234::/64 -c 100

# 指定接口（如 wg0、eth0、lo 等）
sudo python3 batch_add_ipv6.py -p 2001:db8:abcd:1234::/64 -c 10 -i wg0

# 从指定编号开始添加
sudo python3 batch_add_ipv6.py -p 2001:db8::/64 -s 1000 -c 50 -i eth0

# 仅预览将执行的命令（不实际添加）
python3 batch_add_ipv6.py -p 2001:db8::/64 -c 5 --dry-run

# 删除该前缀下所有已添加的地址：
sudo python3 batch_add_ipv6.py -p 2001:db8:abcd:1234::/64 -i wg0 --remove

# 参数说明
<table>
  <thead>
    <tr>
      <th>参数</th>
      <th>简称</th>
      <th>必填</th>
      <th>默认值</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>--prefix</td>
      <td>-p</td>
      <td>是</td>
      <td>无</td>
      <td>IPv6 子网前缀，例如 2001:db8::/64 或 2001:db8:1:2::/64</td>
    </tr>
    <tr>
      <td>--interface</td>
      <td>-i</td>
      <td>否</td>
      <td>eth0</td>
      <td>目标网络接口名（如 eth0、wg0、lo）</td>
    </tr>
    <tr>
      <td>--start</td>
      <td>-s</td>
      <td>否</td>
      <td>1</td>
      <td>起始主机编号（生成 ::1、::2 ...）</td>
    </tr>
    <tr>
      <td>--count</td>
      <td>-c</td>
      <td>否</td>
      <td>100</td>
      <td>要添加的地址数量</td>
    </tr>
    <tr>
      <td>--dry-run</td>
      <td></td>
      <td>否</td>
      <td>无</td>
      <td>仅显示命令，不实际执行</td>
    </tr>
    <tr>
      <td>--remove</td>
      <td></td>
      <td>否</td>
      <td>无</td>
      <td>删除该前缀下接口上所有 IPv6 地址</td>
    </tr>
  </tbody>
</table>


# 注意事项
如果你的前缀写成 2001:db8:abcd:abcd:3::/64 或 2001:db8:abcd:abcd:5::/64（主机位非零），脚本会自动规范为 2001:db8:abcd:abcd::/64，并提示说明。<br>
添加到 lo（loopback）接口是一种常见技巧，配合 sysctl net.ipv6.ip_nonlocal_bind=1 可实现无需实际路由即可绑定任意子网内地址（推荐用于 rinetd 等工具）。<br>
添加过多地址（>1000）可能略微影响系统性能，请根据实际需求控制数量。<br>
在 LXC 容器中运行时，确保容器具有 CAP_NET_ADMIN 权限。<br>

# 许可证
MIT License - 可自由使用、修改和分发。
