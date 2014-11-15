from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
                       url(r'^register/', views.register, name='register'),
                       url(r'^login/', views.login, name='login'),
                       url(r'^create-item/', views.create_item, name='create_item'),
                       url(r'^get-items/', views.get_items, name='get_items'),
                       url(r'^pick-item/', views.get_items, name='pick_item'),
                       url(r'^check-login/', views.check_login, name='check_login'),
                       url(r'^delete-user-item/', views.delete_user_item, name='delete_user_item'),
                       url(r'^finish-user-item/', views.finish_user_item, name='finish_user_item'),
                       url(r'^unfinish-user-item/', views.unfinish_user_item, name='unfinish_user_item'),
                       url(r'^get-public-items/', views.get_public_items, name='get_public_items'),

)