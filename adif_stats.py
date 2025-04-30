# Lists totals of QSOs per day and per band
#
# Requirements: adif_io
# pip install adif-io

import adif_io
import sys

ALL_STATES = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
ALL_PROVINCES = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']

def check_log(filename):
	qsos, header =  adif_io.read_from_file(filename)

	check_dxcc_missing = 1
	total_qso_count = 0
	unique_callsigns = set()
	dates = set()

	for qso in qsos:
		date = qso["QSO_DATE"]
		dates.add(date)
		dxcc = qso.get("DXCC", None)
		if (dxcc != None):
			check_dxcc_missing = 0
		total_qso_count += 1
		call = qso["CALL"]
		unique_callsigns.add(call)

	unique_callsigns_count = len(unique_callsigns)
	total_days = len(dates)
	return total_qso_count, unique_callsigns_count, total_days, check_dxcc_missing


def read_log(filename):

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

	for qso in qsos:

		call = qso["CALL"]
		date = qso["QSO_DATE"]
		band = qso["BAND"]
		mode = qso["MODE"]
		dxcc = qso.get("DXCC", None)
		state = qso.get("STATE", None)
		operator = qso.get("OPERATOR", None)
		# cqz = qso["CQZ"]


		if (date >= "19010101"):
			total_qso_count += 1
			# unique_callsigns.add(call)

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
			if state and state in ALL_STATES and (dxcc == "291" or dxcc == "6" or dxcc == None):
				states.setdefault(state, 0)
				states[state] += 1

				states_by_mode.setdefault(mode, set())
				state_by_mode = states_by_mode.get(mode, set())
				state_by_mode.add(state)
				states_by_mode[mode] = state_by_mode

			# parse Canadian provinces
			if state and state in ALL_PROVINCES and (dxcc == "1" or dxcc == None):
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

	return dates, modes, bands, all_bands, dxccs, dxccs_by_mode, states, states_by_mode, provinces, provinces_by_mode, operators, operators_by_mode


# PRINT STATS
def print_qso_by_mode(modes):

	# print QSO by mode
	print("Total QSO by mode:")
	total = 0
	for mode in sorted(modes.keys()):
		qso_count = modes[mode]
		print(f"{mode}\t{qso_count}")
		total += modes[mode]
	print(f"TOTAL\t{total}\r\n")


def print_dxcc_stats(dxccs_by_mode):

	check_dxcc_missing = True
	for mode in sorted(modes.keys()):
		dxcc_by_mode = dxccs_by_mode.get(mode, set())
		if len(dxcc_by_mode) > 0:
			check_dxcc_missing = False

	# print dxcc stats
	if check_dxcc_missing:
		print("Total DXCC worked by mode: NOT AVAILABLE\r\n")
	else:
		print("Total DXCC worked by mode:")
		for mode in sorted(modes.keys()):
			dxcc_by_mode = dxccs_by_mode[mode]
			print(f"{mode}\t{len(dxcc_by_mode)}")
		print("")

def print_states_by_mode(modes, states, states_by_mode):
	# print states by mode stats
	print("Total US states worked by mode:")
	for mode in sorted(modes.keys()):
		state_by_mode = states_by_mode.get(mode, set())
		# qso_count = len(state_by_mode)
		# print(f"{mode}\t{qso_count}")
		# print(state_by_mode)

		missing_states = ""
		worked_states = 0
		for state in ALL_STATES:
			if state in state_by_mode:
				worked_states += 1
			else:
				missing_states += f"{state} "

		if len(missing_states) >= len(ALL_STATES)*3:
			missing_states = str(len(ALL_STATES))
		if (missing_states == ""):
			missing_states = "None"

		print(f"{mode}\t{len(state_by_mode)} out of {len(ALL_STATES)}; missing: {missing_states}")

	missing_states = ""
	worked_states = 0
	for state in ALL_STATES:
		qso_count = states.get(state, 0)
		if qso_count == 0:
			missing_states += f"{state} "
		else:
			worked_states += 1

	if len(missing_states) >= len(ALL_STATES)*3:
		missing_states = str(len(ALL_STATES))
	else:
		if (missing_states == ""):
			missing_states = "None"

	print(f"Overall: {worked_states} out of {len(ALL_STATES)} total; missing: {missing_states}\r\n")


