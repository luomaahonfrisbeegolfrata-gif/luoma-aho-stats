import json, pathlib
pathlib.Path("data/metrix_kilpailut.json").write_text(json.dumps({"upcoming":[]}), encoding='utf-8')
print("competitions placeholder")
