#from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . models import Post

class PostList(ListView):
    model = Post
    ordering = '-pk' #최신순 포스팅
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
class single_post_page(DetailView):
    model = Post
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