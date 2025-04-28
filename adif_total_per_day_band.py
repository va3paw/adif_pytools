# Lists totals of QSOs per day and per band
#
# Requirements: adif_io
# pip install adif-io

import adif_io
import sys

filename = sys.argv[1]
if not filename:
	raise "Usage: adif_total_per_day_band.py logfile.adif"

qsos, header =  adif_io.read_from_file(filename)

days = 0
qso_count = 0
all_bands = dict()
dates = dict()
for qso in qsos:

	date = qso["QSO_DATE"]
	band = qso["BAND"]

	if (date >= "19010101"):
		qso_count += 1

		dates.setdefault(date, dict())
		bands = dates[date]
		bands.setdefault(band, 0)
		bands[band] += 1
		dates[date] = bands

		all_bands.setdefault(band, 0)
		all_bands[band] += 1

header = "DATE\t"
for band in sorted(all_bands):
	header += "\t" + band
header += "\tTOTAL"
print(header)

for date in sorted(dates):
	days += 1
	total = 0
	line = date
	bands = dates[date]
	for band in sorted(all_bands):
		bands.setdefault(band, 0)
		line += "\t" + str(bands[band])
		total += bands[band]
	line += "\t" + str(total)
	print(line)

footer = "TOTAL\t"
for band in sorted(all_bands):
	footer += "\t" + str(all_bands[band])
footer += "\t" + str(qso_count)
print(footer)

print(f"{days} days; {qso_count} QSOs; {round(qso_count/days)} QSO/day")
