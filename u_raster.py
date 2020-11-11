'''


1 用gdal 从 3857 tiff里 得到 transform 6 个参数

仿射变换中的一些参数，分别含义见下
    transform[0]  左上角x坐标 
    transform[1]  东西方向分辨率
    transform[2]  旋转角度, 0表示图像 "北方朝上"
    transform[3]  左上角y坐标 
    transform[4]  旋转角度, 0表示图像 "北方朝上

2 构造转换函数 py版+js版。 PROJ4JS

实际需要
经纬度4326 -> 3857 -> xy


'''

from osgeo import gdal, osr
import numpy as np
import os
from pyproj import CRS, Transformer

def get_EPSG(dataset):
    proj = osr.SpatialReference(wkt=dataset.GetProjection())
    #print(proj)
    #EPSG用于geopandas中构造geometry
    return int(proj.GetAttrValue('AUTHORITY',1))

def get_shape(dataset):
    cols = dataset.RasterXSize#图像长度
    rows = dataset.RasterYSize#图像宽度
    return [cols, rows]

def load_dataset(fname):
    return gdal.Open(fname)

def make_pixeltiff_2_meter(pos0, stride):
    '''对x y都适用 stride可以为负 如UTM的y方向'''
    return lambda pixel: pos0 + stride * pixel

def make_meter_2_pixeltiff(pos0, stride):
    '''对x y都适用 stride可以为负 如UTM的y方向'''
    return lambda meter: int((meter-pos0) / stride)

def get_proj(dataset_src):
    source = osr.SpatialReference()
    source.ImportFromWkt(dataset_src.GetProjection())
    return source

def get_proj_epsg(epsg:int):
    proj_target = osr.SpatialReference()
    proj_target.ImportFromEPSG(epsg)
    return proj_target

def get_transform_by_epsg(epsg_src, epsg_dst=4326):
    #https://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
    #print(epsg_src, type(epsg_src))
    source = get_proj_epsg(epsg_src)
    target = get_proj_epsg(epsg_dst)
    # Create the transform - this can be used repeatedly
    return osr.CoordinateTransformation(source, target)

def transform_point(transform, point):
    '''有Z得去掉，但是x y方向似乎反了'''
    lat, lon, _ = transform.TransformPoint(point[0], point[1])
    return [lon, lat]


def createProj2ImageRowCol(transform):

    def lonlat2RowCol(lon, lat):
        dTemp = transform[1]*transform[5] - transform[2]*transform[4];

        dCol = (transform[5]*(lon - transform[0]) - 
            transform[2]*(lat - transform[3])) / dTemp + 0.5;
        dRow = (transform[1]*(lat - transform[3]) - 
            transform[4]*(lon - transform[0])) / dTemp + 0.5;

        return int(dCol), int(dRow)

    return latlon2RowCol

def createImageRowCol2LonLat(transform):

    def RowCol2LonLat(iRow, iCol):

        lon = transform[0] + transform[1] * iCol + transform[2] * iRow;
        lat = transform[3] + transform[4] * iCol + transform[5] * iRow;
        return lon, lat

    return RowCol2LonLat



if __name__ == '__main__':
    #原图是3857坐标系  为了充满平面直角
    fname = 'D:/xqh/4dev/zgy/data-origin/gis/谷歌卫星_200907103109.tif'
    dataset = gdal.Open(fname)

    epsg_src = get_EPSG(dataset)
    print(epsg_src)

    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    print(cols, rows)
    #d3-geo 可以
    transform_3857_4326 = get_transform_by_epsg(epsg_src, epsg_dst=4326)
    #image
    transform_para_image_3857 = dataset.GetGeoTransform()
    print(transform_para_image_3857)
    #print(transform_image_3857)
    transform_image_3857 = createImageRowCol2LonLat(transform_para_image_3857)
    transform_3857_image = createImageRowCol2LonLat(transform_para_image_3857)

    #x, y->3857
    x, y = int(rows/2), int(rows/2)
    print(x, y)
    row_col_3857 = fn_RowCol2LonLat(x, y)
    print('row_col_3857 ', row_col_3857)
    lat,lon, z = transform_3857_4326.TransformPoint(*row_col_3857)
    # 39.847557957355505 116.18968963622903
    print(lat,lon)
    # 4326->3857
    transform_4326_3857 = get_transform_by_epsg(4326, epsg_src)
    row_col_3857 = transform_4326_3857.TransformPoint(lat,lon)
    print('row_col_3857 ', row_col_3857)
    #3857 ->x y
