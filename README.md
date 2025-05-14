# PPARC-Octave-VLF-network-data-decoder
OCTAVES : VLF/LF ionosphere observation network is a project by Planetary Plasma and Atmosphere Research Centre (PPARC) in Tohoku University.
The new version of data is stored in a binary format.
The documentation given were not clear and will have a weird output if not interprate properly.
This script is an attempt to solve this issue.
Data can be downloaded from https://pparc.gp.tohoku.ac.jp/research/vlf/

# Usage
## For .dat file
To process one hour data:
```
import pandas as pd
filepath = "C:/KAG2025051501.dat"
file = open(filepath, "rb")
header = Header(file)
amplitude, phase, lightning = read_data(file, header)

```
output: 3 dataframes with amplitude, phase, and lightning data

top process one day of data:
```
date = pd.Timestamp("2025-05-15")
station = "KAG"
root_folder = "D:/raw"
export_folder = "D:/daily"

amplitude, phase, lightning = lf2df(date, station, root_folder)    # export_folder is optional. Skip this option to skip export.
```

to process multiple day of data:
```
import os
import pandas as pd

date_range = pd.date_range("2022-01-30", "2022-01-31", freq="D")
station = 'KAG'
root_folder = "D:/daily/wget"
export_folder = "D:/daily/OCTAVE"    ## OPTIONAL

for date in date_range:
    data_oneday(date, station, root_folder, export_folder)    # export_folder is optional. Skip this option to skip export.
```
output: 3 dataframe with combined one-day data

## For .spc file
To process one hour data:
```
import pandas as pd
filepath = path_to_your_data
amplitude, phase = spec2df(filepath)
```
output: two dataframes with amplitude and phase data

to process whole day of data:
```
import os
import pandas as pd
station = 'KAG'
date = pd.Timestamp('2022-01-15')
date_str = date.strftime('%Y%m%d')
folder = path_to_your_data

amplitude = pd.DataFrame()
phase = pd.DataFrame()

for i in range(0,24):
    hour = str(i).zfill(2)
    filepath = os.path.join(folder, f"{station}{date_str}{hour}.spc")
    # print(filepath)
    amp, ph = spec2df(filepath)
    amplitude = pd.concat([amplitude, amp], axis=0)
    phase = pd.concat([phase, ph], axis=0)
    print(f"Data for {hour} hours processed.")
```
output: 2 dataframe with combined one-day data
### NOTE: .spc data will be updated soon. I need to catch some zzz now.
