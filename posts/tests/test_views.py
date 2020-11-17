from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from PIL import Image

from posts.models import Follow, Group, Post, User


class ViewsTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='testuser')
        self.client = Client()
        self.client.force_login(self.user)
        self.anonym = Client()
        self.follow_user = User.objects.create_user(username='test_follower')
        self.follower_client = Client()
        self.follower_client.force_login(self.follow_user)
        self.unfollow_user = User.objects.create_user(
            username='test_unfollower')
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.unfollow_user)
        self.POST_TEXT = 'Это тестовый пост.'
        self.group = Group.objects.create(
            title='testgroup', slug='testgroup')
        self.urls = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}), 
            reverse('post', kwargs={'username': self.user.username,
                    'post_id': 1})
        )

    def test_get_newpost(self):
        post = Post.objects.create(
            author=self.user, text=self.POST_TEXT, group=self.group)
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertTrue('post' in response.context
                                or 'page' in response.context)
                if 'page' in response.context:
                    checking_post = response.context['page'][0]
                elif 'post' in response.context:
                    checking_post = response.context['post']
                self.assertEqual(checking_post, post)

    def test_image_check(self):
        image = Image.new('L', (20, 20), color=0)
        uploaded_file = SimpleUploadedFile(
            'image.jpg',
            image.tobytes('jpeg', 'L'),
            'image/jpeg'
        )
        response = self.client.post(
            reverse('new_post'), {
                'author': self.user.username,
                'group': self.group.id,
                'text': self.POST_TEXT,
                'image': uploaded_file},
            follow=True)
        self.assertEqual(response.status_code, 200)
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertContains(response, 'img', status_code=200)

    def test_incorrect_img_upload(self):
        fake_image = b'a'
        uploaded_file = SimpleUploadedFile(
            'image.jpg',
            fake_image,
            'image/jpeg'
        )
        error = ('Загрузите правильное изображение. '
                 'Файл, который вы загрузили, '
                 'поврежден или не является изображением.')
        response = self.client.post(
            reverse('new_post'), {
                'author': self.user.username,
                'group': self.group.id,
                'text': self.POST_TEXT,
                'image': uploaded_file},
            follow=True)
        self.assertFormError(
            response, form='form', field='image', errors=error)

    def test_check_follow_posts(self):
        post = Post.objects.create(
            author=self.user, text=self.POST_TEXT, group=self.group)
        relation = Follow.objects.create(
            author=self.user, user=self.follow_user)
        url = reverse('follow_index')
        response_follower = self.follower_client.get(url)
        response_unfollower = self.unfollower_client.get(url)
        self.assertEqual(response_follower.context['page'][0], post)
        self.assertTrue(len(response_unfollower.context['page']) == 0)

    def test_cache_page(self):
        get_cache = self.client.get(reverse('index'))
        post = Post.objects.create(
            author=self.user, text=self.POST_TEXT, group=self.group)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.content, get_cache.content)
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['page'][0], post)
