import logging
from datetime import datetime
from time import time

from courseware.courses import get_course_by_id
from courseware.models import StudentModule
from lms.djangoapps.instructor_task.tasks_helper.runner import TaskProgress
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_structures.models import CourseStructure
from pytz import UTC
from student.models import CourseEnrollment

from django.contrib.auth.models import User

from utils import upload_csv_to_report_store

log = logging.getLogger(__name__)


class ViewsReportReport(object):
    @classmethod
    def generate(cls, _xmodule_instance_args, _entry_id, course_id, task_input, action_name):
        start_time = time()
        start_date = datetime.now(UTC)
        num_reports = 1
        task_progress = TaskProgress(action_name, num_reports, start_time)

        enrolled_students = CourseEnrollment.objects.users_enrolled_in(course_id, include_inactive=True)

        current_step = {'step': 'Calculating views report'}
        rows = cls._get_vr(course_id, enrolled_students)
        upload_csv_to_report_store(rows, 'views_report', course_id, start_date, config_name='GRADES_DOWNLOAD')
        task_progress.update_task_state(extra_meta=current_step)

        return task_progress.update_task_state(extra_meta=current_step)

    @classmethod
    def _get_vr(cls, course_id, enrolled_students):
        headers = ('user_id', 'email', 'viewed', 'subsection')
        rows = []
        structure = CourseStructure.objects.get(course_id=course_id).ordered_blocks

        course = get_course_by_id(course_id)
        chapters = [chapter for chapter in course.get_children() if not chapter.hide_from_toc]
        vertical_map = []

        for chapter in chapters:
            sequentials = chapter.children
            for sequential in sequentials:
                vertical_map.append(sequential)

        def _viewed(_subsection, _student):
            _sm = StudentModule.objects.filter(student=_student,
                                               module_state_key=_subsection
                                               ).first()
            if _sm:
                return 1
            return 0

        for student in enrolled_students:
            for subsection in vertical_map:
                rows.append([
                    student.id,
                    User.objects.get(student.id).email,
                    _viewed(subsection, student),
                    structure[str(subsection)]["display_name"],
                ])
        rows.insert(0, headers)
        return rows

    @classmethod
    def _get_course_json_data(cls, course_id):
        course = CourseKey.from_string(str(course_id))
        course_data = {
            "short_name": "+".join([course.org, course.course, course.run]),
            "long_name": get_course_by_id(CourseKey.from_string(str(course_id))).display_name
        }
        return course_data
