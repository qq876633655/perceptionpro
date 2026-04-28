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
