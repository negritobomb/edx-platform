"""
Registers the "edX Notes" feature for the edX platform.
"""

from django.utils.translation import ugettext as _

from courseware.tabs import EnrolledCourseViewType


class EdxNotesCourseViewType(EnrolledCourseViewType):
    """
    The representation of the edX Notes course view type.
    """

    name = "edxnotes"
    title = _("Notes")
    view_name = "edxnotes"

    @classmethod
    def is_enabled(cls, course, user=None):  # pylint: disable=unused-argument
        """Returns true if the edX Notes feature is enabled in the course.

        Args:
            course (CourseDescriptor): the course using the feature
            settings (dict): a dict of configuration settings
            user (User): the user interacting with the course
        """
        if not super(EdxNotesCourseViewType, cls).is_enabled(course, user=user):
            return False
        return course.edxnotes
