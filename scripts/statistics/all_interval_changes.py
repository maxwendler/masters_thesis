import argparse
import json
import csv
import os

parser = argparse.ArgumentParser()
parser.add_argument("ref_periods_csv")
parser.add_argument("ref_periods_jsons_dir")
parser.add_argument("new_periods_csv")
parser.add_argument("new_periods_jsons_dir")
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("output_path")

args = parser.parse_args()

ref_periods_jsons_dir = args.ref_periods_jsons_dir if args.ref_periods_jsons_dir.endswith("/") else args.ref_periods_jsons_dir + "/"
new_periods_jsons_dir = args.new_periods_jsons_dir if args.new_periods_jsons_dir.endswith("/") else args.new_periods_jsons_dir + "/"

# read ref period sequence
ref_period_seq = []
with open(args.ref_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    period_sequence_num = 0
    for row in row_reader:
        ref_period_seq.append( f"{row[0]}{str(period_sequence_num)}" ) 
        period_sequence_num += 1

# read period properties
ref_periods_properties = {}
for period_json_fname in filter(lambda fname: fname.endswith("communication-periods.json"), os.listdir(ref_periods_jsons_dir)):

    with open(ref_periods_jsons_dir + period_json_fname, "r") as json_f:
        comm_periods = json.load(json_f)
    
    modname = comm_periods['modname']
    modname_seq_period_names = list(filter(lambda pname: pname.startswith(modname), ref_period_seq))

    for period_idx in range(len(modname_seq_period_names)):
        modname_seq_pname = modname_seq_period_names[period_idx]
        ref_periods_properties[modname_seq_pname] = {
            "period": comm_periods["periods"][period_idx],
            "epoch_offset": comm_periods["period_start_to_epoch_offsets"][period_idx],
            "zenith": comm_periods["zenith_times"][period_idx]
        }

ref_periods_properties["end"] = {
    "period": [args.sim_time_limit, args.sim_time_limit],
    "zenith": args.sim_time_limit,
    "epoch_offset": 0
}

# create mapping for each period: the following periods with which it overlaps and the one after that, i.e.
# for which there is a time interval inbetween
ref_period_relations = {}
for seq_pidx in range(len(ref_period_seq)):
    
    seq_pname = ref_period_seq[seq_pidx]
    seq_period = ref_periods_properties[seq_pname]["period"]

    if seq_pidx == len(ref_period_seq) - 1:
        ref_period_relations[seq_pname] = {
            "overlap_periods": [],
            "next_nonoverlap_period": "end"     
        }
    
    else:
        overlap_periods = []
        next_nonoverlap_period = None
        # iterate until period that does not overlap is found (or no periods left)
        for seq_p_subidx in range(seq_pidx + 1, len(ref_period_seq)):
            
            comparison_seq_pname = ref_period_seq[seq_p_subidx]
            comparison_period = ref_periods_properties[comparison_seq_pname]["period"]

            # period end lies in current seq_period -> overlap -> continue iteration
            # only may occur
            if comparison_period[0] <= seq_period[1]:
                overlap_periods.append(comparison_seq_pname)
            # always occurs with exception that only overlapping periods remain, and then end of simulation
            # in this case, remains None and "end" will be saved as related period
            else:
                next_nonoverlap_period = comparison_seq_pname
                break

        ref_period_relations[seq_pname] = {
            "overlap_periods": overlap_periods,
            "next_nonoverlap_period": next_nonoverlap_period if next_nonoverlap_period else "end"
        }

# read new period sequence
new_period_seq = []
with open(args.new_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    period_sequence_num = 0
    for row in row_reader:
        new_period_seq.append( f"{row[0]}{str(period_sequence_num)}" ) 
        period_sequence_num += 1

# read period properties
new_periods_properties = {}
for period_json_fname in filter(lambda fname: fname.endswith("communication-periods.json"), os.listdir(new_periods_jsons_dir)):

    with open(new_periods_jsons_dir + period_json_fname, "r") as json_f:
        comm_periods = json.load(json_f)
    
    modname = comm_periods['modname']
    modname_seq_period_names = list(filter(lambda pname: pname.startswith(modname), new_period_seq))

    for period_idx in range(len(modname_seq_period_names)):
        modname_seq_pname = modname_seq_period_names[period_idx]
        new_periods_properties[modname_seq_pname] = {
            "period": comm_periods["periods"][period_idx],
            "epoch_offset": comm_periods["period_start_to_epoch_offsets"][period_idx],
            "zenith": comm_periods["zenith_times"][period_idx]
        }

new_periods_properties["end"] = {
    "period": [args.sim_time_limit, args.sim_time_limit],
    "zenith": args.sim_time_limit,
    "epoch_offset": 0
}

# create mapping of reference period with sequence number to new period with sequence number
# and save lost / added periods
consecutive_lost_periods = []
current_consecutive_lost_periods = []
consecutive_added_periods = []
refp_newp_mapping = {}
new_seq_pidx = 0
for ref_seq_pidx in range(len(ref_period_seq)):

    new_seq_num_offset = new_seq_pidx - ref_seq_pidx

    ref_pname = ref_period_seq[ref_seq_pidx]

    # lost periods at end of ref list
    if new_seq_pidx > len(new_period_seq) - 1:
        current_consecutive_lost_periods.append(ref_pname)
        # save on last ref period
        if ref_seq_pidx == len(ref_period_seq) - 1:
            consecutive_lost_periods.append(current_consecutive_lost_periods)
        continue

    new_pname = new_period_seq[new_seq_pidx]
    new_pname_adapted_seqnum = new_pname.split("]")[0] + "]" + str( int(new_pname.split("]")[1]) - new_seq_num_offset) 

    # match, no issue with lost or added periods
    if ref_pname == new_pname_adapted_seqnum:
        
        refp_newp_mapping[ref_pname] = new_pname

        if len(current_consecutive_lost_periods) > 0:
            consecutive_lost_periods.append(current_consecutive_lost_periods)
            current_consecutive_lost_periods = []

        new_seq_pidx += 1

    else:
        # periods might be added, ref_pname might occur later with other sequence number
        potentially_added_periods = [new_pname]
        added_periods_num = 0
        related_new_pname = None

        for new_p_search_idx in range(new_seq_pidx + 1, len(new_period_seq)):
            new_period_search_name = new_period_seq[new_p_search_idx]

            new_period_search_name_adapted_seqnum = None
            if ref_seq_pidx == 0:
                new_period_search_name_adapted_seqnum = new_period_search_name.split("]")[0] + "]" + str( int(new_period_search_name.split("]")[1]) - (new_p_search_idx - new_seq_pidx) - new_seq_num_offset)
            else:
                new_period_search_name_adapted_seqnum = new_period_search_name.split("]")[0] + "]" + str(new_p_search_idx - 1 - new_seq_num_offset)

            if ref_pname == new_period_search_name_adapted_seqnum:
                added_periods_num = new_p_search_idx - new_seq_pidx
                related_new_pname = new_period_search_name
                break
            else:
                potentially_added_periods.append(new_period_search_name)
        
        # added periods confirmed
        if added_periods_num > 0:
            
            if len(current_consecutive_lost_periods) > 0:
                consecutive_lost_periods.append(current_consecutive_lost_periods)
                current_consecutive_lost_periods = []

            consecutive_added_periods.append(potentially_added_periods)
            new_seq_pidx += added_periods_num + 1
            refp_newp_mapping[ref_pname] = related_new_pname
        
        # added periods not confired -> ref period is a lost period
        else:
            current_consecutive_lost_periods.append(ref_pname) 

# added period at end of new list
if new_seq_pidx < len(new_period_seq):
    current_consecutive_added_periods = []
    for i in range(new_seq_pidx, len(new_period_seq)):
        current_consecutive_added_periods.append(new_period_seq[i])
    consecutive_added_periods.append(current_consecutive_added_periods)


refp_newp_mapping["end"] = "end"

# map relations to periods of new mobilitiy and potentially modifiy them:
# if period is lost, don't evaluate its relations
# if overlap_period was lost, have no such relation
# if next_nonoverlap_period was lost, have the next period as new next_nonoverlap_period in both ref_period_relations and new_period_relations
# if new overlap_period appeared, ignore this relation
# if new period appeared that is actual next_nonoverlap_period, skip it as no comparison is possible
new_period_relations = {}
ref_pnames_to_remove_from_relations = []
for ref_pname in ref_period_relations.keys():
    
    current_ref_p_relations = ref_period_relations[ref_pname]

    new_pname = refp_newp_mapping[ref_pname] if ref_pname in refp_newp_mapping.keys() else None
    # skip period and remove reference relations if lost
    if not new_pname:
        ref_pnames_to_remove_from_relations.append(ref_pname)
        continue
    
    # collect periods that are overlap in sgp4 and exist in kepler,
    # if not existing, remove from sgp4 overlap periods
    new_overlap_periods = []
    overlap_periods_to_remove = []
    for overlap_period in current_ref_p_relations["overlap_periods"]:
        new_overlap_period = refp_newp_mapping[overlap_period] if overlap_period in refp_newp_mapping.keys() else None
        if new_overlap_period:
            new_overlap_periods.append(new_overlap_period)
        else:
            overlap_periods_to_remove.append(overlap_period)
    for overlap_period in overlap_periods_to_remove:
        ref_period_relations[ref_pname]["overlap_periods"].pop(ref_period_relations[ref_pname]["overlap_periods"].index(overlap_period))
    
    newp_next_nonoverlap = None
    refp_next_nonoverlap = current_ref_p_relations["next_nonoverlap_period"]
    was_lost = refp_next_nonoverlap not in refp_newp_mapping.keys()
    if was_lost:
        while was_lost:
            new_refp_next_nonoverlap_idx = ref_period_seq.index(refp_next_nonoverlap) + 1
            new_refp_next_nonoverlap = ref_period_seq[new_refp_next_nonoverlap_idx] if new_refp_next_nonoverlap_idx < len(ref_period_seq) else "end"
            was_lost = new_refp_next_nonoverlap not in refp_newp_mapping.keys()
            if not was_lost:
                refp_next_nonoverlap = new_refp_next_nonoverlap
        ref_period_relations[ref_pname]["next_nonoverlap_period"] = refp_next_nonoverlap
    newp_next_nonoverlap = refp_newp_mapping[refp_next_nonoverlap]

    new_period_relations[new_pname] = {
        "overlap_periods": new_overlap_periods,
        "next_nonoverlap_period": newp_next_nonoverlap
    }

for ref_pname in ref_pnames_to_remove_from_relations:
    ref_period_relations.pop(ref_pname)

same_periods_changes = {}
for ref_pname in ref_period_relations.keys():
    
    current_ref_p_relations = ref_period_relations[ref_pname]
    current_ref_p_props = ref_periods_properties[ref_pname]

    new_pname = refp_newp_mapping[ref_pname]
    current_new_p_relations = new_period_relations[new_pname]
    current_new_p_props = new_periods_properties[new_pname]

    # compare overlap periods
    overlap_changes = []
    for overlap_p_idx in range(len(current_ref_p_relations["overlap_periods"])):
        
        ref_overlap_pname = current_ref_p_relations["overlap_periods"][overlap_p_idx]
        ref_overlap_p_props = ref_periods_properties[ref_overlap_pname]
        
        refp_end_to_overlap_p_start_interval = ref_overlap_p_props["period"][0] - current_ref_p_props["period"][1]
        ref_overlap_time = abs(refp_end_to_overlap_p_start_interval) + 1 if refp_end_to_overlap_p_start_interval <= 0 else 0
        refp_to_overlap_zenith_interval = ref_overlap_p_props["zenith"] - current_ref_p_props["zenith"]

        new_overlap_pname = current_new_p_relations["overlap_periods"][overlap_p_idx]
        new_overlap_p_props = new_periods_properties[new_overlap_pname]
        
        newp_end_to_overlap_p_start_interval = new_overlap_p_props["period"][0] - current_new_p_props["period"][1]
        new_overlap_time = abs(newp_end_to_overlap_p_start_interval) + 1 if newp_end_to_overlap_p_start_interval <= 0 else 0
        new_time_distance = newp_end_to_overlap_p_start_interval if newp_end_to_overlap_p_start_interval > 0 else 0
        newp_to_overlap_zenith_interval = new_overlap_p_props["zenith"] - current_new_p_props["zenith"]

        overlap_changes.append({
            "name": f"{ref_pname}-{ref_overlap_pname}",
            "original_end_to_start_interval": refp_end_to_overlap_p_start_interval,
            "new_end_to_start_interval": newp_end_to_overlap_p_start_interval,
            "end_to_start_interval_difference": newp_end_to_overlap_p_start_interval - refp_end_to_overlap_p_start_interval,
            "overlap_time_difference": new_overlap_time - ref_overlap_time,
            "new_time_distance": new_time_distance,
            "zenith_interval_difference": newp_to_overlap_zenith_interval - refp_to_overlap_zenith_interval,
            "start_offset_to_epoch": ref_periods_properties[ref_pname]["epoch_offset"],
            "end_offset_to_epoch": ref_periods_properties[ref_overlap_pname]["epoch_offset"],
            "abs_offset_difference": abs(abs(ref_periods_properties[ref_pname]["epoch_offset"]) - abs(ref_periods_properties[ref_overlap_pname]["epoch_offset"]))
        })

    ref_next_nonoverlap_pname = current_ref_p_relations["next_nonoverlap_period"]
    ref_next_nonoverlap_p_props = ref_periods_properties[ref_next_nonoverlap_pname]
    refp_end_to_nonoverlap_p_start_interval = ref_next_nonoverlap_p_props["period"][0] - current_ref_p_props["period"][1]
    refp_to_nonoverlap_zenith_interval = ref_next_nonoverlap_p_props["zenith"] - current_ref_p_props["zenith"]

    new_next_nonoverlap_pname = current_new_p_relations["next_nonoverlap_period"]
    new_next_nonoverlap_p_props = new_periods_properties[new_next_nonoverlap_pname]
    newp_end_to_nonoverlap_p_start_interval = new_next_nonoverlap_p_props["period"][0] - current_new_p_props["period"][1]
    newp_to_nonoverlap_zenith_interval = new_next_nonoverlap_p_props["zenith"] - current_new_p_props["zenith"]

    new_overlap_time = abs(newp_end_to_nonoverlap_p_start_interval) + 1 if newp_end_to_nonoverlap_p_start_interval <= 0 else 0
    new_time_distance = newp_end_to_nonoverlap_p_start_interval if newp_end_to_nonoverlap_p_start_interval > 0 else 0

    next_nonoverlap_changes = {
        "name": f"{ref_pname}-{ref_next_nonoverlap_pname}",
        "original_end_to_start_interval": refp_end_to_nonoverlap_p_start_interval,
        "new_end_to_start_interval": newp_end_to_nonoverlap_p_start_interval,
        "end_to_start_interval_difference": newp_end_to_nonoverlap_p_start_interval - refp_end_to_nonoverlap_p_start_interval,
        "new_overlap_time": new_overlap_time,
        "new_time_distance": new_time_distance,
        "zenith_interval_difference": newp_to_nonoverlap_zenith_interval - refp_to_nonoverlap_zenith_interval,
        "start_offset_to_epoch": ref_periods_properties[ref_pname]["epoch_offset"],
        "end_offset_to_epoch": ref_periods_properties[ref_next_nonoverlap_pname]["epoch_offset"],
        "abs_offset_difference": abs(abs(ref_periods_properties[ref_pname]["epoch_offset"]) - abs(ref_periods_properties[ref_next_nonoverlap_pname]["epoch_offset"]))
    }

    same_periods_changes[ref_pname] = {
        "overlap_changes": overlap_changes,
        "next_nonoverlap_changes": next_nonoverlap_changes
    }

# save lost and added periods with their period indeces for the respective satellite
consecutive_lost_periods_out = []
for current_consecutive_lost_periods in consecutive_lost_periods:    
    current_consecutive_lost_periods_out = []
    for pname in current_consecutive_lost_periods:
        pname_without_seq_num = pname.split("]")[0] + "]"
        pidx = -1
        for ref_pname in ref_period_seq:
            if pname_without_seq_num in ref_pname:
                pidx += 1
            if pname == ref_pname:
                break
        current_consecutive_lost_periods_out.append({
            "period_name": pname,
            "sat_period_idx": pidx
        })
    consecutive_lost_periods_out.append(current_consecutive_lost_periods_out)

consecutive_added_periods_out = []
for current_consecutive_added_periods in consecutive_added_periods:    
    current_consecutive_added_periods_out = []
    for pname in current_consecutive_added_periods:
        pname_without_seq_num = pname.split("]")[0] + "]"
        pidx = -1
        for new_pname in new_period_seq:
            if pname_without_seq_num in new_pname:
                pidx += 1
            if pname == new_pname:
                break
        current_consecutive_added_periods_out.append({
            "period_name": pname,
            "sat_period_idx": pidx
        })
    consecutive_added_periods_out.append(current_consecutive_added_periods_out)

output = {
    "same_periods_changes": same_periods_changes,
    "consecutive_lost_periods": consecutive_lost_periods_out,
    "consecutive_added_periods": consecutive_added_periods_out
}

with open(args.output_path, "w") as out_json:
    json.dump(output, out_json, indent=4)