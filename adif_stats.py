# Lists totals of QSOs per day and per band
#
# Requirements: adif_io
# pip install adif-io

import adif_io
import sys

filename = sys.argv[1]
if not filename:
	raise "Usage: adif_stats.py logfile.adif"

qsos, header =  adif_io.read_from_file(filename)

days = 0
total_qso_count = 0
all_bands = dict()
all_modes = dict()
dates = dict()
modes = dict()
states = dict()
provinces = dict()
dxccs = dict()
operators = dict()

all_states = ['AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'La', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
all_provinces = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']

for qso in qsos:

	date = qso["QSO_DATE"]
	band = qso["BAND"]
	mode = qso["MODE"]
	dxcc = qso["DXCC"]
	state = qso.get("STATE", None)
	operator = qso.get("OPERATOR", None)
	# cqz = qso["CQZ"]

	if (date >= "19010101"):
		total_qso_count += 1

		dates.setdefault(date, dict())

		# parse bands
		bands = dates[date]
		bands.setdefault(band, 0)
		bands[band] += 1
		dates[date] = bands

		all_bands.setdefault(band, 0)
		all_bands[band] += 1

		# parse modes
		modes.setdefault(mode, 0)
		modes[mode] += 1

		# parse states
		if state and dxcc == "291" and state in all_states:
			states.setdefault(state, 0)
			states[state] += 1

		# parse Canadian provinces
		if state and dxcc == "1" and state in all_provinces:
			provinces.setdefault(state, 0)
			provinces[state] += 1

		# parse dxcc
		dxccs.setdefault(dxcc, 0)
		dxccs[dxcc] += 1

		# parse operators
		if operator:
			operators.setdefault(operator, 0)
			operators[operator] += 1

			operators_by_mode.setdefault(operator, dict())
			operator_by_mode = operators_by_mode[operator]
			operator_by_mode.setdefault(mode, 0)
			operator_by_mode[mode] += 1
			operators_by_mode[operator] = operator_by_mode

total_days = len(dates.keys())
total_operators = len(operators.keys())

# print(total_operators)
# print(sorted(states.keys()))
print(sorted(provinces.keys()))

print(f"Loaded {total_qso_count} QSOs from {filename}")

# print QSO by mode
print("\r\nTotal QSO by mode:")
header = ""
for mode in sorted(modes.keys()):
	header += mode + "\t"
header += "TOTAL"
print(header)

line = ""
total = 0
for mode in sorted(modes.keys()):	
	line += str(modes[mode]) + "\t"
	total += modes[mode]
line += str(total)
print(line)

if total_operators > 1:
	print("\r\nTotal QSO by operator by mode")
	header = "OPERATOR\t"
	for mode in sorted(modes.keys()):
		header += mode + "\t"
	header += "TOTAL"

	line = ""
	for operator in operators:
		line = operator + "\t"
		qso_per_operator = 0
		operator_by_mode = operators_by_mode[operator]
		for mode in sorted(modes.keys()):
			qso_count = operator_by_mode.get(mode, 0)
			line += str(qso_count) + "\t"
			qso_per_operator += qso_count
		line += str(qso_per_operator)
		print(line)

# print totals
print(f"\r\nTOTAL: {total_qso_count} QSOs; {total_days} days; {round(total_qso_count/total_days)} QSO/day; {len(dxccs.keys())} DXCC; {len(states.keys())} US States; {len(provinces.keys())} Canadian provinces")

