from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import connection
from django.contrib.auth import get_user_model

from apps.documents.models import LiveDocument
from apps.processes.models import Process, ProcessInstance
from apps.questions.models import Question, Answer

from ...models import Organization, UserStatistic, OrganizationStatistic

User = get_user_model()


class Command(BaseCommand):
    help = 'Collect statistics for primary organizations and users.'

    def handle(self, *args, **options):
        ## Collect yesterday stats for organizations.
        ## Should be run shortly after midnight each day.
        yesterday = datetime.now() - timedelta(days=1)
        orgs = Organization.objects.filter(parent=None)
        for org in orgs:
            kwargs = {
                'organization': org,
                'date': yesterday,
            }
            stat, created = OrganizationStatistic.objects.get_or_create(
                **kwargs)

            stat.num_roles = org.roles.count()
            stat.num_roles_filled = org.roles.filter(
                user__isnull=False).count()
            stat.num_roles_unfilled = org.roles.filter(
                user__isnull=True).count()
            # num_external_roles

            stat.num_teams = org.get_descendants().filter(
                type=org.STRUCTURAL).count()
            stat.num_workgroups = org.get_descendants().filter(
                type=org.WORKGROUP).count()

            stat.num_livedocs_active = org.live_documents.filter(
                complete=False).count()

            stat.num_documents = org.documents.count()
            # NOTE: Static document is a document without a new version
            # for at least 24 hours.
            stat.num_documents_static = stat.num_documents - org.documents \
                .filter(versions__created_on__gte=yesterday).count()

            answers = 0
            answer_minutes = 0
            for question in org.questions.filter(
                    closed_datetime__gte=yesterday):
                minutes = question.minutes_before_question_closed
                if minutes:
                    answers = answers + 1
                    answer_minutes = answer_minutes + minutes
            if answers > 0:
                stat.average_time_questions_open = answer_minutes / answers

            stat.save()
        del orgs, org, stat, yesterday

        ## NOTE: Organization stats
        try:
            start_date = OrganizationStatistic.objects.latest().date
        except OrganizationStatistic.DoesNotExist:
            start_date = None

        # NOTE: Organization LiveDocs completed
        qs = LiveDocument.objects.filter(complete=True)
        data = get_data(qs, start_date, 'completed_on', ('organization', ))
        for item in data:
            kwargs = {
                'organization': Organization.objects.get(
                    pk=item['organization']),
                'date': item['day'],
            }
            stat, created = OrganizationStatistic.objects.get_or_create(
                **kwargs)
            stat.num_livedocs_completed = item['count']
            stat.save()

        # NOTE: Questions
        qs = Question.objects.all()
        data = get_data(qs, start_date, 'created_datetime', ('organization', ))
        for item in data:
            kwargs = {
                'organization': Organization.objects.get(
                    pk=item['organization']),
                'date': item['day'],
            }
            stat, created = OrganizationStatistic.objects.get_or_create(
                **kwargs)
            stat.num_questions = item['count']
            stat.save()

        # NOTE: Answers
        qs = Answer.objects.all()
        data = get_data(qs, start_date, 'created_datetime',
                        ('question__organization', ))
        for item in data:
            kwargs = {
                'organization': Organization.objects.get(
                    pk=item['question__organization']),
                'date': item['day'],
            }
            stat, created = OrganizationStatistic.objects.get_or_create(
                **kwargs)
            stat.num_answers = item['count']
            stat.save()

        ## NOTE: User stats
        try:
            start_date = UserStatistic.objects.latest().date
        except UserStatistic.DoesNotExist:
            start_date = None

        # NOTE: User processes
        qs = Process.objects.all()
        data = get_data(qs, start_date, 'created_datetime', ('created_by',
                                                             'organization'))
        for item in data:
            kwargs = {
                'user': User.objects.get(pk=item['created_by']),
                'organization': Organization.objects.get(
                    pk=item['organization']),
                'date': item['day'],
            }
            stat, created = UserStatistic.objects.get_or_create(**kwargs)
            stat.num_processes_developed = item['count']
            stat.save()

        # NOTE: User process instances
        qs = ProcessInstance.objects.all()
        data = get_data(qs, start_date, 'start_datetime', ('initiated_by',
                                                           'organization'))
        for item in data:
            kwargs = {
                'user': User.objects.get(pk=item['initiated_by']),
                'organization': Organization.objects.get(
                    pk=item['organization']),
                'date': item['day'],
            }
            stat, created = UserStatistic.objects.get_or_create(**kwargs)
            stat.num_processes_initiated = item['count']
            stat.save()


def get_data(qs, start_date, date_field, extra_fields):
    """
    Helper function that:
        1) Limits results to after start_date
        2) Group results by day on date_field and annotate with count
    """
    if start_date:
        kwargs = {'{0}__gt'.format(date_field): start_date}
        qs = qs.filter(**kwargs)
    else:
        qs = qs.all()

    truncate = connection.ops.date_trunc_sql('day',
                                             '.'.join([qs.model._meta.db_table,
                                                       date_field]))
    fields = ('day', ) + extra_fields
    return qs.extra({'day': truncate}).values(*fields) \
        .annotate(count=Count('pk'))
