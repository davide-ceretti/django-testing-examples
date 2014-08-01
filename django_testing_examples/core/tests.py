import time

from django.test import TestCase
from django.contrib.auth.models import User

from model_mommy import mommy
from mock import patch, Mock

from core.models import Article, Blog


def time_method(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '{0:.5f} sec'.format(te-ts)
        return result
    return timed


def time_test_methods(cls):
    class NewClass(cls):
        def __getattribute__(self, attr_name):
            obj = super(NewClass, self).__getattribute__(attr_name)
            if hasattr(obj, '__call__') and attr_name.startswith('test'):
                return time_method(obj)
            return obj

    return NewClass


@time_test_methods
class TestGetArticlesBlankTitle(TestCase):
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

    def test_model_mommy(self):
        """
        0.00435 sec [sqlite in memory]
        """
        mommy.make(Article, title='title', _quantity=2)
        three = mommy.make(Article, title='')

        articles = Article.get_set_of_articles_blank_title()

        self.assertSetEqual(articles, {three})

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


@time_test_methods
class TestUpdateAllArticlesWithBlankTitle(TestCase):
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
