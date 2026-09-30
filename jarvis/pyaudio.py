import pyaudiowpatch as pyaudio

# PyAudio class
PyAudio = pyaudio.PyAudio

# Audio format constants
paInt8 = pyaudio.paInt8
paInt16 = pyaudio.paInt16
paInt24 = pyaudio.paInt24
paInt32 = pyaudio.paInt32
paFloat32 = pyaudio.paFloat32
paUInt8 = pyaudio.paUInt8

# Create a PyAudio instance for compatibility
_audio = pyaudio.PyAudio()

def get_sample_size(format):
    return _audio.get_sample_size(format)