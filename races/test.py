import json

a = '''{
	"foo": "bar",
	"foo2": "bar2",
	"baz": {
				"baz1": "1",
				"baz2": "2"
			}
	}'''

json_obj = json.loads(a)
for key in json_obj.items():
	print(key)