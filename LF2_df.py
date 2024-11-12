import struct
import pandas as pd
import datetime as dt

def read_datablock(file, year, hour, num_freq_channels, block_size, month, day):
    data_block = file.read(block_size)
    start_mark = struct.unpack('h', data_block[:2])[0]
    if start_mark == 32767:
        minute_second = struct.unpack('h', data_block[2:4])[0]
        # separate minute and second
        minute = minute_second // 60
        second = minute_second % 60
        # print(minute, second)
        # read the rest of the second block
        # First {no of freq channels} * 2 bytes are amplitude for 0.0s offset from Time
        # Next {no of freq channels} * 2 bytes are phase for 0.0s offset from Time
        # Next {no of freq channels} * 2 bytes are amplitude for 0.1s offset from Time
        # Next {no of freq channels} * 2 bytes are phase for 0.1s offset from Time
        # ... repeated for 10 intervals (0.1s each)
        offset = 4
        da = []
        dp = []
        for i in range(10):
            time = dt.datetime(year, month, day, hour, minute, second, i*100000)
            amplitudes = struct.unpack(f'<{num_freq_channels}h', data_block[offset:offset + num_freq_channels * 2])
            phases = struct.unpack(f'<{num_freq_channels}h', data_block[offset + num_freq_channels * 2:offset + num_freq_channels * 4])
            offset += num_freq_channels * 4
            # convertion factors: Amplitude = Amplitude * 0.01, Phase = Phase * 0.0001
            amplitudes = [round(a * 0.01,2) for a in amplitudes]
            phases = [round(p * 0.0001,1) for p in phases]
            amplitudes.insert(0, time)
            phases.insert(0, time)
            # print(amplitudes)
            # print(phases)
            da.append(amplitudes)
            dp.append(phases)
    else:
        print("Start mark not found in the data block.")
        return None
    return da, dp

def read_header(file):
    header = file.read(14)
    year, month_day, hour, sampling_freq, fft_length, num_freq_channels, block_size = struct.unpack('<7H', header)
    month = month_day // 100
    day = month_day % 100
    frequencies = struct.unpack(f'<{num_freq_channels}H', file.read(2 * num_freq_channels))
    # convert frequencies to Hz
    frequencies = [f*10 for f in frequencies]
    station = file.read(3).decode('utf-8')
    # read the rest of the first block
    empty_bytes = block_size - 3 - 14 - 2 * num_freq_channels
    data_block = file.read(empty_bytes)
    return year,hour,num_freq_channels,block_size,month,day,frequencies

def lf2_df(filepath):
    with open(filepath, "rb") as file:
        year, hour, num_freq_channels, block_size, month, day, frequencies = read_header(file)
    
        da = []; dp = []
        while True:
            try:
                amplitudes, phases = read_datablock(file, year, hour, num_freq_channels, block_size, month, day)
                da.extend(amplitudes)
                dp.extend(phases)
            except:
                # print("Process completed.")
                break
    
    df_a = pd.DataFrame(da, columns=['Time'] + [f'{i}' for i in frequencies])
    df_p = pd.DataFrame(dp, columns=['Time'] + [f'{i}' for i in frequencies])
    return df_a,df_p
