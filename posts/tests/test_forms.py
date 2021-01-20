import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

USERNAME = "antonio"
INDEX_URL = reverse("index")
NEW_POST_URL = reverse("new_post")


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title="title",
            slug="slug-test",
            description="some information",
        )
        cls.group_off = Group.objects.create(
            title="title1",
            slug="slug-test-1",
            description="some information",
        )
        cls.post = Post.objects.create(
            text="some text",
            author=cls.user,
            group=cls.group,
        )
        cls.POST_URL = reverse("post", args=[USERNAME, cls.post.id])
        cls.POST_EDIT_URL = reverse(
            "post_edit",
            args=[USERNAME, cls.post.id]
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """ Пост появляется в базе с верными аргументами, картинка загружается"""
        tasks_count = Post.objects.count()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        form_data = {
            "text": "text text",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        created_post = Post.objects.exclude(id=self.post.id)[0]
        self.assertEqual(created_post.group, self.group)
        self.assertEqual(created_post.author, self.user)
        self.assertEqual(created_post.text, form_data["text"])
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertEqual(created_post.image.file.read(),
                         form_data['image'].file.getvalue())

    def test_edit_post(self):
        """ Пост обновляется в базе """
        tasks_count = Post.objects.count()
        form_data = {
            "text": "correct text!",
            "group": self.group_off.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True,
        )
        post_edited = response.context["post"]
        self.assertEqual(post_edited.text, form_data["text"])
        self.assertEqual(post_edited.group, self.group_off)
        self.assertEqual(post_edited.author, self.user)
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(Post.objects.count(), tasks_count)

    def test_forms_new_and_edit(self):
        """ Поля формы имеют верные значения """
        urls = [NEW_POST_URL, self.POST_EDIT_URL]
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    form_field = response.context["form"].fields.get(value)
                    self.assertIsInstance(form_field, expected)
