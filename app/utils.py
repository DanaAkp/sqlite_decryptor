from flask import request, abort


def check_body_request(fields):
    if not request.is_json:
        abort(400, 'Request body is required.')
    json_data = request.json
    for field in fields:
        if field not in json_data:
            abort(400, f'Field {field.replace("_", " ")} is required.')


def serializer(object_to_serialize, attributes):
    result = {}
    for i in attributes:
        result.setdefault(i, str(object_to_serialize.__getattribute__(i)))
    return result
