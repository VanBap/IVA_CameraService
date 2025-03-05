# Một số convention hiện đang dùng cho các apps: review, respond, devices
Tham khảo: https://github.com/HackSoftware/Django-Styleguide
## 1. Database
+ Table name: danh từ, chữ thường, dạng số ít
+ Model class name: danh từ, chữ thường, dạng số ít

## 2. Tổ chức project
Mỗi apps chứa các folders:
+ models: chứa ORM model, tương tự repository
+ services: chứa code handle business logic (CRUD, query,...), tách biệt với request/response
+ views: chứa các view, handle parse request, call service, return response to client
+ serializers: hiện đang follow theo convention sau:
  + serializer chỉ dùng để:
    + validate data (request params, request body)
    + serialize model instance, lấy json trả về 
  + Không chứa logic CRUD model trong serializer, bất cứ business logic gì đều nằm trong services
+ urls.py: tương tự controller trong mô hình MVC, trỏ request đến view thích hợp

VD: API
```python
# VIEW
def post(self, request):
    serializer = self.InputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    validated_data = serializer.validated_data
    try:
        camera = service.create_camera(validated_data, user=request.user)
    except IntegrityError as ex:
        raise ApplicationError({f'{str(ex)}': 'Database error'})
    return Response(self.OutputSerializer(camera).data, status=status.HTTP_201_CREATED)

# validated_data sẽ chưa các field để set trực tiếp vào model, và cả các fields KHÔNG dùng để set vào model (dùng cho nghiệp vụ khác).
# Ở phía service, phải pop các field không liên quan model ra khỏi validated_data, trước khi gọi đến drf.model_create,
# drf.model_update

# SERVICE
@transaction.atomic
def create_camera(validated_data: dict, user) -> Camera:
    # add user_id to validated_data
    validated_data['user_id'] = getattr(user, 'id', None)
    
    # pop các field trong validated_data mà không phải là field của Model

    # validate, VD: camera_id, group_id
    group_id = validated_data.pop('group', None)
    if group_id:
        group = get_camera_group(group_id=group_id)
        validated_data['group_id'] = group.id

    # create camera with group
    return drf.model_create(Camera, validated_data)
    
```




## 3. Xóa model
Model nào dùng soft delete, thì tất cả các model tham chiếu fk đến nó, luôn để on_delete=models.DO_NOTHING. 
Application code chủ động handle xóa mểm model, và xóa (hard or soft) các related model.

Model nào hard delete, thì các related model có thể set on_delete=models.CASCADE, django handle việc xóa model, và xóa 
các related model.

## 4. Giải thích một số hàm drf
### 4.1 drf.model_create(model_class, validated_data)
+ Set các field created_at, created_by, updated_at, updated_by
  + Hỗ trợ model dùng created_by, updated_by là FK đến table user
+ Call model.custom_clean, để validate data và bắn các exception có code ý nghĩa hơn so với code của DRF

### 4.2 model_update(instance, data, force_updated_fields=None):
+ Set các field updated_at, updated_by
+ Chỉ updated các field của model nằm trong data và có giá trị thay đổi
+ Call model.custom_clean, để validate data và bắn các exception có code ý nghĩa hơn so với code của DRF

#### Chú ý
Nếu field cần update là related model (FK đến model khác), VD user.group -> Group model. Với django, ta có thể dùng cả 
user.group, hoặc user.group_id tức có thể truyền data['group'] = group, hoặc data['group_id] = group.id.
Với drf.model_update phải dùng data['group_id'], vì nếu dùng data['group'], drf sẽ query DB để load group nên, trong khi
ta chỉ cần set giá trị group_id là được.


## 5. Style chung khi làm việc với DRF serializer
Bản thân, django cũng tự validate các field, khi gọi model.clean (hoặc model.full_clean,...). DRF ModelSerializer cũng
tự động generate các field và validator theo các field trong model. Chú ý: DRF sẽ generate cho các unique field (unique=True),
nhưng không generate validator cho Model.Meta.constrains, mà phải dùng unique_together khi define Model.
Một số nguyên tắc chung:
- Dùng serializer để validate các field trong model
- Không dùng serializer để validate các ForeignKey field, ManyToManyField. Do vậy luôn redefine các field này trong serializer.
VD: group = serializers.IntegerField(). Tầng service chịu trách nhiệm validate các field này.
- Dùng hàm model.custom_clean để validate các unique field, unique_together,... để có thể bắn ra error code theo ý muốn.

Do ModelSerializer tự động thực hiện generate validator cho unique field, nên ta cần disable validator này:
- Redefine lại field trong serializer class
  + VD: trong model, name = CharField(max_length=255, unique=True)
  + Trong serializer: name = CharField()
- Hoặc set trong Meta của serializer class

    extra_kwargs = {
        'name': {
            'validators': []
        }
    }

ModelSerializer
- It will automatically generate a set of fields for you, based on the model.
- It will automatically generate validators for the serializer, such as unique_together validators.
- It includes simple default implementations of .create() and .update().

Với DRF <= 3.14, ModelSerializer không tự động generate validator cho models.UniqueConstraint, mà chỉ generate validator 
nếu dùng unique_together trong model. Tuy nhiên, DRF phiên bản mới có thể support models.UniqueConstraint. Do vậy,
tốt nhất luôn disable việc generate unique validator của ModelSerializer theo cách bên trên.
