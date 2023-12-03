import argparse
import json

parser = argparse.ArgumentParser(prog="compare_comm_period_info.py", 
                                 description="""
    Creates JSON of overlapping and non-overlapping communication periods of the reference mobility and alternative (new) mobility,
    for the specified satellite module name of the specified constellation.
    For each period group (overlap) and unmatched period, the JSON includes: 
     - start and end times of the periods
     - offset to the used TLE's epoch
     - if there are multiple matches ??? 
     - "ref_coverage" statistic: How much of the reference period is covered by the period of the alternative mobility.
     - "new_excluded" statistic: How much of the period of the alternative mobility is included in the reference period.
     - "excluded_time_to_ref_time" statistic: Ratio of the time that's not included in the reference period to the time of the reference period.
    """)
parser.add_argument("ref_mobility_periods_path", help="")
parser.add_argument("new_mobility_periods_path")
parser.add_argument("output_path")
args = parser.parse_args()

ref_mobility_periods_stats = None
with open(args.ref_mobility_periods_path, "r") as stats_f:
    ref_mobility_periods_stats = json.load(stats_f)
new_mobility_periods_stats = None
with open(args.new_mobility_periods_path, "r") as stats_f:
    new_mobility_periods_stats = json.load(stats_f)

ref_mobility = ref_mobility_periods_stats["mobility"]
new_mobility = new_mobility_periods_stats["mobility"]

# find overlapping communication periods
ref_periods = ref_mobility_periods_stats["periods"]
new_periods = new_mobility_periods_stats["periods"]

period_groups = []
unmatched_periods = []
matched_new_mobility_periods = []

ref_time_total_sum = 0
excluded_time_total_sum = 0

for ref_period_idx in range(0, len(ref_periods)):
    ref_p = ref_periods[ref_period_idx]
    ref_p_start = ref_p[0]
    ref_p_end = ref_p[1]

    ref_time_total_sum += ref_p_end - ref_p_start

    match_found = False
    ref_p_period_groups = []

    # find a matching communication period of alternative (new) mobility
    for new_period_idx in range(0, len(new_periods)):
        new_p = new_periods[new_period_idx]
        new_p_start = new_p[0]
        new_p_end = new_p[1]

        # match found
        # new_start in ref_period | new_end end ref_period | ref_period in new_period
        if (new_p_start >= ref_p_start and new_p_start <= ref_p_end) or (new_p_end >= ref_p_start and new_p_end <= ref_p_end) or (new_p_start <= ref_p_start and new_p_end >= ref_p_end):
            ref_p_period_groups.append( {ref_mobility: {"period_idx": ref_period_idx, "period": ref_p}, 
                                         new_mobility: {"period_idx": new_period_idx, "period": new_p},
                                         "ref_start_to_epoch_offset": ref_mobility_periods_stats["period_start_to_epoch_offsets"][ref_period_idx]} 
                                      )
            matched_new_mobility_periods.append(new_p)
            match_found = True
    
    if not match_found:
        
        unmatched_periods.append({ref_mobility: {"period_idx": ref_period_idx, "period": ref_p}, "ref_coverage": 0, "new_excluded": 0, "ref_start_to_epoch_offset": ref_mobility_periods_stats["period_start_to_epoch_offsets"][ref_period_idx]})

    else:

        if len(ref_p_period_groups) > 1:
            for g in ref_p_period_groups:
                g["multiple_matches"] = True
        else:
            for g in ref_p_period_groups:
                g["multiple_matches"] = False
        
        for g in ref_p_period_groups:
            period_groups.append(g)
    
    ref_period_idx += 1

ref_coverage_sum = 0
new_excluded_sum = 0

for g in period_groups:
    
    ### calc coverage of ref ###
    # start second of ref period, or start second of new period if after ref start
    new_in_ref_start = max(g[ref_mobility]["period"][0], g[new_mobility]["period"][0])
    # end second of ref period, or end second of new period if before ref start
    new_in_ref_end = min(g[ref_mobility]["period"][1], g[new_mobility]["period"][1])
    coverage = (new_in_ref_end - new_in_ref_start) / (g[ref_mobility]["period"][1] - g[ref_mobility]["period"][0])
    ref_coverage_sum += coverage

    ### calc excluded percent of new ###
    excluded_sum = 0
    if g[new_mobility]["period"][0] < g[ref_mobility]["period"][0]:
        excluded_sum += g[ref_mobility]["period"][0] - g[new_mobility]["period"][0]
    if g[new_mobility]["period"][1] > g[ref_mobility]["period"][1]:
        excluded_sum += g[new_mobility]["period"][1] - g[ref_mobility]["period"][1]
    
    excluded_time_total_sum += excluded_sum
    excluded_perc = None
    if excluded_sum > 0:
        excluded_perc = excluded_sum / (g[new_mobility]["period"][1] - g[new_mobility]["period"][0]) 
    else:
        excluded_perc = 0
    new_excluded_sum += excluded_perc

    #  calc excluded time to ref time
    excluded_time_to_ref_time = excluded_sum / ( g[ref_mobility]["period"][1] - g[ref_mobility]["period"][0] ) 

    g["ref_coverage"] = coverage
    g["new_excluded"] = excluded_perc
    g["excluded_time_to_ref_time"] = excluded_time_to_ref_time

# find unmatched periods of alternative (new) mobility
for new_period_idx in range(0, len(new_periods)):
    
    period = new_periods[new_period_idx]

    if period not in matched_new_mobility_periods:
        excluded_time_total_sum += period[1] - period[0]
        unmatched_periods.append({new_mobility: {"period_idx": new_period_idx, "period": period}, 
                                  "ref_coverage": 0, 
                                  "new_excluded": 1, 
                                  "new_start_to_epoch_offset": new_mobility_periods_stats["period_start_to_epoch_offsets"][new_period_idx]})

# calculate average values
ref_period_num = (len(period_groups) + len( list( filter(lambda p: ref_mobility in p.keys(), unmatched_periods))) )
new_period_num = (len(period_groups) + len( list( filter(lambda p: new_mobility in p.keys(), unmatched_periods))) )
avg_ref_coverage = ref_coverage_sum / ref_period_num if ref_period_num > 0 else 1
avg_new_excluded = new_excluded_sum / new_period_num if new_period_num > 0 else 0

# calculate total excluded new time to ref time ratio
total_excluded_time_to_ref_time_perc = excluded_time_total_sum / ref_time_total_sum if ref_time_total_sum > 0 else 0

modname = args.output_path.split("/")[-1].split("_")[1]

output = {"modname": modname,
          "period_groups": period_groups, 
          "unmatched_periods": unmatched_periods, 
          "avg_ref_coverage": avg_ref_coverage,
          "avg_new_exluded": avg_new_excluded,
          "total_excluded_time_to_ref_time": total_excluded_time_to_ref_time_perc}

with open(args.output_path, "w") as output_f:
    json.dump(output, output_f, indent=4)