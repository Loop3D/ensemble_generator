from math import sin, cos, atan, atan2, asin, radians, degrees, sqrt, pow, acos


####################################################
# calculate 3D direction cosines from dip, dipdirection
#
# ddd2dircos(dip,dipdir)
# Args:
# dip dip of bedding from horizontal
# dipdir clockwise degrees from North of dip direction
# Returns:
# l,m,n direction cosines of pole to plane
#
# Converts dip, dip direction to three direction cosine arrays(l,m,n)
####################################################
def ddd2dircos(dip, dipdir):
    l = sin(radians(dipdir)) * cos(radians(90 - dip))
    m = cos(radians(dipdir)) * cos(radians(90 - dip))
    n = sin(radians(90 - dip))
    return (l, m, n)


####################################################
# calculate dip, dipdirection from 3D direction cosines
#
# dircos2ddd(l,m,n)
# Args:
# l,m,n direction cosines of pole to plane Returns: dip dip of bedding from horizontal
# dipdir clockwise degrees from North of dip direction
#
# Converts (l,m,n) direction cosine arrays to dip, dip direction
####################################################
def dircos2ddd(l, m, n):
    if (m > 0):
        dipdir = (360 + degrees(atan(l / m))) % 360
    elif (m < 0):
        dipdir = (540 + degrees(atan(l / m))) % 360
    else:
        dipdir = 90
    dip = 90 - degrees(asin(n))
    return (dip, dipdir)