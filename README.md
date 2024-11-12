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
filepath = path_to_your_data
amplitude, phase = lf2_df(filepath)
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
    filepath = os.path.join(folder, f"{station}{date_str}{hour}.dat")
    # print(filepath)
    amp, ph = lf2_df(filepath)
    amplitude = pd.concat([amplitude, amp], axis=0)
    phase = pd.concat([phase, ph], axis=0)
    print(f"Data for {hour} hours processed.")
```
output: 2 dataframe with combined one-day data

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
