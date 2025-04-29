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
states_by_mode = dict()
provinces = dict()
provinces_by_mode = dict()
dxccs = dict()
dxccs_by_mode = dict()
operators = dict()
operators_by_mode = dict()

check_dxcc_missing = 1

all_states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
all_provinces = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']

for qso in qsos:

	date = qso["QSO_DATE"]
	band = qso["BAND"]
	mode = qso["MODE"]
	dxcc = qso.get("DXCC", None)
	state = qso.get("STATE", None)
	operator = qso.get("OPERATOR", None)
	# cqz = qso["CQZ"]

	if (dxcc != None):
		check_dxcc_missing = 0

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
		if state and state in all_states and (dxcc == "291" or dxcc == "6" or dxcc == None):
			states.setdefault(state, 0)
			states[state] += 1

			states_by_mode.setdefault(mode, set())
			state_by_mode = states_by_mode.get(mode, set())
			state_by_mode.add(state)
			states_by_mode[mode] = state_by_mode

		# parse Canadian provinces
		if state and state in all_provinces and (dxcc == "1" or dxcc == None):
			provinces.setdefault(state, 0)
			provinces[state] += 1

			provinces_by_mode.setdefault(mode, set())
			province_by_mode = provinces_by_mode.get(mode, set())
			province_by_mode.add(state)
			provinces_by_mode[mode] = province_by_mode
			

		# parse dxcc
		# https://adif.org/315/ADIF_315.htm#DXCC_Entity_Code_Enumeration
		if dxcc:
			dxccs.setdefault(dxcc, 0)
			dxccs[dxcc] += 1
			
			dxccs_by_mode.setdefault(mode, set())
			dxcc_by_mode = dxccs_by_mode.get(mode, set())
			dxcc_by_mode.add(dxcc)
			dxccs_by_mode[mode] = dxcc_by_mode


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
# print(sorted(provinces.keys()))

# PRINT RESULTS
print(f"Loaded {total_qso_count} QSOs from {filename}")

# RUN CHECKS
if check_dxcc_missing:
	print("Warning: DXCC column is missing / empty.")

# PRINT STATS

# print QSO by mode
print("\r\nTotal QSO by mode:")
total = 0
for mode in sorted(modes.keys()):
	qso_count = modes[mode]
	print(f"{mode}\t{qso_count}")
	total += modes[mode]
print(f"TOTAL\t{total}")

# print provinces stats
if check_dxcc_missing:
	print("\r\nTotal DXCC worked by mode: NOT AVAILABLE")
else:
	print("\r\nTotal DXCC worked by mode:")
	for mode in sorted(modes.keys()):
		dxcc_by_mode = dxccs_by_mode[mode]
		print(f"{mode}\t{len(dxcc_by_mode)}")

# print states by mode stats
print("\r\nTotal US states worked by mode:")
for mode in sorted(modes.keys()):
	state_by_mode = states_by_mode.get(mode, set())
	# qso_count = len(state_by_mode)
	# print(f"{mode}\t{qso_count}")
	# print(state_by_mode)

	missing_states = ""
	worked_states = 0
	for state in all_states:
		if state in state_by_mode:
			worked_states += 1
		else:
			missing_states += f"{state} "

	if len(missing_states) >= len(all_states)*3:
		missing_states = " " + str(len(all_states))

	print(f"{mode}\t{len(state_by_mode)} out of {len(all_states)}; missing: {missing_states}")

missing_states = ""
worked_states = 0
for state in all_states:
	qso_count = states.get(state, 0)
	if qso_count == 0:
		missing_states += " " + state
	else:
		worked_states += 1

if len(missing_states) >= len(all_states)*3:
	missing_states = " " + str(len(all_states))

print(f"Overall: {worked_states} out of {len(all_states)} total (missing:{missing_states})")

# print provinces stats
print("\r\nTotal Canadian provinces worked by mode:")
for mode in sorted(modes.keys()):
	province_by_mode = provinces_by_mode.get(mode, set())

	missing_provinces = ""
	worked_provinces = set()
	for province in all_provinces:
		if province in province_by_mode:
			worked_provinces.add(province)
		else:
			missing_provinces += f"{province} "

	if len(missing_provinces) >= len(all_provinces)*3:
		missing_provinces = " " + str(len(all_states))

	print(f"{mode}\t{len(province_by_mode)} ({' '.join(sorted(worked_provinces))}) out of {len(all_provinces)}; missing: {missing_provinces}")

missing_provinces = ""
worked_provinces = 0
for province in all_provinces:
	qso_count = provinces.get(province, 0)
	if qso_count == 0:
		missing_provinces += " " + province
	else:
		worked_provinces += 1

if len(missing_provinces) >= 150:
	missing_provinces = " " + str(len(all_provinces))

print(f"Overall: {worked_provinces} out of {len(all_provinces)} total (missing:{missing_provinces})")


# print qso by operator
if total_operators > 1:
	print("\r\nTotal QSO by operator by mode")
	header = "CALL\t"
	for mode in sorted(modes.keys()):
		header += mode + "\t"
	header += "TOTAL"
	print(header)

	line = ""
	for operator in sorted(operators):
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

