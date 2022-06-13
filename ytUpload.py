import argparse
import http
import httplib2
import os
import random

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow


httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,http.client.IncompleteRead,http.client.ImproperConnectionState,http.client.CannotSendRequest, http.client.CannotSendHeader,http.client.ResponseNotReady, http.client.BadStatusLine)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'client_secret.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.force-ssl']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')


vidNames = [] #List of video/thumbnail names (mp4 & jpg files must have same filename)
playId = "" #Playlist ID OPTIONAL
descriptionV = "" # Video Description
tagKeyWord = "" # Video Keywords

vidDirectory = "" # Folder must consist of mp4/mov
vidForm = "" # .mov / .mp4
thumbnailDirectory = "" # Folder must consist of jpg/png
thumbnailForm = "" # .jpg / .png

idList = [] # Video ID list for playlist upload

count = 0 # Display Counter

def insertPlaylist(idListF,pID):
	# Adds Video IDs To Playlist
	if len(pID)!=0:
		def playlist(playlistItemsList):
			# Uploads To Playlist
			count = 0
			for videoId in playlistItemsList:
				request = youtube.playlistItems().insert(part="snippet",
				  	body={"snippet": {
				      "playlistId": playId,
				      "position": count,
				      "resourceId": {"kind": "youtube#video", "videoId": videoId},}})
				response = request.execute()
				print (count)
				count += 1

		playlist(idListF)
	else:
		print ("Playlist ID Not Entered")

def upload_thumbnail(youtube, video_id, file):
	# Upload JPG Thumbnails To Video
	youtube.thumbnails().set(
	videoId=video_id,
	media_body=file
	).execute()


def get_authenticated_service():
	# Authenticate Step
	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
	credentials = flow.run_console()
	return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def initialize_upload(youtube, options, vName):
	# Formats Videos Details
	tags = None
	if options.keywords:
		tags = options.keywords.split(',')

	body=dict(
	snippet=dict(
	title=options.title,
	description=options.description,
	tags=tags,
	categoryId=options.category
	),
	status=dict(
	privacyStatus=options.privacyStatus
	)
	)

	insert_request = youtube.videos().insert(
	part=','.join(body.keys()),
	body=body,

	media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
	)

	resumable_upload(insert_request, vName)


def resumable_upload(request, vN):
	# Uploads Video
	response = None
	error = None
	retry = 0
	while response is None:
		try:
			print ('Uploading file...')
			status, response = request.next_chunk()
			if response is not None:
				if 'id' in response:
					
					upload_thumbnail(youtube, response['id'], thumbnailDirectory+str(vN)+thumbnailForm)
					print ('Video id "%s" was successfully uploaded.' % response['id'])
					idList.append(response['id'])
				else:
					exit('The upload failed with an unexpected response: %s' % response)
		except (HttpError, e):
			if e.resp.status in RETRIABLE_STATUS_CODES:
				error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                             e.content)
			else:
				raise
		except (RETRIABLE_EXCEPTIONS, e):
			error = 'A retriable error occurred: %s' % e

		if error is not None:
			print (error)
			retry += 1
			if retry > MAX_RETRIES:
				exit('No longer attempting to retry.')

			max_sleep = 2 ** retry
			sleep_seconds = random.random() * max_sleep
			print ('Sleeping %f seconds and then retrying...' % sleep_seconds)




if __name__ == '__main__':
	print ("UPLOADING")
	print ("#:",len(vidNames))
	
	youtube = get_authenticated_service()
	
	for v in vidNames:
		print (count,":",v)
		
		parser = argparse.ArgumentParser()
		parser.add_argument('--file', default=vidDirectory+str(v)+vidForm, help='Video file to upload')
		parser.add_argument('--title', help='Video title', default=v)
		parser.add_argument('--description', help='Video description',
			default=descriptionV)
		parser.add_argument('--category', default='27',
			help='Numeric video category. ' +
			'See https://developers.google.com/youtube/v3/docs/videoCategories/list')
		parser.add_argument('--keywords', help='Video keywords, comma separated',
			default=tagKeyWord)
		parser.add_argument('--privacyStatus', choices=VALID_PRIVACY_STATUSES,
			default='unlisted', help='Video privacy status.')
		args = parser.parse_args()
		count += 1


		try:
			initialize_upload(youtube, args,v)
		except (HttpError, e):
			print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))



insertPlaylist(idList,playId)

