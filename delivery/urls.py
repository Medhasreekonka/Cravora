from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('open_signin', views.open_signin, name='open_signin'),
    path('open_signup', views.open_signup, name='open_signup'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'), 
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('open_show_restaurant', views.open_show_restaurant, name='open_show_restaurant'), 
    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'), 
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'), 
    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'), 
    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'), 
    path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),
    path('view_menu/<int:restaurant_id>/<str:username>', views.view_menu, name='view_menu'),

    path('add_to_cart/<int:item_id>/<str:username>', views.add_to_cart, name='add_to_cart'),
    path('show_cart/<str:username>', views.show_cart, name='show_cart'), 
    path('remove_from_cart/<int:item_id>/<str:username>', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/<str:username>', views.clear_cart, name='clear_cart'),
    path('checkout/<str:username>/', views.checkout, name='checkout'),
    path('customer_home/<str:username>', views.customer_home, name='customer_home'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('increase_quantity/<int:item_id>/<str:username>',views.increase_quantity,name='increase_quantity'),
    path('decrease_quantity/<int:item_id>/<str:username>',views.decrease_quantity,name='decrease_quantity'),
    
    path('orders/<str:username>/', views.orders, name='orders'),
]