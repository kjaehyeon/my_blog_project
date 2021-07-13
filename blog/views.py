import re

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .models import Post, Category, Tag
from .forms import CommentForm


class PostList(ListView):
    model = Post
    ordering = '-pk'  # 최신순 포스팅

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['total_post_count'] = Post.objects.count()
        return context
    # template_name = 'blog/post_list.html'
    # Post_list.html파일을 만들거나 template_name을 지정해준다.


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

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['total_post_count'] = Post.objects.count()
        context['comment_form'] = CommentForm
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
            'categories': Category.objects.all(),  # 카테고리 위젯 채우기 위해 보내줌
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,  # 페이지 타이틀 옆 카테고리 이름 알려준다.
            'total_post_count': Post.objects.count(),
        }
    )


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),  # 카테고리 위젯 채우기 위해 보내줌
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'total_post_count': Post.objects.count(),
            'tag': tag,
        }
    )


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):  # 포스트의 작성자 자동으로 들어가게 함
        current_user = self.request.user  # 웹사이트의 방문자 가져옴
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):  # 로그인 한 상태인지 검사
            form.instance.author = current_user  # form에서 생성한 instance의 author필드에 current user를 담는다.
            response = super(PostCreate, self).form_valid(form)
            # Post와 Tag는 다대다 관계이므로 db에 Post레코드가 존재해야한다. 그래서 CreateView의 form_valid함수를 사용하고 결과를 response에 저장해둠
            tags_str = self.request.POST.get('tags_str')  # post방식으로 전달된 정보 중 name이 tags_str인 input의 값을 가져온다.
            if tags_str:
                tags_str = tags_str.strip()
                tags_str_list = re.split(r'[,;#]', tags_str)

                for t in tags_str_list:
                    if t != "":
                        t = t.strip()
                        tag, is_tag_created = Tag.objects.get_or_create(name=t)

                        if is_tag_created:
                            tag.slug = slugify(t, allow_unicode=True)
                            tag.save()
                        self.object.tags.add(tag)

            return response
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'

    # CreateView와 UpdateView는 모두 _form.html이 붙은 템플릿 파일을 사용하므로 지금 PostUpdate에서 post_form.html을 자동으로 가져오는데 이를
    # 변경시키기 위해 template_name을 설정한다.

    def dispatch(self, request, *args, **kwargs):  # 방문자가 포스트의 작성자가 맞는지 확인함
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied  # 권한이 없는 방문자가 타인의 포스트 수정하려하면 403오류 메시지

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tag_list = list()
            for t in self.object.tags.all():
                tag_list.append(t.name)
            context['tags_str_default'] = '; '.join(tag_list)

        return context

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')  # post방식으로 전달된 정보 중 name이 tags_str인 input의 값을 가져온다.
        if tags_str:
            tags_str = tags_str.strip()

            tags_str_list = re.split(r'[;,#]', tags_str)

            for t in tags_str_list:
                if t != "":
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)

                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

        return response


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                return redirect(comment.get_absolute_url())
        else:  # post방식이 아니라 get방식으로(주소창에 직접 new_comment/ 로 요청한 경우)요청받으면 그냥 포스트화면으로 리다이렉트 해준다.
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied
