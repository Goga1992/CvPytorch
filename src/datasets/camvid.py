# !/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/10/9 15:34
# @Author : liumin
# @File : camvid.py
import os
import cv2
import torch
from PIL import Image
from glob2 import glob
import numpy as np
import random

from PIL import Image, ImageOps, ImageFilter
from torch.utils.data import Dataset
from torchvision import transforms as transformsT
from ..utils import palette
from torchvision import transforms as tf
from .transforms import custom_transforms as ctf

data_transforms = {
    'train': tf.Compose([
        ctf.Resize((512,512)),
        ctf.RandomHorizontalFlip(p=0.5),
        ctf.RandomTranslation(2),
        ctf.ToTensor(),
        # ctf.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ]),

    'val': tf.Compose([
        ctf.Resize((512, 512)),
        ctf.ToTensor(),
        # ctf.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ]),

    'infer': tf.Compose([
        ctf.Resize((512, 512)),
        ctf.ToTensor(),
        # ctf.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])
}

class CamvidSegmentation(Dataset):
    def __init__(self, data_cfg, dictionary=None, transform=None, target_transform=None, stage='train'):
        self.data_cfg = data_cfg
        self.dictionary = dictionary
        self.transform = data_transforms[stage]
        self.target_transform = target_transform
        self.stage = stage

        self.num_classes = len(self.dictionary)

        self._imgs = list()
        self._targets = list()
        if self.stage == 'infer':
            if data_cfg.INDICES is not None:
                with open(data_cfg.INDICES, 'r') as fd:
                    self._imgs.extend([os.path.join(data_cfg.IMG_DIR, line.strip()) for line in fd])
            else:
                for root, fnames, _ in sorted(os.walk(data_cfg.IMG_DIR)):
                    for fname in sorted(fnames):
                        self._imgs.extend(glob(os.path.join(root, fname, data_cfg.IMG_SUFFIX)))

            if len(self._imgs) == 0:
                raise RuntimeError(
                    "Found 0 images in subfolders of: " + data_cfg.IMG_DIR if data_cfg.INDICES is not None else data_cfg.INDICES + "\n")
        else:
            if data_cfg.INDICES is not None:
                for line in open(data_cfg.INDICES):
                    imgpath, labelpath = line.strip().split(' ')
                    self._imgs.append(os.path.join(data_cfg.IMG_DIR, imgpath))
                    self._targets.append(os.path.join(data_cfg.LABELS.SEG_DIR, labelpath))
            else:
                self._imgs = glob(os.path.join(data_cfg.IMG_DIR, 'leftImg8bit', self.stage, '*', data_cfg.IMG_SUFFIX))
                self._targets = glob(
                    os.path.join(data_cfg.LABELS.SEG_DIR, 'gtFine', self.stage, '*', data_cfg.LABELS.SEG_SUFFIX))

            assert len(self._imgs) == len(self._targets), 'len(self._imgs) should be equals to len(self._targets)'
            assert len(self._imgs) > 0, 'Found 0 images in the specified location, pls check it!'

    def __getitem__(self, idx):
        if self.stage == 'infer':
            _img = Image.open(self._imgs[idx]).convert('RGB')
            img_id = os.path.splitext(os.path.basename(self._imgs[idx]))[0]
            sample = {'image': _img, 'mask': None}
            return self.transform(sample), img_id
        else:
            _img, _target = Image.open(self._imgs[idx]).convert('RGB'), Image.open(self._targets[idx]).convert('P')
            sample = {'image': _img, 'target': _target}
            return self.transform(sample)

    def __len__(self):
        return len(self._imgs)