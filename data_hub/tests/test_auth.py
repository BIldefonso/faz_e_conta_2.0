from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 302)  # Redirect to index

    def test_logout(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to login