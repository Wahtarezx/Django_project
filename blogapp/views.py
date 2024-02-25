from django.views.generic import ListView, DetailView
from django.contrib.syndication.views import Feed
from blogapp.models import Article
from django.urls import reverse, reverse_lazy


class ArticleListView(ListView):
    template_name = 'blogapp/articles-list.html'
    context_object_name = 'articles'
    queryset = (
        Article.objects.
        defer('content').
        select_related('author', 'category').
        prefetch_related('tags')
    )


class ArticleDetailView(DetailView):
    model = Article
    context_object_name = 'article'
    template_name = 'blogapp/article-details.html'


class LatestArticlesFeed(Feed):
    title = 'Blog articles (latest)'
    description = 'Updates on changes and addition blog articles'
    link = reverse_lazy('blogapp:article_list')

    def items(self):
        return (
            Article.objects.
            defer('content').
            select_related('author', 'category').
            prefetch_related('tags')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
