from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    hook_text = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True) #blank=True는 해당 필드가 필수가 아니라는 의미
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) # 사용자 지워지면 포스트 작성자 null로 바뀜
    #author = models.ForeignKey(User, on_delete=models.CASCADE) CASCADE이면 사용자 지워질 때 글도 다 지워짐
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True) #ManyToMany는 기본적으로 null=True이다.

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)
        #return self.file_upload.name 이렇게 하면 경로가 다 나온다.

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return "https://avatars.dicebear.com/api/gridy/"+self.author.username+".svg"

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) #생성될 때 시간저장
    modified_at = models.DateTimeField(auto_now=True) #저장될 때 시간저장

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return "https://avatars.dicebear.com/api/gridy/"+self.author.username+".svg"

    def __str__(self):
        return f'[{self.pk}]{self.author}::{self.content}'




