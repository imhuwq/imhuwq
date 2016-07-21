from app.models import Post, Tag, Category, Task, Flow, Settings, User
from config import BASE_DIR
from datetime import datetime
import os
import json


def run():
    models = [Post, Tag, Category, Task, Flow, Settings, User]

    time = str(datetime.utcnow().replace(microsecond=0)).replace(' ', '_')

    target_dir = os.path.abspath(os.path.join(BASE_DIR, "database/backup/%s" % time))

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    database = dict()
    for model in models:
        database[model.__name__] = model.export_json(target_dir)

    with open('%s/database.json' % target_dir, 'w') as  j:
        json.dump(database, j)
