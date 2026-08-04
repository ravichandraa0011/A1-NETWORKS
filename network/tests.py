from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from network.models import (
    Profile, Review, Connection, Message, Post, Comment,
    TopicGroup, GroupMessage, ProjectPortfolio, ProjectReview
)

User = get_user_model()

class NetworkModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='Password123!', first_name='Alice', headline='Engineer')
        self.user2 = User.objects.create_user(username='bob', password='Password123!', first_name='Bob', headline='Designer')

    def test_profile_auto_created_and_saved(self):
        self.assertTrue(hasattr(self.user1, 'profile'))
        self.assertEqual(str(self.user1.profile), 'alice')

    def test_connection_model(self):
        conn = Connection.objects.create(sender=self.user1, receiver=self.user2)
        self.assertFalse(conn.is_accepted)
        self.assertEqual(str(conn), 'alice -> bob (Pending)')

    def test_post_and_like(self):
        post = Post.objects.create(author=self.user1, content='Hello A1 Network!')
        self.assertEqual(str(post), 'Post by alice')
        post.likes.add(self.user2)
        self.assertEqual(post.likes.count(), 1)

    def test_topic_group_and_message(self):
        group = TopicGroup.objects.create(name='python', description='Python Chat', created_by=self.user1)
        group.members.add(self.user1)
        msg = GroupMessage.objects.create(group=group, author=self.user1, content='Hi pythonistas!')
        self.assertEqual(str(group), 'python')
        self.assertEqual(group.messages.count(), 1)

class NetworkViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='Password123!', first_name='Alice', last_name='Smith')
        self.user2 = User.objects.create_user(username='bob', password='Password123!', first_name='Bob', last_name='Jones')

    def test_feed_access(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.get(reverse('network:feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network/feed.html')

    def test_create_post(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:feed'), {
            'content': 'Check out #python and #django!'
        })
        self.assertRedirects(response, reverse('network:feed'))
        self.assertTrue(Post.objects.filter(content__contains='#python').exists())
        self.assertTrue(TopicGroup.objects.filter(name='python').exists())

    def test_like_post_ajax(self):
        post = Post.objects.create(author=self.user2, content='Great day!')
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:like_post', kwargs={'post_id': post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'liked': True, 'like_count': 1})

    def test_add_comment(self):
        post = Post.objects.create(author=self.user2, content='Awesome project')
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:add_comment', kwargs={'post_id': post.id}), {
            'content': 'Looks amazing!'
        })
        self.assertRedirects(response, reverse('network:feed'))
        self.assertTrue(Comment.objects.filter(post=post, author=self.user1).exists())

    def test_send_connection_request(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:send_request', kwargs={'username': 'bob'}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'sent', 'message': 'Request sent!'})
        self.assertTrue(Connection.objects.filter(sender=self.user1, receiver=self.user2).exists())

    def test_accept_connection_request(self):
        conn = Connection.objects.create(sender=self.user1, receiver=self.user2, is_accepted=False)
        self.client.login(username='bob', password='Password123!')
        response = self.client.post(reverse('network:accept_request', kwargs={'connection_id': conn.id}))
        self.assertRedirects(response, reverse('network:my_network'))
        conn.refresh_from_db()
        self.assertTrue(conn.is_accepted)

    def test_directory_view(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.get(reverse('network:directory') + '?q=Bob')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bob')

    def test_profile_view(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.get(reverse('network:profile', kwargs={'username': 'bob'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bob Jones')

    def test_inbox_messaging(self):
        Connection.objects.create(sender=self.user1, receiver=self.user2, is_accepted=True)
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:inbox_chat', kwargs={'username': 'bob'}), {
            'content': 'Hello Bob!'
        })
        self.assertRedirects(response, reverse('network:inbox_chat', kwargs={'username': 'bob'}))
        self.assertTrue(Message.objects.filter(sender=self.user1, receiver=self.user2, content='Hello Bob!').exists())

    def test_toggle_radar(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:toggle_availability'))
        self.assertEqual(response.status_code, 302)
        self.user1.profile.refresh_from_db()
        self.assertTrue(self.user1.profile.is_available_today)

    def test_add_and_delete_project(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('network:add_project'), {
            'title': 'AI Chatbot',
            'description': 'Built an intelligent chatbot assistant.',
            'external_link': 'https://github.com/example/chatbot'
        })
        self.assertRedirects(response, reverse('network:profile', kwargs={'username': 'alice'}))
        project = ProjectPortfolio.objects.get(title='AI Chatbot')
        self.assertEqual(project.owner, self.user1)

        del_resp = self.client.post(reverse('network:delete_project', kwargs={'project_id': project.id}))
        self.assertRedirects(del_resp, reverse('network:profile', kwargs={'username': 'alice'}))
        self.assertFalse(ProjectPortfolio.objects.filter(id=project.id).exists())
