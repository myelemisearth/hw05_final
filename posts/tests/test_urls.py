from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


class URLTests(TestCase):


    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='testuser')
        self.client = Client()
        self.client.force_login(self.user)
        self.anonym = Client()
        self.follow_user = User.objects.create_user(username='test_follower')
        self.follower_client = Client()
        self.follower_client.force_login(self.follow_user)
        self.first_group = Group.objects.create(
            title='testgroup', slug='testgroup')
        self.second_group = Group.objects.create(
            title='newgroup', slug='newgroup')
        self.POST_TEXT = 'Это тестовый пост.'
        self.POST_EDIT_TEXT = 'Это измененный тестовый пост.'
        self.urls = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.first_group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('new_post')
        )


    def test_get_urls(self):
        for url in self.urls:
            response_client = self.client.get(url)
            response_anonym = self.anonym.get(url, follow=True)
            for response in response_client, response_anonym:
                with self.subTest(url=url):
                    self.assertEqual(response.status_code, 200)


    def test_post_add(self):
        current_posts_count = Post.objects.count()
        response = self.client.post(
            reverse('new_post'), {
                'text': self.POST_TEXT, 'group': self.first_group.id},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), current_posts_count + 1)
        post = response.context['page'][0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.first_group)
        self.assertEqual(post.text, self.POST_TEXT)


    def test_post_edit(self):
        post = Post.objects.create(
            author=self.user, text=self.POST_TEXT, group=self.first_group)
        response = self.client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username, 'post_id': post.id}),
            {'text': self.POST_EDIT_TEXT, 'group': self.second_group.id},
            follow=True)
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.second_group)
        self.assertEqual(post.text, self.POST_EDIT_TEXT)


    def test_comment_url(self):
        post = Post.objects.create(
            author=self.user, text=self.POST_TEXT, group=self.first_group)
        url = reverse('add_comment', kwargs={
            'username': post.author.username, 'post_id': post.id })
        response_anon = self.anonym.get(
            reverse('add_comment', kwargs={
            'username': post.author.username, 'post_id': post.id }))
        response_client = self.client.get(
            reverse('add_comment', kwargs={
            'username': post.author.username, 'post_id': post.id }))
        with self.subTest():
            self.assertEqual(response_client.status_code, 200)
            self.assertRedirects(
                response_anon, reverse('login')+'?next='+url, 302, 200)


    def test_following(self):
        response = self.follower_client.get(
            reverse('profile_follow', kwargs={
                'username': self.user.username}))
        self.assertRedirects(
            response, reverse('profile', kwargs={
                'username': self.user}), 302, 200)
        relation = Follow.objects.filter(author=self.user, user=self.follow_user).exists()
        self.assertTrue(relation, 'Подписка не создалась')


    def test_unfollowing(self):
        relation = Follow.objects.create(
            author=self.user, user=self.follow_user)
        response = self.follower_client.get(
            reverse('profile_unfollow', kwargs={
                'username': self.user.username}))
        self.assertRedirects(
            response, reverse('profile', kwargs={
                'username': self.user}), 302, 200)
        check_relation = Follow.objects.filter(author=self.user, user=self.follow_user).exists()
        self.assertFalse(check_relation, 'Подписка не удалилась')
