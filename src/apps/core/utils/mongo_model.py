
def create_model_instance(model_class, **data):
    obj = model_class()
    for field, value in data.items():
        setattr(obj, field, value)
    return obj


def create_model_instance_v2(model_class, **data):
    filtered_data = {key: value for key, value in data.items() if key in model_class._fields} # noqa
    return model_class(**filtered_data)
