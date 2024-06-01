import os
import json
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetBase:
    def __init__(self):
        self.Google_Key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self._scope = self.scope()

    def scope(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        return scope

    def AuthCredential(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(self.Google_Key), self._scope
        )

    def GetSpreadSheet(self):
        pass

    def get_sheets(self):
        pass


class GoogleSheet(GoogleSheetBase):
    def __init__(self):
        super().__init__()
        self._no_records = self.no_records()

    def create_sheet(self):
        pass

    def rename_sheet(self, sheet_name, new_sheet_name):
        pass

    def no_records(self):
        return False

    def get_records(self):
        pass

    def add_column(self):
        pass


class Record(GoogleSheet):
    def __init__(self):
        super().__init__()

    def add_record(self):
        pass


