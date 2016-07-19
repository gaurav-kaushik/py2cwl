from __future__ import print_function
import json
from os import environ
import sevenbridges as sbg
import purifyCWL

class sevenBridges:

    def __init__(self):
        """
        To set up, add API_URL and AUTH_TOKEN to your environment
        API_URL is "https://cgc-api.sbgenomics.com/v2" for all users
        AUTH_TOKEN can be found in the Developer Settings on SBG or CGC
        """
        self.api = sbg.Api(config=sbg.Config(url=environ['API_URL'], token=environ['AUTH_TOKEN']))

    def get_user(self):
        # get user info
        return self.api.users.me()

    def get_projects(self, query_limit=100):
        # query your projects
        return self.api.projects.query(limit=query_limit)

    def get_projects_all(self):
        return list(self.api.projects.query().all())

    def get_apps_all(self):
        return list(self.api.apps.query().all())

    def get_files_all(self):
        return list(self.api.files.query().all())

    def get_projects_ids(self):
        # return a list of project ids
        return [item.id for item in self.get_projects_all()]

    def get_apps_ids(self):
        # return a list of project ids
        return [item.id for item in self.get_apps_all()]

    def get_files_ids(self):
        # return a list of project ids
        return [item.id for item in self.get_files_all()]

    def get_projects_by_string(self, query):
        return filter(lambda q: query in q, self.get_projects_ids())

    def get_apps_by_string(self, query):
        return filter(lambda q: query in q, self.get_apps_ids())

    def get_projects_files(self, project):
        # fetch files from a project
        return project.get_files()

    def get_project_by_id(self, id):
        projects = self.get_projects_by_string(id)
        if len(projects) == 0:
            print("No match found.")
        elif len(projects) > 1:
            print("Multiple matches found.")
        print(str(projects))

    def get_project_by_id(self, id):
        apps = self.get_apps_by_string(id)
        if len(apps) == 0:
            print("No match found.")
        elif len(apps) > 1:
            print("Multiple matches found.")
        print(str(apps))

    def download_clean_apps_from_project(self, project, save=False):
        """
        :param project: str of project name, e.g. 'dream-project'
        :param fileNames: arr of filenames, size of list of apps in project
        """
        apps = self.api.apps.query(project)._items
        for idx, app in enumerate(apps):
            pure_app = purifyCWL.purify(app.raw)
            pure_app_name = app.name.lower().replace (" ", "_")
            if save: purifyCWL.save_app(pure_app, pure_app_name) # will route to file is save=True else prints
        return

    def add_app_to_project(self, project_id, app_name, app_file):
        # TODO: add array of apps instead of general list
        with open(app_file, "r") as a:
            app = json.load(a)
        self.api.apps.install_app(str(project_id + "/" + app_name), raw=app)
        print(app_file + " added to the " + project_id + " project as " + app_name)
        # TODO: print true app-name as well so when the user sees it in the project
        return

    def transfer_clean_apps(self, project_old, project_new):
        """
        :param project: str of project name, e.g. 'dream-project'
        :param fileNames: arr of filenames, size of list of apps in project
        """
        apps = self.api.apps.query(project_old)._items
        for idx, app in enumerate(apps):
            try:
                pure_app = purifyCWL.purify(app.raw, recursion=True)
                pure_app_name = app.name.lower().replace (" ", "_")
                pure_app_filename = purifyCWL.save_app(pure_app, pure_app_name) # will route to file is save=True else prints
                self.add_app_to_project(project_id=project_new, app_name=pure_app_name, app_file=pure_app_filename)
            except:
                print("Either there is a duplicate file or you do not have permissions to copy to " + project_new)
                continue
        return

if __name__ == "__main__":
    s = sevenBridges()
    # s.download_clean_apps_from_project(project='gauravCGC/dream-project', save=True)
    # s.api.apps.install_app('gauravCGC/dream-project-open/test', raw=CwlReader(in_json=open('tophat2.cwl','r')))
    # s.add_app_to_project(project_id="gauravCGC/dream-project-open", app_name="tophat_test", app_file="tophat2.cwl")
    s.transfer_clean_apps("gauravADMIN/dream-tool-repo", "gauravCGC/icgc-tcga-dream-somatic-mutation-calling-challenge-rna")
