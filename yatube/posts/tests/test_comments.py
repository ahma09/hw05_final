from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Comment

User = get_user_model()


class CommentsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='comments_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='form-text',
            group=None,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='first-comment',
            post=cls.post,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        comments_count = Comment.objects.count()
        comments_data = {
            'text': 'comments-text',
            'pk': self.post.pk,
        }

        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comments_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        expected_comment = Comment.objects.latest("id")
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertContains(response, expected_comment)
