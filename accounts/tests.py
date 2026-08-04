from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsModelAndFormTests(TestCase):
    def test_create_custom_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            first_name='Test',
            last_name='User',
            headline='Software Engineer',
            industry='Technology'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(str(user), 'Test User (@testuser)')
        self.assertEqual(user.headline, 'Software Engineer')

class AccountsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='johndoe',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

    def test_register_view_get(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_view_post_valid(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'headline': 'Developer',
            'industry': 'Tech'
        })
        self.assertRedirects(response, reverse('network:profile', kwargs={'username': 'newuser'}))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'johndoe',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse('accounts:edit_profile'))
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_post_logged_in(self):
        self.client.login(username='johndoe', password='Password123!')
        response = self.client.post(reverse('accounts:edit_profile'), {
            'first_name': 'Johnathan',
            'last_name': 'Doe',
            'headline': 'Senior Cloud Architect',
            'industry': 'Cloud',
            'mobile_number': '+1234567890'
        })
        self.assertRedirects(response, reverse('network:profile', kwargs={'username': 'johndoe'}))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Johnathan')
        self.assertEqual(self.user.headline, 'Senior Cloud Architect')
