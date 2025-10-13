# from django.conf.urls import url
from django.urls import path, re_path, include
from oscar.apps.promotions.models import KeywordPromotion, PagePromotion
from oscar.core.application import Application
from oscar.core.loading import get_class


class PromotionsApplication(Application):
    name = 'promotions_app'
    label = 'promotions_app_core'
    home_view = get_class('promotions.views', 'HomeView')
    record_click_view = get_class('promotions.views', 'RecordClickView')

    def get_urls(self):        
        urls = [
            re_path(r'page-redirect/(?P<page_promotion_id>\d+)/$',
                self.record_click_view.as_view(model=PagePromotion),
                name='page-click'),
            re_path(r'keyword-redirect/(?P<keyword_promotion_id>\d+)/$',
                self.record_click_view.as_view(model=KeywordPromotion),
                name='keyword-click'),
            re_path(r'^$', self.home_view.as_view(), name='home'),
        ]
        return self.post_process_urls(urls)


application = PromotionsApplication()
