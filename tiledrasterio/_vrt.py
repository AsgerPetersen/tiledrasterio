import xml.etree.ElementTree as ET
from affine import Affine
import os

def rect_to_win(rect):
    rows = (int(rect['yOff']), int(rect['yOff']) + int(rect['ySize']))
    cols = (int(rect['xOff']), int(rect['xOff']) + int(rect['xSize']))
    return (rows, cols)

def parse_vrt( filename ):
    vrt = {"shape": None, "bands":[], "srs": "", "transformation": None, "rootpath": "", "filename": ""}
    vrt["filename"] = filename
    vrt["rootpath"] = os.path.dirname(filename)
    
    xmltree = ET.parse( filename )
    xmlroot = xmltree.getroot()
    vrt["shape"] = (int(xmlroot.attrib['rasterYSize']), int(xmlroot.attrib['rasterXSize']))
    
    # Iterate over children of root
    for rootchild in xmlroot:
        if rootchild.tag == 'SRS':
            vrt["srs"] = rootchild.text
        elif rootchild.tag == 'GeoTransform':
            params = [float(f) for f in rootchild.text.split(',')]
            vrt["transformation"] = Affine( params[1], params[2], params[0], params[4], params[5], params[3] )
        elif rootchild.tag == 'VRTRasterBand':
            from rasterio import dtypes
            if len(vrt["bands"]) > 0:
                raise Exception('Only single band supported for now')
            band = { 'sources' : [] }
            vrt["bands"].append(band)
            typename = rootchild.attrib['dataType']
            band['dtype'] = dtypes.dtype_fwd[ dtypes.dtype_rev[typename.lower()] ]
            for bandchild in rootchild:
                if bandchild.tag in ['ColorInterp', 'Histograms']:
                    continue
                elif bandchild.tag == 'NoDataValue':
                    band['nodata'] = float( bandchild.text )
                elif bandchild.tag == 'ComplexSource':
                    complexSource = {'sourcetype': 'ComplexSource'}
                    band['sources'].append( complexSource )
                    for sourcechild in bandchild:
                        if sourcechild.tag == 'SourceFilename':
                            complexSource['sourcefile'] = {
                                'filename': sourcechild.text, 
                                'relative': sourcechild.get('relativeToVRT') == '1'}
                        elif sourcechild.tag == 'SourceBand' :
                            complexSource['sourceband']= int( sourcechild.text )
                        elif sourcechild.tag == 'SrcRect':
                            complexSource['srcwin'] = rect_to_win(sourcechild.attrib) 
                        elif sourcechild.tag == 'DstRect':
                            complexSource['dstwin'] = rect_to_win(sourcechild.attrib)
                        elif sourcechild.tag == 'NODATA':                        
                            complexSource['nodata'] = float( sourcechild.text )
    return vrt