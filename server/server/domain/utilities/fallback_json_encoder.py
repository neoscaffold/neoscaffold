import json

def dumps(obj):
    return json.dumps(obj, cls=FallbackJSONEncoder)

class FallbackJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)