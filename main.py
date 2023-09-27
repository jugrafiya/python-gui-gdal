import tkinter as tk
from tkinter import filedialog,messagebox  
import csv
from tkinter import ttk
from osgeo import ogr, osr, gdal, gdalconst
import numpy as np
import pandas as pd
import os


sensors_csv_file = ""
chemical_csv_file = ""
columns_to_check= ["232-Th", "238-U", "40-K", "137-Cs", "Countrate"]


def open_sensor_file():
    global sensors_csv_file 
    sensors_csv_file= filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if sensors_csv_file:
        text_box.insert("end", "reading file: " + sensors_csv_file+ "\n")

def open_chemical_file():
    global chemical_csv_file
    chemical_csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if chemical_csv_file:
        text_box.insert("end", "reading file: " + chemical_csv_file+ "\n")


def create_shapefiles(output_path):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    
    # Spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # WGS84

    dataset = pd.read_csv(sensors_csv_file)
    for col in columns_to_check:
        shp_filename = output_path + "/" + col + ".shp"
        text_box.insert("end", "Creating Shapefile: " + shp_filename + "\n")
        if os.path.exists(shp_filename):
            driver.DeleteDataSource(shp_filename)
        ds = driver.CreateDataSource(shp_filename)
        layer = ds.CreateLayer(col, srs, ogr.wkbPoint)
        layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("value", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("lat", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("lon", ogr.OFTReal))

        for index, row in dataset.iterrows():
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("id", index)
            feature.SetField("value", row[col])
            feature.SetField("lat", row["lat"])
            feature.SetField("lon", row["lon"])
            wkt = "POINT(%f %f)" % (float(row["lon"]), float(row["lat"]))
            point = ogr.CreateGeometryFromWkt(wkt)
            feature.SetGeometry(point)
            layer.CreateFeature(feature)
            feature.Destroy()
        ds.Destroy()

    # Create rasters
    rasters_path = output_path.replace("shapefiles", "rasters")
    if not os.path.exists(rasters_path):
        os.makedirs(rasters_path)
    create_rasters(rasters_path)

def create_rasters(output_path):

    # Create rasters using inverse distance weighting grid
    power = 3
    smoothing = 0.0006
    radius= 1500
    angle: 0
    max_points = 0
    min_points = 0
    nodata = 0
    output_type = gdalconst.GDT_Float32
    for col in columns_to_check:
        src_shp = output_path.replace("rasters", "shapefiles") + "/" + col + ".shp"

        # get shp bounds
        ds = ogr.Open(src_shp)
        layer = ds.GetLayer()
        extent = layer.GetExtent()
        ds.Destroy()


        raster_filename = output_path + "/" + col + ".tif"
        text_box.insert("end", "using "+ "invdist:power={}smoothing={}:radius1={}:radius2={}:angle={}:max_points={}:min_points={}:nodata={}".format(power_entry.get(), smoothing_entry.get(), radius_entry.get(), radius_entry.get(), angle_entry.get(), max_points_entry.get(), min_points_entry.get(), nodata_entry.get()) + "\n")
        if os.path.exists(raster_filename):
            driver.DeleteDataSource(raster_filename)
        text_box.insert("end", "using: " + raster_filename + "\n")
        gdal.Grid(raster_filename, src_shp, zfield='value', format="GTiff", outputType=output_type, outputSRS="EPSG:4326", noData=nodata, algorithm= "invdist:power={}smoothing={}:radius1={}:radius2={}:angle={}:max_points={}:min_points={}:nodata={}".format(power_entry.get(), smoothing_entry.get(), radius_entry.get(), radius_entry.get(), angle_entry.get(), max_points_entry.get(), min_points_entry.get(), nodata_entry.get()))

    # for all rasters, get the pixel value for each point in the chemical csv file and save it in a new csv file
    dataset = pd.read_csv(chemical_csv_file)
    for col in columns_to_check:
        raster_filename = output_path + "/" + col + ".tif"
        dataset[col] = dataset.apply(lambda row: get_pixel_value(row["Longitude"], row["Latitude"], get_geo_transform(raster_filename), get_raster_data(raster_filename)), axis=1)
    
    csv_path = output_path.replace("rasters", "results")
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    
    dataset.to_csv(csv_path + "/results.csv", index=False)

def get_raster_data(raster_filename):
    raster = gdal.Open(raster_filename)
    band = raster.GetRasterBand(1)
    return band.ReadAsArray()

def get_geo_transform(raster_filename):
    raster = gdal.Open(raster_filename)
    return raster.GetGeoTransform()

def get_pixel_value(x, y, geotransform, raster_data):
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = -geotransform[5]

    pixel_x = int((x - origin_x) / pixel_width)
    pixel_y = int((y - origin_y) / pixel_height)

    return raster_data[pixel_y, pixel_x]

def save_file():
    #Open file dialog to ask for folder
    folder_path = filedialog.askdirectory()
    if folder_path:
        shapefile_path = folder_path + "/shapefiles"

        if not os.path.exists(shapefile_path):
            os.makedirs(shapefile_path)
        
        # Create shapefiles
        create_shapefiles(shapefile_path)

        text_box.insert("end", "Process Finished \n")
        

# Create the main application window
root = tk.Tk()
root.geometry("350x900")
root.title("CSV File Reader")


label = tk.Label(root, text="CSV File Reader", font=("Arial", 16))
label.pack(pady=10)

upload_button = tk.Button(root, text="Upload Sensors data CSV", command=open_sensor_file)
upload_button.pack(pady=5, anchor=tk.W, padx=5)
 
upload_button2 = tk.Button(root, text="Upload Chemical CSV", command=open_chemical_file)
upload_button2.pack(pady=5, anchor=tk.W, padx=5)

# Parameters
label2 = tk.Label(root, text="Parameters", font=("Arial", 14))
label2.pack(pady=10)

#power = 3
label_power = tk.Label(root, text="Power", font=("Arial", 12))
label_power.pack(pady=5, anchor=tk.W, padx=5)
power_entry = tk.Entry(root)
power_entry.pack(pady=5, anchor=tk.W, padx=5)
power_entry.insert(0, "3")
power_entry.pack(anchor=tk.W, padx=5, pady=5)

#smoothing = 0.0006
label_smoothing = tk.Label(root, text="Smoothing", font=("Arial", 12))
label_smoothing.pack(anchor=tk.W, padx=5, pady=5)
smoothing_entry = tk.Entry(root)
smoothing_entry.pack(anchor=tk.W, padx=5, pady=5)
smoothing_entry.insert(0, "0.0006")

#radius= 1500
label_radius = tk.Label(root, text="Radius", font=("Arial", 12))
label_radius.pack(pady=5, padx=5, anchor=tk.W)
radius_entry = tk.Entry(root)
radius_entry.pack(pady=5, padx=5, anchor=tk.W)
radius_entry.insert(0, "1500")

#angle: 0
label_angle = tk.Label(root, text="Angle", font=("Arial", 12))
label_angle.pack(pady=5, padx=5, anchor=tk.W)
angle_entry = tk.Entry(root)
angle_entry.pack(pady=5, padx=5, anchor=tk.W)
angle_entry.insert(0, "0")

#max_points = 0
label_max = tk.Label(root, text="Max Points", font=("Arial", 12))
label_max.pack(pady=5, padx=5, anchor=tk.W)
max_points_entry = tk.Entry(root)
max_points_entry.pack(pady=5, padx=5, anchor=tk.W)
max_points_entry.insert(0, "0")

#min_points = 0
label_min = tk.Label(root, text="Min Points", font=("Arial", 12))
label_min.pack(pady=5, padx=5, anchor=tk.W)
min_points_entry = tk.Entry(root)
min_points_entry.pack(pady=5, padx=5, anchor=tk.W)
min_points_entry.insert(0, "0")

#nodata = 0
label_nodata = tk.Label(root, text="No Data", font=("Arial", 12))
label_nodata.pack(pady=5, padx=5, anchor=tk.W)
nodata_entry = tk.Entry(root)
nodata_entry.pack(pady=5, padx=5, anchor=tk.W)
nodata_entry.insert(0, "0")

 
upload_button3 = tk.Button(root, text="Save CSV", command=save_file)
upload_button3.pack(pady=5)

## Text box for logs
lable_logs = tk.Label(root, text="Logs", font=("Arial", 14))
lable_logs.pack(pady=5, anchor=tk.W, padx=5)
text_box = tk.Text(root, height=10, width=30)
text_box.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
