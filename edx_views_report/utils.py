from eventtracking import tracker
from lms.djangoapps.instructor_task.models import ReportStore
from lms.djangoapps.instructor_task.tasks_helper.utils import tracker_emit
from util.file import course_filename_prefix_generator

REPORT_REQUESTED_EVENT_NAME = u'edx.instructor.report.requested'

# define value to use when no task_id is provided:
UNKNOWN_TASK_ID = 'unknown-task_id'

# define values for update functions to use to return status to perform_module_state_update
UPDATE_STATUS_SUCCEEDED = 'succeeded'
UPDATE_STATUS_FAILED = 'failed'
UPDATE_STATUS_SKIPPED = 'skipped'


def upload_csv_to_report_store(rows, csv_name, course_id, timestamp, config_name='GRADES_DOWNLOAD'):
    report_store = ReportStore.from_config(config_name)
    report_name = u"{course_prefix}_{csv_name}_{timestamp_str}.csv".format(
        course_prefix=course_filename_prefix_generator(course_id),
        csv_name=csv_name,
        timestamp_str=timestamp.strftime("%Y-%m-%d-%H%M")
    )

    report_store.store_rows(course_id, report_name, rows)
    tracker_emit(csv_name)
    return report_name


def tracker_emit(report_name):
    tracker.emit(REPORT_REQUESTED_EVENT_NAME, {"report_type": report_name, })
