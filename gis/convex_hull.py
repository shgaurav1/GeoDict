# coding = utf-8
from scipy.spatial import ConvexHull

def parseHull(hull_object,points):
    hull=[]
    for simplex in hull_object.simplices:
        hull.append(points[simplex[0]])
        hull.append(points[simplex[1]])
    return hull

def get_convex_hull(osm_data):
    boundaries = osm_data["geometry"]
    if boundaries["type"] == "Polygon":
        hull = parseHull(ConvexHull(boundaries["coordinates"][-1]), boundaries["coordinates"][-1])
        return {"type": "polygon", "coordinates": hull}
    else:
        hull = []
        for bound in boundaries["coordinates"][-1]:
            hull.append(parseHull(ConvexHull(bound), bound))
        return {"type":"mutipolygon","coordinates":hull}
