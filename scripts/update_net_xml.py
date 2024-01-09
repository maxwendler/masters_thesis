import argparse

parser = argparse.ArgumentParser()
parser.add_argument("net_xml_path")
parser.add_argument("location_str")
parser.add_argument("output_path")
args = parser.parse_args()

location_str = args.location_str if args.location_str.endswith("\n") else args.location_str + "\n"

out_lines = []
with open(args.net_xml_path) as in_xml:
    org_lines = in_xml.readlines()

org_location = None
for line_idx in range(len(org_lines)):
    line = org_lines[line_idx]
    if "<location" in line:
        org_location = line
        out_lines.append(args.location_str)
        out_lines.append("\n")
    else:
        out_lines.append(line)
    
if not org_location:
    raise KeyError("No location element found!")

with open(args.output_path, "w") as out_xml:
    out_xml.writelines(out_lines)