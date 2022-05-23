import alarm
import struct

MAX_LENGTH = 2048

def store_string(offset, item_to_save):
    text_bytes = item_to_save.encode('utf-8')
    text_length = len(text_bytes)
    assert text_length < MAX_LENGTH
    alarm.sleep_memory[offset:offset+2] = struct.pack('H', text_length)
    data_offset = offset + 2
    alarm.sleep_memory[data_offset:data_offset+len(text_bytes)] = text_bytes

def read_string(offset):
    text_length, = struct.unpack('H', alarm.sleep_memory[offset:offset+2])
    assert text_length < MAX_LENGTH
    data_offset = offset + 2
    return alarm.sleep_memory[data_offset:data_offset+text_length].decode('utf-8')
