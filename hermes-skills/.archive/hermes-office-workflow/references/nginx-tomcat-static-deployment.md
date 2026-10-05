# Nginx + Tomcat 静态文件部署（中文企业场景）

## 常见场景

企业内部用 Tomcat 运行 Java Web 应用（如 OA 系统），同时需要用 Nginx 反向代理并额外提供静态 HTML 文件的访问。

典型结构：

```
用户 → Nginx (80/443)
         ├── /api/* → Tomcat (8080)  # Java 应用
         └── /docs/* → 本地静态文件   # HTML 文档/验收单/报告
```

## Nginx 的关键配置：root vs alias

### root（常用，但不适合子路径）

```nginx
location /docs/ {
    root /path/to/files/;
}
```

访问 `/docs/report.html` → 实际路径 `/path/to/files/docs/report.html`

**问题：** root 会把 location 的路径追加到 root 路径后。如果你的文件在 `/path/to/html/report.html`，但浏览器 URL 是 `/docs/report.html`，用 root 会找 `/path/to/html/docs/report.html`（多了一层 docs）。

### alias（推荐用于子路径）

```nginx
location /docs/ {
    alias /path/to/html/;
}
```

访问 `/docs/report.html` → 实际路径 `/path/to/html/report.html`

**alias 不会追加 location 路径**，而是直接替换。适合将 URL 子路径映射到文件系统中的**不同目录名**。

## 完整示例

```nginx
# Tomcat Java 应用
server {
    listen 80;
    server_name oa.example.com;

    # Java 应用代理到 Tomcat
    location / {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态 HTML 文件（如验收单）
    location /static/ {
        alias /data/tomcat/webapps/ROOT/static/;
        autoindex on;           # 显示目录列表，方便找文件
        autoindex_exact_size off;
        autoindex_localtime on;
    }
}

# 或者独立端口提供静态文件
server {
    listen 18001;               # 独立端口
    server_name _;

    location / {
        alias /data/tomcat/webapps/ROOT/;
        autoindex on;
    }
}
```

## 常见坑点

### 1. alias 路径末尾必须有 `/`

```nginx
# ❌ 错误
location /docs/ {
    alias /path/to/html;
}

# ✅ 正确
location /docs/ {
    alias /path/to/html/;
}
```

如果 alias 末尾没有 `/`，Nginx 会去掉 location 的最后一个路径段，导致路径拼接错误。

### 2. proxy_pass 末尾的 `/`

```nginx
# ❌ 不传原始路径
location /api/ {
    proxy_pass http://127.0.0.1:8080;
}
# 请求 /api/login → http://127.0.0.1:8080/api/login（保持了 api 前缀）

# ✅ 传原始路径
location /api/ {
    proxy_pass http://127.0.0.1:8080/;
}
# 请求 /api/login → http://127.0.0.1:8080/login（去掉了 api 前缀）
```

### 3. 配置文件语法检查

修改 nginx 配置后一定要先检查语法再 reload：

```bash
nginx -t                    # 检查语法
nginx -s reload             # 重新加载配置
```

### 4. 权限问题

Nginx worker 进程通常以 `nginx` 或 `nobody` 用户运行，确保静态文件目录对该用户可读：

```bash
chmod +r /path/to/files/*.html
chmod o+x /path/to/files/   # 目录需要执行权限
```

## 快速排查

| 问题 | 可能原因 | 解决 |
|------|---------|------|
| 404 Not Found | root/alias 路径错误，或文件不存在 | 检查路径拼接方式，确认文件存在 |
| 403 Forbidden | 目录无执行权限，或autoindex被禁 | `chmod o+x /path/` 或 `autoindex on;` |
| 502 Bad Gateway | proxy_pass 后端不通 | 检查 Tomcat 是否运行、端口是否正确 |
| 文件列表空白 | HTML文件没有`index.html` | 加上 `autoindex on;` 显示目录列表 |
