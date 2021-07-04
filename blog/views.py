from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . models import Post, Category


class PostList(ListView):
    model = Post
    ordering = '-pk' #최신순 포스팅

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
    #template_name = 'blog/post_list.html'
    #Post_list.html파일을 만들거나 template_name을 지정해준다.
# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#     #views.py에서 db에 쿼리를 날려 원하는 레코드 가져옴
#     #oreder_by()로 최신순으로 post나열
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts' : posts,
#         }
#     )

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(), #카테고리 위젯 채우기 위해 보내줌
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category, #페이지 타이틀 옆 카테고리 이름 알려준다.
        }
    )

class PostDetail(DetailView):
    model = Post
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post':post,
#         }
#     )