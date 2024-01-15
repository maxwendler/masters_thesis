import argparse

parser = argparse.ArgumentParser()
parser.add_argument("nod_xml_path")
parser.add_argument("location_str")
parser.add_argument("output_path")
args = parser.parse_args()

location_str = args.location_str.replace("\\n", "\n")

out_lines = []
with open(args.nod_xml_path) as in_xml:
    org_lines = in_xml.readlines()

insert_in_next_line = False
for line_idx in range(len(org_lines)):
    line = org_lines[line_idx]
    if insert_in_next_line:
        out_lines.append(location_str)
        insert_in_next_line = False
    else:
        line = line.removesuffix("\n")
        out_lines.append(line)
    if "<nodes>" in line:
        insert_in_next_line = True

with open(args.output_path, "w") as out_xml:
    out_xml.write("\n".join(out_lines))