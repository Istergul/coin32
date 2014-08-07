#coding=utf-8
import pprint
import httplib2
import datetime

from apiclient.errors import HttpError
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, AccessTokenRefreshError
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

    def callAPI(self, date_from, date_to, metrics='ga:sessions', dimensions=None, sort=None, filters=None):

        if self.profile_id is None:
            return None

        params = {
            "ids": 'ga:' + self.profile_id,                 # айдишники профилей
            "start_date": date_from.strftime("%Y-%m-%d"),   # дата начала
            "end_date": date_to.strftime("%Y-%m-%d"),       # дата конца
            "metrics": metrics,
        }

        dimensions is not None and params.update(dimensions=dimensions)
        sort is not None and params.update(sort=sort)
        filters is not None and params.update(filters=filters)

        return self.service.data().ga().get(**params).execute()


def main():

    try:
        client_id = "911007141855-a4rp0airq4djqlqg36esk1eujo6db8fh.apps.googleusercontent.com"
        client_secret = "bltQmWD_ElJQwzi7I8PAOsgo"
        api = GAAPI(client_id, client_secret)
        date_from = datetime.date.today() - datetime.timedelta(days=10)
        date_to = datetime.date.today()

        res = api.callAPI(date_from, date_to, dimensions="ga:browser,ga:city", filters="ga:browser==Firefox")
        pprint.pprint(res)

    except TypeError as error:
        print ('There was an error in constructing your query : %s' % error)
    except HttpError as error:
        print ('Arg, there was an API error : %s : %s' % (error.resp.status, error._get_reason()))
    except AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the application to re-authorize')

# http://localhost:8080/?code=4/o8MhTfjtVp2TgvySp7Rf2RPWt7Ax.gsy34lo2n3UZYFZr95uygvXDyBRXjwI


if __name__ == "__main__":
    main()

