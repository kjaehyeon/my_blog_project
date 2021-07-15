from django.shortcuts import render
from blog.models import Post
def landing(request):
    recent_post = Post.objects.order_by('-pk')[:3]
    return render(
        request,
        'single_pages/landing.html',
        {
            'recent_post':recent_post
        }
    )

def about_me(request):
    return render(request, 'single_pages/about_me.html')

#single page들은 데이터 베이스와 연결할 필요가 없으므로 render함수 내에 딕셔너리로 인자를 전달할 필요가 없다.