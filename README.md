# 3857-for-leaflet-rastercoords

leaflet-rastercoords 是自己独有的坐标系统，不是3857

但实际需要显示3857坐标时，需要先转换为raster图像所在的图像xy坐标，然后调用L.project 变成独有的坐标。用于显示

根据tiff 构造python和js两个版本的"函数"