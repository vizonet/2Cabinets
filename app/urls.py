from django.urls import path
from . import views
from .forms import BootstrapAuthenticationForm
from utils.context import *
from django.contrib.auth.views import LoginView, LogoutView
from datetime import datetime

urlpatterns = [
    path('', views.index, name='index'),

    # по категориям
    path('cat/<int:pk>', views.category, name='category'),                          # проекты и заказы по категориям

    # проекты
    path('offer/<int:pk>', views.offer, name='offer'),                              # просмотр + заказ проекта
    path('offer/new', views.offer_edit, name='offer_edit'),                         # создать проект пользователя
    path('offer/form/<int:pk>', views.offer_edit, name='offer_edit'),               # редактировать проект
    path('offer/delete/<int:pk>', views.offer_delete, name='offer_delete'),                     # удалить проект
    path('offer/restore/<int:pk>/<str:flag>', views.offer_delete, name='offer_delete'),         # восстановить проект

    path('offers', views.offers, name='offers'),                                                # все проекты
    path('offers/<str:username>', views.offers, name='offers'),                                 # проекты пользователя
    path('offers/inwork/', views.offers_inwork, name='offers_inwork'),                          # проекты в работе

    # заказы
    path('order/new/<int:pkOffer>', views.order_new, name='order_new'),                         # создать заказ
    path('order/form/<int:pk>', views.order_edit, name='order_edit'),                           # редактировать заказ
    path('order/<int:pk>', views.order, name='order'),                                          # просмотр заказа
    path('orders/<str:username>', views.orders, name='orders'),                                 # заказы пользователя
    path('order/success/<int:pk>', views.order_success, name='order_success'),                  # выполнить заказ
    path('order/unsuccess/<int:pk>/<str:flag>', views.order_success, name='order_success'),     # отменить выполнение
    path('order/accept/<int:pk>', views.order_accept, name='order_accept'),                     # принять заказ
    path('order/<int:pk>/score/<int:score>', views.order_score, name='order_score'),            # оценить заказ

    # аккаунт
    path('accounts/login/',
         LoginView.as_view(
             template_name='login.html',
             authentication_form=BootstrapAuthenticationForm,
             # next_page='/',
             extra_context={
                 'title': 'Авторизация',
                 'titleFooter': SITE_NAME,
                 'year': datetime.now().year,
             }
         ),
         name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='offers'), name='logout'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('accounts/profile/', views.profile, name='profile'),                                   # профиль пользователя

    # кабинеты
    path('cabinet/client/', views.cab_client, name='cab_client'),                               # кабинет заказчика
    path('cabinet/worker/', views.cab_worker, name='cab_worker'),                               # кабинет исполнителя
]
