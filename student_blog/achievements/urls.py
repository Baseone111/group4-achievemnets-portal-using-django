from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('achievements/', views.achievements, name='achievements'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('delete-achievement/<int:achievement_id>/', views.delete_achievement, name='delete_achievement'),
    path('contact-submit/', views.contact_submit, name='contact_submit'),
    path('api/achievements/', views.get_achievements_api, name='achievements_api'),
    
    # Staff routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('register-staff/', views.register_staff, name='register_staff'),


    
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('students/<int:user_id>/compute-cgpa/', views.compute_and_store_student_cgpa, name='compute_student_cgpa'),
]


handler404 = 'achievements.views.handler404'
handler500 = 'achievements.views.handler500'