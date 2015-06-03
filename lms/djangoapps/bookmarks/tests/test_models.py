"""
Tests for Bookmarks models.
"""
import copy
import datetime
import ddt
from freezegun import freeze_time
import mock
import pytz

from opaque_keys.edx.locator import CourseLocator, BlockUsageLocator

from bookmarks.models import Bookmark, XBlockCache
from student.tests.factories import UserFactory

from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase


@ddt.ddt
class BookmarkModelTest(ModuleStoreTestCase):
    """
    Test the Bookmark model.
    """
    def setUp(self):
        super(BookmarkModelTest, self).setUp()

        self.user = UserFactory.create(password='test')

        self.course = CourseFactory.create(display_name='An Introduction to API Testing')
        self.course_id = unicode(self.course.id)

        self.chapter = ItemFactory.create(
            parent_location=self.course.location, category='chapter', display_name='Week 1'
        )
        self.sequential = ItemFactory.create(
            parent_location=self.chapter.location, category='sequential', display_name='Lesson 1'
        )
        self.vertical = ItemFactory.create(
            parent_location=self.sequential.location, category='vertical', display_name='Subsection 1'
        )
        self.vertical_2 = ItemFactory.create(
            parent_location=self.sequential.location, category='vertical', display_name='Subsection 2'
        )

        self.path = [
            {'display_name': self.chapter.display_name, 'usage_id': unicode(self.chapter.location)},
            {'display_name': self.sequential.display_name, 'usage_id': unicode(self.sequential.location)}
        ]

    def get_bookmark_data(self, block):
        """
        Returns bookmark data for testing.
        """
        return {
            'user': self.user,
            'usage_key': block.location,
            'course_key': self.course.id,
            'display_name': block.display_name,
        }

    def assert_valid_bookmark(self, bookmark, bookmark_data):
        """
        Check if the given data matches the specified bookmark.
        """
        self.assertEqual(bookmark.user, bookmark_data['user'])
        self.assertEqual(unicode(bookmark.usage_key), unicode(bookmark_data['usage_key']))
        self.assertEqual(bookmark.course_key, bookmark_data['course_key'])
        self.assertEqual(bookmark.display_name, bookmark_data['display_name'])
        self.assertEqual(bookmark.path, self.path)
        self.assertIsNotNone(bookmark.created)

        self.assertEqual(bookmark.xblock_cache.course_key, bookmark_data['course_key'])
        self.assertEqual(bookmark.xblock_cache.display_name, bookmark_data['display_name'])

    def test_create_bookmark_success(self):
        """
        Tests creation of bookmark.
        """
        bookmark_data = self.get_bookmark_data(self.vertical)
        bookmark = Bookmark.create(bookmark_data)
        self.assert_valid_bookmark(bookmark, bookmark_data)

        bookmark_data_different_values = self.get_bookmark_data(self.vertical)
        bookmark_data_different_values['display_name'] = 'Introduction Video'
        bookmark2 = Bookmark.create(bookmark_data_different_values)
        # The bookmark object already created should have been returned without modifications.
        self.assertEqual(bookmark, bookmark2)
        self.assertEqual(bookmark.xblock_cache, bookmark2.xblock_cache)
        self.assert_valid_bookmark(bookmark2, bookmark_data)

        bookmark_data_different_user = self.get_bookmark_data(self.vertical)
        bookmark_data_different_user['user'] = UserFactory.create()
        bookmark3 = Bookmark.create(bookmark_data_different_user)
        self.assertNotEqual(bookmark, bookmark3)
        self.assert_valid_bookmark(bookmark3, bookmark_data_different_user)

    @ddt.data(
        (None, 2),
        ([[{'usage_id': 'usage_id1'}]], 1),
        ([[{'usage_id': 'usage_id1'}], [{'usage_id': 'usage_id2'}]], 2),
    )
    @ddt.unpack
    @mock.patch('bookmarks.models.Bookmark.get_path_data')
    def test_calls_to_get_path_data(self, paths, call_count, mock_get_path_data):

        path = [
            {'usage_id': unicode(self.chapter.location), 'display_name': self.chapter.display_name }
        ]
        mock_get_path_data.return_value = path

        bookmark_data = self.get_bookmark_data(self.vertical)
        bookmark = Bookmark.create(bookmark_data)
        self.assertIsNotNone(bookmark.xblock_cache)
        self.assertEqual(mock_get_path_data.call_count, 1)

        bookmark.xblock_cache.paths = paths
        bookmark.xblock_cache.save()

        bookmark = Bookmark.create(bookmark_data)
        self.assertEqual(mock_get_path_data.call_count, call_count)

    @ddt.data(
        (-30, [[{'usage_id': 'usage_id'}]], False, 1),
        (30, None, False, 2),
        (30, None, True, 1),
        (30, [], False, 2),
        (30, [[{'usage_id': 'usage_id'}]], False, 1),
        (30, [[{'usage_id': 'usage_id'}], [{'usage_id': 'usage_id2'}]], False, 2),
    )
    @ddt.unpack
    @mock.patch('bookmarks.models.Bookmark.get_path_data')
    def test_updated_path(self, seconds_delta, paths, alter_usage_key, get_path_data_call_count, mock_get_path_data):

        block_path = [{'usage_id': 'usage_id'}]
        mock_get_path_data.return_value = block_path

        bookmark_data = self.get_bookmark_data(self.vertical)
        bookmark = Bookmark.create(bookmark_data)
        self.assertIsNotNone(bookmark.xblock_cache)

        modification_datetime = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=seconds_delta)
        with freeze_time(modification_datetime):
            bookmark.xblock_cache.paths = paths
            bookmark.xblock_cache.save()

        if alter_usage_key:
            bookmark.usage_key = bookmark.usage_key.replace(category='video')
            bookmark.save()

        self.assertEqual(bookmark.updated_path, block_path)
        self.assertEqual(mock_get_path_data.call_count, get_path_data_call_count)


