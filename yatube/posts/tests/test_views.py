from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

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
        cls.group_blank = Group.objects.create(
            title='blank',
            slug='blank-slug',
            description='blank'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'teo'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, f'{self.post.text}')
        self.assertEqual(first_post.author.username, f'{self.user}')
        self.assertEqual(first_post.group.title, f'{self.group}')
        self.assertEqual(first_post.image, f'{self.post.image}')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, f'{self.post.text}')
        self.assertEqual(first_post.author.username, f'{self.user}')
        self.assertEqual(first_post.group.title, f'{self.group}')
        self.assertEqual(first_post.group.slug, f'{self.group.slug}')
        self.assertEqual(
            first_post.group.description, f'{self.group.description}'
        )
        self.assertEqual(first_post.image, f'{self.post.image}')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_detail = response.context['post']
        self.assertEqual(post_detail.text, f'{self.post.text}')
        self.assertEqual(post_detail.author.username, f'{self.user}')
        self.assertEqual(post_detail.group.title, f'{self.group}')
        self.assertEqual(post_detail.image, f'{self.post.image}')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, f'{self.post.text}')
        self.assertEqual(first_post.author.username, f'{self.user}')
        self.assertEqual(first_post.image, f'{self.post.image}')

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_appears_on_pages(self):
        """
        При создании поста с указанием группы он появляется на странице
        с используемой группой, и не попадает в другую группу
        """
        expected_post = Post.objects.get(id=self.post.pk)
        list_url = {
            'posts:index': None,
            'posts:group_posts': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username},
        }
        for url, arg in list_url.items():
            with self.subTest():
                response = self.authorized_client.get(
                    reverse(url, kwargs=arg)
                )
                self.assertContains(response, expected_post)

        response = self.authorized_client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': self.group_blank.slug}
            )
        )
        self.assertNotContains(response, expected_post)
