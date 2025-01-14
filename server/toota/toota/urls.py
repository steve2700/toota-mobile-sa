from django.contrib import admin
from django.urls import path, include, re_path  # <-- Add re_path here
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define the schema view for Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="Toota API Documentation",
        default_version="v1",
        description=(
            "Welcome to the Toota API documentation! This API is designed to support a goods "
            "transportation platform, including user authentication, KYC updates, and more."
        ),
        terms_of_service="https://www.toota.com/terms/",
        contact=openapi.Contact(email="support@toota.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    # Define schemes at the schema level
    url="https://toota-mobile-sa.onrender.com",  # Use your Render URL
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("auth/", include("authentication.urls")),  # Authentication-related endpoints
    # path("trips/", include("trips.urls")),          # Trips-related endpoints
    # path("payments/", include("payments.urls")),    # Payments-related endpoints
    # path("notifications/", include("notification.urls")),  # Notifications-related endpoints
]
