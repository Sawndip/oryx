import os
import glob
import struct 


from numba import jit


from oryx.utilities import dataIO



@jit(nopython=True)
def FindSurface(point_cloud, zres, yres, xres):
    # go through all points and find which are on the surface
    surface_points = []
    
    for iv in point_cloud:
        iz = iv // (yres * xres)
        iy = (iv - iz * yres * xres) // xres
        ix = iv % xres

        surface = False

        # consider the six cardinal neighbors
        if ix > 0:
            neighbor_index = iz * yres * xres + iy * xres + (ix - 1)
            if not neighbor_index in point_cloud: surface = True
        if ix < xres - 1:
            neighbor_index = iz * yres * xres + iy * xres + (ix + 1)
            if not neighbor_index in point_cloud: surface = True

        if iy > 0:
            neighbor_index = iz * yres * xres + (iy - 1) * xres + ix
            if not neighbor_index in point_cloud: surface = True
        if iy < yres - 1:
            neighbor_index = iz * yres * xres + (iy + 1) * xres + ix
            if not neighbor_index in point_cloud: surface = True

        if iz > 0:
            neighbor_index = (iz - 1) * yres * xres + iy * xres + ix
            if not neighbor_index in point_cloud: surface = True
        if iz < zres - 1:
            neighbor_index = (iz + 1) * yres * xres + iy * xres + ix
            if not neighbor_index in point_cloud: surface = True
        if surface: surface_points.append(iv)

    return surface_points


def Segment2Surface(prefix, label):
    if not os.path.exists('segmentations/{}/{:06d}.pts'.format(prefix, label)): return

    # get the grid size for this prefix
    zres, yres, xres = dataIO.GridSize(prefix)

    point_cloud = set(dataIO.ReadPoints(prefix, label, 'segmentations'))

    surface_points = FindSurface(point_cloud, zres, yres, xres)
    
    surface_filename = 'surfaces/{}/{:06d}.pts'.format(prefix, label)

    with open(surface_filename, 'wb') as fd:
        nsurface_points = len(surface_points)
        fd.write(struct.pack('qqqq', zres, yres, xres, nsurface_points))
        fd.write(struct.pack('%sq' % nsurface_points, *surface_points))
