from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

GROUP_SLUG = "test-slug"
USERNAME = "user1"
INDEX_URL = reverse("index")
GROUP_URL = reverse("group", args=[GROUP_SLUG])
PROFILE_URL = reverse("profile", args=[USERNAME])
NEW_POST_URL = reverse("new_post")
LOGIN_URL = reverse("login")
FOLLOW_INDEX_URL = reverse("follow_index")
PROFILE_FOLLOW_URL = reverse("profile_follow", args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse("profile_unfollow", args=[USERNAME])


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(username="ne_user2")
        cls.group = Group.objects.create(
            title="TitleTitle",
            slug=GROUP_SLUG,
            description="",
        )
        cls.post = Post.objects.create(
            text="some text",
            author=cls.user,
            group=cls.group,
        )
        cls.POST_URL = reverse(
            "post",
            args=[USERNAME, cls.post.id]
        )
        cls.POST_EDIT_URL = reverse(
            "post_edit",
            args=[USERNAME, cls.post.id]
        )
        cls.ADD_COMMENT_URL = reverse(
            "add_comment",
            args=[USERNAME, cls.post.id]
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user_not_author)

    def test_status_code_for_urls(self):
        """ Страницы возвращают верные коды """
        urls_clients = [
            [INDEX_URL, self.authorized_client, 200],
            [INDEX_URL, self.guest_client, 200],
            [GROUP_URL, self.authorized_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [NEW_POST_URL, self.authorized_client, 200],
            [NEW_POST_URL, self.guest_client, 302],
            [PROFILE_URL, self.guest_client, 200],
            [PROFILE_URL, self.authorized_client, 200],
            [self.POST_URL, self.authorized_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [self.POST_EDIT_URL, self.authorized_client, 200],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [FOLLOW_INDEX_URL, self.authorized_client, 200],
            [PROFILE_UNFOLLOW_URL, self.authorized_client, 302],
            [PROFILE_FOLLOW_URL, self.authorized_client, 302],
            [self.ADD_COMMENT_URL, self.authorized_client, 200]
        ]
        for url, client, code in urls_clients:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, code)

    def test_redirects_for_urls(self):
        """ Срабатывает перенаправление пользователя """
        urls_clients = [
            [NEW_POST_URL,
             self.guest_client,
             LOGIN_URL + "?next=" + NEW_POST_URL],
            [self.POST_EDIT_URL,
             self.guest_client,
             LOGIN_URL + "?next=" + self.POST_EDIT_URL],
            [self.POST_EDIT_URL,
             self.authorized_client2,
             self.POST_URL],
            [PROFILE_FOLLOW_URL,
             self.guest_client,
             LOGIN_URL + "?next=" + PROFILE_FOLLOW_URL],
            [PROFILE_UNFOLLOW_URL,
             self.guest_client,
             LOGIN_URL + "?next=" + PROFILE_UNFOLLOW_URL],
            [FOLLOW_INDEX_URL,
             self.guest_client,
             LOGIN_URL + "?next=" + FOLLOW_INDEX_URL],
            [self.ADD_COMMENT_URL,
             self.guest_client,
             LOGIN_URL + "?next=" + self.ADD_COMMENT_URL]
        ]
        for url, client, redirect_url in urls_clients:
            with self.subTest(url=url):
                response = client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_not_found_page(self):
        """ несуществующая страница возвращает код 404 """
        response = self.authorized_client.get('auf/')
        self.assertEqual(response.status_code, 404)

    def test_templates_posts(self):
        """ страницы используют нужные шаблоны """
        templates_url_names = {
            INDEX_URL: "posts/index.html",
            GROUP_URL: "group.html",
            NEW_POST_URL: "posts/new_post.html",
            self.POST_EDIT_URL: "posts/new_post.html",
            PROFILE_URL: "posts/profile.html",
            self.POST_URL: "posts/post.html",
            FOLLOW_INDEX_URL: "posts/follow.html"
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
