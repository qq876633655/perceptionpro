#!/usr/bin/env python3
"""
仿真测试任务占位脚本（用于 Celery 任务本地测试）
用法：python sim_test_loop.py <run_docker> <agv_task_id>
- 每秒打印一次进度，共运行 60 秒后正常退出（return code 0）
- 收到 SIGTERM / SIGINT 时立即退出（return code 1）
"""

import sys
import time
import signal

_stop = False


def _handle_signal(signum, frame):
    global _stop
    print(f"[sim_test_loop] 收到信号 {signum}，准备退出", flush=True)
    _stop = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)

run_docker = sys.argv[1] if len(sys.argv) > 1 else 'unknown'
agv_task_id = sys.argv[2] if len(sys.argv) > 2 else '0'

print(f"[sim_test_loop] 启动 | docker={run_docker} | task_id={agv_task_id}", flush=True)

TOTAL = 60
for i in range(1, TOTAL + 1):
    if _stop:
        print("[sim_test_loop] 已中止", flush=True)
        sys.exit(1)
    print(f"[sim_test_loop] 进度 {i}/{TOTAL}s", flush=True)
    time.sleep(1)

print("[sim_test_loop] 正常完成", flush=True)
sys.exit(0)
