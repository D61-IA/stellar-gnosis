from django.test import TestCase
from catalog.models import CommentFlag
from django.contrib.auth.models import User


class FlaggedCommentModelTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        flagged_comment = CommentFlag.objects.create(
            comment_id=1,
            description="test description",
            violation="unwanted commercial content or spam",
            proposed_by=test_user1
        )
        self.flag_id = flagged_comment.id
        self.user_id = test_user1.id

    def tearDown(self):
        CommentFlag.objects.get(id=self.flag_id).delete()
        User.objects.get(id=self.user_id).delete()

    def test_object_create(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        self.assertEquals(fl_comment.comment_id, 1)
        self.assertEquals(fl_comment.description, "test description")
        self.assertEquals(fl_comment.violation, "unwanted commercial content or spam")
        self.assertEquals(fl_comment.proposed_by.username, 'testuser1')

    def test_comment_id_label(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        field_label = fl_comment._meta.get_field('comment_id').verbose_name
        self.assertEquals(field_label, 'comment id')

    def test_violation_label(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        field_label = fl_comment._meta.get_field('violation').verbose_name
        self.assertEquals(field_label, 'violation')

    def test_description_label(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        field_label = fl_comment._meta.get_field('description').verbose_name
        self.assertEquals(field_label, 'description')

    def test_created_at_label(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        field_label = fl_comment._meta.get_field('created_at').verbose_name
        self.assertEquals(field_label, 'created at')

    def test_proposed_by_label(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        field_label = fl_comment._meta.get_field('proposed_by').verbose_name
        self.assertEquals(field_label, 'proposed by')

    def test_violation_max_length(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)
        max_length = fl_comment._meta.get_field('violation').max_length
        self.assertEquals(max_length, 100)

    def test_get_absolute_url(self):
        fl_comment = CommentFlag.objects.get(id=self.flag_id)

        # return reverse('paper_detail', args=[str(self.id)])
        self.assertEquals(fl_comment.get_absolute_url(), '/catalog/paper/1/')