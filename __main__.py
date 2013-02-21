from __future__ import division
from threading import Thread
from collections import deque
from utils.input import wave_to_list
from utils.comparison import find_out_which_peer_this_guy_mentioned
from utils.data import Peer, Slice
import pyaudio
import time
import struct
import copy


# these need to be global since we cant control what args pyaudio calls back with
peers = []
realtime_stream = deque()
slice_comparison_lookup = dict()
twice_longest_template_length = 0
analyzer = Thread()
missed_cycles = 0


def main():
  RECORD_RATE = 44100
  RECORD_FORMAT = pyaudio.paInt16
  CHUNK = 2048

  global peers
  peers.append(Peer('jiehan', wave_to_list('samples/jiehan-kane.wav'), CHUNK)) 
  peers.append(Peer('kane', wave_to_list('samples/kane-kane.wav'), CHUNK))

  # start recording process
  p = pyaudio.PyAudio()
  p_stream = p.open(format=RECORD_FORMAT,
                    channels=1,
                    rate=RECORD_RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=receive_new_slice)

  global twice_longest_template_length
  longest_template_length = max([len(peer.audio) for peer in peers])
  twice_longest_template_length = 2*longest_template_length
  
  global realtime_stream
  realtime_stream = deque(maxlen=twice_longest_template_length)

  p_stream.start_stream()

  while p_stream.is_active():
    time.sleep(RECORD_RATE/CHUNK)


def receive_new_slice(in_data, frame_count, time_info, status):
  # print "new audio data of size %s saved" % frame_count
  
  format = "%dh"%(frame_count)

  global realtime_stream
  realtime_stream.append(Slice(struct.unpack(format, in_data),
                               'realtime_' + str(time.time())))

  global twice_longest_template_length
  if twice_longest_template_length == len(realtime_stream):

    # kill existing analyzers
    global analyzer, missed_cycles
    if analyzer.is_alive():
      missed_cycles = missed_cycles + 1
      print "analyzer is behind realtime_stream by", missed_cycles, "slices"
    else:
      global peers, slice_comparison_lookup

      # FIXME: cache cleanup

      analyzer = Thread(target=find_out_which_peer_this_guy_mentioned,
                        args=(copy.copy(realtime_stream), peers, 
                              slice_comparison_lookup, start_lan_stream))
      analyzer.start()

  return ("", pyaudio.paContinue)


def start_lan_stream(peer, confidence=0):
  analyzer_complete_run()
  print "--->", peer.address, confidence


def end_lan_stream(peer):
  pass


def analyzer_complete_run():
  global missed_cycles
  missed_cycles = 0


if __name__ == "__main__":
  main()
