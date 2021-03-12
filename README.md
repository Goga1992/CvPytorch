CvPytorch

CvPytorch is an open source COMPUTER VISION toolbox based on PyTorch.

## Dependencies

- Python 3.8
- PyTorch 1.6.0
- Torchvision 0.7.0
- tensorboardX 2.1 

## Models 

## Image Classification
- [x] (**VGG**) VGG: Very Deep Convolutional Networks for Large-Scale Image Recognition

- [x] (**ResNet**) ResNet: Deep Residual Learning for Image Recognition

- [x] (**DenseNet**) DenseNet: Densely Connected Convolutional Networks

- [x] (**ShuffleNet**) ShuffleNet: An Extremely Efficient Convolutional Neural Network for Mobile Devices

- [x] (**ShuffleNet V2**) ShuffleNet V2: Practical Guidelines for Ecient CNN Architecture Design

## Object Detection
- [x] (**SSD**) SSD: Single Shot MultiBox Detector

- [ ] (**Faster R-CNN**) Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks

- [ ] (**YOLOv3**) YOLOv3: An Incremental Improvement
- [ ] (**YOLOv5**) 

- [ ] (**FPN**) FPN: Feature Pyramid Networks for Object Detection

- [ ] (**FCOS**) FCOS: Fully Convolutional One-Stage Object Detection

## Semantic Segmentation
- [ ] (**FCN**) Fully Convolutional Networks for Semantic Segmentation 

- [x] (**Deeplab V3+**) Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation

- [x] (**PSPNet**) Pyramid Scene Parsing Network

- [x] (**ENet**) A Deep Neural Network Architecture for Real-Time Semantic Segmentation

- [x] (**U-Net**) Convolutional Networks for Biomedical Image Segmentation

- [x] (**SegNet**) A Deep ConvolutionalEncoder-Decoder Architecture for ImageSegmentation

## Instance Segmentation
- [x] (**Mask-RCNN**) Mask-RCNN

### Datasets

- **Pascal VOC:** For pascal voc, first download the [original dataset](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar), after extracting the files we'll end up with `VOCtrainval_11-May-2012/VOCdevkit/VOC2012` containing, the image sets, the XML annotation for both object detection and segmentation, and JPEG images.\
The second step is to augment the dataset using the additionnal annotations provided by [Semantic Contours from Inverse Detectors](http://home.bharathh.info/pubs/pdfs/BharathICCV2011.pdf). First download the image sets (`train_aug`, `trainval_aug`, `val_aug` and `test_aug`) from this link: [Aug ImageSets](https://www.dropbox.com/sh/jicjri7hptkcu6i/AACHszvCyYQfINpRI1m5cNyta?dl=0&lst=), and  add them the rest of the segmentation sets in `/VOCtrainval_11-May-2012/VOCdevkit/VOC2012/ImageSets/Segmentation`, and then download new annotations [SegmentationClassAug](https://www.dropbox.com/s/oeu149j8qtbs1x0/SegmentationClassAug.zip?dl=0) and add them to the path `VOCtrainval_11-May-2012/VOCdevkit/VOC2012`, now we're set, for training use the path to `VOCtrainval_11-May-2012`

- **CityScapes:** First download the images and the annotations (there is two types of annotations, Fine `gtFine_trainvaltest.zip` and Coarse `gtCoarse.zip` annotations, and the images `leftImg8bit_trainvaltest.zip`) from the official website [cityscapes-dataset.com](https://www.cityscapes-dataset.com/downloads/), extract all of them in the same folder, and use the location of this folder in `config.json` for training.

- **ADE20K:** For ADE20K, simply download the images and their annotations for training and validation from [sceneparsing.csail.mit.edu](http://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip), and for the rest visit the [website](http://sceneparsing.csail.mit.edu/).


- **COCO Stuff:** For COCO, there is two partitions, CocoStuff10k with only 10k that are used for training the evaluation, note that this dataset is outdated, can be used for small scale testing and training, and can be downloaded [here](https://github.com/nightrome/cocostuff10k). For the official dataset with all of the training 164k examples, it can be downloaded from the official [website](http://cocodataset.org/#download).\
Note that when using COCO dataset, 164k version is used per default, if 10k is prefered, this needs to be specified with an additionnal parameter `partition = 'CocoStuff164k'` in the config file with the corresponding path.

### Install

#### 



### Training

For this example, we will use [COCO](https://github.com/ultralytics/yolov5/blob/master/data/get_coco2017.sh) dataset with `yolov5l.yaml` . Feel free to use your own custom dataset and configurations.

#### Single GPU:

```bash
$ python trainer.py --setting 'conf/hymenoptera.yml'
```

#### Multiple GPUs:

```bash
$ python -m torch.distributed.launch --nproc_per_node=2 trainer.py --setting 'conf/hymenoptera.yml'
```

### Inference



### TODO
- [x] Train Custom Data

- [x] Multi-GPU Training

- [x] Mixed Precision Training

- [x] Warm-Up

- [ ] Model Pruning/Sparsity

- [ ] Quantization

- [ ] TensorRT Deployment

- [ ] ONNX and TorchScript Export

- [ ] Class Activation Mapping (CAM)

- [ ] Test-Time Augmentation (TTA)


## License

MIT License

Copyright (c) 2020 min liu

  