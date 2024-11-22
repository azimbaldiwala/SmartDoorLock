from tensorflow.keras.models import model_from_json
import tensorflow as tf

# Load the model architecture from a JSON file
with open('antispoofing_models/antispoofing_model.json', 'r') as json_file:
    model_json = json_file.read()

model = model_from_json(model_json)

# Load weights into the model
model.load_weights('antispoofing_models/antispoofing_model.h5')

# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the .tflite model
with open("antispoofing_model.tflite", "wb") as f:
    f.write(tflite_model)