def print_provinces_by_mode(modes, provinces, provinces_by_mode):
	# print provinces stats
	print("Total Canadian provinces worked by mode:")
	for mode in sorted(modes.keys()):
		province_by_mode = provinces_by_mode.get(mode, set())

		missing_provinces = ""
		worked_provinces = set()
		for province in ALL_PROVINCES:
			if province in province_by_mode:
				worked_provinces.add(province)
			else:
				missing_provinces += f"{province} "

		if len(missing_provinces) >= len(ALL_PROVINCES)*3:
			missing_provinces = str(len(ALL_STATES))
		else:
			if (missing_provinces == ""):
				missing_provinces = "None"

		print(f"{mode}\t{len(province_by_mode)} ({' '.join(sorted(worked_provinces))}) out of {len(ALL_PROVINCES)}; missing: {missing_provinces}")

	missing_provinces = ""
	worked_provinces = 0
	for province in ALL_PROVINCES:
		qso_count = provinces.get(province, 0)
		if qso_count == 0:
			missing_provinces += f"{province} "
		else:
			worked_provinces += 1

	if len(missing_provinces) >= 150:
		missing_provinces = str(len(ALL_PROVINCES))
	else:
		if (missing_provinces == ""):
			missing_provinces = "None"
	print(f"Overall: {worked_provinces} out of {len(ALL_PROVINCES)} total; missing: {missing_provinces}\r\n")


def print_operators_by_mode(modes, operators, operators_by_mode):
	# print qso by operator
	total_operators = len(operators.keys())
	if total_operators > 1:
		print("Total QSO by operator by mode:")
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

		print("")


def print_qso_per_day(bands, all_bands):

	days = 0
	qso_count = 0

	print("Total QSO per day:")
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
		qso_count += total
		print(line)

	footer = "TOTAL\t"
	for band in sorted(all_bands):
		footer += "\t" + str(all_bands[band])
	footer += "\t" + str(qso_count)
	print(footer)

	print(f"Overall: {len(all_bands)} bands; {days} days; {qso_count} QSOs; {round(qso_count/days)} QSO/day\r\n")

# MAIN
filename = sys.argv[1]
if filename:

	# GET LOG TOTALS
	total_qso_count, unique_callsigns_count, total_days, check_dxcc_missing = check_log(filename)
	print(f"Loaded {total_qso_count} QSOs ({unique_callsigns_count} unique callsigns) from {filename}")
	if check_dxcc_missing:
		print("Warning: DXCC column is missing / empty.")

	# GET LOG DETAILS
	dates, modes, bands, all_bands, dxccs, dxccs_by_mode, states, states_by_mode, provinces, provinces_by_mode, operators, operators_by_mode = read_log(filename)

	print("")
	print_qso_by_mode(modes)
	print_dxcc_stats(dxccs_by_mode)
	print_states_by_mode(modes, states, states_by_mode)
	print_provinces_by_mode(modes, provinces, provinces_by_mode)
	print_operators_by_mode(modes, operators, operators_by_mode)

	print_qso_per_day(bands, all_bands)

	# print totals
	print(f"TOTAL: {total_qso_count} QSOs; {unique_callsigns_count} unique callsigns; {total_days} days; {round(total_qso_count/total_days)} QSO/day; {len(dxccs.keys())} DXCC; {len(states.keys())} US States; {len(provinces.keys())} Canadian provinces")

else:
	raise "Usage: adif_total_per_day_band.py logfile.adif"
