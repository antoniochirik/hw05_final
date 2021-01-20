from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Группа", max_length=200)
    slug = models.SlugField(max_length=70, unique=True)
    description = models.TextField("Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст записи",
                            help_text="Пиши что хочешь и сколько хочешь."
                                      "Цензура сегодня не для нас.")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name="posts",
                              verbose_name="Группа",
                              help_text="Группа из существующих")
    image = models.ImageField(upload_to="posts/", blank=True,
                              null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments",
                             verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор")
    text = models.TextField("Текст комментария",
                            help_text="Скажи что-нибудь по этому поводу")
    created = models.DateTimeField("Дата комментирования", auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "author"],
                name="following")
        ]
