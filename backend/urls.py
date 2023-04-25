from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from backend.views import PartnerUpdate, RegisterAccount, LoginAccount, CategoryView, ShopView, ProductInfoView, \
    BasketView, AccountDetails, ContactView, OrderView, PartnerState, PartnerOrders, ConfirmAccount


app_name = 'backend'
urlpatterns = [
    path('partner/update', PartnerUpdate.as_view()),
    path('partner/state', PartnerState.as_view()),
    path('partner/orders', PartnerOrders.as_view()),

    path('user/register', RegisterAccount.as_view()),
    path('user/register/confirm', ConfirmAccount.as_view()),
    path('user/details', AccountDetails.as_view()),
    path('user/contact', ContactView.as_view()),
    path('user/login', LoginAccount.as_view()),
    path('user/password_reset', reset_password_request_token),
    path('user/password_reset/confirm', reset_password_confirm),

    path('categories', CategoryView.as_view()),
    path('shops', ShopView.as_view()),
    path('products', ProductInfoView.as_view()),
    path('basket', BasketView.as_view()),
    path('order', OrderView.as_view()),

]