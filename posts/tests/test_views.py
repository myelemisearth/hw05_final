from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ViewsTests(TestCase):
    def setUp(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='testuser')
        self.client = Client()
        self.client.force_login(self.user)
        self.anonym = Client()
        self.group = Group.objects.create(
            title='testgroup', slug='testgroup')
        self.post = Post.objects.create(
            author=self.user, text='Тестовый пост.', group=self.group)
        self.urls = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username,
                    'post_id': self.post.id})
        )

    def test_get_newpost(self):
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(url=url):
                if ('page' not in response.context and
                        'post' not in response.context):
                    raise ValueError(
                            'Response doesnt have page or post in context')
                elif 'page' in response.context:
                    checking_post = response.context['page'][0]
                else:
                    checking_post = response.context['post']
                self.assertEqual(checking_post, self.post)
