from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Follow

User = get_user_model()


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow_me = User.objects.create_user(username='follow_me')
        cls.follow_you = User.objects.create_user(username='follow_you')
        cls.post = Post.objects.create(
            author=cls.follow_me,
            text='follow-text',
            group=None,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follow_you)

    def test_subscribe_redirect_anonymous_on_login(self):
        """Страница profile/username/follow/ перенаправляет анонима."""

        url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.follow_me.username}
        )
        response = self.guest_client.get(
            url,
            follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={url}'
        )

    def test_subscribe_authorized_user(self):
        """Авторизованный пользователь может подписываться, но не на себя"""

        count = Follow.objects.count()
        follow_self = User.objects.create_user(username='follow_self')
        authorized_client = Client()
        authorized_client.force_login(follow_self)

        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': follow_self.username},
            )
        )
        self.assertEqual(Follow.objects.count(), count)

        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.follow_me.username},
            )
        )
        self.assertEqual(Follow.objects.last().user, follow_self)
        self.assertEqual(Follow.objects.last().author, self.follow_me)

    def test_unsubscribe_authorized_user(self):
        """Авторизованный пользователь может отписываться."""

        Follow.objects.get_or_create(
            user=self.follow_you, author=self.follow_me
        )
        count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.follow_me.username},
            )
        )
        self.assertEqual(Follow.objects.count(), count - 1)

    def test_author_posts_appear_subscribed_user_page(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        response = self.authorized_client.get(reverse('posts:follow_index',))
        self.assertEqual(len(response.context['page_obj']), 0)

        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.follow_me.username},
            )
        )
        response = self.authorized_client.get(reverse('posts:follow_index',))
        post = response.context['page_obj'].object_list[0]
        self.assertEqual(post.text, self.post.text)
