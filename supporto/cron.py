from django_cron import CronJobBase, Schedule
from supporto.models import KBCache


class CronAggiornaKBCache(CronJobBase):

    ARTICLE_INTERVAL = 100
    RUN_AT_TIMES = ['03:00']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = 'supporto.aggiorna_kb_cache'

    def do(self):
        KBCache.aggiorna_kb_cache(article_interval=self.ARTICLE_INTERVAL)
