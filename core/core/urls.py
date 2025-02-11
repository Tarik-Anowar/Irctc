from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings  
from django.contrib.auth.views import LogoutView

from home.views import *
from accounts.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name="home"),

    path('add_train/', add_train, name="add_train"),
    path('bookings/', my_bookings, name="my_bookings"),

    path('signup/', signup, name="signup"),
    path('signin/', signin, name="signin"),
    path('signout/', LogoutView.as_view(next_page='/'), name='signout'),

    path('api/get_trains/', get_trains, name="get_trains"),
    path('api/get_seats/<int:train_number>/', get_seats, name="get_seats"),
    path('api/book_seat/<int:train_number>/<int:seat_number>/', book_seat, name="book_seat"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
