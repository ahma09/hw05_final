from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестслаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост про изучение тестов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        group = PostModelTest.group
        post = PostModelTest.post
        title = group.title
        text = post.text[:15]
        self.assertEqual(title, str(group))
        self.assertEqual(text, str(post))
        self.assertEqual(
            post._meta.get_field('text').verbose_name, 'Текст поста'
        )
        self.assertEqual(
            post._meta.get_field('text').help_text, 'Введите текст поста'
        )
        self.assertEqual(
            post._meta.get_field('group').verbose_name, 'Группа поста'
        )
        self.assertEqual(
            post._meta.get_field('group').help_text, 'Выбрать группу для поста'
        )
