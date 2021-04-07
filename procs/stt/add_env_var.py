import os

# add environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=os.path.dirname(os.path.realpath(__file__))+'\\account.json'
