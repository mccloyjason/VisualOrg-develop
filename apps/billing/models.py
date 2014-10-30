from django.db import models


class PaymentPlanManager(models.Manager):
    def get_free_plan(self):
        return self.get_query_set().get(monthly_cost=0)


class PaymentPlan(models.Model):
    max_users = models.PositiveIntegerField()
    monthly_cost = models.FloatField()
    objects = PaymentPlanManager()

    def __unicode__(self):
        return u"%s"%self.max_users
