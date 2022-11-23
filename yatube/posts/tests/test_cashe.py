from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


from posts.models import Post, Group

User = get_user_model()


class postPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='teo')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.post_new = Post.objects.create(
            author=cls.user,
            text='Новый текст',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_show_correct_context(self):
        """Тест для проверки кэширования главной страницы"""
        response = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.filter(pk=self.post_new.id).delete()
        new_response = self.authorized_client.get(reverse(
            'posts:index')).content
        self.assertEqual(response, new_response)
        cache.clear()
        new_response = self.authorized_client.get(reverse(
            'posts:index')).content
        self.assertNotEqual(response, new_response)
