from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='paginator_user')
        cls.group = Group.objects.create(
            title='paginator',
            slug='paginator-slug',
            description='paginator-group'
        )
        posts_list = []
        for i in range(1, 14):
            new_post = Post(
                author=cls.user,
                text='paginator-text',
                group=cls.group,
            )
            posts_list.append(new_post)

        Post.objects.bulk_create(posts_list)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contains_records(self):
        """Проверка пагинации на страницах."""
        COUNT_1 = 10
        COUNT_2 = 3
        records_on_page = {
            reverse('posts:index'): COUNT_1,
            reverse(
                'posts:group_posts', kwargs={'slug': 'paginator-slug'}
            ): COUNT_1,
            reverse(
                'posts:profile', kwargs={'username': 'paginator_user'}
            ): COUNT_1,
            reverse('posts:index') + '?page=2': COUNT_2,
            reverse(
                'posts:group_posts', kwargs={'slug': 'paginator-slug'}
            ) + '?page=2': COUNT_2,
            reverse(
                'posts:profile', kwargs={'username': 'paginator_user'}
            ) + '?page=2': COUNT_2,
        }

        for reverse_name, count_records in records_on_page.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), count_records
                )
                post = response.context['page_obj'].object_list[0]
                self.assertEqual(post.text, 'paginator-text')
                self.assertEqual(post.author.username, 'paginator_user')
                self.assertEqual(post.group.title, 'paginator')
