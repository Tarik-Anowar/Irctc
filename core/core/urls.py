from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings  
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


from home.views import *
from accounts.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),

    path('signup/', signup, name="signup"),
    path('signin/', signin, name="signin"),
    path('signout/', LogoutView.as_view(), {'next_page': '/'}, name='signout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

] 