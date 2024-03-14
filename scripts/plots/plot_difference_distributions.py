import argparse
import csv
import plotly.express as px
import json

def parse_difference_csv(csv_path):
    with open(csv_path, "r") as csv_f:
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()

        satnames = []
        sat_distances = []

        for row in row_reader:
            # filter dimensional distances
            if not "_vector" in row[0]:
                satnames.append(row[0])
                distances = [ float(d) for d in row[1:] ]
                sat_distances.append(distances)
                
    return satnames, sat_distances

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="plot_difference_distributions", description="Plots sum histrogram of coordinate differences & difference box plot of each satellite.")
    parser.add_argument("difference_csv_path", help="Path of the csv of coordinate differences per satellite.")
    parser.add_argument("output_basepath", help="Directory where both plots will be saved.")
    args = parser.parse_args()

    difference_csv_path = args.difference_csv_path
    satnames, sat_distances = parse_difference_csv(difference_csv_path)

    sat_distsums = [sum(distances) for distances in sat_distances]
    avg_distsum = sum(sat_distsums) / len(sat_distsums)
    avg_dist = avg_distsum / len(sat_distances[0])

    # sum of distances histogram with horizontal line for avg distsum
    # subtitle: avg. dist
    fig = px.bar(x=satnames, y=sat_distsums, labels={'x': f'Average difference: {round(avg_dist, 6)} km', 'y': "difference sum in km"})
    fig.add_hline(y=avg_distsum, annotation={"text": "avg sum"})

    fig.write_image(args.output_basepath + "sum-histogram.svg")
    fig.write_html(args.output_basepath + "sum-histogram.html")
    
    out_dict = {}
    out_dict["avg_diff_sum"] = avg_distsum
    out_dict["avg_diff"] = avg_dist
    out_dict["sats"] = {}
    for i in range(len(satnames)):
        out_dict["sats"][satnames[i]] = {
            "diff_sum": sat_distsums[i],
            "avg_diff": sat_distsums[i] / len(sat_distances[0])
        }

    with open(args.output_basepath + "avg_difference.json", "w") as avg_difference_f:
        json.dump(out_dict, avg_difference_f, indent=4)