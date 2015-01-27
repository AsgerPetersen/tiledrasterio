from tiledrasterio._virtualraster import Band, VirtualRaster, Source
import numpy as np

def create_virtual_raster():
    src_path = "tests/data/dummy.asc"
    source_band = 1
    source_window = ( (1,4),(1,4) )
    destination_window = ( (3,6),(3,6) )
    band = Band(1,'int64')
    for r, c in np.ndindex((3,3)):
        src_win = ((0,3),(0,3))
        dst_win = ((r*3,r*3+3),(c*3,c*3+3))
        band.sources.append(Source(src_path, source_band, src_win, dst_win, source_nodata = None))
    dataset = VirtualRaster((9,9))
    dataset.bands.append(band)
    return dataset
    
def test_has_legs():
    assert not tiledrasterio.has_legs

def test_read_full():
    expected = np.array(
        [[-9999, -9999,     5, -9999, -9999,     5, -9999, -9999,     5],
         [-9999,    20,   100, -9999,    20,   100, -9999,    20,   100],
         [    3,     8,    35,     3,     8,    35,     3,     8,    35],
         [-9999, -9999,     5, -9999, -9999,     5, -9999, -9999,     5],
         [-9999,    20,   100, -9999,    20,   100, -9999,    20,   100],
         [    3,     8,    35,     3,     8,    35,     3,     8,    35],
         [-9999, -9999,     5, -9999, -9999,     5, -9999, -9999,     5],
         [-9999,    20,   100, -9999,    20,   100, -9999,    20,   100],
         [    3,     8,    35,     3,     8,    35,     3,     8,    35]])
    ds = create_virtual_raster()
    ds.open()
    actual = ds.read_band(1, masked=True)
    
    assert np.all(expected == actual)
    
