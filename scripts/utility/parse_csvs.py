import csv

def parse_coords_csv_to_list(csv_path: str) -> tuple[list[tuple[float, float, float], int]]:
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

def get_mod_row(csv_path, modname):
    """
    Reads row of values for given satellite module name. Also return used range of simulation seconds.
    """
    with open(csv_path, "r") as csv_f:
        
        row_reader = csv.reader(csv_f)
        
        header = row_reader.__next__()
        second_range = None
        
        start_second = int(header[1])
        end_second = int(header[-1])
        second_range = list(range(start_second, end_second + 1))

        vals = None
        for row in row_reader:
            if row[0] == modname:
                vals = [ float(v) for v in row[1:] ]
                break
        
        if not vals:
            raise NameError(f"No values for satellite module {modname} could be found!")
        
        return vals, second_range