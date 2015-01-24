#! /usr/bin/env python
import numpy as np

from .diffusion import Diffusion

from ...core.model_parameter_dictionary import ModelParameterDictionary
from ...grid.raster import RasterModelGrid


class BmiStreamPower(object):
    """BMI implementation of the landlab diffusion component.
    """
    _name = 'Diffusion'
    _input_var_names = ('land_surface__elevation', )
    _output_var_names = (
        'land_surface__elevation',
        'land_surface_water_suspended-sediment__divergence_of_unit-width_discharge',
    )
    _var_units = {
        'land_surface__elevation': 'm',
        'land_surface_water_suspended-sediment__divergence_of_unit-width_discharge': 'm/y',
    }
    def __init__(self):
        self._diffusion = None
        self._grid = None
        self._values = {}

    def initialize(self, filename):
        """Initialize the component from a file.

        Parameters
        ----------
        filename : str
            Name of input file.
        """
        params = ModelParameterDictionary(filename)

        self._grid = RasterModelGrid(int(params['nrows']),
                                     int(params['ncols']),
                                     float(params['dx']))
        self._diffusion = Diffusion(self._grid, input_stream=params,
                                    current_time=0.)

        self._values = {
            'land_surface__elevation': self._grid.at_node['landscape_surface__elevation'],
            'land_surface_water_suspended-sediment__divergence_of_unit-width_discharge': self._grid.at_node['sediment_flux_divergence'],
        }

    def update(self):
        """Update the model by one time step.
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

        self._diffusion.run_one_step_internal(self.get_time_step() * dt_frac)

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
        return self._diffusion.current_time

    def get_time_step(self):
        """Model time step.

        Returns
        -------
        dt : float
            Time step.
        """
        return self._diffusion.dt

    def get_time_units(self):
        """Units that all time is reported in.

        Returns
        -------
        units : str
            Units for time values.
        """
        return 'd'
