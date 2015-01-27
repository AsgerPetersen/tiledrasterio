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
    actual = ds.read_band(1)
    ds.close()
    assert np.all(expected == actual)

def test_read_masked():
    expected = np.array(
      [[ True,  True, False,  True,  True, False,  True,  True, False],
       [ True, False, False,  True, False, False,  True, False, False],
       [False, False, False, False, False, False, False, False, False],
       [ True,  True, False,  True,  True, False,  True,  True, False],
       [ True, False, False,  True, False, False,  True, False, False],
       [False, False, False, False, False, False, False, False, False],
       [ True,  True, False,  True,  True, False,  True,  True, False],
       [ True, False, False,  True, False, False,  True, False, False],
       [False, False, False, False, False, False, False, False, False]], dtype='bool')
    ds = create_virtual_raster()
    ds.open()
    actual = ds.read_band(1, masked=True)
    ds.close()
    assert np.all(actual.mask == expected)    
    
def test_read_full_scaled():
    expected = np.array(
      [[-9999,     5, -9999,     5, -9999,     5],
       [    3,    35,     3,    35,     3,    35],
       [-9999,     5, -9999,     5, -9999,     5],
       [    3,    35,     3,    35,     3,    35],
       [-9999,     5, -9999,     5, -9999,     5],
       [    3,    35,     3,    35,     3,    35]], dtype='int32')
    ds = create_virtual_raster()
    ds.open()
    out = np.zeros((6,6), dtype='int32')
    actual = ds.read_band(1, out=out)
    ds.close()
    assert np.all(expected == actual)
