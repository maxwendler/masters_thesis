import argparse
import csv
import plotly.express as px

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

    # distances boxplot
    satnames_list = []
    for name in satnames:
        satnames_list += [name] * len(sat_distances[0]) 
    distances_list = []
    for distance_list in sat_distances:
        distances_list += distance_list

    fig = px.box(x=satnames_list, y=distances_list, labels={'y': "difference in km"})
    fig.write_image(args.output_basepath + "boxplot.svg")
    fig.write_html(args.output_basepath + "boxplot.html")
    with open(args.output_basepath + "avg_difference.txt", "w") as avg_difference_f:
        avg_difference_f.write("avg_diff_sum: " + str(avg_distsum) + "\n" + "avg_diff: " + str(avg_dist))