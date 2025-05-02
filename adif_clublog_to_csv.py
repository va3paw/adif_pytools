# Convert Clublog OQRS ADIF file to CSV
#
# Requirements: adif_io
# pip install adif-io

import adif_io
import sys

def convert_adif_log(filename):

	qsos, header =  adif_io.read_from_file(filename)
	csv_filename = filename + ".csv"

	total_qso_count = 0
	header = ['CALL', 'QSO_DATE', 'TIME_ON', 'BAND', 'MODE'
		, 'QSL_RCVD', 'QSLRDATE', 'QSL_RCVD_VIA', 'QSL_SENT_VIA', 'QSL_SENT'
		, 'EMAIL', 'ADDRESS', 'NOTES'
		, 'DONATION', 'CURRENCY'
		, 'GRIDSQUARE', 'RST_SENT', 'RST_RCVD', 'FREQ'
		]
	lines = list()

	for qso in qsos:

		line = list()
		for item in header:
			
			value = qso.get(item, '\"\"')
			line.append(f"\"{value}\"")
		lines.append(line)

	return header, lines


def print_csv(header, lines):

	print(','.join(header))

	for line in lines:
		print(','.join(line))

# MAIN
filename = sys.argv[1]
if filename:
	header, lines = convert_adif_log(filename)
	print_csv(header, lines)

else:
	raise "Usage: adif_clublog_to_csv.py logfile.adif"
