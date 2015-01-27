
# coding: utf-8

# In[1]:

import os
import rasterio
from math import floor, ceil
import numpy as np


# In[24]:

class VirtualRaster():
    def __init__(self, shape, transformation = None, proj4_crs = None):
        self.height = shape[0]
        self.width = shape[1]
        self.transform = transformation
        self.crs = proj4_crs
        self.bands = []
    
    def read_band(self, bidx, out=None, window=None, masked=None):
        """Read the `bidx` band into an `out` array if provided, 
        otherwise return a new array.

        Band indexes begin with 1: read_band(1) returns the first band.

        The optional `window` argument is a 2 item tuple. The first item
        is a tuple containing the indexes of the rows at which the
        window starts and stops and the second is a tuple containing the
        indexes of the columns at which the window starts and stops. For
        example, ((0, 2), (0, 2)) defines a 2x2 window at the upper left
        of the raster dataset.
        """
        band = self.bands[ bidx - 1]
        if window is None:
            window = ((0,self.height),(0,self.width))
        if out is None:
            window_shape = rasterio._base.window_shape(window, self.height, self.width)
            if masked:
                out = np.ma.zeros(window_shape, band.dtype)
            else:
                out = np.zeros(window_shape, band.dtype)
        return band.read(out, window, masked)
                
    def open(self, mode = 'r', base_path = None):
        #map( lambda b: map( lambda s: s.open, b.sources ),self.bands)
        for b in self.bands:
            for s in b.sources:
                s.open()
                
    def close(self):
        #map( lambda b: map( lambda s: s.open, b.sources ),self.bands)
        for b in self.bands:
            for s in b.sources:
                s.close()

# In[25]:

class Band():
    def __init__(self, band_number, dtype, nodata = None):
        self.band_number = band_number
        self.dtype = dtype
        self.nodata = nodata
        self.sources = []
    
    def read(self, out, req_window, masked=None):
        # Consider using indexed dest_windows instead of brute force
        map(lambda src: src.read(out, req_window, masked), self.sources)
        return out
        


# In[26]:

def crop_window(window, cropper_window):
    """Returns a version of window cropped against cropper_window. 
    Also returns a tuple containing two bools: (cropped_rows, cropped_cols)"""
    (changed_rows, changed_cols) = (False, False)
    ((row_start,row_end),(col_start, col_end)) = window
    if row_start < cropper_window[0][0]:
        row_start = cropper_window[0][0]
        changed_rows = True
    if col_start < cropper_window[1][0]:
        col_start = cropper_window[1][0]
        changed_cols = True
    if row_end > cropper_window[0][1]:
        row_end = cropper_window[0][1]
        changed_rows = True
    if col_end > cropper_window[1][1]:
        col_end = cropper_window[1][1]
        changed_cols = True
    return ( (row_start,row_end),(col_start,col_end) ), (changed_rows, changed_cols)


# In[27]:

def windows_overlap(win1, win2):
        (ymin1, ymax1), (xmin1, xmax1) = win1
        (ymin2, ymax2), (xmin2, xmax2) = win2
        if ymin1 > ymax2 - 1 or ymax1 - 1 < ymin2 or xmin1 > xmax2 - 1 or xmax1 - 1 < xmin2:
            return False
        return True


# In[28]:

