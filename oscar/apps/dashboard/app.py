# from django.conf.urls import url
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

from oscar.core.application import (
    DashboardApplication as BaseDashboardApplication)
from oscar.core.loading import get_class


class DashboardApplication(BaseDashboardApplication):
    name = 'dashboard'
    permissions_map = {
        'index': (['is_staff'], ['partner.dashboard_access']),
    }

    index_view = get_class('dashboard.views', 'IndexView')
    reports_app = get_class('dashboard.reports.app', 'application')
    orders_app = get_class('dashboard.orders.app', 'application')
    users_app = get_class('dashboard.users.app', 'application')
    catalogue_app = get_class('dashboard.catalogue.app', 'application')
    promotions_app = get_class('dashboard.promotions.app', 'application')
    pages_app = get_class('dashboard.pages.app', 'application')
    partners_app = get_class('dashboard.partners.app', 'application')
    offers_app = get_class('dashboard.offers.app', 'application')
    ranges_app = get_class('dashboard.ranges.app', 'application')
    reviews_app = get_class('dashboard.reviews.app', 'application')
    vouchers_app = get_class('dashboard.vouchers.app', 'application')
    comms_app = get_class('dashboard.communications.app', 'application')
    shipping_app = get_class('dashboard.shipping.app', 'application')

    def get_urls(self):
        urls = [
            re_path(r'^$', self.index_view.as_view(), name='index'),
            re_path(r'^catalogue/', self.catalogue_app.urls),
            re_path(r'^reports/', self.reports_app.urls),
            re_path(r'^orders/', self.orders_app.urls),
            re_path(r'^users/', self.users_app.urls),
            re_path(r'^content-blocks/', self.promotions_app.urls),
            re_path(r'^pages/', self.pages_app.urls),
            re_path(r'^partners/', self.partners_app.urls),
            re_path(r'^offers/', self.offers_app.urls),
            re_path(r'^ranges/', self.ranges_app.urls),
            re_path(r'^reviews/', self.reviews_app.urls),
            re_path(r'^vouchers/', self.vouchers_app.urls),
            re_path(r'^comms/', self.comms_app.urls),
            re_path(r'^shipping/', self.shipping_app.urls),

            re_path(r'^login/$', auth_views.login, {
                'template_name': 'dashboard/login.html',
                'authentication_form': AuthenticationForm,
            }, name='login'),
            re_path(r'^logout/$', auth_views.logout, {
                'next_page': '/',
            }, name='logout'),

        ]
        return self.post_process_urls(urls)


application = DashboardApplication()
