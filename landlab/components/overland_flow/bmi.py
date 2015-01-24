#! /usr/bin/env python
import numpy as np
import yaml

from .generate_overland_flow_DEM import OverlandFlow

from ...core.model_parameter_dictionary import ModelParameterDictionary
from ...grid.raster import RasterModelGrid


class BmiOverlandFlow(object):
    """BMI implementation of the landlab overland flow component.
    """
    _name = 'Overland Flow'
    _input_var_names = (
        'land_surface_water__depth',
        'atmosphere_water__precipitation_rate',
        'atmosphere_water__precipitation_duration',
        'land_surface__elevation',
    )
    _output_var_names = (
        'land_surface_water__depth',
        'land_surface_water__volume_flow_rate',
        'land_surface_water__magnitude_of_shear_stress',
        'land_surface__slope',
    )
    _var_units = {
        'land_surface__water_depth': 'm',
        'atmosphere_water__precipitation_rate': 'm/s',
        'atmosphere_water__precipitation_duration': 's',
        'land_surface_water__volume_flow_rate': 'm3/s',
        'land_surface_water__magnitude_of_shear_stress': 'Pa',
        'land_surface__slope': '-',
        'land_surface__elevation': 'm',
    }

    def __init__(self):
        self._overland_flow = None
        self._flow_router = None
        self._grid = None
        self._values = {}
        self._time_step = None
        self._time = None

    def initialize(self, filename):
        """Initialize the component from a file.

        Parameters
        ----------
        filename : str
            Name of input file.
        """
        params = yaml.load(filename)

        (self._grid, z) = read_esri_ascii(params['data_file'])

        nodata_val=-9999
        self._grid.set_nodata_nodes_to_inactive(z, nodata_val) 

        outlet_row = params['outlet_row']
        outlet_column = params['outlet_column']

        outlet_node = self._grid.grid_coords_to_node_id(outlet_row,
                                                        outlet_column)
        self._grid.set_fixed_value_boundaries(outlet_node)

        self._overland_flow = OverlandFlow(self._grid)   

        self._time_step = self._overland_flow.model_duration
        self._time = 0.

        self._values = {
            'land_surface_water__depth': self._grid.at_node['water_depth'],
            'land_surface_water__volume_flow_rate': self._grid.at_node['water_discharge'],
            'land_surface_water__magnitude_of_shear_stress': self._grid.at_node['shear_stress'],
            'land_surface__slope': self._grid.at_node['slope_at_nodes'],
            'atmosphere_water__precipitation_rate': self._grid.at_node['rainfall_intensity'],
            'atmosphere_water__precipitation_duration': self._grid.at_node['rainfall_duration'],
            'land_surface__elevation': self._grid.at_node['elevation'],
        }

    def update(self):
        """Update the model by one time step.
        """
        self._overland_flow.flow_across_grid(self._grid, z)
        self._overland_flow.update_across_grid(self._grid,
                                               rainfall_duration=900,
                                               model_duration=3000,
                                               rainfall_intensity=0.0000093133)

    def update_until(self, then):
        """Update model until a time.

        Parameters
        ----------
        then : float
            Time to run model to.

        Raises
        ------
        ValueError : *then* is less than now.
        """
        n_steps = (then - self.get_current_time()) / self.get_time_step()
        if n_steps < 0:
            raise ValueError('negative time step')

        for _ in xrange(int(n_steps)):
            self.update()
        raise NotImplementedError()
        #self.update_frac(n_steps - int(n_steps))

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

        raise NotImplementedError()

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
        return (self._grid.number_of_node_rows,
                self._grid.number_of_node_columns)

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
