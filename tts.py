# coding:utf-8
import http.client
import json
import wave
import time
import os
import pyaudio
import configparser

    
def tts():
    inifile = configparser.SafeConfigParser()
    inifile.read("./config.ini")

    # RECAIUS TTS API Setting.
    conn = http.client.HTTPSConnection(inifile.get("recaius-tts","url"))
    params = {
          'id': str(inifile.get("recaius-tts","id")),
          'password': str(inifile.get("recaius-tts","password")),
          'plain_text': str(inifile.get("recaius-tts","speech_text")),
          'lang': str(inifile.get("recaius-tts","lang")),
          'speaker_id':  str(inifile.get("recaius-tts","speaker_id")),
          'codec': 'audio/x-linear'
        }
    json_params = json.dumps(params);
    headers = {"Content-type": "application/json"}
    conn.request("POST", "/tts/v1/plaintext2speechwave",json_params,headers)
    
    # temporary audio data file
    audio_data_path = 'output.wav'
    
    #save response wav file.
    with open(audio_data_path, 'wb') as handle:
        res = conn.getresponse()
        handle.write(res.read())
        
    #close api connection    
    conn.close()
    
    # open wav file.
    wav = wave.open(audio_data_path, "rb")
    # create PyAudio instanse
    p = pyaudio.PyAudio()

    # define callback for playing audio
    def play_callback(in_data, frame_count, time_info, status):
        data = wav.readframes(frame_count)
        return (data, pyaudio.paContinue)

    # open stream.
    stream = p.open(format=p.get_format_from_width(wav.getsampwidth()),
                    channels=wav.getnchannels(),
                    rate=wav.getframerate(),
                    output=True,
                    stream_callback=play_callback)
                    
    # play start.
    stream.start_stream()

    # waiting while playing audio.
    while stream.is_active():
        time.sleep(0.1)

    # When playback ends , stop and release the stream.
    stream.stop_stream()
    stream.close()
    wav.close()

    # close PyAudio
    p.terminate()
    
    # delete wav file
    os.remove(audio_data_path)
            
tts()