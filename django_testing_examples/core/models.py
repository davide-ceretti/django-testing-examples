from django.db import models
from django.contrib.auth.models import User


class Blog(models.Model):
    title = models.CharField(max_length=255)


class Article(models.Model):
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    creator = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)

    @staticmethod
    def get_set_of_articles_blank_title():
        articles = Article.objects.filter(title='')
        return set(articles)

    @staticmethod
    def update_all_articles_with_blank_title_v1(new_value):
        # Decent django developer
        Article.objects.filter(title='').update(title=new_value)

    @staticmethod
    def update_all_articles_with_blank_title_v2(new_value):
        # Junior django developer
        for each in Article.objects.filter(title=''):
            each.title = new_value
            each.save()

    @staticmethod
    def update_all_articles_with_blank_title_v3(new_value):
        # Retarded django developer
        all_pks = Article.objects.filter(title='').values_list('id', flat=True)
        for pk in all_pks:
            article = Article.objects.filter(pk=pk).get()
            article.title = new_value
            article.save()

    def __unicode__(self):
        return u'Article {}'.format(self.id)
