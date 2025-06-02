import intake,os,sys
import intake_esm
import pandas as pd

directory = os.path.dirname(__file__)+"/"

def search_to_subcat(output_name, catalog, variables_df):
    empty_cat = catalog.search()
    empty_cat.serialize(directory=directory, name=output_name, catalog_type="file")
    dfs = []
    for index,row in variables_df.iterrows():
        dfs.append(catalog.search(realm=row['realm'], 
                   variable_id=row['variable_id']).df)

    concat_df = pd.concat(dfs, ignore_index=True)
    concat_df.to_csv(directory+output_name+".csv", header=False, index=None, mode='a')
    return

def main():
    if len(sys.argv) < 2:
        var_df = pd.read_csv(directory+"variables.csv")
    else:
        var_df = pd.read_csv(sys.argv[1])

    cat_url = "https://raw.githubusercontent.com/aradhakrishnanGFDL/sandbox/refs/heads/spear/cats/spear/mycatalog-spear.json"
    cat = intake.open_esm_datastore(cat_url)

    search_to_subcat("spear_subcat", cat, var_df)

if __name__ == "__main__":
    main()