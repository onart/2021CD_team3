#
# code sample from https://cloud.google.com/speech-to-text/docs/samples/speech-quickstart?hl=ko
# authorize from https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable
# to run the code
#


# Imports the Google Cloud client library
from google.cloud import speech

import os

# add environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=os.path.dirname(os.path.realpath(__file__))+'\\account.json'


# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

audio = speech.RecognitionAudio(uri=gcs_uri)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
)

# Detects speech in the audio file
response = client.recognize(config=config, audio=audio)

for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))
