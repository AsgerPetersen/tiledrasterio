import rasterio
import os
from tiledrasterio._vrt import parse_vrt

class TiledRaster():
    def __init__(self,vrtfile):
        self.vrt = parse_vrt(vrtfile)
        self.vrtfile = self.vrt['filename']
        self.shape =  tuple(self.vrt['shape'])
        self.basepath = self.vrt['rootpath']
        
    def tiles(self, bandnumber = 1):
        for t in self.vrt['bands'][bandnumber - 1]['sources']:
            yield t
    
    def get_tile_file(self, tile):
        src = tile['sourcefile'] 
        filename = src['filename']
        if src['relative']:
            filename = os.path.join(self.basepath, filename)
        return filename
    
    def read_tile_buffered(self, tile, bufferpixels, masked=None):
        """Returns ( numpyarray, tiledata_window)
        tiledatawindow is a window indicating which part of the numpy array stems from the tile"""
        bufferinfo = self._adjust_buffer(tile, bufferpixels)
        win = self._expand_window(tile, bufferinfo)
        tile_data_window = self._unbuffered_window(win, bufferinfo)
        with rasterio.open(self.vrtfile, mode='r') as f:
            data = f.read_band(1, window=win, masked=masked)
        return data, tile_data_window
        
    def _adjust_buffer(self, tile, bufferpixels):
        """Adjust left/top/right/bottom buffer to stay within vrt bounds"""
        left = top = right = bottom = bufferpixels
        dstwin = tile['dstwin']
        if dstwin[1][0] - bufferpixels < 0:
            left = dstwin[1][0]
        if dstwin[0][0] - bufferpixels < 0:
            top = dstwin[0][0]
        if dstwin[1][1] + bufferpixels > self.shape[1]:
            right = self.shape[1] - dstwin[1][1]
        if dstwin[0][1] + bufferpixels > self.shape[0]:
            bottom = self.shape[0] - dstwin[0][1]
        return (left, top, right, bottom)
    
    def _expand_window(self, tile, bufferinfo):
        """Expands a window by bufferinfo"""
        window = tile['dstwin']
        rows = ( window[0][0] - bufferinfo[1], window[0][1] + bufferinfo[3] )
        cols = ( window[1][0] - bufferinfo[0], window[1][1] + bufferinfo[2] )
        return (rows, cols)
    
    def _unbuffered_window(self, window, bufferinfo):
        """ Takes a buffered window and bufferinfo and calculates indices for the unbuffered data"""
        winshape = [ end - start for start, end in window ]
        return ((bufferinfo[1], winshape[0] - bufferinfo[3]),(bufferinfo[0], winshape[1] - bufferinfo[2]))