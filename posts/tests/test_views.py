from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

GROUP_ON_SLUG = "test-slug"
GROUP_OFF_SLUG = "test-slug-1"
USERNAME = "user1"
INDEX_URL = reverse("index")
GROUP_ON_URL = reverse("group", args=[GROUP_ON_SLUG])
GROUP_OFF_URL = reverse("group", args=[GROUP_OFF_SLUG])
PROFILE_URL = reverse("profile", args=[USERNAME])
NEW_POST_URL = reverse("new_post")
FOLLOW_INDEX_URL = reverse("follow_index")
PROFILE_FOLLOW_URL = reverse("profile_follow", args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse("profile_unfollow", args=[USERNAME])


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_follow = User.objects.create_user(username="Alesha")
        cls.group_on = Group.objects.create(
            title="title",
            slug=GROUP_ON_SLUG,
            description="some information",
        )
        cls.group_off = Group.objects.create(
            title="title",
            slug=GROUP_OFF_SLUG,
            description="some information",
        )
        cls.post = Post.objects.create(
            text="some text",
            author=cls.user,
            group=cls.group_on,
        )
        cls.POST_URL = reverse("post", args=[USERNAME, cls.post.id])
        cls.ADD_COMMENT_URL = reverse(
            "add_comment", args=[USERNAME, cls.post.id])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follow)

    def test_follow_for_authorized(self):
        """ Подписка доступна для авторизованного пользователя """
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        self.assertTrue(Follow.objects.get(user=self.user_follow,
                                           author=self.user))
        #self.assertEqual(self.user_follow, Follow.objects.first().user)

    def test_unfollow_for_authorized(self):
        """ Отписка доступна для подписчика """
        Follow.objects.create(
            user=self.user_follow,
            author=self.user
        )
        self.authorized_client.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(Follow.objects.filter(user=self.user_follow,
                                               author=self.user))

    def test_context_for_posts_pages(self):
        """ Страницы возвращают верный контекст """
        cache.clear()
        Follow.objects.create(
            user=self.user_follow,
            author=self.user
        )
        test_pages = [
            INDEX_URL,
            GROUP_ON_URL,
            PROFILE_URL,
            self.POST_URL,
            FOLLOW_INDEX_URL
        ]
        for url_name in test_pages:
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                if "post" in response.context:
                    response_context = response.context["post"]
                else:
                    response_context = response.context["page"][0]
                expect_context = self.post
                self.assertEqual(response_context, expect_context)

    def test_post_not_in_group_off(self):
        """ Созданный пост не появляется в группе, к которой не привязан """
        response = self.authorized_client.get(GROUP_OFF_URL)
        response_posts = response.context["page"]
        self.assertNotIn(self.post, response_posts)

    def test_cache_index_page(self):
        """ Кэш главной страницы срабатывает правильно """
        response_1 = self.authorized_client.get(INDEX_URL)
        Post.objects.create(
            text="meme_co",
            author=self.user
        )
        # Другой вариант проверки:
        #context_cache = len(response_1.context.get("page").object_list)
        #post_len = Post.objects.count()
        #self.assertNotEqual(context_cache, post_len)
        # cache.clear()
        response_2 = self.authorized_client.get(INDEX_URL)
        #context_cache = len(response_2.context.get("page").object_list)
        #self.assertEqual(context_cache, post_len)
        self.assertHTMLEqual(str(response_1), str(response_2))

    def test_post_for_follow(self):
        """У пользователя в follow появляется пост автора"""
        """на которого он подписан"""
        Follow.objects.create(
            user=self.user_follow,
            author=self.user
        )
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        self.assertIn(self.post, response.context["page"])

    def test_post_for_unfollow(self):
        """ У пользователя в ленте "избранные авторы" нет"""
        """ поста автора, на которого он не подписан"""
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        self.assertFalse(response.context["page"])

    def test_authorized_comments(self):
        """ Авторизованный пользователь может комментить посты """
        form_data = {"text": "test comment"}
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL, data=form_data, follow=True)
        comment = Comment.objects.first()
        # потому что он единственный в базе
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.text, form_data["text"])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        for post_num in range(0, 12):
            Post.objects.create(
                text="some text" + str(post_num),
                author=cls.user,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        """ на первой странице верное значение постов """
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_containse_three_records(self):
        """ на второй странице верное значение постов """
        response = self.guest_client.get(INDEX_URL + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 2)
