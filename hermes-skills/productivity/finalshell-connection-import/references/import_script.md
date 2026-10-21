# 导入脚本模板

以 `/Users/jesseyoung/.hermes/cache/scratch/fs_import.py` 为原型（26 条一次成功）。核心：

```python
import json, os, glob, random, string, shutil, time
FS = os.path.expanduser('~/Library/FinalShell'); CONN = FS + '/conn'
TS = [("root","10.15.70.8",22)]          # (user, host, port)

def rand_id():
    return ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(16))

bak = FS + '/conn.bak-' + time.strftime('%Y%m%d-%H%M%S')
if not os.path.exists(bak): shutil.copytree(CONN, bak)

have = set()
for f in glob.glob(CONN + '/*_connect_config.json'):
    d = json.load(open(f, encoding='utf-8'))
    have.add((d.get('user_name'), d.get('host'), int(d.get('port', 22))))

now = int(time.time() * 1000)
for user, host, port in TS:
    if (user, host, port) in have: continue
    cid = rand_id()
    name = '%s@%s' % (user, host) + ('' if port == 22 else ':%d' % port)
    cfg = {'forwarding_auto_reconnect': False, 'custom_size': False, 'delete_time': 0,
           'secret_key_id': '', 'user_name': user, 'remote_port_forwarding': {},
           'conection_type': 100, 'sort_time': 0, 'description': '', 'proxy_id': '0',
           'authentication_type': 1, 'drivestoredirect': True, 'delete_key_sequence': 0,
           'password': '', 'modified_time': now, 'host': host, 'accelerate': False,
           'id': cid, 'height': 0, 'order': 0, 'create_time': now,
           'port_forwarding_list': [], 'parent_update_time': 0, 'rename_time': 0,
           'backspace_key_sequence': 2, 'fullscreen': False, 'port': port,
           'terminal_encoding': 'UTF-8', 'parent_id': 'root', 'exec_channel_enable': True,
           'width': 0, 'name': name, 'access_time': 0}
    json.dump(cfg, open('%s/%s_connect_config.json' % (CONN, cid), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
```

## Terminal.app 历史提取

```python
import plistlib, re, os
d = plistlib.load(open(os.path.expanduser('~/Library/Preferences/com.apple.Terminal.plist'), 'rb'))
cmds = []
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'PreviousCommands' and isinstance(v, list):
                cmds.extend([x for x in v if isinstance(x, str)])
            else: walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(d)
seen = []
for c in cmds:
    for m in re.finditer(r'ssh\s+([A-Za-z0-9_.\-]+)@\s*([0-9.]+)(?:\s+-[pP]\s*(\d+))?', c):
        t = (m.group(1), m.group(2), int(m.group(3) or 22))
        if t not in seen: seen.append(t)
```

## known_hosts 提取

```python
for f in ['~/.ssh/known_hosts', '~/.ssh/known_hosts.old']:
    for line in open(os.path.expanduser(f), errors='replace'):
        h = line.split()[0] if line.split() else ''
        if h and '|' not in h:                  # 跳过哈希项
            for hp in h.split(','): print(hp)   # [1.2.3.4]:60005 连端口一起取
```

## 排除性提醒

- `ssh.github.com:443`、`github.com` 这类 git over SSH 目标不要导入成服务器连接。
- 内网(10.15.x) 与公网(183.x/106.x/59.x) 混在一张列表里，连接名 `user@host` 自身够区分，不必造分组。
