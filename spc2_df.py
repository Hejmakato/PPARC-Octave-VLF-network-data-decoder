import struct
import numpy as np
import pandas as pd
import datetime as dt

filepath = r"c:\Users\godkn\Downloads\LF_data\KAG2022011500.spc"

def read_header_spec(file):
    header = file.read(20)
    year, month_day, hour, samp_freq, fft_length, avg_time, samp_point, n_freq, resolution, block_size = struct.unpack('<10H', header)
    month = month_day // 100
    day = month_day % 100
#     print(
#         f'''Date: {pd.Timestamp(year, month, day, hour).strftime('%Y-%m-%d %H:%M:%S')}
# Sampling Frequency: {samp_freq} kHz
# FFT Length: {fft_length}
# Average Time: {avg_time}
# Sampling Points: {samp_point}
# Number of Frequencies: {n_freq}
# Resolution: {resolution}
# Block Size: {block_size}''')
    
    # determine frequency channels
    freq_channels = np.arange(0, samp_freq*1000/2 + resolution, resolution)
    # print(f"Frequency Channels: {freq_channels}")

    # read empty bytes
    station = file.read(3).decode('utf-8')
    empty_bytes = block_size - 20 - 3
    data_block = file.read(empty_bytes)
    return year,hour,n_freq,block_size,month,day,freq_channels

def read_data_spec(file, year, hour, n_freq, block_size, month, day):
    da = []
    dp = []
    while True:
        try:
            # read the data block
            data_block = file.read(block_size)
            # print(data_block)
            start_mark = struct.unpack('h', data_block[:2])[0]
            # print(start_mark)
            if start_mark == 32767:
                minute_second = struct.unpack('h', data_block[2:4])[0]
                minute = minute_second // 60
                second = minute_second % 60
                # print(minute, second)
                offset = 4
                # Read spectral data
                # Amplitude spectral data: signed single (2 bytes) * no of freq channels
                # Phase spectral data: signed single (2 bytes) * no of freq channels
                time = dt.datetime(year, month, day, hour, minute, second)
                amplitudes = struct.unpack(f'<{n_freq}h', data_block[offset:offset + n_freq * 2])
                phases = struct.unpack(f'<{n_freq}h', data_block[offset + n_freq * 2:offset + n_freq * 4])
                offset += n_freq * 4
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
                break
        except:
            # print("End of file.")
            break
    return da,dp

def spec2df(filepath):
    with open(filepath, "rb") as file:
    # read the header
        year, hour, n_freq, block_size, month, day, freq_channels = read_header_spec(file)
    # print(data_block)
        da, dp = read_data_spec(file, year, hour, n_freq, block_size, month, day)
    
        df_a = pd.DataFrame(da, columns=['Time'] + [f'{i}' for i in freq_channels])
        df_p = pd.DataFrame(dp, columns=['Time'] + [f'{i}' for i in freq_channels])
    return df_a, df_p

# df_a, df_p = spec2df(filepath)
        