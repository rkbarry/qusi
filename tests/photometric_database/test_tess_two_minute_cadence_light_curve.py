from pathlib import Path
from unittest.mock import patch, Mock

import numpy as np
import pandas as pd
import pytest

import ramjet.photometric_database.tess_two_minute_cadence_light_curve as module
from ramjet.photometric_database.tess_two_minute_cadence_light_curve import TessTwoMinuteCadenceColumnName, \
    TessTwoMinuteCadenceMastFitsIndex, TessTwoMinuteCadenceFileBasedLightCurve


class TestTessTwoMinuteCadenceFileBasedLightCurve:
    @pytest.fixture
    def fake_hdu_list(self):
        mock_hdu_data = {TessTwoMinuteCadenceColumnName.TIME.value: [0, 1],
                         TessTwoMinuteCadenceColumnName.PDCSAP_FLUX.value: [2, 3],
                         TessTwoMinuteCadenceColumnName.SAP_FLUX.value: [4, 5],
                         TessTwoMinuteCadenceColumnName.PDCSAP_FLUX_ERROR.value: [6, 7],
                         TessTwoMinuteCadenceColumnName.SAP_FLUX_ERROR.value: [8, 9]}
        mock_hdu = Mock()
        mock_hdu.data = mock_hdu_data
        mock_hdu_list = [None, mock_hdu]  # TESS light curve data is in index 1 of the HDU list.
        return mock_hdu_list

    def test_fits_index_enum_have_the_same_entries_as_column_name_enum(self):
        column_name_entry_names = [entry.name for entry in TessTwoMinuteCadenceColumnName]
        fits_index_entry_names = [entry.name for entry in TessTwoMinuteCadenceMastFitsIndex]
        assert np.array_equal(sorted(column_name_entry_names), sorted(fits_index_entry_names))

    def test_from_path_factory_creates_data_frame_from_fits_hdu_list(self, fake_hdu_list):
        with patch.object(module.fits, 'open') as mock_open:
            mock_open.return_value.__enter__.return_value = fake_hdu_list
            light_curve = TessTwoMinuteCadenceFileBasedLightCurve.from_path(Path('TIC 169480782 sector 5.fits'))
            expected_data_frame = pd.DataFrame(fake_hdu_list[1].data)
            assert light_curve.data_frame.sort_index(axis=1).equals(expected_data_frame.sort_index(axis=1))

    def test_from_path_factory_light_curve_uses_correct_default_times_and_fluxes(self, fake_hdu_list):
        with patch.object(module.fits, 'open') as mock_open:
            mock_open.return_value.__enter__.return_value = fake_hdu_list
            light_curve = TessTwoMinuteCadenceFileBasedLightCurve.from_path(Path('TIC 169480782 sector 5.fits'))
            assert np.array_equal(light_curve.times, fake_hdu_list[1].data[TessTwoMinuteCadenceColumnName.TIME.value])
            assert np.array_equal(light_curve.fluxes,
                                  fake_hdu_list[1].data[TessTwoMinuteCadenceColumnName.PDCSAP_FLUX.value])

    def test_can_get_tic_id_and_sector_from_human_readable_file_name(self):
        tic_id0, sector0 = TessTwoMinuteCadenceFileBasedLightCurve.get_tic_id_and_sector_from_file_path(
            'TIC 289890301 sector 15 second half')
        assert tic_id0 == 289890301
        assert sector0 == 15
        tic_id1, sector1 = TessTwoMinuteCadenceFileBasedLightCurve.get_tic_id_and_sector_from_file_path(
            'output/TIC 169480782 sector 5.png')
        assert tic_id1 == 169480782
        assert sector1 == 5

    def test_get_tic_id_and_sector_raises_error_with_unknown_pattern(self):
        with pytest.raises(ValueError):
            TessTwoMinuteCadenceFileBasedLightCurve.get_tic_id_and_sector_from_file_path('a b c d e f g')

    def test_can_get_tic_id_and_sector_from_tess_obs_id_style_file_name(self):
        tic_id0, sector0 = TessTwoMinuteCadenceFileBasedLightCurve.get_tic_id_and_sector_from_file_path(
            'mast:TESS/product/tess2019006130736-s0007-0000000278956474-0131-s_lc.fits')
        assert tic_id0 == 278956474
        assert sector0 == 7
        tic_id1, sector1 = TessTwoMinuteCadenceFileBasedLightCurve.get_tic_id_and_sector_from_file_path(
            'tess2018319095959-s0005-0000000278956474-0125-s')
        assert tic_id1 == 278956474
        assert sector1 == 5

    def test_from_path_factory_sets_the_tic_id_and_sector_of_the_light_curve(self, fake_hdu_list):
        with patch.object(module.fits, 'open') as mock_open:
            mock_open.return_value.__enter__.return_value = fake_hdu_list
            light_curve = TessTwoMinuteCadenceFileBasedLightCurve.from_path(Path('TIC 169480782 sector 5.fits'))
            assert light_curve.tic_id == 169480782
            assert light_curve.sector == 5
