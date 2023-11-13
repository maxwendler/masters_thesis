import csv

def _parse_coords_csv(csv_path: str) -> tuple[list[tuple[float, float, float], int]]:
    coords = []
    with open(csv_path, "r") as csv_f:
        
        row_reader = csv.reader(csv_f, delimiter="\t")
        
        # find indexes of coordinate fields 
        header = row_reader.__next__()
        coord_field_idxs = []
        for field in range(0, len(header)):
            if "Coord" in header[field]:
                coord_field_idxs.append(field)
        if len(coord_field_idxs) > 3:
            raise AssertionError("No 3D coordinates - found more than three coordinate fields in this CSV.")

        start_second = None
        for row in row_reader:
            if not start_second:
                start_second = int(row[1])
            row_coords = []
            for i in coord_field_idxs:
                row_coords.append(float(row[i]))
            coords.append( tuple(row_coords) )
    
    return coords, start_second

def _parse_trace_coords(trace_path: str) -> list[tuple[float, float, float]]:
    """
    Parses file with 3d coordinates of a satellite per row to list of float tuple coordinates, 
    supporting CSV and .trace files.
    For CSVs also returns start second of simulation too (for plotting purposes). 
    """
    coords = []
    with open(trace_path, "r") as trace_f:
        name = trace_f.readline()
        coords = []
        for line in trace_f.readlines():
            line_coords = [float(c) for c in line.split(",")]
            coords.append( tuple(line_coords) )
    return coords

def parse_coords_file(path: str, format: str) -> tuple[list[tuple[float, float, float], int]]:
    if format == "csv":
        return _parse_coords_csv(path)
    elif format == "trace":
        return _parse_trace_coords(path)
    else:
        error_str = f"Format {format} is not supported, only 'csv' and 'trace'."
        raise ValueError(error_str)