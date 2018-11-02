"""
Retrain the YOLO model for your own dataset.
"""
import json

from keras.optimizers import Adam
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

from backend.road_damages.yolo_bad.dataset.data_generator import BatchGenerator
from backend.road_damages.yolo_bad.training.model_initialization import get_anchors, create_model, create_tiny_model


def _main():
    config_path = r'C:\Users\Martyna\PycharmProjects\roadDamageDetectionApp\backend\road_damages\yolo3\training\configs\training_config.json'
    model_data_path = r'C:\Users\Martyna\PycharmProjects\roadDamageDetectionApp\backend\road_damages\yolo3\model\model_data'
    with open(config_path) as config_buffer:
        config = json.loads(config_buffer.read())

    train_path = config['train']['train_real']
    test_path = config['valid']['valid_real_folder']

    log_dir = 'logs/000/'
    class_names = config['model']['labels']
    num_classes = len(class_names)
    anchors_path = model_data_path + r'\damages_tiny_anchors.txt'
    anchors = get_anchors(anchors_path)
    input_size = config['model']['input_size']
    input_shape = (input_size, input_size)  # multiple of 32, hw

    is_tiny_version = len(anchors) == 6  # default setting
    if is_tiny_version:
        model = create_tiny_model(input_shape, anchors, num_classes, freeze_body=2,
                                  weights_path=model_data_path + r'\tiny_yolo_weights.h5')
    else:
        model = create_model(input_shape, anchors, num_classes, freeze_body=2,
                             weights_path=model_data_path + r'\yolo_weights.h5')

    # prepare dataset

    batch_size = config['train']['frozen_train']['batch_size']

    with open(train_path) as f:
        train_set = f.readlines()
    with open(test_path) as f:
        test_set = f.readlines()
    num_val = len(test_set)
    num_train = len(train_set)

    training_generator = BatchGenerator(batch_size, input_shape, anchors,
                                        num_classes, train_set)
    real_validation_generator = BatchGenerator(batch_size, input_shape, anchors, num_classes,
                                               test_set, is_training=False)

    logging = TensorBoard(log_dir=log_dir)
    checkpoint = ModelCheckpoint(log_dir + 'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5',
                                 monitor='val_loss', save_weights_only=True, save_best_only=True,
                                 period=3)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, verbose=1)
    early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1)

    # Train with frozen layers first, to get a stable loss.
    # Adjust num epochs to your dataset. This step is enough to obtain a not bad model.
    learning_rate = config['train']['frozen_train']['learning_rate']
    epochs = config['train']['frozen_train']['nb_epoch']
    initial_epoch = config['train']['frozen_train']['initial_epoch']
    if True:
        model.compile(optimizer=Adam(lr=learning_rate), loss={# use custom yolo_loss Lambda layer.
            'yolo_loss': lambda y_true, y_pred: y_pred})

        print(
            'Train on {} samples, val on {} samples, with batch size {}.'.format(num_train, num_val,
                                                                                 batch_size))
        model.fit_generator(training_generator.data_generator_wrapper(),
                            steps_per_epoch=max(1, num_train // batch_size),
                            validation_data=real_validation_generator.data_generator_wrapper(),
                            validation_steps=max(1, num_val // batch_size),
                            epochs=epochs,
                            initial_epoch=initial_epoch,
                            callbacks=[logging, checkpoint])
        model.save_weights(log_dir + 'trained_weights_stage_1.h5')

    # Unfreeze and continue training, to fine-tune.
    # Train longer if the result is not good.
    learning_rate = config['train']['fine_tune_train']['learning_rate']
    epochs = config['train']['fine_tune_train']['nb_epoch']
    initial_epoch = config['train']['fine_tune_train']['initial_epoch']
    batch_size = config['train']['fine_tune_train']['batch_size']

    training_generator = BatchGenerator(batch_size, input_shape, anchors,
                                        num_classes, train_set)
    real_validation_generator = BatchGenerator(batch_size, input_shape, anchors, num_classes,
                                               test_set, is_training=False)

    if True:
        for i in range(len(model.layers)):
            model.layers[i].trainable = True
        model.compile(optimizer=Adam(lr=learning_rate), loss={
            'yolo_loss': lambda y_true, y_pred: y_pred})  # recompile to apply the change
        print('Unfreeze all of the layers.')
        print(
            'Train on {} samples, val on {} samples, with batch size {}.'.format(num_train, num_val,
                                                                                 batch_size))
        model.fit_generator(training_generator.data_generator_wrapper(),
                            steps_per_epoch=max(1, num_train // batch_size),
                            validation_data=real_validation_generator.data_generator_wrapper(),
                            validation_steps=max(1, num_val // batch_size),
                            epochs=epochs,
                            initial_epoch=initial_epoch,
                            callbacks=[logging, checkpoint, reduce_lr,
                                       early_stopping])
        model.save_weights(log_dir + 'trained_weights_final.h5')

    # Further training if needed.


if __name__ == '__main__':
    _main()
