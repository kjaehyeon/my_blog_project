from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create(username='trump', password='somepassword')
        self.user_obama = User.objects.create(username='obama', password='somepassword')

        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트',
            content='첫 번째 글',
            author=self.user_trump,
            category=self.category_programming
        )
        self.post_001.tags.add(self.tag_hello)
        self.post_002 = Post.objects.create(
            title='두 번째 포스트',
            content='두 번째 글',
            author=self.user_obama,
            category=self.category_music
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트',
            content='세 번째 글',
            author=self.user_obama,
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            content='첫번째 댓글',
            author=self.user_obama
        )

    def category_card_test(self, soup):
        category_card = soup.find('div', id='category-card')
        self.assertIn('Categories', category_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})',
                      category_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})',
                      category_card.text)
        self.assertIn(f'미분류 (1)', category_card.text)

    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.nav_bar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        post_001_card = soup.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)

        post_002_card = soup.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)

        post_003_card = soup.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)

        self.assertIn(self.user_obama.username, main_area.text)
        self.assertIn(self.user_trump.username, main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있다.
        # 1.2 포스트의 url은 '/blog/1/'이다
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2 포스트의 상세페이지 테스트
        # 2.1 첫번째 포스트의 url로 접근하면 정상작동한다.
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 포스트 목록 페이지와 같은 네비게이션 바가 있다.
        self.nav_bar_test(soup)
        self.category_card_test(soup)
        # 2.3 첫번째 포스트의 제목이 브라우저 탭 타이틀에 있다.
        self.assertIn(self.post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 post_area에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        # 2.5 첫번째 포스트의 작성자가 포스트 영역에 있다.
        self.assertIn(self.post_001.author.username, post_area.text)
        # 2.6 첫번째 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertNotIn(self.tag_python_kor.name, main_area.text)
        self.assertNotIn(self.tag_python.name, main_area.text)

        #comment area
        comment_area= soup.find('section', id='comment-area')
        comment_001_area = comment_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def nav_bar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do it Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_btn.attrs['href'], '/about_me/')

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.category_card_test(soup)
        self.nav_bar_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.category_card_test(soup)
        self.nav_bar_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # login하지 않은 상태
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # trump가 login하고 난 후
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # obama가 login하고 난 후
        self.client.login(username=self.post_003.author.username, password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tags_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tags_str_input)

        # 포스트를 작성한 후 제출한 경우
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post form 만들기',
                'content': "Post form 페이지를 만듭시다.",
                'tags_str': "New Tag; 한글태그, python"
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, 'Post form 만들기')
        self.assertEqual(last_post.author.username, 'trump')

        self.assertIn(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='New Tag'))
        self.assertTrue(Tag.objects.get(name='한글태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_test(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        #로그인 했지만 작성자가 아닌경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username=self.user_trump.username, password='somepassword')
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        #작성자가 접근하는 경우
        self.client.login(username=self.post_003.author.username, password='somepassword')
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tags_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tags_str_input)
        self.assertIn('파이썬 공부;한글태그, some tag', tags_str_input.attrs['value'])


        response = self.client.post(
            update_post_url,
            {
                'title' : '세번째 포스트 수정',
                'content' : '수정완료',
                'category' : self.category_music.pk,
                'tags_str' : '파이썬 공부;한글태그, some tag'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세번째 포스트 수정', main_area.text)
        self.assertIn('수정완료', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글태그', main_area.text)
        self.assertIn('some tag', main_area.text)


