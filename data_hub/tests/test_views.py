from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.user.is_staff = True
        self.user.save()

    def test_index_view_authenticated(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_reports_view_authenticated(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financas/reports.html')

    def test_dashboard_alunos_view_authenticated(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('alunos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'alunos/dashboard.html')