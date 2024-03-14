import csv

with open("/home/s3997128/git/ma-max-wendler/examples/space_veins/csv/vectors/kunlun_starlinkShortLow-sgp4_omnet_sorted.csv", "r") as csv_f:
    dict_reader = csv.DictReader(csv_f, delimiter="\t")
    sat_num = 1
    prev_modname = ""
    for row in dict_reader:
        if row["node"] != prev_modname:
            print(sat_num, row["node"])
            prev_modname = row["node"]
            sat_num += 1