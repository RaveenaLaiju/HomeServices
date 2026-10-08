from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ProviderViewSet, BookingRequestViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'booking-requests', BookingRequestViewSet, basename='booking-request')

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.login, name='login'),
    path('provider_login/', views.provider_login, name='provider_login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout, name='logout'),
    path('provider_logout/', views.provider_logout, name='provider_logout'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path("register/", views.register, name="register"),
    path("provider_dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('admin_provider/',views.admin_provider,name='admin_provider'),
    path('provider_add/',views.add_provider,name='add_provider'),
    path('admin_services/', views.admin_services,name='admin_services'),
    # path('service_view/', views.service_view,name='service_view'),
    path('admin_services_add/', views.admin_service_add,name='admin_services_add'),
    path('admin_packages_update/', views.admin_service_update,name='admin_services_update'),
    path('admin_provider_view/<int:id>', views.admin_provider_view, name='admin_provider_view'),
    path('admin_provider_view_update/<int:id>/', views.admin_provider_view_update, name='admin_provider_view_update'),
    path('admin_service_provider/<int:id>/', views.admin_service_provider, name='admin_service_provider'),
    path('admin_service_section/<str:name>', views.admin_service_section,name='admin_service_section'),
    path("admin_section_contents/<int:id>/",views.admin_section_contents,name="admin_section_contents"),
    path('services/', views.services,name='services'),
    path('providers/', views.providers,name='providers'),
    path('service_view/<str:name>', views.service_view,name='service_view'),
    path('check_availability/', views.check_availability, name='check_availability'),
    path('book_service/', views.book_service, name='book_service'),
    path('bookings/', views.bookings, name='bookings'),
    path('cancel_booking/<int:request_id>/', views.cancel_booking, name='cancel_booking'),
    path('provider_bookings/', views.provider_bookings, name='provider_bookings'),
    path('customer_pay/<int:booking_id>/', views.customer_pay, name='customer_pay'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('request_rework/<int:request_id>/', views.request_rework, name='request_rework'),
    path('review/<int:booking_id>/', views.leave_review, name='leave_review'),
    path('reviews/', views.all_reviews, name='all_reviews'),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),
     path('admin_bookings/', views.admin_booking_list, name='admin_booking_list'),
    path('admin_booking/<int:id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path("admin_customers/", views.admin_customer_list, name="admin_customer_list"),
    path("admin_enquiries/", views.admin_enquiry_list, name="admin_enquiry_list"),
    path("admin_enquiries/<int:id>/", views.admin_enquiry_detail, name="admin_enquiry_detail"),
    path("admin_payments/", views.admin_payment_list, name="admin_payment_list"),
    path('admin_reviews/', views.review_list, name='review_list'),
    path('provider_service/',views.provider_service, name='provider_service'),
    path('provider_review/',views.provider_review, name='provider_review'),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),



    

]

    



