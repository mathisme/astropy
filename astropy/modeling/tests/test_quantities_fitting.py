# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Tests that relate to fitting models with quantity parameters
"""

from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

from ...utils import NumpyRNGContext


@pytest.mark.xfail
def test_fitting_simple():

    # Generate fake data
    with NumpyRNGContext(12345):
        x = np.linspace(-5., 5., 200)
        y = 3 * np.exp(-0.5 * (x - 1.3)**2 / 0.8**2)
        y += np.random.normal(0., 0.2, x.shape)

    # Attach units to data
    x = x * u.m
    y = y * u.Jy

    # Fit the data using a Gaussian with units
    g_init = models.Gaussian1D(amplitude=1. * u.mJy, mean=3 * u.cm, stddev=2 * u.mm)
    fit_g = fitting.LevMarLSQFitter()
    g = fit_g(g_init, x, y)

    # TODO: update actual numerical results, but these should be close
    assert_quantity_allclose(g.amplitude, 3 * u.Jy)
    assert_quantity_allclose(g.mean, 1.3 * u.m)
    assert_quantity_allclose(g.stddev, 0.8 * u.m)


@pytest.mark.xfail
def test_fitting_missing_data_units():
    """
    Raise an error if the model has units but the data doesn't
    """
    g_init = models.Gaussian1D(amplitude=1. * u.mJy, mean=3 * u.cm, stddev=2 * u.mm)
    fit_g = fitting.LevMarLSQFitter()

    with pytest.raises(UnitsError) as exc:
        g = fit_g(g_init, [1, 2, 3], [4, 5, 6])
    assert exc.value.args[0] == ("Units of input 'x', (dimensionless), does not "
                                 "match required units for model input, cm (length)")

    with pytest.raises(UnitsError) as exc:
        g = fit_g(g_init, [1, 2, 3] * u.m, [4, 5, 6])
    assert exc.value.args[0] == ("Units of input 'y', (dimensionless), does not "
                                 "match required units for model output, Jy")

@pytest.mark.xfail
def test_fitting_missing_model_units():
    """
    Raise an error if the data has units but the model doesn't.
    """

    # TODO: determine whether this breaks backward-compatibility

    g_init = models.Gaussian1D(amplitude=1., mean=3, stddev=2)
    fit_g = fitting.LevMarLSQFitter()

    with pytest.raises(UnitsError) as exc:
        g = fit_g(g_init, [1, 2, 3] * u.m, [4, 5, 6] * u.Jy)
    assert exc.value.args[0] == ("Units of input 'x', m (length), does not "
                                 "match required units for model input, "
                                 "(dimensionless)")

    g_init = models.Gaussian1D(amplitude=1., mean=3 * u.m, stddev=2 * u.m)
    fit_g = fitting.LevMarLSQFitter()

    with pytest.raises(UnitsError) as exc:
        g = fit_g(g_init, [1, 2, 3] * u.m, [4, 5, 6] * u.Jy)
    assert exc.value.args[0] == ("Units of input 'y', Jy, does not "
                                 "match required units for model output, "
                                 "(dimensionless)")

@pytest.mark.xfail
def test_fitting_incompatible_units():
    """
    Raise an error if the data and model have incompatible units
    """

    g_init = models.Gaussian1D(amplitude=1. * u.Jy, mean=3 * u.m, stddev=2 * u.cm)
    fit_g = fitting.LevMarLSQFitter()

    with pytest.raises(UnitsError) as exc:
        g = fit_g(g_init, [1, 2, 3] * u.Hz, [4, 5, 6] * u.Jy)
    assert exc.value.args[0] == ("Units of input 'x', Hz (frequency), does not "
                                 "match required units for model input, "
                                 "m (length)")


@pytest.mark.xfail
def test_fitting_with_equivalencies():
    """
    Raise an error if the data and model have incompatible units
    """

    g_init = models.Gaussian1D(amplitude=1. * u.Jy, mean=3 * u.m, stddev=2 * u.cm)
    g_init.input_equivalencies = u.spectral()

    fit_g = fitting.LevMarLSQFitter()
    g = fit_g(g_init, [1, 2, 3] * u.Hz, [4, 5, 6] * u.Jy)

    # TODO: check value of result
