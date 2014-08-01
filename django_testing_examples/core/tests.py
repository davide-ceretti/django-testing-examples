import time

from django.test import TestCase
from django.contrib.auth.models import User

from model_mommy import mommy
from mock import patch, Mock

from core.models import Article, Blog


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '{0:.5f} sec'.format(te-ts)
        return result
    return timed


class TestGetArticlesBlankTitle(TestCase):
    @timeit
    def test_vanilla_django(self):
        """
        0.02883 sec [sqlite in memory]
        """
        blog = Blog.objects.create(title='Blog title')
        user = User.objects.create_user(username='user', password='pass')
        article_kwargs = {
            'blog': blog,
            'creator': user,
            'body': 'body',
        }
        Article.objects.create(title='title_one', **article_kwargs)
        Article.objects.create(title='title_two', **article_kwargs)
        three = Article.objects.create(**article_kwargs)

        articles = Article.get_set_of_articles_blank_title()

        self.assertSetEqual(articles, {three})

    @timeit
    def test_model_mommy(self):
        """
        0.00435 sec [sqlite in memory]
        """
        mommy.make(Article, title='title', _quantity=2)
        three = mommy.make(Article, title='')

        articles = Article.get_set_of_articles_blank_title()

        self.assertSetEqual(articles, {three})

    @timeit
    @patch('core.models.Article.objects')
    def test_patch_orm(self, objects):
        """
        0.00029 sec [sqlite in memory]
        """
        result = Mock()
        objects.filter.return_value = [result]

        articles = Article.get_set_of_articles_blank_title()

        self.assertSetEqual(articles, {result})
        objects.filter.assert_called_with(title='')


class TestUpdateAllArticlesWithBlankTitle(TestCase):
    @timeit
    def test_model_mommy_v1_v2_v3(self):
        """
        v1 0.00429 sec [sqlite in memory]
        v2 0.00490 sec [sqlite in memory]
        v3 0.00557 sec [sqlite in memory]
        """
        mommy.make(Article, title='title', _quantity=2)
        three, four = mommy.make(Article, title='', _quantity=2)

        Article.update_all_articles_with_blank_title_v1('new_val')

        new_val_articles = Article.objects.filter(title='new_val')
        new_val_ids = set(new_val_articles.values_list('id', flat=True))

        self.assertSetEqual(new_val_ids, {three.id, four.id})

    @timeit
    @patch('core.models.Article.objects')
    def test_patch_orm_v1(self, objects):
        """
        0.00038 sec [sqlite in memory]
        """
        articles = Mock()
        objects.filter.return_value = articles

        Article.update_all_articles_with_blank_title_v1('new_val')

        objects.filter.assert_called_with(title='')
        articles.update.assert_called_with(title='new_val')

    @timeit
    @patch('core.models.Article.objects')
    def test_patch_orm_v2(self, objects):
        """
        0.00050 sec [sqlite in memory]
        """
        first_article = Mock()
        second_article = Mock()
        objects.filter.return_value = [first_article, second_article]

        Article.update_all_articles_with_blank_title_v2('new_val')

        objects.filter.assert_called_with(title='')
        first_article.title = 'new_val'
        first_article.save.assert_called_with()
        second_article.title = 'new_val'
        second_article.save.assert_called_with()
