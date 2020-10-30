"""
Read directional graph from Open Street Maps osm format
Based on ToFull's OSM parser here https://gist.github.com/Tofull/49fbb9f3661e376d2fe08c2e9d64320e
Based on the osm to networkx tool from aflaxman : https://gist.github.com/aflaxman/287370/
Use python3.6
"""

import copy
import networkx
import xml.sax  # parse osm file
import urllib.request
from pathlib import Path  # manage cached tiles
from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2, unit_m = True):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    default unit : km
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    if unit_m:
        r *= 1000
    return c * r


def download_osm(left, bottom, right, top, proxy = False, proxyHost="10.0.4.2", proxyPort="3128",
                 cache=False, cacheTempDir="/tmp/tmpOSM/", verbose=True):
    """ Return a filehandle to the downloaded data from osm api."""

    if cache:
        ## cached tile filename
        cachedTileFilename = "osm_map_{:.8f}_{:.8f}_{:.8f}_{:.8f}.map".format(left, bottom, right, top)

        if verbose:
            print("Cached tile filename :", cachedTileFilename)

        Path(cacheTempDir).mkdir(parents=True, exist_ok=True)  # Create cache path if not exists

        osmFile = Path(cacheTempDir + cachedTileFilename).resolve()  # Replace the relative cache folder path to absolute path

        if osmFile.is_file():
            # download from the cache folder
            if (verbose):
                print("Tile loaded from the cache folder.")

            fp = urllib.request.urlopen("file://"+str(osmFile))
            return fp

    if (proxy):
        # configure the urllib request with the proxy
        proxy_handler = urllib.request.ProxyHandler({'https': 'https://' + proxyHost + ":" + proxyPort, 'http': 'http://' + proxyHost + ":" + proxyPort})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)


    request = "http://api.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f"%(left,bottom,right,top)

    if (verbose):
        print("Download the tile from osm web api ... in progress")
        print("Request :", request)

    fp = urllib.request.urlopen(request)

    if (verbose):
        print("OSM Tile downloaded")

    if (cache):
        if (verbose):
            print("Write osm tile in the cache"
            )
        content = fp.read()
        with open(osmFile, 'wb') as f:
            f.write(content)

        if osmFile.is_file():
            if (verbose):
                print("OSM tile written in the cache")

            fp = urllib.request.urlopen("file://"+str(osmFile)) ## Reload the osm tile from the cache (because fp.read moved the cursor)
            return fp

    return fp


def read_osm(filename_or_stream, only_roads=True):
    """Read graph in OSM format from file specified by name or by stream object.
    Parameters
    ----------
    filename_or_stream : filename or stream object
    Returns
    -------
    G : Graph
    Examples
    --------
    >>> G=nx.read_osm(nx.download_osm(-122.33,47.60,-122.31,47.61))
    >>> import matplotlib.pyplot as plt
    >>> plt.plot([G.node[n]['lat']for n in G], [G.node[n]['lon'] for n in G], 'o', color='k')
    >>> plt.show()
    """
    osm = OSM(filename_or_stream)
    G = networkx.DiGraph()

    # Add ways
    for w in osm.ways.values():
        if only_roads and 'highway' not in w.tags:
            continue

        if ('oneway' in w.tags) and (w.tags['oneway'] == 'yes'):
            # ONLY ONE DIRECTION
            G.add_path(w.nds, id=w.id, **w.tags)
        
        else:
            # BOTH DIRECTION
            augmented_edge_attrs = w.tags
            augmented_edge_attrs['bidrectional'] = True
            G.add_path(w.nds, id=w.id, **w.tags)
            G.add_path(w.nds[::-1], id=w.id, **augmented_edge_attrs)

    # Complete the used nodes' information
    for n_id in G.nodes():
        n = osm.nodes[n_id]
        G.node[n_id]['lat'] = n.lat
        G.node[n_id]['lon'] = n.lon
        G.node[n_id]['id'] = n.id

    # Estimate the length of each way
    print(type(G))
    for u,v,d in G.edges(data=True):
        # Give a realistic distance estimation (neither EPSG nor projection nor reference system are specified)
        distance = haversine(G.node[u]['lon'], G.node[u]['lat'], G.node[v]['lon'], G.node[v]['lat'], unit_m=True)
        G.add_weighted_edges_from([(u, v, distance)], weight='length')

    return G


class Node:
    def __init__(self, id, lon, lat):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.tags = {}

    def __str__(self):
        return "Node (id : %s) lon : %s, lat : %s "%(self.id, self.lon, self.lat)


class Way:
    def __init__(self, id, osm):
        self.osm = osm
        self.id = id
        self.nds = []
        self.tags = {}

    def split(self, dividers):
        # slice the node-array using this nifty recursive function
        def slice_array(ar, dividers):
            for i in range(1,len(ar)-1):
                if dividers[ar[i]]>1:
                    left = ar[:i+1]
                    right = ar[i:]

                    rightsliced = slice_array(right, dividers)

                    return [left]+rightsliced
            return [ar]

        slices = slice_array(self.nds, dividers)

        # create a way object for each node-array slice
        ret = []
        i=0
        for slice in slices:
            littleway = copy.copy( self )
            littleway.id += "-%d"%i
            littleway.nds = slice
            ret.append( littleway )
            i += 1

        return ret


class OSM:
    def __init__(self, filename_or_stream):
        """ File can be either a filename or stream/file object."""
        nodes = {}
        ways = {}

        superself = self

        class OSMHandler(xml.sax.ContentHandler):
            @classmethod
            def setDocumentLocator(self,loc):
                pass

            @classmethod
            def startDocument(self):
                pass

            @classmethod
            def endDocument(self):
                pass

            @classmethod
            def startElement(self, name, attrs):
                if name=='node':
                    self.currElem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']))
                elif name=='way':
                    self.currElem = Way(attrs['id'], superself)
                elif name=='tag':
                    self.currElem.tags[attrs['k']] = attrs['v']
                elif name=='nd':
                    self.currElem.nds.append( attrs['ref'] )

            @classmethod
            def endElement(self,name):
                if name=='node':
                    nodes[self.currElem.id] = self.currElem
                elif name=='way':
                    ways[self.currElem.id] = self.currElem

            @classmethod
            def characters(self, chars):
                pass

        xml.sax.parse(filename_or_stream, OSMHandler)

        self.nodes = nodes
        self.ways = ways

        #count times each node is used
        node_histogram = dict.fromkeys( self.nodes.keys(), 0 )
        for way in self.ways.values():
            if len(way.nds) < 2:       #if a way has only one node, delete it out of the osm collection
                del self.ways[way.id]
            else:
                for node in way.nds:
                    node_histogram[node] += 1

        #use that histogram to split all ways, replacing the member set of ways
        new_ways = {}
        for id, way in self.ways.items():
            split_ways = way.split(node_histogram)
            for split_way in split_ways:
                new_ways[split_way.id] = split_way
        self.ways = new_ways
