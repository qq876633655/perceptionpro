from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from kombu import Queue, Exchange
from celery.schedules import crontab
from datetime import timedelta

# 设置默认的 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_perceptionpro.settings')


# 设置 app 名称
per_celery = Celery('per_celery')

per_celery.conf.task_track_started = True  # 打开任务跟踪
per_celery.conf.broker_connection_retry_on_startup = True
per_celery.conf.task_default_exchange = 'default'
per_celery.conf.task_default_exchange_type = 'topic'
per_celery.conf.task_default_routing_key = 'default'
per_celery.conf.task_default_queue = 'default'
per_celery.conf.broker_url = 'redis://10.20.24.62:6380/13'  # 中间人 url
per_celery.conf.result_backend = "django-db"  # 支持数据库django-db
per_celery.conf.accept_content = ['application/json', ]  # 协议
per_celery.conf.task_serializer = 'json'  # 序列化方式


per_celery.conf.result_serializer = 'json'
per_celery.conf.timezone = 'Asia/Shanghai'  # 时区
per_celery.conf.enable_utc = False  # 是否采用 utc
per_celery.conf.task_result_expires = 24 * 60 * 60  # 结果存储时间
per_celery.conf.worker_enable_remote_control = True
per_celery.conf.worker_send_task_events = True


# 设置特殊路由 execute_sim
per_celery.conf.task_routes = {
    'apps.simulation_test.tasks.execute_sim_test': {'queue': 'execute_sim', 'routing_key': 'execute_sim_key'},
}

# 设置默认队列和特殊队列
per_celery.conf.task_queues = (
    Queue('default', Exchange("default"), routing_key='default'),
    Queue('execute_sim', Exchange("execute_sim"), routing_key='execute_sim_key'),

)


per_celery.conf.beat_schedule = {
    'everyday_defect_total': {
        'task': 'apps.quality_control.tasks.timer_defect_total',
        'schedule': crontab(minute='1', hour='0'),
        # 'schedule': timedelta(seconds=10),
        'options': {'queue': 'default'}
    },
    # 'everyday_defect_onsite':{
    #     'task':"apps.quality_control.tasks.schedule_notification",
    #     'schedule': crontab(minute='00',hour='10',day_of_week="mon,tue,wed,thu,fri"),
    # },
    # 'one_hour_onsite': {
    #     'task': "apps.quality_control.tasks.schedule_one_hour",
    #     'schedule': crontab(minute='*/25',hour='10-12,14-20',day_of_week="mon,tue,wed,thu,fri"),
    # }
}

# 从 Django 配置中加载 Celery 配置
per_celery.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现 Django 应用中的任务
per_celery.autodiscover_tasks()

# ── 生产环境覆盖（celery_prod.py 不被 git 追踪）────────────────────────
try:
    from dev_perceptionpro.celery_prod import *  # noqa
except ImportError:
    pass