class Source():
    def __init__(self, path, source_band, source_window, destination_window, source_nodata = None):
        self.path = path
        self.source_band = source_band
        self.source_window = source_window
        self.source_shape = rasterio._base.window_shape(source_window)
        self.destination_window = destination_window
        self.destination_shape = rasterio._base.window_shape(destination_window)
        self.source_nodata = source_nodata
        self.dataset = None
        self._scale = tuple(float(src)/float(dest) for src,dest in zip(self.source_shape,self.destination_shape))

    def open(self, mode = 'r', base_path = None):
        if self.dataset is None:
            absolute_path = self.path if not base_path else os.path.join(base_path, self.path)
            self.dataset = rasterio.open(absolute_path)
    
    def close(self):
        if self.dataset:
            self.dataset.close()
    
    def _source_to_destination(self, source):
        """Transforms source pixel coordinates into destination pixel coordinates.
        Accepts either a coordinate tuple or a window"""
        if isinstance(source[0], (tuple, list)) :
            # This is a window, not a coord pair
            zipped = zip( *source )
            start = tuple( int(floor(c)) for c in self._source_to_destination(zipped[0]) )
            # vrtsources.cpp does not ceil() the end coord. Rather it floors it
            end =  tuple( int(floor(c)) for c in self._source_to_destination(zipped[1]) )
            return tuple(zip(start, end))

        dest_col = (source[1] - self.source_window[1][0]) / self._scale[1] + self.destination_window[1][0]
        dest_row = (source[0] - self.source_window[0][0]) / self._scale[0] + self.destination_window[0][0]
        return (dest_row, dest_col)
    
    def _destination_to_source(self, destination ):
        """Transforms destination pixel coordinates into source pixel coordinates.
        Accepts either a (row,col) tuple or a window like ((row_start,row_end),(col_start,col_end))"""
        if isinstance(destination[0], (tuple, list)) :
            # This is a window, not a coord pair
            zipped = zip( *destination )
            source_start = tuple( int(floor(c)) for c in self._destination_to_source(zipped[0]) )
            source_end =  tuple( int(ceil(c)) for c in self._destination_to_source(zipped[1]) )
            return tuple(zip(source_start, source_end))
                           
        source_col = (destination[1] - self.destination_window[1][0]) * self._scale[1] + self.source_window[1][0]
        source_row = (destination[0] - self.destination_window[0][0]) * self._scale[0] + self.source_window[0][0]
        return (source_row, source_col)
    
    def read(self, out, req_window, masked=None):
        """ req_window is the total requested window in destination coordinates. 
        Out is a numpy array."""
        
        # Logic is roughly copied from GDAL's vrtsources.cpp
        req_window_shape = rasterio._base.window_shape(req_window)
        
        # Does req_window overlap destination_window
        if not windows_overlap(self.destination_window, req_window):
            return
        
        # Crop req_window to not extent outside dest_window
        dest_req_window, req_window_changed = crop_window(req_window, self.destination_window)
        
        # Translate req_window into source pix coords
        src_req_window = self._destination_to_source( dest_req_window )
        
        # If the requested area does not overlap the source window
        if not windows_overlap(self.source_window, src_req_window):
            return
        
        # Crop source req window to be within source windowed bounds
        src_req_window, src_req_window_changed = crop_window(src_req_window, self.source_window)
        
        # Transform the source req window back into destination pixel coordinates
        dest_req_window = self._source_to_destination(src_req_window)
        
        # Where to put the data in the outarray        
        # Scale between original requested window and output buffer size
        scale_req_win_to_outarray = tuple( float(a)/b for a,b in zip(out.shape, req_window_shape) )
        
        # Calculate resulting window into outarray
        out_start_row = int((dest_req_window[1][0]-req_window[1][0])*scale_req_win_to_outarray[1]+0.001)
        out_end_row   = int((dest_req_window[1][1]-req_window[1][0])*scale_req_win_to_outarray[1]+0.001)
        out_start_col = int((dest_req_window[0][0]-req_window[0][0])*scale_req_win_to_outarray[0]+0.001)
        out_end_col   = int((dest_req_window[0][1]-req_window[0][0])*scale_req_win_to_outarray[0]+0.001)
        
        out_window = ((out_start_row, out_end_row),(out_start_col, out_end_col))
        out_window_shape = rasterio._base.window_shape(out_window)
        
        if out_window_shape[0] < 1 or out_window_shape[1] < 1:
            return
        
        # Create tmp array with source dtype and possibly masked
        if masked:
            tmp_out = np.ma.zeros(out_window_shape, self.dataset.dtypes[0]) 
        else:
            tmp_out = np.zeros(out_window_shape, self.dataset.dtypes[0])
            
        # Ok. Phew. Read
        tmp_out = self.dataset.read_band(self.source_band, out=tmp_out, window=src_req_window, masked=masked)
        
        # Put the data in out
        out[ [slice(*dim) for dim in out_window] ] = tmp_out
        return out
