import pystac
import os,sys
import xarray as xr
from netCDF4 import Dataset
import numpy as np
from datetime import datetime
from shapely.geometry import Polygon, mapping
import time

dirs = [None, None, None, None, 'experiment_id', 'member_id', 'realm', 'cell_methods', 'frequency', 'chunk_freq']
fname = ["realm", "time_range", "variable_id"]
all_columns = ["activity_id", "institution_id", "source_id", "experiment_id",
                "frequency", "realm", "table_id",
                "member_id", "grid_label", "variable_id",
                "time_range", "chunk_freq","platform","dimensions",
                "cell_methods","standard_name","path"]
props_template = {c : '' for c in all_columns}
temporal_extents = {"SPEAR_c192_o1_Scen_SSP585_IC2011_K50" : 
                    [datetime(2011,1,1), datetime(2100, 12, 31, 23)],
                    "SPEAR_c192_o1_Hist_AllForc_IC1921_K50" : 
                    [datetime(1921, 1, 1, 0), datetime(2010, 12, 31, 23)]}



class MetadataSlow():
    def __init__(self, lats, lons, long_name):
        self.lats = lats
        self.lons = lons
        self.long_name = long_name

class MetadataSlowLoader():
    def __init__(self):
        self.dict = {}

    def _get_bbox_footprint(self, variable_id):
        bottom,top = self.dict[variable_id].lats
        left,right = self.dict[variable_id].lons

        bbox = [left, bottom, right, top]
        footprint = Polygon([
            [left, bottom],
            [left, top],
            [right, top],
            [right, bottom]
        ])

        return (bbox, mapping(footprint))
    
    def get(self, path, properties):
        var_id = properties["variable_id"]
        if var_id not in self.dict:
            ds = Dataset(path, memory=None)

            if properties["realm"] == "ocean":
                top = float(np.max(ds.variables["yh"]))
                bottom = float(np.min(ds.variables["yh"]))
                left = float(np.min(ds.variables["xh"]))
                right = float(np.max(ds.variables["xh"]))
            else:
                top = float(np.max(ds.variables["lat"]))
                bottom = float(np.min(ds.variables["lat"]))
                left = float(np.min(ds.variables["lon"]))
                right = float(np.max(ds.variables["lon"]))

            long_name = ds.variables[var_id].long_name
            self.dict[var_id] = MetadataSlow([bottom,top], [left,right], long_name)
        
        bbox,fp = self._get_bbox_footprint(var_id)
        return (bbox,fp,self.dict[var_id].long_name)



def get_metadata(path_to_file, dir_meta, file_meta, properties=props_template):
    d = dict(properties)
    filename = os.path.basename(path_to_file).split('.')
    dir_structure = os.path.dirname(path_to_file).split('/')[1:]
    for (i,x) in enumerate(dir_meta):
        if x is not None:
            d[x] = dir_structure[i]
    for (i,x) in enumerate(file_meta):
        if x is not None:
            d[x] = filename[i]
    starttime, endtime = d["time_range"].split('-')
    if len(starttime) == 8:
        starttime = datetime.strptime(starttime,'%Y%m%d')
        endtime = datetime.strptime(endtime,'%Y%m%d')
    elif len(starttime) == 6:
        starttime = datetime.strptime(starttime,'%Y%m')
        endtime = datetime.strptime(endtime,'%Y%m')
    elif len(starttime) == 10:
        starttime = datetime.strptime(starttime,'%Y%m%d%H')
        endtime = datetime.strptime(endtime,'%Y%m%d%H')
    return (d, starttime, endtime)

# [-89.75, 89.75] ; [0.3125, 359.6875]
# two collections, one for Hist and one for SSP585. the temporal extent is 
# hard-coded, so need to figure out a better way to do this
def make_catalog(directory, dir_meta=dirs, f_meta=fname):
    catalog = pystac.Catalog(id="test-catalog", description="Test Catalog")
    collections = {}

    files = [os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in 
             os.walk(directory) for f in filenames]
    N_files = len(files)
    digits_files = int(np.ceil(np.log10(N_files)))

    slow_metadata = MetadataSlowLoader()

    IDs = [str(i).zfill(digits_files) for i in range(N_files)]

    for i,f in enumerate(files):
        print(f)
        metadata_d, stime, etime = get_metadata(f, dir_meta, f_meta)
        bbox, footprint, long_name = slow_metadata.get(f, metadata_d)
        metadata_d["standard_name"] = long_name

        item = pystac.Item(id=IDs[i], geometry=footprint, 
                bbox=bbox, properties=metadata_d, start_datetime=stime, 
                end_datetime=etime, datetime=None)

        asset = pystac.Asset(href=f)
        item.add_asset(key="dataset", asset=asset)

        exp_id = metadata_d["experiment_id"]
        if exp_id in collections:
            collections[exp_id].add_item(item)
        else:
            collections[exp_id] = pystac.Collection(
                id=exp_id,
                description="NA",
                extent=pystac.collection.Extent(
                    pystac.collection.SpatialExtent([bbox]),
                    pystac.collection.TemporalExtent([temporal_extents[exp_id]])
                )
            )
            collections[exp_id].add_item(item)
        
    for coll in collections.values():
        catalog.add_child(coll)

    return catalog

def main(directory):
    c = make_catalog(directory)
    c.normalize_hrefs(os.path.join(directory, "catalog"))
    c.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

if __name__ == "__main__":
    start = time.time()
    main(sys.argv[1])
    print(time.time() - start)
    