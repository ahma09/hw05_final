from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{str(PostURLTests.post.pk)}/': 'posts/post_detail.html',
            f'/posts/{str(PostURLTests.post.pk)}/edit/':
            'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists(self):
        """Страница group/slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists(self):
        """Страница profile/username/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/auth/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists(self):
        """Страница posts/post_id/ доступна любому пользователю."""
        response = self.guest_client.get(
            f'/posts/{str(PostURLTests.post.pk)}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url_and_used_template(self):
        """Несуществующая страница и используемый шаблон."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_edit_url_for_author(self):
        """Страница posts/post_id/edit/ доступна только автору."""
        author = User.objects.create_user(username='edit')
        post = Post.objects.create(
            author=author,
            text='edit',
            group=self.group
        )
        self.authorized_client.force_login(author)
        response = self.authorized_client.get(f'/posts/{post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_authorized(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_login(self):
        """Страница create/ перенаправляет анонима."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_url_redirect_anonymous_on_login(self):
        """Страница posts/<int:post_id>/edit/ перенаправляет анонима."""
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )
