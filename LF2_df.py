import struct
import pandas as pd
import os

class Header:
    '''
    Define the header class
    NOTE: run  ```header = Header(file)``` to create header object
    attributes:
    year: year of the data
    month: month of the data
    day: day of the data
    hour: hour of the data
    date_time: date and time of the data
    sampling_frequency: sampling frequency of the data
    fft_length: FFT length of the data
    num_freq_channels: number of frequency channels
    block_size: size of the data block
    frequencies: list of frequencies
    station: station name
    lightning_range: lightning observation frequency
    WDT_no: WDT occurrence
    channel_no: channel number
    num_channels: number of channels
    fft_window: FFT window
    sw_version: software version
    '''
    def __init__(self, file):
        self.year, self.month_day, self.hour, self.sampling_frequency, self.fft_length, self.num_freq_channels, self.block_size = struct.unpack('<7h', file.read(14))
        self.month = self.month_day // 100
        self.day = self.month_day % 100
        self.date_time = pd.Timestamp(self.year, self.month, self.day, self.hour)
        self.frequencies = struct.unpack(f'<{self.num_freq_channels}h', file.read(2 * self.num_freq_channels))
        # convert frequencies to Hz
        self.frequencies = [f*10 for f in self.frequencies]
        self.station = file.read(4).decode('utf-8')
        self.lightning_range = struct.unpack('<2h', file.read(4))
        self.WDT_no = struct.unpack('<h', file.read(2))[0]
        self.channel_no = struct.unpack('<B', file.read(1))[0]
        self.num_channels = struct.unpack('<B', file.read(1))[0]
        self.fft_window = struct.unpack('<B', file.read(1))[0]
        # read the rest of the first block
        empty_bytes = self.block_size - 14 - 2 * self.num_freq_channels - 15
        empty_block = file.read(empty_bytes)
        # SW version: unsigned character (2 byte)
        self.sw_version = struct.unpack('<B', file.read(1))[0]
        self.sw_subversion = struct.unpack('<B', file.read(1))[0]
        self.sw_version = f"{self.sw_version}.{self.sw_subversion}"
    
    def print_header(self):
        ''' print the header information '''
        print(f"Header Information:")
        print(f'''
        Date = {self.year}-{self.month}-{self.day} 
        Time = {self.hour}:00:00
        Sampling Frequency = {self.sampling_frequency} kHz
        FFT Length = {self.fft_length}
        Number of Frequency Channels = {self.num_freq_channels}
        Block Size = {self.block_size}
        Frequencies = {self.frequencies[i]}
        Station = {self.station}
        Lightning observation frequency = {self.lightning_range}
        WDT Occurance = {self.WDT_no}
        Channel Number = {self.channel_no}
        Number of Channels = {self.num_channels}
        FFT Window = {self.fft_window}
        SW Version = {self.sw_version}''')
        
def read_data(file, header):
    ''' read the data block and return amplitude, phase and lightning data 
    parameters:
    file: opened file object. NOTE: file should be opened in binary mode
    header: header object containing header attributes. run ```header = Header(file)``` to create header object
    
    return:
    amplitude: dataframe of amplitude data
    phase: dataframe of phase data
    lightning: dataframe of lightning data
    '''
    amplitude = []
    phase = []
    lightning = []

    while True:
        try:
            # read the first block
            data_block = file.read(header.block_size)
            start_mark = struct.unpack('<h', data_block[:2])[0]
            if start_mark == 32767:
                minute_second = struct.unpack('<h', data_block[2:4])[0]
                # separate minute and second
                minute = minute_second // 100
                second = minute_second % 100
                # print(minute, second)
                
                # read data of first milisecond
                n = 4   # keep track of number of bytes read
                for i in range(10):
                    time = pd.Timestamp(header.year, header.month, header.day, header.hour, minute, second, i*100000)
                    amp = list(struct.unpack(f'<{header.num_freq_channels}h', data_block[n:n + header.num_freq_channels * 2]))
                    n += header.num_freq_channels * 2
                    ph = list(struct.unpack(f'<{header.num_freq_channels}h', data_block[n:n + header.num_freq_channels * 2]))
                    n += header.num_freq_channels * 2
                    li = list(struct.unpack('<h', data_block[n:n + 2]))
                    n += 2

                    amp = [round(a * 0.01, 2) for a in amp]
                    ph = [round(p * 0.0001, 3) for p in ph]
                    li = [round(l * 0.01, 2) for l in li]

                    # insert time at the beginning of each list
                    amp.insert(0, time)
                    ph.insert(0, time)
                    li.insert(0, time)

                    # append to the list directly to improve performance
                    amplitude.append(amp)
                    phase.append(ph)
                    lightning.append(li)
            else:
                print("Start mark not found in the data block.")
                break
        except:
            break
    file.close()

    # convert to dataframe
    amplitude = pd.DataFrame(amplitude, columns=['Time'] + [f'{i}' for i in header.frequencies])
    phase = pd.DataFrame(phase, columns=['Time'] + [f'{i}' for i in header.frequencies])
    lightning = pd.DataFrame(lightning, columns=['Time', header.lightning_range[0]])

    return amplitude, phase, lightning

def lf2df(date, station, root_folder, export_folder = None):
    '''
    Process 1 day data
    
    parameters:
    date: date of the data
    station: station name
    root_folder: folder containing the data
    export_folder: folder to export the data. Leave it blank to skip exporting
    '''
    print(f"Processing data for {date.strftime('%Y-%m-%d')}...")
    amplitude = {}
    phase = {}
    lightning = {}
    for i in range(0,24):
        hour = str(i).zfill(2)
        filepath = os.path.join(root_folder, f"{station}{date.strftime('%Y%m%d')}{hour}.dat")
    # print(filepath)
        try:
            file = open(filepath, "rb")
            header = Header(file)
            amp, ph, li = read_data(file, header)
            amplitude[hour] = amp
            phase[hour] = ph
            lightning[hour] = li
            print(f"Data for {hour} hours processed.")
        except FileNotFoundError:
            print(f"File not found for {hour} hours.")
            continue

    print("Cleaning up data...")

    try:    # convert to dataframe
        amplitude = pd.concat(amplitude.values(), axis=0)
        phase = pd.concat(phase.values(), axis=0)
        lightning = pd.concat(lightning.values(), axis=0)
        amplitude.sort_values(by='Time', inplace=True)
        amplitude.reset_index(drop=True, inplace=True)
        phase.sort_values(by='Time', inplace=True)
        phase.reset_index(drop=True, inplace=True)
        lightning.sort_values(by='Time', inplace=True)
        lightning.reset_index(drop=True, inplace=True)
    except ValueError:  # if no data is found for the day, skip the day
        # print(f"No data found for {date.strftime('%Y-%m-%d')}.")
        return None, None, None

    if export_folder:
        print("Exporting data...")
        export_folder = os.path.join(export_folder, station, date.strftime('%Y'), date.strftime('%m'))
        try:
            amplitude.to_csv(os.path.join(export_folder, f"{station}_{date.strftime('%Y-%m-%d')}_amp.csv"), index=False)
            print("Amplitude data exported.")
            phase.to_csv(os.path.join(export_folder, f"{station}_{date.strftime('%Y-%m-%d')}_ph.csv"), index=False)
            print("Phase data exported.")
        except OSError:
            print(f"Export folder {export_folder} not found. Creating folder...")
            os.makedirs(export_folder, exist_ok=True)
            amplitude.to_csv(os.path.join(export_folder, f"{station}_{date.strftime('%Y-%m-%d')}_amp.csv"), index=False)
            print("Amplitude data exported.")
            phase.to_csv(os.path.join(export_folder, f"{station}_{date.strftime('%Y-%m-%d')}_ph.csv"), index=False)
            print("Phase data exported.")
            lightning.to_csv(os.path.join(export_folder, f"{station}_{date.strftime('%Y-%m-%d')}_lightning.csv"), index=False)
            print("Lightning data exported.")
    else:
        print("Data processing completed.")

    return amplitude, phase, lightning
