# LidarHD Data Processing Tool

This Python script automates the downloading of LidarHD data from IGN based on a user-provided shapefile and optionally rasterize this data.

## Prerequisites

Before running this script, ensure you have Conda installed on your system. Also, be sure to download and unzip the LidarHD tiles in data.zip next to download_LidarHD.py

You can install the necessary Python packages using the following Conda commands:

```bash
conda create --name lidar_processing python=3.8
conda activate lidar_processing
conda install geopandas requests tqdm
conda install -c conda-forge pdal python-pdal gdal
```

## Installation

Clone this repository or download the script to your local machine:

```bash
git clone https://github.com/r-wenger/LidarHD-Download.git
```

Navigate to the script directory:

```bash
cd path/to/your/script
```

## Usage

Run the script using the following command:

```bash
python process_lidar.py -input path/to/your/shapefile.shp -output path/to/output/directory -verbose 1 -to_dtm 1 --classes 2 3 4 5 --res 0.5
```

### Command Line Arguments

- `-input`: Specifies the path to the user's shapefile.
- `-output`: Specifies the directory where the Lidar files and any generated raster files will be stored.
- `-verbose`: Enables verbose mode; 1 for detailed logs, 0 for minimal output.
- `-to_dtm`: Indicates whether to process the downloaded Lidar data into DTM/DSM; 1 for yes, 0 for no.
- `--classes`: Specifies Lidar classes to include. Use a space-separated list of class numbers, or 'ALL' for all classes.
- `--res`: Sets the resolution for the output raster files.

## Features

- Downloads LidarHD data from IGN using specified geographic boundaries from a shapefile.
- Optionally converts point cloud data to raster using PDAL.
- Flexible class filtering with support for specific classes or all classes.

## Support

For issues and questions, please contact [romain.wenger@live-cnrs.unistra.fr].
