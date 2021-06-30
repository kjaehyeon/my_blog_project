from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    #blank=True는 해당 필드가 필수가 아니라는 의미
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def __str__(self):
        return f'[{self.pk}]{self.title}'
    #author 추후작성
