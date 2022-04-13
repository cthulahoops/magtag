import alarm

def store_string(offset, item_to_save):
    text_bytes = item_to_save.encode('utf-8')
    alarm.sleep_memory[offset] = len(text_bytes)
    alarm.sleep_memory[offset+1:offset+1+len(text_bytes)] = text_bytes

def read_string(offset):
    text_length = alarm.sleep_memory[offset]
    assert text_length < 256
    return alarm.sleep_memory[offset+1:1+offset+text_length].decode('utf-8')
