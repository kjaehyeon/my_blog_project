from django.shortcuts import render
from . models import Post

def index(request):
    posts = Post.objects.all().order_by('-pk')
    #views.py에서 db에 쿼리를 날려 원하는 레코드 가져옴
    #oreder_by()로 최신순으로 post나열

    return render(
        request,
        'blog/index.html',
        {
            'posts' : posts,
        }
    )

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'blog/single_post_page.html',
        {
            'post':post,
        }
    )