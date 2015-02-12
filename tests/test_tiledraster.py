from tiledrasterio._tiledraster import TiledRaster

def test_from_vrt():
    # TODO: Embed in data
    vrtfile = '/Users/asger/Data/DHM/DSM_2014/DSM_605_68.vrt'
    tr = TiledRaster(vrtfile)
    assert len(list(tr.tiles())) > 0