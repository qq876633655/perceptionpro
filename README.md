# perceptionpro

## 端口规划

| 角色 | 测试环境 | 生产环境 |
|---|---|---|
| Nginx 对外端口 | 8009 | 7898 |
| Gunicorn 内部端口 | 8009 | 8010 |
| 生产目录 | /home/user/workspace/perceptionpro/ | /home/user/deploy/perceptionpro/ |

---

## 首次生产部署

### 1. 拉取代码

```bash
mkdir -p /home/user/deploy
cd /home/user/deploy
git clone <git地址> perceptionpro
cd perceptionpro/backend
ln -s <media挂载路径> media    # 挂载或新建一个 media用于存储
```

### 2. 创建三个生产覆盖配置文件（只做一次，不被 git 追踪）

```bash
# ① Django 设置覆盖
cat > /home/user/deploy/perceptionpro/backend/dev_perceptionpro/local_settings.py << 'EOF'
DEBUG = False
SECRET_KEY = '替换为随机字符串，用命令生成: python3 -c "import secrets; print(secrets.token_hex(50))"'
ALLOWED_HOSTS = ['10.20.24.62', '127.0.0.1']
EOF

# ② 业务配置覆盖
cat > /home/user/deploy/perceptionpro/backend/config/perceptionpro_cfg_prod.py << 'EOF'
ENV = 'prod'
PER_DB_NAME = 'perceptionpro_prod'
PER_PRO_LOCAL_SERVER_URL = r'http://10.20.24.62:7898'
PER_PRO_FRONTEND_URL = r'http://10.20.24.62:7898'
EOF

# ③ Celery 覆盖
cat > /home/user/deploy/perceptionpro/backend/dev_perceptionpro/celery_prod.py << 'EOF'
# 只定义变量，由 celery.py 读取应用，不做任何 import
BROKER_URL = 'redis://127.0.0.1:6380/0'
EOF
```

### 3. 安装依赖

```bash
conda activate py312
cd /home/user/deploy/perceptionpro/backend
pip install -r requirements.txt
```

### 4. 数据库迁移 + 静态文件

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5. 前端构建

```bash
cd /home/user/deploy/perceptionpro/frontend
npm install
npm run build
```

### 6. 配置 Nginx

```bash
sudo tee /etc/nginx/conf.d/perceptionpro.conf << 'EOF'
server {
    listen 7898;
    server_name 10.20.24.62;

    # 前端静态文件
    root /home/user/deploy/perceptionpro/frontend/dist;
    index index.html;

    client_max_body_size 0;      # 不限制上传大小（由 Django/Gunicorn 控制）

    # Vue router history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理到 gunicorn（生产用 8010）
    location /api/ {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 7200;    # 2 小时，支持大文件上传
        proxy_send_timeout 7200;
        proxy_request_buffering off;  # 关闭请求缓冲，大文件直接流式转发给 gunicorn
    }

    # 钉钉回调代理到 gunicorn（/dd/no_sign_in/ 不在 /api/ 前缀下）
    location /dd/ {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60;
    }

    # 媒体文件
    location /media/ {
        alias /home/user/deploy/perceptionpro/backend/media/;
    }

    # 收集后的静态文件
    location /static/ {
        alias /home/user/deploy/perceptionpro/backend/staticfiles/;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

### 7. 配置 Gunicorn systemd 服务（开机自启）

```bash
sudo tee /etc/systemd/system/perceptionpro.service << 'EOF'
[Unit]
Description=PerceptionPro Gunicorn
After=network.target

[Service]
User=user
Group=user
WorkingDirectory=/home/user/deploy/perceptionpro/backend
Environment="PATH=/home/user/miniconda3/envs/py312/bin"
ExecStart=/home/user/miniconda3/envs/py312/bin/gunicorn dev_perceptionpro.wsgi:application \
    --bind 127.0.0.1:8010 \
    --workers 4 \
    --timeout 7200 \
    --pid /home/user/deploy/perceptionpro/gunicorn.pid \
    --access-logfile /home/user/deploy/perceptionpro/backend/logs/gunicorn_access.log \
    --error-logfile /home/user/deploy/perceptionpro/backend/logs/gunicorn_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable perceptionpro
sudo systemctl start perceptionpro
sudo systemctl status perceptionpro --no-pager
```

---

## 日常更新步骤

```bash
cd /home/user/deploy/perceptionpro
git pull

# 后端（有 model 变更时）
cd backend
conda activate py312
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart perceptionpro

# 前端（有前端改动时）
cd ../frontend
npm run build
# Nginx 自动生效，无需重启
```

---

## 服务管理命令

```bash
# Gunicorn
sudo systemctl start perceptionpro
sudo systemctl stop perceptionpro
sudo systemctl restart perceptionpro
sudo systemctl status perceptionpro --no-pager

