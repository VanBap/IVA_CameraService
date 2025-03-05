## Authentication và permission trong DRF

settings.py
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.user_management.auth.token_authentication.CustomJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'apps.user_management.auth.permissions.IsAuthenticatedByTokenOrKey',
    ],
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'EXCEPTION_HANDLER': 'drf_standardized_errors.handler.exception_handler',
}
```
## Các bước xử lý request
request -> authentication_classes -> User -> permission_classes -> check user có quyền với APIView không ? 
-> permission decorator -> check user có quyền với method không ? 

### DEFAULT_AUTHENTICATION_CLASSES: CustomJWTAuthentication
- Get JWT token from request headers
- Validate token được generate bởi secret key do server tạo
- Check token có nằm trong danh sách blacklist
- Query user_id xem user có tồn tại
- Trả về 1 User()

Trong APIView sẽ mặc định dùng default class này, để chỉ định class khác,
`authentication_classes = [MyJWTAuthentication]`

Để bỏ authentication
`authentication_classes = []`

### DEFAULT_PERMISSION_CLASSES: IsAuthenticatedByTokenOrKey
```
is_valid_token = bool(request.user and request.user.id and request.user.is_authenticated)
api_key = request.headers.get(API_KEY_HEADER)
is_valid_api_key = bool(api_key and api_key == settings.API_KEY)
return is_valid_token or is_valid_api_key
```
- User tồn tại và status là active (user.is_authenticated)
- Hoặc có API_KEY hợp lệ

# Thêm 1 permission mới
Cần define 1 constant cho permission này trong apps/user_management/auth/constants.py.
- PERMISSIONS: Define permission
- CONTENT_TYPES: Add permission vào content type tương ứng
- ROLES: điêu chỉnh các permission mặc định của các role
  - SYSTEM_ADMIN: không cần điền, role này có tất cả các permission. Script sync_permission sẽ add permission này vào cho role SYSTEM_ADMIN
  - ADMIN:
  - VIEWER

Run `python manage.py sync_permission` để sync permission mới vào các user, và vào các role.
