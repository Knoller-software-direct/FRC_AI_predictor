import numpy as np
from tensorflow import keras


training_data_features = np.load("training_data_features.npy")
training_data_labels = np.load("training_data_labels.npy")
testing_data_features = np.load("training_data_features.npy")
testing_data_labels = np.load("training_data_labels.npy")

model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(training_data_features.shape[1],)), # Input layer
    keras.layers.Dense(32, activation='relu'),  # Hidden layer
    keras.layers.Dense(16, activation='relu'),  # Hidden layer
    keras.layers.Dense(1, activation='sigmoid')  # Output layer (binary classification)
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.summary()
early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history = model.fit(training_data_features, training_data_labels, epochs=100, batch_size=32,
                    validation_data=(testing_data_features, testing_data_labels), callbacks=[early_stop])

test_loss, test_acc = model.evaluate(testing_data_features, testing_data_labels)
print(f"Test Accuracy: {test_acc:.4f}")

model.save("frc_match_predictor_v5.keras")
