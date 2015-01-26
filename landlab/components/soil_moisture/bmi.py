#! /usr/bin/env python
import types

import numpy as np
import yaml

from ...grid.raster import RasterModelGrid
from .soil_moisture_field import SoilMoisture

_NAME_MAP = (
    ('vegetated_land__area_fraction',
     'VegetationCover'),
    ('land_vegetation__leaf-area-index',
     'LiveLeafAreaIndex'),
    ('potential_land_surface_water__evaporation_volume_flux',
     'PotentialEvapotranspiration'),
    ('land_surface_water__magnitude_of_shear_stress',
     'WaterStress'),
    ('soil_water__saturated_volume_fraction',
     'SaturationFraction'),
    ('Drainage',
     'Drainage'),
    ('land_surface_water__volume_flow_rate',
     'Runoff'),
    ('land_surface_water__evaporation_volume_flux',
     'ActualEvapotranspiration'),
)


class BmiSoilMoisture(object):
    """BMI implementation of the landlab soil moisture component.

    Examples
    --------
    Create an instance of a soil moisture component with a Basic Modeling
    Interface.

    >>> from landlab.components.soil_moisture.bmi import BmiSoilMoisture
    >>> sm = BmiSoilMoisture()

    Note that although you have created an instance of the component, it is
    not initiaized and so it is not yet ready to run. Some of its attributes,
    such as input and output names, have been set but not everything (a
    time step, for instance).

    >>> sm.get_component_name()
    'Soil Moisture'
    >>> sm.get_input_var_names() #doctest: +NORMALIZE_WHITESPACE
    ('vegetated_land__area_fraction',
     'land_vegetation__leaf-area-index',
     'potential_land_surface_water__evaporation_volume_flux')
    >>> sm.get_time_step() is None
    True

    To initialize the component, use the :meth:`~.BmiSoilMoisture.initialize`
    method, which initializes the instance from a YAML-formatted file.

    >>> from StringIO import StringIO
    >>> params = StringIO('''
    ... n_rows: 10
    ... n_cols: 10
    ... spacing: 1
    ... dt: 1.
    ... tb_frac: 1.
    ... ''')
    >>> sm.initialize(params)

    The component now has a time step.

    >>> sm.get_current_time(), sm.get_time_units()
    (0.0, 'd')
    >>> sm.get_time_step()
    1.0

    Use the :meth:`~.BmiSoilMoisture.update` method to advance the component
    through time one time step at a time.

    >>> sm.update()
    >>> sm.get_current_time()
    1.0

    As an alternative, use the :meth:`~.BmiSoilMoisture.update_until` method
    to advance the component until a particular time.

    >>> sm.update_until(2.3)
    >>> print round(sm.get_current_time(), 6)
    2.3
    """
    _name = 'Soil Moisture'

    _input_var_names = (
        'vegetated_land__area_fraction',
        'land_vegetation__leaf-area-index',
        'potential_land_surface_water__evaporation_volume_flux',
    )

    _output_var_names = (
        'land_surface_water__magnitude_of_shear_stress',
        'soil_water__saturated_volume_fraction',
        'Drainage',
        'land_surface_water__volume_flow_rate',
        'land_surface_water__evaporation_volume_flux',
    )

    _var_units = {
        'vegetated_land__area_fraction' : '-',
        'land_vegetation__leaf-area-index': '-',
        'potential_land_surface_water__evaporation_volume_flux' : 'mm',
        'land_surface_water__magnitude_of_shear_stress' : 'Pa',
        'soil_water__saturated_volume_fraction' : '-',
        'Drainage' : 'mm',
        'land_surface_water__volume_flow_rate' : 'mm',
        'land_surface_water__evaporation_volume_flux' : 'mm',
    }

    def __init__(self):
        self._sm = None
        self._values = {}
        self._time_step = None
        self._time = None
        self._grid = None

    def initialize(self, param_file):
        """Initialize the component from a file.

        Parameters
        ----------
        filename : str
            Name of input file.
        """
        if isinstance(param_file, types.StringTypes):
            self.from_path(param_file)
        else:
            self.from_file_like(param_file)

    def from_path(self, path):
        """Initialze from a named file.

        Parameters
        ----------
        path : str
            Path to the initialization file.
        """
        with open(filename, 'r') as fp:
            params = yaml.load(fp)
        self.from_keywords(**params)

    def from_file_like(self, file_like):
        """Initialze from a file-like object.

        Parameters
        ----------
        file_like : file_like
            File-like object for the initialization file.
        """
        params = yaml.load(file_like)
        self.from_keywords(**params)

    def from_keywords(self, n_rows=0, n_cols=0, spacing=1., dt=1., tb_frac=1.):
        """Initialize from keywords.

        Parameters
        ----------
        n_rows : int
            Number of rows of nodes.
        n_cols : int
            Number of columns of nodes.
        spacing : float
            Spacing between node rows and columns (meters).
        dt : float
            Time step (days).
        tb_frac : float
            Fraction of time step for Tb.
        """
        if tb_frac < 0. or tb_frac > 1.:
            raise ValueError('tb_frac is out of range')
        if n_rows <= 0 or n_cols <= 0:
            raise ValueError('Non-positive rows or columns')
        if spacing <= 0.:
            raise ValueError('Non-positive spacing')

        self._tb_frac = tb_frac
        self._time_step = dt
        self._time = 0.

        grid = RasterModelGrid(n_rows, n_cols, spacing)

        grid.add_field('cell','VegetationCover',
                       np.random.rand(grid.number_of_cells), units='-')
        grid.add_field('cell','LiveLeafAreaIndex',
                       np.ones(grid.number_of_cells) * 3, units='-')
        grid.add_field('cell','PotentialEvapotranspiration',
                       np.ones(grid.number_of_cells) * 6, units='mm')
        grid.add_field('cell','InitialSaturationFraction',
                       np.random.rand(grid.number_of_cells), units='-')

        self._sm = SoilMoisture(grid)
        self._grid = grid

        self._values = {}
        for (standard_name, local_name) in _NAME_MAP:
            self._values[standard_name] = grid.at_cell[local_name]

    def update(self):
        """Update the model by one time step.

        Examples
        --------
        >>> from landlab.components.soil_moisture.bmi import BmiSoilMoisture
        >>> sm = BmiSoilMoisture()
        >>> sm.from_keywords(n_rows=10, n_cols=10)
        >>> sm.get_current_time()
        0.0
        >>> sm.get_time_step()
        1.0
        >>> sm.update()
        >>> sm.get_current_time()
        1.0
        """
        self.update_frac(1.)

    def update_until(self, then):
        """Update model until a time.

        Parameters
        ----------
        then : float
            Time to run model to.

        Raises
        ------
        ValueError : *then* is less than now.

        Examples
        --------
        >>> from landlab.components.soil_moisture.bmi import BmiSoilMoisture
        >>> sm = BmiSoilMoisture()
        >>> sm.from_keywords(n_rows=10, n_cols=10)
        >>> sm.get_current_time()
        0.0
        >>> sm.update_until(10.2)
        >>> print round(sm.get_current_time(), 6)
        10.2
        """
        n_steps = (then - self.get_current_time()) / self.get_time_step()
        if n_steps < 0:
            raise ValueError('negative time step')

        for _ in xrange(int(n_steps)):
            self.update()
        self.update_frac(n_steps - int(n_steps))

    def update_frac(self, dt_frac):
        """Run model for a fraction of a time step.

        Parameters
        ----------
        dt_frac : float
            Fraction of time step to run model for.

        Raises
        ------
        ValueError : *dt_frac* is outside of (0., 1.]
        """
        if dt_frac <= 0. or dt_frac > 1.:
            raise ValueError('dt_frac out of bounds')

        dt = self.get_time_step() * dt_frac

        tb = dt * self._tb_frac 
        tr = dt * (1 - self._tb_frac)

        self._sm.update(0., Tb=tb * 24., Tr=tr * 24.)

        self._time += dt

    def get_component_name(self):
        """The name of the component.

        Returns
        -------
        name : str
            Name of the model.
        """
        return self._name

    def get_input_var_names(self):
        """Standard names for input variables.

        Returns
        -------
        names : tuple
            Names of input variables as CSDMS Standard Names.
        """
        return self._input_var_names

    def get_output_var_names(self):
        """Standard names for output variables.

        Returns
        -------
        names : tuple
            Names of output variables as CSDMS Standard Names.
        """
        return self._output_var_names

    def get_grid_shape(self, name):
        """Shape of the grid for a variable.

        Parameters
        ----------
        name : str
            Variable name

        Returns
        -------
        shape : tuple of ints
            Grid shape.
        """
        return (self._grid.number_of_cell_rows,
                self._grid.number_of_cell_columns)

    def get_grid_spacing(self, name):
        """Spacing of grid rows and columns for a variable.

        Parameters
        ----------
        name : str
            Variable name

        Returns
        -------
        spacing : tuple of floats
            Grid spacing.
        """
        return (self._grid.node_spacing, self._grid.node_spacing)

    def get_grid_origin(self, name):
        """Coordinates of lower-left corner of grid variable.

        Parameters
        ----------
        name : str
            Variable name

        Returns
        -------
        origin : tuple of floats
            Grid origin.
        """
        return (0., 0.)

    def get_value(self, name):
        """Copy of grid variable data.

        Parameters
        ----------
        name : str
            Variable name

        Returns
        -------
        data : ndarray
            Variable data.
        """
        return self.get_value_ptr(name).copy()

    def get_value_ptr(self, name):
        """Grid variable data.

        Parameters
        ----------
        name : str
            Variable name

        Returns
        -------
        data : ndarray
            Variable data.
        """
        if name in self._output_var_names:
            return self._values[name]
        else:
            raise KeyError(name)

    def set_value(self, name, src):
        """Set the values for a grid variable.

        Parameters
        ----------
        name : str
            Variable name
        src : ndarray
            New values for the variable.
        """
        if name in self._input_var_names:
            val = self._values[name]
            val[:] = src.flat
        else:
            raise KeyError(name)

    def get_start_time(self):
        """Model start time.

        Returns
        -------
        time : float
            Start time.
        """
        return 0.

    def get_end_time(self):
        """Model end time.

        Returns
        -------
        time : float
            End time.
        """
        return np.finfo('d').max

    def get_current_time(self):
        """Current time of model.

        Returns
        -------
        time : float
            Current time.
        """
        return self._time

    def get_time_step(self):
        """Model time step.

        Returns
        -------
        dt : float
            Time step.
        """
        return self._time_step

    def get_time_units(self):
        """Units that all time is reported in.

        Returns
        -------
        units : str
            Units for time values.
        """
        return 'd'
