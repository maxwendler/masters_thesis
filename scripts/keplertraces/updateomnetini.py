CONFIG_TEMPLATE_PATH = "./config_template.txt"

def update(ini_path: str, tles_fname: str):
    
    template_str = None    
    with open(CONFIG_TEMPLATE_PATH, "r") as template_f:
        template_str = template_f.read()
    
    tles_params = tles_fname.split("_")
    constellation = tles_params[0]
    wall_clock_start_time = tles_params[2]