"""Code for representing a database of lightcurves for binary classification with a single label per time step."""
from abc import abstractmethod

import numpy as np
import pandas as pd
import tensorflow as tf
from typing import Union

from ramjet.photometric_database.lightcurve_database import LightcurveDatabase


class LightcurveLabelPerTimeStepDatabase(LightcurveDatabase):
    """A representation of a database of lightcurves for binary classification with a single label per time step."""

    def __init__(self, data_directory='data'):
        super().__init__(data_directory=data_directory)
        self.meta_data_frame: Union[pd.DataFrame, None] = None
        self.time_steps_per_example = 6400
        self.length_multiple_base = 32
        self.batch_size = 100

    def training_preprocessing(self, example_path_tensor: tf.Tensor) -> (tf.Tensor, tf.Tensor):
        """
        Loads and preprocesses the data for training.

        :param example_path_tensor: The tensor containing the path to the example to load.
        :return: The example and its corresponding label.
        """
        example, label = self.general_preprocessing(example_path_tensor)
        example, label = example.numpy(), label.numpy()
        example, label = self.make_uniform_length_requiring_positive(
            example, label, self.time_steps_per_example, required_length_multiple_base=self.length_multiple_base
        )
        return tf.convert_to_tensor(example, dtype=tf.float32), tf.convert_to_tensor(label, dtype=tf.float32)

    def evaluation_preprocessing(self, example_path_tensor: tf.Tensor) -> (tf.Tensor, tf.Tensor):
        """
        Loads and preprocesses the data for evaluation.

        :param example_path_tensor: The tensor containing the path to the example to load.
        :return: The example and its corresponding label.
        """
        example, label = self.general_preprocessing(example_path_tensor)
        example, label = example.numpy(), label.numpy()
        example, label = self.make_uniform_length_requiring_positive(
            example, label, required_length_multiple_base=self.length_multiple_base
        )
        return tf.convert_to_tensor(example, dtype=tf.float32), tf.convert_to_tensor(label, dtype=tf.float32)

    @abstractmethod
    def general_preprocessing(self, example_path_tensor: tf.Tensor) -> (tf.Tensor, tf.Tensor):
        """
        Loads and preprocesses the data.

        :param example_path_tensor: The tensor containing the path to the example to load.
        :return: The example and its corresponding label.
        """
        pass

    def make_uniform_length_requiring_positive(self, example: np.ndarray, label: np.ndarray,
                                               length: Union[int, None] = None,
                                               required_length_multiple_base: Union[int, None] = None
                                               ) -> (np.ndarray, np.ndarray):
        """
        Extracts a random segment from an example of the length specified. For examples with a positive label,
        the segment is required to include at least 1 positive time step. Examples shorter than the specified length
        will be repeated to fit the length.

        :param example: The example to extract a segment from.
        :param label: The label whose matching segment should be extracted.
        :param length: The length to make the example.
        :param required_length_multiple_base: An optional base which the length is rounded to.
        :return: The extracted segment and corresponding label.
        """
        if length is None:
            length = label.shape[0]
        if required_length_multiple_base is not None:
            length = self.round_to_base(length, base=required_length_multiple_base)
        if length == label.shape[0]:
            return example, label
        if label.shape[0] > length and any(label):
            valid_start_indexes = self.valid_start_indexes_for_segment_including_positive(label.astype(np.bool), length)
            start_index = np.random.choice(valid_start_indexes)
            end_index = start_index + length
            example = example[start_index:end_index]
            label = label[start_index:end_index]
        example_and_label = np.concatenate([example, np.expand_dims(label, axis=-1)], axis=1)
        example_and_label = self.make_uniform_length(example_and_label, length)
        extracted_example, extracted_label = example_and_label[:, :2], example_and_label[:, 2]
        return extracted_example, extracted_label

    @staticmethod
    def valid_start_indexes_for_segment_including_positive(boolean_array: np.bool, segment_length: int):
        """
        Gets all indexes of an array where a segment started at that index will include at least one True entry.
        In other words, an

        :param boolean_array: The array indicating which positions are positive.
        :param segment_length: The length of the segments to consider.
        :return: The valid start indexes.
        """
        for _ in range(segment_length - 1):
            boolean_array = boolean_array | np.roll(boolean_array, -1)
        assert boolean_array.shape[0] >= segment_length
        boolean_array = boolean_array[:-(segment_length - 1)]  # Segments extending beyond the array are invalid.
        return np.where(boolean_array)[0]

    @staticmethod
    def round_to_base(number: int, base: int) -> int:
        """
        Rounds a number to a specific base/multiple.

        :param number: The number to round.
        :param base: The base to round to.
        :return: The rounded number.
        """
        return base * round(number / base)
