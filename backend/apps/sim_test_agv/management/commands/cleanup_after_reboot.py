"""
断电/重启后清理命令：
  1. 清空 Redis 中未被 Worker 取走的 Celery 消息（--purge-queue，默认开启）
  2. 把 DB 中所有 RUNNING / DISPATCHED / CANCELING 的 AGV 任务标为 CANCELED

用法：
    python manage.py cleanup_after_reboot              # 清队列 + 改 DB
    python manage.py cleanup_after_reboot --no-purge   # 仅改 DB，不动 Redis 队列
    python manage.py cleanup_after_reboot --dry-run    # 预览，不实际修改
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


CANCEL_STATUSES = ('RUNNING', 'DISPATCHED', 'CANCELING')


class Command(BaseCommand):
    help = '断电/重启后：清空 Celery 队列消息并将未完成任务标为 CANCELED'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-purge',
            action='store_true',
            default=False,
            help='跳过 Redis 队列清理，仅修改 DB 状态',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='预览将被取消的任务，不做任何实际修改',
        )

    def handle(self, *args, **options):
        from apps.sim_test_agv.models import AgvTestTask

        dry_run = options['dry_run']
        skip_purge = options['no_purge']

        # ── 1. 查询受影响的任务 ──────────────────────────────────────
        qs = AgvTestTask.objects.filter(task_status__in=CANCEL_STATUSES).order_by('id')
        count = qs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('没有需要取消的任务，无需清理。'))
            return

        self.stdout.write(f'发现 {count} 个未完成任务：')
        for t in qs:
            self.stdout.write(
                f'  ID={t.id:>6}  状态={t.task_status:<12}  队列={t.queue_name}  '
                f'资产版本={t.sim_test_version}  创建人={t.created_by}'
            )

        if dry_run:
            self.stdout.write(self.style.WARNING('[dry-run] 以上任务将被标为 CANCELED，未实际修改。'))
            return

        # ── 2. 清空 Redis 队列 ─────────────────────────────────────
        if not skip_purge:
            purged = self._purge_queues()
            self.stdout.write(f'已清空 Redis 队列，共删除 {purged} 条待执行消息。')
        else:
            self.stdout.write(self.style.WARNING('已跳过 Redis 队列清理（--no-purge）。'))

        # ── 3. 更新 DB 状态 ────────────────────────────────────────
        updated = qs.update(
            task_status='CANCELED',
            error_msg='系统重启后自动取消，请确认仿真环境正常后手动重发。',
        )
        self.stdout.write(self.style.SUCCESS(f'已将 {updated} 个任务标为 CANCELED。'))

    # ──────────────────────────────────────────────────────────────
    def _purge_queues(self):
        """清空所有 Celery 队列，返回删除的消息总数。"""
        from dev_perceptionpro.celery import per_celery
        from kombu import Connection

        broker_url = per_celery.conf.broker_url
        purged_total = 0

        try:
            with Connection(broker_url) as conn:
                queues = [q.name for q in per_celery.conf.task_queues]
                for queue_name in queues:
                    try:
                        with conn.SimpleQueue(queue_name) as q:
                            n = q.clear()
                            purged_total += n or 0
                            self.stdout.write(f'  队列 [{queue_name}] 清除 {n or 0} 条消息')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'  队列 [{queue_name}] 清理失败：{e}')
                        )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'连接 Redis 失败，队列未清理：{e}')
            )

        return purged_total
