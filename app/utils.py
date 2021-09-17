from flask import request, abort


def check_body_request(fields):
    if not request.json:
        abort(400, 'Request body is required.')
    for field in fields:
        if field not in request.json:
            abort(400, f'Field {field.replace("_", " ")} is required.')


def serializer(object_to_serialize, attributes):
    result = {}
    for i in attributes:
        result.setdefault(i, str(object_to_serialize.__getattribute__(i)))
    return result
