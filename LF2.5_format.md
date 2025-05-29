This page archives the format of LF data used by OCTAVES : VLF/LF ionosphere observation network for future researchers who wish to use the data. The original website seems no longer available. The data is still available at https://pparc.gp.tohoku.ac.jp/research/vlf/#data.

The original documentation is in Japanese, and I'm actually not proficient in it. Therefore some of the words might be translated poorly (and English is not my primary, so please don't judge :( )

=================================================================
# LF Data Format
=================================================================

## Update History
Date | Note | Version | Contributor
|----|----|----|----|
|2010/01/21 | First version | Ver.1 | 土屋 |
|2010/01/23 | Fixed a bug while saving time.| Ver.1.1 | 土屋
|2010/01/23 | Header format correction	    | Ver.1.1 | 土屋
|2010/01/23 | Add the observation point name to the header. | Ver.1.1 | 土屋
|2015/03/--	| Adding lightning monitor data	|Ver.2.2 | 土屋
|2016/08/03	| Addidng WDT events			|Ver.2.3 | 土屋
|2016/08/04	| Multi-channel input supported |Ver.2.4 | 土屋
|2017/07/09	| Unit of power is dBVpp@ADC    |Ver.2.5 | Tsuchiya

### Phase and amplitude data for selected frequencies (NF points)
Filename: SSSYYYYMMDDHH_CH.dat
SSS: Station name
CH: Channel number

*** Note: When there is only one channel, _CH is not added to the file name.

### Parameters of the files
Number of selected frequencies: n_fq=10 (maximum 20 points, adjustable by n_fq and fq_list.txt)
Time resolution: 0.1 seconds

### Data structure
For each 1-second data:

header block
Data block 1: (4 bytes + [n_fq × 2 bytes × 2 + 2 bytes] × 10)
Data block 2: (4 bytes + [n_fq × 2 bytes × 2 + 2 bytes] × 10)
…
etc.

For each block, the number of bytes in a block is

```math
40 \times \text{no. of frequency} + 24
```

So if the number of frequencies is 10, each block contains 424 bytes; if 15, each contains 624 bytes; and if 20, each contains 824 bytes.

### Header block structure
|Parameters `(units)`| Byte type | Byte location in block |
|:---- | :----: | :----: |
|Year `(YYYY)` | signed single (2byte) | 2 |
|Month and Day `(MMDD)` | signed single (2byte) | 4 |
|Hour `(HH)` | signed single (2byte) | 6 |
|Sampling frequency `(kHz)` | signed single (2byte) | 8 |
|Data length for FFT | signed single (2byte) | 10 |
|Number of saved frequency (n_fq) | signed single (2byte) | 12 |
|Block size `(byte)` | signed single (2byte) | 14
|Saved frequency `(0.1 MHz)` | signed single (2byte) × n_fq | 14 + n_fq × 2
|Station name | char[4] (4byte) | 18+n_fq*2
|Lightning monitor frequency lower bound `(kHz)` | signed single (2byte) | 20+n_fq*2
|Lightning monitor frequency lower bound `(kHz)` | signed single (2byte) | 22+n_fq*2
|WDT events | signed single (2byte) | 24+n_fq*2
|Channel number | unsigned char (1byte) | 25+n_fq*2
|Number of Channels | unsigned char (1byte) | 26+n_fq*2
|FFT window | unsigned char (1byte) | 27+n_fq*2
|zero padding | zero (Block size - 14 - 2 × n_fq - 15)  | 28+n_fq*2
|SW version | unsigned char (1byte) | Block size - 2	
|SW sub-version | unsigned char (1byte) | Block size - 1

### Data block structure
|Parameters `(units)`| Byte type |
|:---- | :----: |
| Header block (must be 32767) | signed single (2byte)
|Time(MMSS) | signed single (2byte)
|Amplitude×NF @ HHMMSS.0 | signed single (2byte)×n_fq	
|Phase×NF @ HHMMSS.0 | signed single (2byte)×n_fq
|Lightning monitor @ HHMMSS.0 | signed single (2byte)		
|Amplitude×NF @ HHMMSS.1 | signed single (2byte)×n_fq	
|Phase×NF @ HHMMSS.1 | signed single (2byte)×n_fq
|Lightning monitor @ HHMMSS.1 | signed single (2byte)
|・・・							
|Amplitude×NF @ HHMMSS.9 | signed single (2byte)×n_fq	
|Phase×NF @ HHMMSS.9 | signed single (2byte)×n_fq
|Lightning monitor @ HHMMSS.9 | signed single (2byte)

Number of bytes in data = $10 \times (2 \times 2 \text{bytes} \times \text{n}_{fq} + 2)$

#### Unit conversion factor
|Parameter | Recorded units | Conversion factor |
|:---- | :----: | :----: |
|Amplitude | dBc×100 | 0.01 |
|Phase | radians×1000 | 0.001 |
|Lightning monitor | dBc×100 | 0.01 |

#### $dB_c$ to $dB_{V_{pp}}$
```math
dB_{V_{pp}} = dB_c + P_{cnv}
```
|FFT window| Blackman | Flat | Hanning | Hamming |
|:---- | :----: | :----: | :----: | :----: |
|$P_{cnv}$ | -52.5 | -60 | -54 | -54.7


## Frequency and Phase spectrum data
Filename: SSSYYYYMMDDHH_CH.spc
SSS: station name
CH : channel number

### Parameters
Time decomposition (n_save_t)：	30s on average
Time resolution (n_save_f)：	50Hz
Frequency range：	0-100kHz
FFT points (n_fft):   4000
No. of data points：	NS = n_fft/n_save_f/2+1 = 2001

### Data format
	30(n_save_t)秒に1blockのデータを生成

	[header block]
	[data block1] (NS x 2 x 2byte + 2 x 2byte)
	[data block2] (NS x 2 x 2byte + 2 x 2byte)
	[data block3] (NS x 2 x 2byte + 2 x 2byte)
	・・・

	blockサイズ：NS x 2 x 2byte + 2 x 2byte
			NS=2001の時、8,008 byte (ファイルサイズ：8,008 ×(2 * 60 + 1) = 968,968)

	header block内データフォーマット
		年(YYYY)		signed single (2byte)		2 [Total Byte]
		月日(MMDD)		signed single (2byte)		4
		時(HH)			signed single (2byte)		6
		サンプリング周波数[kHz]	signed single (2byte)		8
		FFT点数			signed single (2byte)		10
		時間方向平均[sec]	signed single (2byte)		12
		周波数方向平均[pt]	signed single (2byte)		14
		周波数方向点数		signed single (2byte)		16
		周波数分解能[Hz]	signed single (2byte)		18
		ブロックサイズ[Byte]	signed single (2byte)		20
		観測地点名		char[4]	      (4byte)		24
		WDT発生回数		signed single (2byte)		26
		チャンネル番号		unsigned char (1byte)		27
		チャンネル数		unsigned char (1byte)		28
		FFT window		unsigned char (1byte)		29
		ブロックの残り部分は0詰
		SW version		unsigned char (1byte)		30
		SW sub-version		unsigned char (1byte)		31

	data block内フォーマット
		先頭データ(32767) 	signed single (2byte)
		時間(MMSS)※		signed single (2byte)
		振幅値[dBc]×NS		signed single (2byte)×NS
		位相値[rad]×NS		signed single (2byte)×NS
		※時刻は、平均に使用した最後のデータの取得時刻

