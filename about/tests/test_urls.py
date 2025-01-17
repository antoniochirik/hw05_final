from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_technology(self):
        response = self.guest_client.get(reverse("about:tech"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about/tech.html")

    def test_author(self):
        response = self.guest_client.get(reverse("about:author"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about/author.html")