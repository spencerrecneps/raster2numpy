# adapted from http://gis.stackexchange.com/questions/28583/gdal-perform-simple-least-cost-path-analysis
import gdal, osr
import numpy as np


def raster2array(raster,npType):
    '''
    Converts an input raster to a numpy array of type npType

    Inputs: raster -> input raster openable by GDAL
            npType -> Numpy data type (e.g. numpy.uint16, see https://docs.scipy.org/doc/numpy/user/basics.types.html)
    '''
    raster = gdal.Open(raster)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray().astype(npType)
    return array

def coord2pixelOffset(referenceRaster,x,y):
    '''
    Converts x-y geographic coordinates into x-y offsets for a numpy array
    based on a reference raster

    Inputs: referenceRaster -> reference raster to use for coordinate conversion
            x -> x coordinate in the CRS of the reference raster
            y -> y coordinate in the CRS of the reference raster
    '''
    raster = gdal.Open(referenceRaster)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    xOffset = int((x - originX)/pixelWidth)
    yOffset = int((y - originY)/pixelHeight)
    return xOffset,yOffset

def array2raster(outRaster,gdalType,referenceRaster,array):
    '''
    Converts a numpy array into a raster using a reference raster as a
    template

    Inputs: outRaster -> file path to save the output raster to
            gdalType -> GDAL data type (e.g. gdal.GDT_UInt16, see http://www.gdal.org/gdal_8h.html#a22e22ce0a55036a96f652765793fb7a4)
            referenceRaster -> reference raster to use for coordinate conversion
            array -> numpy array to be converted to raster
    '''
    raster = gdal.Open(referenceRaster)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRaster, cols, rows, eType=gdalType)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
