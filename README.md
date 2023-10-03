Certainly, below is the `README.md` file that includes both the code explanation and instructions for installing required dependencies.

---

# CSV File Reader to Shapefile and Rasters

This python application takes the first csv (sensors) and creates shapefiles and rasters through interpolation.It then uses the second csv (chemicals) and correlates their points with the rasters and calculates the values for each raster pixel at those points.
The application has a GUI interface built with Tkinter.

## Features

- Read CSV files through a GUI.
- Generate shapefiles based on sensor data.
- Generate raster files from shapefiles.
- Save output files to a user-defined directory.
  
## Prerequisites

Make sure you have installed the following Python packages. You can install them using `pip`:

```bash
pip install pandas numpy gdal
```

## How to Run

1. Clone the repository.
2. Navigate to the folder containing the script.
3. Run the Python script.

```bash
python main.py
```

### GUI

- **Upload Sensors data CSV**: Allows the user to upload a CSV file containing sensor data.
- **Upload Chemical CSV**: Allows the user to upload a CSV file containing chemical data.
- **Parameters**: Allows the user to set various parameters like Power, Smoothing, etc.
- **Save CSV**: Initiates the shapefile and raster file creation and saving process.
- **Logs**: Displays logs of the ongoing processes.

## Function Descriptions

- `open_sensor_file()`: Opens file dialog and allows the user to select a sensor data CSV file.
- `open_chemical_file()`: Opens file dialog and allows the user to select a chemical data CSV file.
- `create_shapefiles(output_path)`: Creates shapefiles based on the sensor data.
- `create_rasters(output_path)`: Creates raster files based on the generated shapefiles.
- `get_raster_data(raster_filename)`: Gets the raster data from a raster file.
- `get_geo_transform(raster_filename)`: Gets the geotransform information from a raster file.
- `get_pixel_value(x, y, geotransform, raster_data)`: Gets the pixel value from a raster file based on x, y coordinates.
- `save_file()`: Saves the generated files to a user-defined directory.

## Built With

- [Tkinter](https://docs.python.org/3/library/tkinter.html) - For the GUI.
- [GDAL](https://gdal.org/) - For creating shapefiles and rasters.
- [Pandas](https://pandas.pydata.org/) - For data manipulation.
- [NumPy](https://numpy.org/) - For numerical operations.
