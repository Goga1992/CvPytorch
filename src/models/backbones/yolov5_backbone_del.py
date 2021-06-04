# !/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2021/1/8 16:31
# @Author : liumin
# @File : yolov5_backbone_del.py

import torch
import torch.nn as nn
# from ..modules.yolov5_modules import parse_yolov5_model
from CvPytorch.src.models.modules.yolov5_modules import parse_yolov5_model


class YOLOv5Backbone(nn.Module):
                # [from, number, module, args]
    model_cfg = [[-1, 1, 'Focus', [64, 3]],  # 0-P1/2
                 [-1, 1, 'Conv', [128, 3, 2]],  # 1-P2/4
                 [-1, 3, 'C3', [128]],
                 [-1, 1, 'Conv', [256, 3, 2]],  # 3-P3/8
                 [-1, 9, 'C3', [256]],
                 [-1, 1, 'Conv', [512, 3, 2]],  # 5-P4/16
                 [-1, 9, 'C3', [512]],
                 [-1, 1, 'Conv', [1024, 3, 2]],  # 7-P5/32
                 [-1, 1, 'SPP', [1024, [5, 9, 13]]],
                 [-1, 3, 'C3', [1024, False]]  # 9
                 ]
    def __init__(self, subtype='yolov5s', out_stages=[2,3,4], output_stride = 32, backbone_path=None, pretrained = False):
        super(YOLOv5Backbone, self).__init__()
        self.subtype = subtype
        self.out_stages = out_stages
        self.output_stride = output_stride
        self.backbone_path = backbone_path
        self.pretrained = pretrained
        #  num_outs = 18 # na * (nc + 5)  # number of outputs = anchors * (classes + 5)

        if self.subtype == 'yolov5s':
            depth_mul = 0.33  # model depth multiple
            width_mul = 0.50  # layer channel multiple
            backbone = parse_yolov5_model(self.model_cfg, depth_mul, width_mul)
            self.out_channels = [64, 128, 256, 512]
        elif self.subtype == 'yolov5m':
            depth_mul = 0.67  # model depth multiple
            width_mul = 0.75  # layer channel multiple
            backbone = parse_yolov5_model(self.model_cfg, depth_mul, width_mul)
            self.out_channels = [96, 192, 384, 768]
        elif self.subtype == 'yolov5l':
            depth_mul = 1.0  # model depth multiple
            width_mul = 1.0  # layer channel multiple
            backbone = parse_yolov5_model(self.model_cfg, depth_mul, width_mul)
            self.out_channels = [128, 256, 512, 1024]
        elif self.subtype == 'yolov5x':
            depth_mul = 1.33  # model depth multiple
            width_mul = 1.25  # layer channel multiple
            backbone = parse_yolov5_model(self.model_cfg, depth_mul, width_mul)
            self.out_channels = [160, 320, 640, 1280]
        else:
            raise NotImplementedError

        self.conv1 = nn.Sequential(list(backbone.children())[0])
        self.layer1 = nn.Sequential(*list(backbone.children())[1:3])
        self.layer2 = nn.Sequential(*list(backbone.children())[3:5])
        self.layer3 = nn.Sequential(*list(backbone.children())[5:7])
        self.layer4 = nn.Sequential(*list(backbone.children())[7:])

        self.init_weights()
        if self.pretrained:
            self.load_pretrained_weights()

    def init_weights(self):
        for m in self.modules():
            t = type(m)
            if t is nn.Conv2d:
                pass  # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif t is nn.BatchNorm2d:
                m.eps = 1e-3
                m.momentum = 0.03
            elif t in [nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6]:
                m.inplace = True

    def forward(self, x):
        x = self.conv1(x)
        output = []
        for i in range(1, 5):
            res_layer = getattr(self, 'layer{}'.format(i))
            x = res_layer(x)
            if i in self.out_stages:
                output.append(x)
        return tuple(output)


if __name__ == "__main__":
    model = YOLOv5Backbone('yolov5x')
    print(model)

    input = torch.randn(1, 3, 640, 640)
    out = model(input)
    for o in out:
        print(o.shape)