from drf_yasg import openapi
from .models import Driver, User

# Common Parameters (for both Driver and User KYC)
token_param = openapi.Parameter(
    'Authorization', openapi.IN_HEADER,
    description="Bearer token for authentication",
    type=openapi.TYPE_STRING,
    required=True
)

first_name_param = openapi.Parameter(
    'first_name', openapi.IN_FORM,
    description="First name",
    type=openapi.TYPE_STRING,
    required=True
)

last_name_param = openapi.Parameter(
    'last_name', openapi.IN_FORM,
    description="Last name",
    type=openapi.TYPE_STRING,
    required=True
)

physical_address_param = openapi.Parameter(
    'physical_address', openapi.IN_FORM,
    description="Physical address",
    type=openapi.TYPE_STRING,
    required=True
)

phone_number_param = openapi.Parameter(
    'phone_number', openapi.IN_FORM,
    description="Phone number",
    type=openapi.TYPE_STRING,
    required=True
)

profile_pic_param = openapi.Parameter(
    'profile_pic', openapi.IN_FORM,
    description="Profile picture file upload",
    type=openapi.TYPE_FILE,
    required=False
)

# Driver KYC Schema
driver_kyc_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=[
        'first_name', 'last_name', 'phone_number', 'physical_address',
        'profile_pic', 'license_image', 'car_images',
        'vehicle_registration', 'vehicle_type', 'vehicle_load_capacity'
    ],
    properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        'physical_address': openapi.Schema(type=openapi.TYPE_STRING),
        'profile_pic': openapi.Schema(type=openapi.TYPE_FILE, description="Profile Picture"),
        'license_image': openapi.Schema(type=openapi.TYPE_FILE, description="Driver's License"),
        'car_images': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_FILE),
            description="Exactly two car images"
        ),
        'vehicle_registration': openapi.Schema(type=openapi.TYPE_STRING),
        'vehicle_type': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=[choice[0] for choice in Driver.VEHICLE_CHOICES]
        ),
        'vehicle_load_capacity': openapi.Schema(type=openapi.TYPE_NUMBER),
    }
)

# User KYC Schema (User-specific, without vehicle info)
user_kyc_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['first_name', 'last_name', 'phone_number', 'physical_address', 'profile_pic'],
    properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        'physical_address': openapi.Schema(type=openapi.TYPE_STRING),
        'profile_pic': openapi.Schema(type=openapi.TYPE_FILE, description="Profile Picture"),
    }
)
