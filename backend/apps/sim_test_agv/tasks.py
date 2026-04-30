# -*- coding: utf-8 -*-
"""
Time:23/12/23 15:02
Author:yanglei
File:tasks.py
"""

import os
import django
import subprocess
import psutil
import time
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_perceptionpro.settings")
django.setup()
from apps.sim_test_agv import models
from dev_perceptionpro.celery import per_celery


@per_celery.task(name="kill_pid", queue='default', bind=True)
def kill_pid(self, pid, auto_task_id):
    if pid:
        try:
            parent_process = psutil.Process(int(pid))
            for child in parent_process.children(recursive=True):
                child.kill()
            parent_process.kill()
        except psutil.NoSuchProcess:
            pass


def _kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass


def _monitor_process(task, process):
    while True:
        # subprocess 自然退出
        ret = process.poll()
        if ret is not None:
            if task.cancel_requested:
                task.task_status = "CANCELED"
            elif ret == 0:
                task.task_status = "SUCCESS"
            else:
                task.task_status = "FAILED"

            task.save(update_fields=["task_status"])
            return

        # 每 1 秒检查一次是否被取消
        task.refresh_from_db(fields=["cancel_requested", "task_status"])

        if task.cancel_requested:
            task.task_status = "CANCELING"
            task.save(update_fields=["task_status"])

            _kill_process_tree(process.pid)

            task.task_status = "CANCELED"
            task.save(update_fields=["task_status"])
            return

        time.sleep(1)


@per_celery.task(name="agv_sim_test_task", bind=True)
def agv_sim_test_task(self, agv_task_id):
    try:
        # ── 幂等守卫：只有 DISPATCHED 状态才允许执行 ──
        task_instance = models.AgvTestTask.objects.get(id=agv_task_id)
        if task_instance.task_status != 'DISPATCHED':
            return

        try:
            worker_name = self.request.hostname
            ip, run_docker = worker_name.split("_")
        except models.WorkerNode.DoesNotExist:
            node = models.WorkerNode.objects.get(hostname=self.request.hostname)
            run_docker = node.docker_type

        # 1. 标记真正开始
        task_instance.task_status = "RUNNING"
        task_instance.worker_name = self.request.hostname
        task_instance.save(update_fields=["task_status", "worker_name"])

        # 2. 启动 subprocess
        command = ["/home/agv/VNSim/vnsimautotest/run_test", run_docker, str(agv_task_id)]
        # command = ["python3", "/home/agv/VNSim/vnsimautotest/demo/sim_test_loop.py", run_docker, str(agv_task_id)]
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        task_instance.process_id = process.pid
        task_instance.save(update_fields=["process_id"])
    except Exception as e:
        task_instance.task_status = "FAILED"
        task_instance.error_msg = str(e)
        task_instance.save(update_fields=["task_status", "error_msg"])
        raise

    try:
        _monitor_process(task_instance, process)
    except Exception as e:
        task_instance.task_status = "FAILED"
        task_instance.error_msg = str(e)
        task_instance.save(update_fields=["task_status", "error_msg"])
        raise


@per_celery.task(name="check_stale_tasks", queue='default')
def check_stale_tasks():
    """巡检：超过 8 天仍为 RUNNING 的任务标记为 FAILED"""
    from django.utils import timezone
    threshold = timezone.now() - timedelta(days=8)
    stale = models.AgvTestTask.objects.filter(
        task_status='RUNNING',
        update_time__lt=threshold,
    )
    count = stale.update(
        task_status='FAILED',
        error_msg='任务超时未完成，系统自动标记失败',
    )
    return f'标记 {count} 个僵死任务'
