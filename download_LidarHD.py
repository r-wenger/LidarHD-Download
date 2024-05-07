import argparse
import geopandas as gpd
from tqdm import tqdm
import requests
import os
import subprocess
import tempfile
import json

def parse_args():
    parser = argparse.ArgumentParser(description="Download LidarHD data from IGN based on a user-provided shapefile.")
    parser.add_argument('-input', type=str, required=True, help='Path to the user shapefile.')
    parser.add_argument('-output', type=str, required=True, help='Path to the output folder.')
    parser.add_argument('-verbose', type=int, choices=[0, 1], default=1, help='Verbose mode (1 for yes, 0 for no).')
    parser.add_argument('-to_dtm', type=int, choices=[0, 1], default=0, help='Indicate if data should be rasterized to DTM (1 for yes, 0 for no).')
    parser.add_argument('--classes', type=str, nargs='*', default=[2, 3, 4, 5], help='Lidar classes to include. Use "ALL" for all classes.')
    parser.add_argument('--res', type=float, default=0.5, help='Resolution of the raster in meters (0.5m by default).')
    return parser.parse_args()


def download_lidar_data(user_shp, verbose, output_path):
    """
    Download LidarHD data from IGN based on a user-provided shapefile.

    Args:
        user_shp (str): Path to the user shapefile.
        verbose (int): Verbose mode (1 for yes, 0 for no).
        output_path (str): Path to the output folder.

    Returns:
        list: List of downloaded files.
    """
    mosaics = gpd.read_file('./data/TA_diff_pkk_lidarhd_classe.shp')
    intersection = gpd.sjoin(user_shp, mosaics, how="inner", op='intersects')

    urls = intersection['url_telech'].unique()

    output_files = []
    
    for url in tqdm(urls, desc="[INFO] Downloading files ..."):
        response = requests.get(url)
        if verbose == 1:
            print('[INFO] Downloading file from:', url)
        if response.status_code == 200:
            filename = url.split('/')[-1]
            with open(os.path.join(output_path, filename), 'wb') as f:
                f.write(response.content)
            if verbose == 1:
                print(f"[INFO] Download done for file: {filename}")
            output_files.append(filename)
        else:
            if verbose == 1:
                print(f"[INFO] Download failed for file: {url}")
                
    return output_files
                
                
def point_cloud_to_tif(input_las, output_directory, classes, resolution):
    """
    Run a PDAL pipeline to generate rasterize a point cloud according to specific classes.
    
    Args:
        input_las (str): Path to the input LAS file.
        output_directory (str): Directory to store the output DTM and DSM TIFF files.
        classes (list or str): List of integer class values to include in the raster, or 'ALL' to include all classes.
        resolution (float): The resolution for the output raster in units of the coordinate system.
    """
    
    pipeline = [
        input_las,
        {
            "type": "writers.gdal",
            "filename": os.path.join(output_directory, input_las.replace(".copc.laz", ".tif")),
            "gdaldriver": "GTiff",
            "output_type": "idw",
            "resolution": resolution,
            "data_type": "float32",
            "nodata": -9999
        }
    ]
    
    if classes != 'ALL':
        expression = " || ".join([f"Classification == {c}" for c in classes])
        pipeline.insert(1, {
            "type": "filters.expression",
            "expression": expression
        })
    
    pipeline_config = {"pipeline": pipeline}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(pipeline_config, temp_file)
        temp_file_path = temp_file.name
        
    command = ['pdal', 'pipeline', temp_file_path]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running PDAL pipeline: {e}")
    finally:
        os.remove(temp_file_path)


def main():
    args = parse_args()
    user_shp = gpd.read_file(args.input)
    
    print("[INFO] Downloading LidarHD data...")
    lidar_data = download_lidar_data(user_shp, args.verbose, args.output)
    print("[INFO] LidarHD data successfully downloaded.")
    
    if args.to_dtm:
        if 'ALL' in args.classes:
            classes = 'ALL'
        else:
            classes = args.classes
        
        for file in tqdm(lidar_data, desc="[INFO] Rasterizing data ..."):
            point_cloud_to_tif(os.path.join(args.output, file), args.output, resolution=args.res, classes=classes)
        print("[INFO] Lidar data successfully rasterized.")

if __name__ == '__main__':
    main()