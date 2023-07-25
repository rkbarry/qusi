from qusi.infer_session import InferSession
from qusi.light_curve_dataset import LightCurveDataset, LimitedIterableDataset
from qusi.single_dense_layer_model import SingleDenseLayerBinaryClassificationModel
from qusi.toy_light_curve_collection import toy_flat_light_curve_collection, toy_sine_wave_light_curve_collection

light_curve_dataset = LimitedIterableDataset.new(
    LightCurveDataset.new(standard_light_curve_collections=[toy_flat_light_curve_collection,
                                                            toy_sine_wave_light_curve_collection]),
    limit=1000
)
model = SingleDenseLayerBinaryClassificationModel(input_size=100)
infer_session = InferSession.new(infer_datasets=[light_curve_dataset], model=model, batch_size=103)
predictions = infer_session.run()
print(predictions)
