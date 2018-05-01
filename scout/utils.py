from flask import jsonify

def execute_with_default(f, default, exception = Exception):
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exception:
            return default
    return wrap

def compose_json_response(success, data, message, code):
    return jsonify({'success': success,'data': data,'message': message}), code