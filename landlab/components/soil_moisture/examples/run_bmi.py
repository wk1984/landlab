#! /usr/bin/env python
from StringIO import StringIO

import matplotlib.pyplot as plt

from landlab.components.soil_moisture.bmi import BmiSoilMoisture


def main():
    c = BmiSoilMoisture()
    params = StringIO(
"""
n_rows: 100
n_cols: 100
spacing: 1
dt: 1.
tb_frac: 0.5
""")
    c.initialize(params)

    for _ in xrange(10):
        c.update()

    runoff = c.get_value('land_surface_water__volume_flow_rate')
    runoff.shape = c.get_grid_shape('land_surface_water__volume_flow_rate')

    evap = c.get_value('land_surface_water__evaporation_volume_flux')
    evap.shape = c.get_grid_shape('land_surface_water__evaporation_volume_flux')

    plt.imshow(evap)
    plt.show()


if __name__ == '__main__':
    main()
