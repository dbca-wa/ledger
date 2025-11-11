# from django.conf.urls import url
from django.urls import path, re_path, include
from django.contrib.auth.decorators import login_required

from oscar.core.application import Application
from oscar.core.loading import get_class


class ProductReviewsApplication(Application):
    name = None
    hidable_feature_name = "reviews"

    detail_view = get_class('catalogue.reviews.views', 'ProductReviewDetail')
    create_view = get_class('catalogue.reviews.views', 'CreateProductReview')
    vote_view = get_class('catalogue.reviews.views', 'AddVoteView')
    list_view = get_class('catalogue.reviews.views', 'ProductReviewList')

    def get_urls(self):
        urls = [
            re_path(r'^(?P<pk>\d+)/$', self.detail_view.as_view(),
                name='reviews-detail'),
            re_path(r'^add/$', self.create_view.as_view(),
                name='reviews-add'),
            re_path(r'^(?P<pk>\d+)/vote/$',
                login_required(self.vote_view.as_view()),
                name='reviews-vote'),
            re_path(r'^$', self.list_view.as_view(), name='reviews-list'),
        ]
        return self.post_process_urls(urls)


application = ProductReviewsApplication()