# Nginx
sudo systemctl stop nginx
sudo systemctl reload nginx
sudo systemctl restart nginx

# 查看日志
tail -f /home/user/deploy/perceptionpro/backend/logs/gunicorn_error.log
tail -f /home/user/deploy/perceptionpro/backend/logs/audit.log
tail -f /home/user/deploy/perceptionpro/backend/logs/app.log
```

---

## Docker 部署

> 将整个平台打包为容器镜像，适合迁移到新机器或做隔离部署。  
> 外部依赖（MySQL、Redis、NAS）保持不变，不容器化。

### 容器架构

```
用户浏览器 → :7898 (frontend 容器 Nginx)
               ├── /           → Vue SPA 静态文件
               ├── /api/       → proxy → backend:8010 (backend 容器 Gunicorn)
               ├── /dd/        → proxy → backend:8010
               ├── /swagger/   → proxy → backend:8010
               ├── /media/     → 直接由 Nginx serve（挂载 NAS 路径，只读）
               └── /static/    → 直接由 Nginx serve（挂载 staticfiles，只读）

backend 容器  → MySQL 10.20.24.62:3306
             → Redis 10.20.24.62:6380

celery-worker 容器 → Redis（消费任务）
celery-beat 容器   → Redis（定时任务调度）
```

### 文件清单

| 文件 | 说明 |
|---|---|
| `backend/Dockerfile` | 后端镜像（Python 3.12-slim + Gunicorn，端口 8010） |
| `frontend/Dockerfile` | 前端镜像（多阶段：Node 构建 → Nginx alpine，端口 7898） |
| `frontend/nginx.conf` | Nginx 配置（反向代理 + 静态文件 serve） |
| `docker-compose.yml` | 编排 4 个服务：backend / celery-worker / celery-beat / frontend |
| `backend/.dockerignore` | 排除 media、logs、pyc 等不进镜像的文件 |
| `frontend/.dockerignore` | 排除 node_modules、dist 等 |

### 前置条件

1. 宿主机已安装 Docker（>=24）和 Docker Compose（>=2.20）
2. 宿主机已完成 NAS 挂载，并建好软链接：
   ```bash
   ln -s <NAS挂载路径> /home/user/deploy/perceptionpro/backend/media
   ```
3. 配置文件已就绪（同非容器部署，见"首次生产部署"中的第 2 步）：
   - `backend/dev_perceptionpro/local_settings.py`
   - `backend/config/perceptionpro_cfg.py`（生产版本）
   - `backend/dev_perceptionpro/celery_prod.py`

### 首次部署

```bash
cd /home/user/workspace/perceptionpro   # 或 deploy 目录

# 1. 构建镜像并启动 web 服务（先不启动 celery）
docker compose up -d --build backend frontend

# 2. 数据库迁移 + 收集静态文件（只需执行一次）
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput

# 3. 创建超级管理员（如果是新库）
docker compose exec backend python manage.py createsuperuser

# 4. 确认 web 服务正常后，启动 celery
docker compose up -d celery-worker celery-beat
```

### 日常更新

```bash
cd /home/user/workspace/perceptionpro

# 拉取最新代码
git pull

# 重新构建并滚动重启（有代码变更时）
docker compose up -d --build

# 仅有 model/migration 变更时，额外执行
docker compose exec backend python manage.py migrate
```

### 常用运维命令

```bash
# 查看所有容器状态
docker compose ps

# 查看实时日志
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f frontend

# 进入容器执行命令
docker compose exec backend bash
docker compose exec backend python manage.py shell

# 停止所有服务
docker compose down

# 停止并删除镜像（重新构建前用）
docker compose down --rmi local

# 单独重启某个服务
docker compose restart backend
docker compose restart frontend
```

### 注意事项

- **NAS media**：宿主机软链接 `/home/user/deploy/perceptionpro/backend/media` 在 Docker bind mount 时会跟随解析到实际物理路径，容器内可直接访问 NAS 文件，无需额外处理。
- **仿真测试 Worker**（webotsC1/C2 等）不在这个 compose 里，仍在各测试机器上独立启动，通过 Redis broker 接收任务。
- **Gunicorn 端口**：容器内监听 `0.0.0.0:8010`，宿主机上暴露 `8010`，供 Nginx 容器通过服务名 `backend:8010` 访问。
- **collectstatic**：静态文件收集到宿主机 `backend/staticfiles/`，通过 bind mount 挂载给前端容器，由 Nginx 直接 serve，不经过 Python 进程。

