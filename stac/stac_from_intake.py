from stac_utils import MetadataSlowLoader, convert_timerange
import pystac
import pandas as pd

catPath = "/home/a3r/Documents/spear-flp/catalog_blue.csv"

properties = [
    "activity_id", 
    "institution_id", 
    "source_id", 
    "experiment_id",
    "frequency", 
    "realm", 
    "table_id",
    "grid_label", 
    "variable_id",
    "chunk_freq",
    "platform",
    "dimensions",
    "cell_methods",
    "standard_name"
]

def make_asset(row):

    a = pystac.Asset(
        href=row['path'],
        title="{}.{}".format(
            row["member_id"],
            row["time_range"]
        ),
        media_type="application/netcdf",
        roles=["data"]
    )

    return a

def stac_from_csv(catalog_path):
    catalog = pd.read_csv(catalog_path)
    metadata_reader = MetadataSlowLoader()
    
    for grp,df in catalog.groupby(["experiment_id","variable_id"]):
        title = grp[0] + '.' + grp[1]

        # all metadata from reading netCDF file should be same across group
        nc_metadata = metadata_reader.get(
            df.iloc[0]['path'],
            df.iloc[0].to_dict()
        )

        print(nc_metadata)

        # times = df["time_range"].apply(convert_timerange)
        # start_time = times.min[0]
        # end_time = times.max[-1]

        # item = pystac.Item(
        #     id = title,
        #     geometry = nc_metadata.footprint,
        #     bbox = nc_metadata.bbox,
        #     properties = df.iloc[0][properties].to_dict('records')[0]
        # )

        # print(df.apply(make_asset,axis=1))

        break

def main():
    stac_from_csv(catPath)

if __name__=="__main__":
    main()