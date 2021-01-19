from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="anton")
        cls.group = Group.objects.create(
            title="ж" * 50,
            description="фрфрфр",
        )
        cls.post = Post.objects.create(
            text="some text, some text, some text",
            author=cls.user,
            group=cls.group
        )

    def test_labels(self):
        """ Поля модели имеют верные имена """
        lable_post = self.post
        verbose_names = {
            "text": "Текст записи",
            "group": "Группа"
        }
        for name, verbose in verbose_names.items():
            with self.subTest(name=name):
                verbose_text = lable_post._meta.get_field(name).verbose_name
                self.assertEquals(verbose_text, verbose)

    def test_helpname_post(self):
        """ Поля формы имеют верные helpnames """
        help_post = self.post
        help_names = {
            "text": "Пиши что хочешь и сколько хочешь."
                    "Цензура сегодня не для нас.",
            "group": "Группа из существующих"
        }
        for name, helps in help_names.items():
            with self.subTest(name=name):
                help_text = help_post._meta.get_field(name).help_text
                self.assertEquals(help_text, helps)

    def test_str_methods(self):
        """ При переводе в строку модели отображаются верно """
        str_post = self.post.__str__()
        str_group = self.group.__str__()
        strs = {
            "some text, some": str_post,
            self.group.title: str_group 
        }
        for string, method in strs.items():
            with self.subTest(string=string):
                self.assertEquals(method, string)
