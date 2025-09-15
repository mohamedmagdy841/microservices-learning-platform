from django.urls import path, include
# from debug_toolbar.toolbar import debug_toolbar_urls
from accounts.views import (
    CustomLoginView,
    CustomRegisterView,
    SendOtpView, VerifyOtpView
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Swagger
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Accounts
    path('accounts/', include('accounts.urls')),
    
    # student endpoints
    path('users/auth/login/', CustomLoginView.as_view(), name='custom-login'),
    path("users/auth/", CustomRegisterView.as_view(), name="custom-register"),
    path('users/auth/send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('users/auth/verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    
    # Djoser defaults
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    
    # Courses
    path('courses/', include('courses.urls')),
    
    # Subscriptions
    path('subscriptions/', include('subscriptions.urls')),
    
    # Quizzes
    path('quiz/', include('quizzes.urls')),
] #+ debug_toolbar_urls()
