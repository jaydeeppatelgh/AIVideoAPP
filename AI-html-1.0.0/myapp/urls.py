from django.urls import path
from . import views
from .views import delete_segment,update_segment_texts,upload_video,merge_edited_audio_video

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('fpswd', views.fpswd, name='fpswd'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path('set_pswd', views.set_pswd, name='set_pswd'),
    path('work_space/<int:pk>', views.work_space, name='work_space'),
    path('user_history/<int:pk>', views.user_history, name='user_history'),
    path('delete-segment/<int:workspace_pk>/<int:segment_index>/', delete_segment, name='delete_segment'),
    path('update-segment-texts/<int:workspace_pk>/', update_segment_texts, name='update_segment_texts'),
    path('upload_video/<int:pk>/', upload_video, name='upload_video'),
    path('merge_edited_audio_video/<int:pk>/', merge_edited_audio_video, name='merge_edited_audio_video'),
]
