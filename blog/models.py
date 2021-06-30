from django.db import models
import os

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    hook_text = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    #blank=True는 해당 필드가 필수가 아니라는 의미

    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)
        #return self.file_upload.name 이렇게 하면 경로가 다 나온다.
    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]
    def __str__(self):
        return f'[{self.pk}]{self.title}'
    #author 추후작성
