# from django.conf.urls import url
from django.urls import path, re_path, include
from oscar.apps.promotions.conf import PROMOTION_CLASSES
from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class PromotionsDashboardApplication(DashboardApplication):
    # name = None
    name = 'dashboard_promotions'
    label = 'dashboard_promotions'
    default_permissions = ['is_staff', ]

    # list_view = get_class('dashboard.promotions.views',
    #                       'ListView')
    # page_list = get_class('dashboard.promotions.views',
    #                       'PageListView')
    # page_detail = get_class('dashboard.promotions.views',
    #                         'PageDetailView')
    # create_redirect_view = get_class('dashboard.promotions.views',
    #                                  'CreateRedirectView')
    # delete_page_promotion_view = get_class('dashboard.promotions.views',
    #                                        'DeletePagePromotionView')

    # Dynamically set the CRUD views for all promotion classes
    view_names = (
        ('create_%s_view', 'Create%sView'),
        ('update_%s_view', 'Update%sView'),
        ('delete_%s_view', 'Delete%sView')
    )
    for klass in PROMOTION_CLASSES:
        for attr_name, view_name in view_names:
            full_attr_name = attr_name % klass.classname()
            full_view_name = view_name % klass.__name__
            view = get_class('dashboard.promotions.views', full_view_name)
            locals()[full_attr_name] = view

    def get_urls(self):
        urls = [
            re_path(r'^$', self.list_view.as_view(), name='promotion-list'),
            re_path(r'^pages/$', self.page_list.as_view(),
                name='promotion-list-by-page'),
            re_path(r'^page/(?P<path>/([\w-]+(/[\w-]+)*/)?)$',
                self.page_detail.as_view(), name='promotion-list-by-url'),
            re_path(r'^create/$',
                self.create_redirect_view.as_view(),
                name='promotion-create-redirect'),
            re_path(r'^page-promotion/(?P<pk>\d+)/$',
                self.delete_page_promotion_view.as_view(),
                name='pagepromotion-delete')]

        for klass in PROMOTION_CLASSES:
            code = klass.classname()
            urls += [
                re_path(r'create/%s/' % code,
                    getattr(self, 'create_%s_view' % code).as_view(),
                    name='promotion-create-%s' % code),
                re_path(r'^update/(?P<ptype>%s)/(?P<pk>\d+)/$' % code,
                    getattr(self, 'update_%s_view' % code).as_view(),
                    name='promotion-update'),
                re_path(r'^delete/(?P<ptype>%s)/(?P<pk>\d+)/$' % code,
                    getattr(self, 'delete_%s_view' % code).as_view(),
                    name='promotion-delete')]

        return self.post_process_urls(urls)


application = PromotionsDashboardApplication()
