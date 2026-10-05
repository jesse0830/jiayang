# 镜像搬运、压缩包与多行命令

## 1. 四个命令别配错对

| 命令 | 出来的是什么 | tag | 对手命令 |
|---|---|---|---|
| `docker save -o app.tar app:1.0` | 镜像（含 layer + manifest） | 保留 | `docker load` |
| `docker load -i app.tar` | 还原镜像 + tag | 保留；原来是 `<none>` 用 `docker tag <IMAGE_ID> repo:tag` 补 | `docker save` |
| `docker export <容器>` | 容器 rootfs 快照 | 无 | `docker import` |
| `docker import app.tar repo:tag` | 单层镜像，**丢历史层** | 必须手给 | `docker export` |

`save`/`load` 配对，`export`/`import` 配对。搞反了要么报错，要么导进去一个没有历史层的怪东西（`docker history` 追不了）。

## 2. `docker load` 直接吃压缩包

官方行为：从文件或 STDIN 读取归档，支持 tar 及 **gzip、bzip2、xz、zstd** 压缩，并还原镜像与 tag。

```bash
docker load -i image.tar
docker load -i image.tar.gz                       # 不用先 gunzip
docker load < image.tar.zst                       # 管道写法
docker load -i image.tar --platform=linux/amd64   # 归档含多平台时挑一个，缺失会报 requested platform ... not found
```

看到 `Loaded image: <repo>:<tag>` 才算成功；打了 `-q` 就没有这行，别以为失败。

打包侧：

```bash
docker save -o all.tar app1:1.0 app2:2.0     # 一个归档多个镜像
docker save app:1.0 | gzip > app.tar.gz      # 边存边压
md5sum app.tar.gz                            # 源机
tar -xOf …                                   # 见第 4 节
docker rmi 旧tag && docker load -i 新包        # 升级镜像：先删旧容器再 run，或直接用 compose 换 tag
```

镜像包通常几百 MB 到几 GB，内网拷贝中断率高：**两端 `md5sum` 对齐再 load**，否则多半在最后一秒报 `unexpected EOF`。

## 3. load 报错速查

| 报错 | 原因 | 处理 |
|---|---|---|
| 无输出但 exit 0 | 用了 `-q` | 去掉 `-q` |
| `open xxx.tar: no such file or directory` | 路径不对 | `ls -lh` 确认文件在 |
| `Error processing tar file(exit status 1): unexpected EOF` | 包不完整（传输中断 / 磁盘满） | 重传 + md5 对齐；`df -h /var/lib/docker` |
| `archive/tar: invalid tar header` | 不是 tar 包 | `file xxx.tar` 看真实类型 |
| `permission denied` / 连不上 `/var/run/docker.sock` | 用户不在 docker 组 | `sudo`，或 `usermod -aG docker $USER` 后重新登录 |
| `no space left on device` | 镜像层所在盘满 | `df -h /var/lib/docker`，`docker image prune` |

## 4. tar 解压速查

```bash
tar -xvf  包.tar                                        # 纯打包
tar -xzvf 包.tar.gz                                     # gzip，最常用
tar -xjvf 包.tar.bz2
tar -xJvf 包.tar.xz
tar -xvf 包.tar.gz -C /opt/app --strip-components=1     # 指定目录 + 去掉最外层目录
tar -tvf  包.tar.gz                                     # 只列表不解压（解之前先验一眼）
tar -xOf  包.tar.gz path/in/archive.conf                # 解单个文件到 stdout
unzip 包.zip                                            # zip 不是 tar
gunzip 文件.gz                                          # 单文件 gz，没有 tar
```

规则：

- GNU tar 与 bsdtar **都会自动识别压缩格式**，`-z/-j/-J` 可以省；省不掉的是 **`-f` 必须紧跟包名**（放前面就报 `-f: 选项需要一个参数`）。
- `-C` 的目标目录**必须先存在**（先 `mkdir -p`），否则 `tar: /dir: Cannot chdir`。
- **镜像 tar 不要 `tar -xf`**：里面是 layer 目录 + manifest，解出来不能直接用，直接 `docker load`。

| tar 报错 | 原因 |
|---|---|
| `gzip: stdin: not in gzip format` | 文件不是 gzip，`file 包` 看真实类型 |
| `tar: /dir: Cannot chdir` | `-C` 目录不存在 |
| `-f: 选项需要一个参数` | `-f` 没紧跟包名 |
| `Error is not recoverable` | 包损坏，重新下载 + md5sum 对比 |

## 5. 多行命令的续行反斜杠

`\` = 行尾续行（line continuation）。三条硬规矩：

1. 必须是**行尾最后一个字符**，后面不能有空格或 Tab（`\ ` 会变成转义空格，命令被腰斩，报错莫名其妙）。
2. 续行时 shell 提示符变成 `>`，不是卡死；`Ctrl+C` 可退。
3. 自测：`echo a \` 换行 `b` → 输出 `a b`。

行数超过 4 行就写成 `docker-compose.yml`：改 tag 只需 `docker compose up -d`，省的不仅是敲字，更是「漏一个续行」这类事故。
