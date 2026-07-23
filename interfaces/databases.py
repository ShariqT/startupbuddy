from coffy.nosql import db
import uuid
import os

def make_db_path(data_path, name: str):
    return os.path.join(data_path, name)
class DBInterface:
    def __init__(self, data_path):

        self.project_db = db("projects", path=make_db_path(data_path, "projects.json"))
        self.settings_db = db("settings", path=make_db_path(data_path, "settings.json"))
    
    def create_new_project(self, name: str, folder: str = None):
        new_id = uuid.uuid4().hex
        self.project_db.add({ "id":  new_id, "name": name, "folder": folder })
        return new_id

    def get_project(self, id: str):
        return self.project_db.where("id").eq(id).first()

    def update_project(self, id: str, changes: dict):
        return self.project_db.where("id").eq(id).update(changes)

    def get_projects(self):
        return self.project_db.all()

    def clear_projects(self):
        return self.project_db.clear()

    def get_settings(self):
        return self.settings_db.first()

    def save_settings(self, changes: dict):
        if self.settings_db.first():
            return self.settings_db.match_all().update(changes)
        return self.settings_db.add(changes)