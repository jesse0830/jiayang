---
name: centos7-docker-internal-install
description: Use when 内网/离线 Linux 服务器装 Docker、导镜像、起容器（CentOS 7 等）。含换源、版本上限、tar/load 命令与报错速查。
---

# 内网 CentOS 7 装 Docker 并跑容器

典型现场：内网机出网按域名白名单卡，`download.docker.com` 被重置（`curl: (35) TCP connection reset by peer`），`mirrors.aliyun.com` 可通。

## 交付风格（每次都适用）

- 命令给**可直接整段粘贴的完整块**：带 `sudo`、带路径、该串联的用 `&&` 串好，不要让用户自己拼碎片。
- 报错不解释「不支持」就收工：**给出替代路径**（换源 / 换包管理器 / 离线 rpm 或 tar / podman）并说明原路径为什么不通。
- 诊断步骤合成**一条**粘贴块一次拿到（OS、架构、包管理器、各域名可达性、repo 列表），别一问一答拖三轮。
- 域名可达性**按域名逐个测**：某个域名被拦不代表同类域名全被拦（`download.docker.com` 与 `registry-1.docker.io` 要分别测）。

## 0. 先探通道，别直接开装

```bash
cat /etc/redhat-release; uname -m
which yum apt dnf podman 2>/dev/null
curl -I --max-time 5 https://mirrors.aliyun.com
curl -I --max-time 5 https://download.docker.com
yum repolist
rm -f /etc/yum.repos.d/docker-ce.repo     # 清掉抓取失败的残留
```

判读：
- `dnf: 未找到命令` + CentOS 7 → 全程用 yum（`yum-utils` / `yum-config-manager` 对标 dnf 的 `dnf-plugins-core` / `dnf config-manager`）
- docker 官方源 reset by peer + aliyun 301 → 走阿里云源（第 1 步）
- 基础源能列出包数（base+extras+updates 如 16771）说明 base 源可用，`container-selinux` 依赖装得上

## 1. 换阿里云 docker-ce 源

```bash
yum install -y yum-utils
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum clean all && yum makecache fast
yum list docker-ce --showduplicates | sort -r | head
yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
```

`yum install` 报「没有可用软件包 docker-ce」且 `add-repo` 报 `[Errno 14] curl#35` = 源根本没落盘，换源即可，别去改包名或怀疑包不存在。

## 2. el7 版本上限（阿里云镜像站实测）

| 包 | el7 最高版本 |
|---|---|
| docker-ce / docker-ce-cli | 26.1.4 |
| containerd.io | 1.6.33 |
| docker-compose-plugin | 2.27.1 |
| docker-buildx-plugin | 0.14.1 |

Docker 27 起不再提供 el7 包。锁版本：`yum install -y docker-ce-26.1.4 docker-ce-cli-26.1.4 containerd.io-1.6.33`。

## 3. 装完验证（缺一不可）

```bash
docker version
docker compose version      # unknown command 就补 yum install -y docker-compose-plugin
systemctl status docker --no-pager | head -12
```

健康日志特征（dockerd 启动段）：`storage-driver=overlay2`、`Daemon has completed initialization`、`API listen on /run/docker.sock`。

## 4. 拉镜像（第二道关，装好≠能用）

```bash
curl -sI --max-time 5 https://registry-1.docker.io/v2/ | head -3
docker pull hello-world
```

不通才配 `/etc/docker/daemon.json` 的 registry-mirrors，且**生产优先问运维要内网 Harbor**——公共加速器近年大批关停，让生产依赖它比一开始配私有仓库更麻烦。内网仓库另需 `insecure-registries`。

## 5. 跑容器

```bash
# 起飞前三查：镜像是否在本地 / 端口占用 / 磁盘与 SELinux
docker images | grep -E "REPOSITORY|<image>"
ss -lntp | grep -E '<port1>|<port2>'
df -h /var/lib/docker; getenforce

# 跑（命名卷不需要 :Z，docker 自管 /var/lib/docker/volumes）
docker run -d --name <name> --restart unless-stopped \
  -p A:A -p B:B -v vol:/path ... <image>:<tag>

# 验收
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker logs --tail 80 <name>
docker inspect <name> --format '{{range .Mounts}}{{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
curl -sv --max-time 5 http://127.0.0.1:<port>/ 2>&1 | head -20
systemctl is-active firewalld   # active 就 firewall-cmd --permanent --add-port=<port>/tcp && firewall-cmd --reload
```

- `curl` 返 `Connection refused` = 容器起来了但应用没监听（配置/依赖问题），不是端口映射问题
- 多行 `docker run` 用 `\` 续行时，`\` 后**不能有空格**（`\ ` 会变成转义空格，命令被腰斩）；行数一多就转 compose 文件，升级只改 tag
- 日志卷会无限增长，跑久了吃满磁盘；应用侧切分或给 dockerd 配 `log-opts` 限流

## 6. 镜像包

镜像 tar **不要 `tar -xf`**（里面是 layer + manifest，解出来不能用，必须 `docker load`）。`docker load` **直接吃压缩包**，`.tar/.tar.gz/.tar.bz2/.tar.xz/.tar.zst` 都能喂，**不要先 gunzip**：

```bash
docker load -i image.tar          # 成功打 Loaded image: repo:tag
docker load -i image.tar.gz       # 压缩包直接导
docker images | grep <image>      # 显示 <none> 就 docker tag <IMAGE_ID> repo:tag 补标签
```

`docker save`↔`docker load` 配对、`docker export`↔`docker import` 配对；load 保留 tag，import 丢 tag。大包跨机搬必须两边 `md5sum` 对齐（`unexpected EOF` 基本都是包不完整）。完整对照表、报错速查、tar 解压速查见 `references/docker-image-transfer-and-archives.md`。

## 7. 必须给用户的前置提醒

CentOS 7 = 内核 3.10 + cgroup v1 → **K8s 1.30+ 上不去**（最多 1.28/1.29），Docker 27+ 无 el7 包。该机若要做生产节点/未来接 K8s，趁早换 Rocky / AlmaLinux / 龙蜥，别等业务堆上去再迁。