@ddt.ddt
class XBlockCacheModelTest(ModuleStoreTestCase):
    """
    Test the XBlockCache model.
    """

    COURSE_KEY = CourseLocator(org='test', course='test', run='test')
    CHAPTER1_USAGE_KEY = BlockUsageLocator(COURSE_KEY, block_type='chapter', block_id='chapter1')
    SECTION1_USAGE_KEY = BlockUsageLocator(COURSE_KEY, block_type='section', block_id='section1')
    SECTION2_USAGE_KEY = BlockUsageLocator(COURSE_KEY, block_type='section', block_id='section1')
    VERTICAL1_USAGE_KEY = BlockUsageLocator(COURSE_KEY, block_type='vertical', block_id='sequential1')
    PATH1 = [
        {'usage_key': unicode(CHAPTER1_USAGE_KEY), 'display_name': 'Chapter 1'},
        {'usage_key': unicode(SECTION1_USAGE_KEY), 'display_name': 'Section 1'},
    ]
    PATH2 = [
        {'usage_key': unicode(CHAPTER1_USAGE_KEY), 'display_name': 'Chapter 1'},
        {'usage_key': unicode(SECTION2_USAGE_KEY), 'display_name': 'Section 2'},
    ]

    def setUp(self):
        super(XBlockCacheModelTest, self).setUp()

    def assert_xblock_cache_data(self, xblock_cache, data):
        self.assertEqual(xblock_cache.usage_key, data['usage_key'])
        self.assertEqual(xblock_cache.course_key, data['usage_key'].course_key)
        self.assertEqual(xblock_cache.display_name, data['display_name'])

        for index, path in enumerate(data.get('paths', [])):
            for depth, node in enumerate(path):
                self.assertDictEqual(xblock_cache.paths[index][depth], node)

    @ddt.data(
        (
            [
                { 'usage_key': VERTICAL1_USAGE_KEY, },
                { 'display_name': '', 'paths': [], },
            ],
            [
                { 'usage_key': VERTICAL1_USAGE_KEY, 'display_name': 'Vertical 5', 'paths': [ PATH2 ] },
                { 'paths': [ PATH2 ] },
            ],
        ),
        (
            [
                { 'usage_key': VERTICAL1_USAGE_KEY, 'display_name': 'Vertical 4', 'paths': [ PATH1 ] },
                { },
            ],
            [
                { 'usage_key': VERTICAL1_USAGE_KEY, 'display_name': 'Vertical 5', 'paths': [ PATH2 ] },
                { 'paths': [ PATH1, PATH2 ] },
            ],
        ),
    )
    def test_create(self, data):
        """
        Test XBlockCache.create() constructs and updates objects correctly.
        """
        for create_data, additional_data_to_expect in data:
            xblock_cache = XBlockCache.create(create_data)
            create_data.update(additional_data_to_expect)
            self.assert_xblock_cache_data(xblock_cache, create_data)
