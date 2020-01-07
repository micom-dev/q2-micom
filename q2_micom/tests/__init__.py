import os.path as path

this_dir, _ = path.split(__file__)


def check_viz(folder):
    return path.isfile(path.join(folder, "index.html"))
