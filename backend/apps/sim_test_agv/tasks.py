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


@per_celery.task(name="agv_sim_test_task", bind=True, acks_late=True)
def agv_sim_test_task(self, agv_task_id):
    worker_name = self.request.hostname
    name, host = worker_name.split("@")
    run_docker = name.split(".")[1]
    task_instance = models.AgvTestTask.objects.get(id=agv_task_id)

    # 1. 标记真正开始
    task_instance.task_status = "RUNNING"
    task_instance.worker_name = self.request.hostname
    task_instance.save(update_fields=["task_status", "worker_name"])

    # 2. 启动 subprocess
    command = ["/home/agv/VNSim/vnsimautotest/run_test", run_docker, str(agv_task_id)]
    # command = ["python3", "/home/user/workspace/perceptionpro/backend/demo/sim_test_loop.py", run_docker, str(agv_task_id)]
    process = subprocess.Popen(
        command,
        preexec_fn=os.setsid,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    task_instance.process_id = process.pid
    task_instance.save(update_fields=["process_id"])

    try:
        _monitor_process(task_instance, process)
    except Exception as e:
        task_instance.task_status = "FAILED"
        task_instance.error_msg = str(e)
        task_instance.save(update_fields=["task_status", "error_msg"])
        raise
