# 
# The file is from https://github.com/googleapis/python-speech/blob/master/samples/microphone/transcribe_streaming_infinite.py
# account.json should be in the same folder with this file
#


#!/usr/bin/env python

# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the dependencies `pyaudio` and `termcolor`.
To install using pip:

    pip install pyaudio
    pip install termcolor

Example usage:
    python transcribe_streaming_infinite.py
"""

# [START speech_transcribe_infinite_streaming]

import re
import sys
import time

from google.cloud import speech_v1p1beta1 as speech
import pyaudio
from six.moves import queue
import threading
import multiprocessing
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager, NamespaceProxy
import os

# add environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=os.path.dirname(os.path.realpath(__file__))+'\\account.json'

# Audio recording parameters
STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

lock = multiprocessing.Lock()

def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):

        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""

        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset)
                        / chunk_time
                    )

                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b"".join(data)


# list_changed : 갱신될때마다 True로 바뀜, 사용후 False
# lock.acquire() 후 record_list 접근하고 lock.release()
# 음성인식 종료시 stop()
class RecognitionManager:
    
    def __init__(self):
        BaseManager.register('RecognitionData', RecognitionData, MyProxy)
        self.base_manager = BaseManager()
        self.base_manager.start()

    def reset(self):
        self.data = self.base_manager.RecognitionData()
        print(self.data)
        self.stop_thread = False

    def start(self, soundIn):
        self.soundIn = soundIn
        self.reset()

        self.checking_thread = threading.Thread(target=check_if_added, args=(self,))
        self.checking_thread.daemon = True
        self.checking_thread.start()

        self.start_process('eng')

    def start_process(self, language):
        # start start_recognition thread
        self.record_process = multiprocessing.Process(target=start_recognition, args=(self.data, language))
        self.record_process.daemon = True
        self.record_process.start()

    # language : 'eng' or 'kor'
    def change_to(self, language):       
        self.record_process.terminate()
        self.start_process(language)            

    def stop(self):
        self.stop_thread = True
        self.record_process.terminate()

class RecognitionData:
    
    def __init__(self):
        self.use_eng = True
        self.stt_list = []
        self.changed = False


def check_if_added(rec_manager):

    while not rec_manager.stop_thread:
        
        if rec_manager.data.changed:
            
            lock.acquire()
            
            print(rec_manager.data.stt_list)
            rec_manager.data.changed = False
            rec_manager.soundIn(rec_manager.data.stt_list[-1])

            lock.release()
            
        else:
            time.sleep(0.05)
            



# Process 안에서 동작하기 위한 Proxy 클래스
class MyProxy(NamespaceProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__', '__getitem__')

    '''
    def reset(self):
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('reset')

    def start(self):
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('reset')

    def stop(self):
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('stop')
    '''



# 실질적인 음성인식을 담당하는 함수
def get_speech_recognition(responses, stream, rec_data):
    
    for response in responses:

        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        result_seconds = 0
        result_micros = 0

        if result.result_end_time.seconds:
            result_seconds = result.result_end_time.seconds

        if result.result_end_time.microseconds:
            result_micros = result.result_end_time.microseconds

        stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))

        corrected_time = (
            stream.result_end_time
            - stream.bridging_offset
            + (STREAMING_LIMIT * stream.restart_counter)
        )
        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.

        if result.is_final:

            stream.is_final_end_time = stream.result_end_time
            stream.last_transcript_was_final = True

            # lock 걸고 데이터 생성

            lock.acquire()
            
            tmp_list = rec_data.stt_list
            
            # 소문자 및 공백 제거
            tmp_list.append(transcript.lower().strip())
            rec_data.stt_list = tmp_list
            print(rec_data.stt_list)
            rec_data.changed = True

            lock.release()

            '''
            lock.acquire()
            
            rec_manager.list_changed = True
            tmp_list = rec_manager.record_list
            tmp_list.append(transcript)
            rec_manager.record_list = tmp_list

            lock.release()

            '''

            '''
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                sys.stdout.write(YELLOW)
                sys.stdout.write("Exiting...\n")
                stream.closed = True
                break
            '''

        else:
            stream.last_transcript_was_final = False


# 음성인식 처리하는 함수
def start_recognition(rec_data, language):

    """start bidirectional streaming from microphone input to speech API"""

    client = speech.SpeechClient()
    if language == 'kor':
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="ko-KR"
        )
    else:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
            alternative_language_codes=["ko-KR"],
        )
    
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)

    with mic_manager as stream:

        while not stream.closed:

            stream.audio_input = []
            audio_generator = stream.generator()

            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            print("before response")

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.            
            get_speech_recognition(responses, stream, rec_data)

            if stream.result_end_time > 0:
                stream.final_request_end_time = stream.is_final_end_time
            stream.result_end_time = 0
            stream.last_audio_input = []
            stream.last_audio_input = stream.audio_input
            stream.audio_input = []
            stream.restart_counter = stream.restart_counter + 1

            if not stream.last_transcript_was_final:
                sys.stdout.write("\n")
            stream.new_stream = True


# 음성인식 결과 리스트가 변한 경우 갱신하는 함수
def get_recognition(rec_manager):

    print("th2 start")

    while not rec_manager.stop_process:
        
        if rec_manager.list_changed:
            
            lock.acquire()
            rec_manager.list_changed  = False
            print(rec_manager.record_list)
            
            lock.release()

    print("th2 end")

            

if __name__ == "__main__":

    # 예전 버전, 작동 안함

    BaseManager.register('RecognitionManager',RecognitionManager, MyProxy)
    manager = BaseManager()
    manager.start()
    rec_manager = manager.RecognitionManager()
    
    th1 = multiprocessing.Process(target=start_recognition, args=(rec_manager,))
    th1.start()
    
    th2 = multiprocessing.Process(target=get_recognition, args=(rec_manager,))
    th2.start()
    

    try:
        while True:
            if len(rec_manager.record_list) > 0:
                if re.search(r"\b(exit|quit)\b", rec_manager.record_list[-1], re.I):
                    print("got exit")
                    rec_manager.stop_process = True
                    th1.join()
                    th2.join()
            time.sleep(1)
    except:
        th1.terminate()
        th2.terminate()
            
# [END speech_transcribe_infinite_streaming]
