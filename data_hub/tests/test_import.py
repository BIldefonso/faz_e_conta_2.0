from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ImportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='test')
        # O nome do modelo deve existir na tua app, por exemplo 'Aluno'
        self.model_name = 'Aluno'

    def test_import_csv_preview(self):
        csv_content = "id,nome_proprio,apelido,idade\n1,Ana,Silva,10\n2,Bruno,Costa,12"
        file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'), content_type="text/csv")
        response = self.client.post(
            reverse('import_data'),
            {'file': file, 'model': self.model_name}
        )
        self.assertContains(response, "Preview Data")
        self.assertContains(response, "Ana")
        self.assertContains(response, "Bruno")

    def test_import_json_preview(self):
        json_content = json.dumps([
            {"id": 1, "nome_proprio": "Ana", "apelido": "Silva", "idade": 10},
            {"id": 2, "nome_proprio": "Bruno", "apelido": "Costa", "idade": 12}
        ])
        file = SimpleUploadedFile("test.json", json_content.encode('utf-8'), content_type="application/json")
        response = self.client.post(
            reverse('import_data'),
            {'file': file, 'model': self.model_name}
        )
        self.assertContains(response, "Preview Data")
        self.assertContains(response, "Ana")
        self.assertContains(response, "Bruno")