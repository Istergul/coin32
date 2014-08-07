#coding=utf-8
import datetime
import pprint

from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError

from api import GAAPI


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


if __name__ == "__main__":
    main()

