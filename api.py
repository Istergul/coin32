#coding=utf-8
import httplib2

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run


TOKEN_FILE_NAME = 'analytics.dat'


class GAAPI(object):

    def __init__(self, client_id, client_secret, redirect_uri='http://localhost:8080/oauth2',
                 user_agent='analytics-api-v3-awesomeness'):

        flow = OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope='https://www.googleapis.com/auth/analytics.readonly',
            redirect_uri=redirect_uri,
            user_agent=user_agent
        )

        storage = Storage(TOKEN_FILE_NAME)
        self.credentials = storage.get()

        if not self.credentials or self.credentials.invalid:
          self.credentials = run(flow, storage)

        self.service = self._initialize_service()

        self.profile_id = self.get_first_profile_id()

    def _initialize_service(self):
        http = self.credentials.authorize(httplib2.Http())
        return build('analytics', 'v3', http=http)

    def get_first_profile_id(self):
        # Get a list of all Google Analytics accounts for this user
        accounts = self.service.management().accounts().list().execute()

        if accounts.get('items'):
            # Get the first Google Analytics account
            firstAccountId = accounts.get('items')[0].get('id')

            # Get a list of all the Web Properties for the first account
            webproperties = self.service.management().webproperties().list(accountId=firstAccountId).execute()

            if webproperties.get('items'):
                # Get the first Web Property ID
                firstWebpropertyId = webproperties.get('items')[0].get('id')

                # Get a list of all Views (Profiles) for the first Web Property of the first Account
                profiles = self.service.management().profiles().list(
                    accountId=firstAccountId,
                    webPropertyId=firstWebpropertyId).execute()

                if profiles.get('items'):
                    # return the first View (Profile) ID
                    return profiles.get('items')[0].get('id')

        return None

    def callAPI(self, date_from, date_to, metrics='ga:sessions', dimensions=None, sort=None, filters=None,
                segment=None, sampling_level=None, start_index=None, max_results=None, output=None, fields=None):

        if self.profile_id is None:
            return None

        params = {
            "ids": 'ga:' + self.profile_id,                 # айдишники профилей
            "start_date": date_from.strftime("%Y-%m-%d"),   # дата начала
            "end_date": date_to.strftime("%Y-%m-%d"),       # дата конца
            "metrics": metrics,
        }

        dimensions is not None and params.update({"dimensions": dimensions})
        sort is not None and params.update({"sort": sort})
        filters is not None and params.update({"filters": filters})
        segment is not None and params.update({"segment": segment})
        sampling_level is not None and params.update({"samplingLevel": sampling_level})
        start_index is not None and params.update({"start-index": start_index})
        max_results is not None and params.update({"max-results": max_results})
        output is not None and params.update({"output": output})
        fields is not None and params.update({"fields": fields})

        return self.service.data().ga().get(**params).execute()
