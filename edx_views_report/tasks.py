import logging
from functools import partial

from celery import task
from django.conf import settings
from django.utils.translation import ugettext_noop

from lms.djangoapps.instructor_task.tasks_helper.runner import run_main_task
from lms.djangoapps.instructor_task.tasks_base import BaseInstructorTask

from .tasks_helper import ViewsReportReport

TASK_LOG = logging.getLogger('edx.celery.task')


@task(base=BaseInstructorTask, routing_key=settings.GRADES_DOWNLOAD_ROUTING_KEY)  # pylint: disable=not-callable
def get_views_report_data(entry_id, xmodule_instance_args):
    """
    Generate views_report reports archive.
    """
    action_name = ugettext_noop('get_views_report_data')
    task_fn = partial(ViewsReportReport.generate, xmodule_instance_args)
    return run_main_task(entry_id, task_fn, action_name)
