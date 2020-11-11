from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class URLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.client = Client()
        self.client.force_login(self.user)
        self.anonym = Client()
        self.first_group = Group.objects.create(
            title='testgroup', slug='testgroup')
        self.second_group = Group.objects.create(
            title='newgroup', slug='newgroup')
        self.post_text = 'Это тестовый пост.'
        self.post_edit_text = 'Это измененный тестовый пост.'
        self.urls = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.first_group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('new_post')
        )

    def test_unfound_pages(self):
        response = self.client.get('/anypage/')
        self.assertEqual(response.status_code, 404)

    def test_get_urls(self):
        for url in self.urls:
            response_client = self.client.get(url)
            response_anonym = self.anonym.get(url, follow=True)
            for response in response_client, response_anonym:
                with self.subTest(url=url):
                    self.assertEqual(response.status_code, 200)
    
    def test_post_newpost(self):
        current_posts_count = Post.objects.count()
        response = self.client.post(
            reverse('new_post'),
            {'text': self.post_text,'group': self.first_group.id},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), current_posts_count + 1)
        post = response.context['page'][0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.first_group)
        self.assertEqual(post.text, self.post_text)
            
    def test_post_editpost(self):
        post = Post.objects.create(
            author=self.user, text=self.post_text, group=self.first_group)
        response = self.client.post(
            reverse('post_edit', kwargs={
                    'username': self.user.username,'post_id': 1}),
            {'text': self.post_edit_text, 'group': self.second_group.id},
            follow=True)
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(response.context['post'], post)
