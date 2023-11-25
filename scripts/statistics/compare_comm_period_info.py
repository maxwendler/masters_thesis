import argparse
import json

parser = argparse.ArgumentParser(prog="compare_comm_period_info.py", description="???")
parser.add_argument("ref_mobility_stats_path")
parser.add_argument("new_mobility_stats_path")
parser.add_argument("output_path")
args = parser.parse_args()

ref_mobility_stats = None
with open(args.ref_mobility_stats_path, "r") as stats_f:
    ref_mobility_stats = json.load(stats_f)
new_mobility_stats = None
with open(args.new_mobility_stats_path, "r") as stats_f:
    new_mobility_stats = json.load(stats_f)

ref_mobility = ref_mobility_stats["mobility"]
new_mobility = new_mobility_stats["mobility"]

# find overlapping communication periods
ref_periods = ref_mobility_stats["periods"]
new_periods = new_mobility_stats["periods"]

period_groups = []
unmatched_periods = []
matched_new_mobility_periods = []

for ref_period_idx in range(0, len(ref_periods)):
    ref_p = ref_periods[ref_period_idx]
    ref_p_start = ref_p[0]
    ref_p_end = ref_p[1]

    match_found = False
    ref_p_period_groups = []

    for new_period_idx in range(0, len(new_periods)):
        new_p = new_periods[new_period_idx]
        new_p_start = new_p[0]
        new_p_end = new_p[1]

        # match found
        if (new_p_start >= ref_p_start and new_p_start <= ref_p_end) or (new_p_end >= ref_p_start and new_p_end <= ref_p_end):
            ref_p_period_groups.append( {ref_mobility: {"period_idx": ref_period_idx, "period": ref_p}, 
                                         new_mobility: {"period_idx": new_period_idx, "period": new_p},
                                         "ref_start_to_epoch_offset": ref_mobility_stats["period_start_to_epoch_offsets"][ref_period_idx]} 
                                      )
            matched_new_mobility_periods.append(new_p)
            match_found = True
    
    if not match_found:
        
        unmatched_periods.append({ref_mobility: {"period_idx": ref_period_idx, "period": ref_p}, "ref_coverage": 0, "new_excluded": 0, "ref_start_to_epoch_offset": ref_mobility_stats["period_start_to_epoch_offsets"][ref_period_idx]})

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

for g in period_groups:
    
    ### calc coverage of ref ###
    # start second of ref period, or start second of new period if after ref start
    new_in_ref_start = max(g[ref_mobility]["period"][0], g[new_mobility]["period"][0])
    # end second of ref period, or end second of new period if before ref start
    new_in_ref_end = min(g[ref_mobility]["period"][1], g[new_mobility]["period"][1])
    coverage = (new_in_ref_end - new_in_ref_start) / (g[ref_mobility]["period"][1] - g[ref_mobility]["period"][0])

    ### calc excluded percent of new ###
    excluded_sum = 0
    if g[new_mobility]["period"][0] < g[ref_mobility]["period"][0]:
        excluded_sum += g[ref_mobility]["period"][0] - g[new_mobility]["period"][0]
    if g[new_mobility]["period"][1] > g[ref_mobility]["period"][1]:
        excluded_sum += g[new_mobility]["period"][1] - g[ref_mobility]["period"][1]
    
    excluded_perc = None
    if excluded_sum > 0:
        excluded_perc = (g[new_mobility]["period"][1] - g[new_mobility]["period"][0]) / excluded_sum
    else:
        excluded_perc = 0
    
    g["ref_coverage"] = coverage
    g["new_excluded"] = excluded_perc

for new_period_idx in range(0, len(new_periods)):
    period = new_periods[new_period_idx]
    if period not in matched_new_mobility_periods:
        unmatched_periods.append({new_mobility: {"period_idx": new_period_idx, "period": period}, 
                                  "ref_coverage": 0, 
                                  "new_excluded": 100, 
                                  "new_start_to_epoch_offset": new_mobility_stats["period_start_to_epoch_offsets"][new_period_idx]})

output = {"period_groups": period_groups, "unmatched periods": unmatched_periods}
with open(args.output_path, "w") as output_f:
    json.dump(output, output_f, indent=4)