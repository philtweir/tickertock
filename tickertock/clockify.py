import requests
import datetime


class ClockifyTocker:
    """
    Clockify API wrapper

    In theory, this should be the only part of the
    app with hard dependencies on Clockify, so other
    timetracking systems could be implemented.

    (Initally, we used Toggl but that's gone by the wayside)
    """

    @classmethod
    def from_config(cls, config):
        return cls(api_key=config["apiKey"], workspace_id=config["workspaceId"])

    def __init__(self, api_key, workspace_id):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.when = None

        self.active_project = None
        self.active_project_id = None
        self.active_entry = None

    def initialize(self):
        projects = self.get_all_projects()
        self.project_ids = {proj["name"]: proj["id"] for proj in projects}

    def get_project_id(self, project):
        return self.project_ids[project]

    def _get_user(self):
        return requests.get(
            "https://api.clockify.me/api/v1/user",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": self.api_key,
            },
        ).json()

    def get_all_projects(self):
        return requests.get(
            f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/projects/",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": self.api_key,
            },
        ).json()

    _user = None

    @property
    def user(self):
        if not self._user:
            self._user = self._get_user()
        return self._user

    def stop_time_entry(self):
        return self._stop_time_entry(self.user["id"])

    def _stop_time_entry(self, user_id):
        time = datetime.datetime.utcnow().isoformat()[:-7] + "Z"
        result = requests.patch(
            f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/user/{user_id}/time-entries/",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": self.api_key,
            },
            json={"end": time},
        ).json()
        self.active_project_id = None
        self.active_project = None
        self.active_entry = None
        self.when = datetime.datetime.utcnow()
        return result

    def elapsed(self):
        self.get_active_time_entry()
        if not self.when:
            return None, None
        return self.active_project, datetime.datetime.utcnow() - self.when

    def get_active_time_entry(self):
        return self._get_active_time_entry(self.user["id"])

    def _get_active_time_entry(self, user_id):
        entry = requests.get(
            f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/user/{user_id}/time-entries?in-progress=true",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": self.api_key,
            },
        ).json()
        if entry:
            if "timeInterval" in entry[0]:
                when = datetime.datetime.fromisoformat(
                    entry[0]["timeInterval"]["start"].replace("T", " ")[:-1]
                )
                if (
                    not self.when
                    or when > self.when
                    or self.active_entry == entry[0]["id"]
                ):
                    self.when = when
                    if "projectId" in entry[0]:
                        self._set_active_project_id(entry[0]["projectId"])
            self.active_entry = entry[0]["id"]
        return entry

    def _set_active_project_id(self, active_project_id):
        self.active_project_id = active_project_id
        self.active_project = {v: k for k, v in self.project_ids.items()}.get(
            self.active_project_id, None
        )

    def start_time_entry(self, detail, project_id):
        self.when = datetime.datetime.utcnow()
        self._set_active_project_id(project_id)
        time = self.when.isoformat()[:-7] + "Z"
        entry = requests.post(
            f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/time-entries/",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": self.api_key,
            },
            json={"description": detail, "projectId": project_id, "start": time},
        ).json()
        self.active_entry = entry["id"]
        return entry
