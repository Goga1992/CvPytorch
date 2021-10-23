# !/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2021/3/10 10:00
# @Author : liumin
# @File : Efficientnet.py

'''https://github.com/narumiruna/efficientnet-pytorch/blob/master/efficientnet/models/efficientnet.py'''

import math
import torch
import torch.nn as nn

'''
    EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks
    https://arxiv.org/pdf/1905.11946.pdf
'''

model_urls = {
    'efficientnet_b0': 'https://www.dropbox.com/s/9wigibun8n260qm/efficientnet-b0-4cfa50.pth?dl=1',
    'efficientnet_b1': 'https://www.dropbox.com/s/6745ear79b1ltkh/efficientnet-b1-ef6aa7.pth?dl=1',
    'efficientnet_b2': 'https://www.dropbox.com/s/0dhtv1t5wkjg0iy/efficientnet-b2-7c98aa.pth?dl=1',
    'efficientnet_b3': 'https://www.dropbox.com/s/5uqok5gd33fom5p/efficientnet-b3-bdc7f4.pth?dl=1',
    'efficientnet_b4': 'https://www.dropbox.com/s/y2nqt750lixs8kc/efficientnet-b4-3e4967.pth?dl=1',
    'efficientnet_b5': 'https://www.dropbox.com/s/qxonlu3q02v9i47/efficientnet-b5-4c7978.pth?dl=1',
    'efficientnet_b6': None,
    'efficientnet_b7': None,
}


class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)


def ConvBNAct(in_channels,out_channels,kernel_size=3, stride=1,groups=1):
    return nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=kernel_size//2, groups=groups),
            nn.BatchNorm2d(out_channels),
            Swish()
        )


def Conv1x1BNAct(in_channels,out_channels):
    return nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1),
            nn.BatchNorm2d(out_channels),
            Swish()
        )

def Conv1x1BN(in_channels,out_channels):
    return nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1),
            nn.BatchNorm2d(out_channels)
        )

def Conv1(in_planes, places, stride=2):
    return nn.Sequential(
        nn.Conv2d(in_channels=in_planes,out_channels=places,kernel_size=7,stride=stride,padding=3, bias=False),
        nn.BatchNorm2d(places),
        Swish(),
        nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
    )

class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.shape[0], -1)


class SEBlock(nn.Module):
    def __init__(self, channels, ratio=16):
        super().__init__()
        mid_channels = channels // ratio
        self.se = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, mid_channels, kernel_size=1, stride=1, padding=0, bias=True),
            Swish(),
            nn.Conv2d(mid_channels, channels, kernel_size=1, stride=1, padding=0, bias=True),
        )

    def forward(self, x):
        return x * torch.sigmoid(self.se(x))


class MBConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, expansion_factor=6):
        super(MBConvBlock, self).__init__()
        self.stride = stride
        self.expansion_factor = expansion_factor
        mid_channels = (in_channels * expansion_factor)

        self.bottleneck = nn.Sequential(
            Conv1x1BNAct(in_channels, mid_channels),
            ConvBNAct(mid_channels, mid_channels, kernel_size, stride, groups=mid_channels),
            SEBlock(mid_channels),
            Conv1x1BN(mid_channels, out_channels)
        )

        if self.stride == 1:
            self.shortcut = Conv1x1BN(in_channels, out_channels)

    def forward(self, x):
        out = self.bottleneck(x)
        out = (out + self.shortcut(x)) if self.stride==1 else out
        return out


class EfficientNet(nn.Module):
    params = {
        'efficientnet_b0': (1.0, 1.0, 224, 0.2),
        'efficientnet_b1': (1.0, 1.1, 240, 0.2),
        'efficientnet_b2': (1.1, 1.2, 260, 0.3),
        'efficientnet_b3': (1.2, 1.4, 300, 0.3),
        'efficientnet_b4': (1.4, 1.8, 380, 0.4),
        'efficientnet_b5': (1.6, 2.2, 456, 0.4),
        'efficientnet_b6': (1.8, 2.6, 528, 0.5),
        'efficientnet_b7': (2.0, 3.1, 600, 0.5),
    }
    def __init__(self, subtype='efficientnet_b0', out_stages=[3, 5, 7], output_stride=16, classifier=False,
                     backbone_path=None, pretrained=False):

        super(EfficientNet, self).__init__()
        self.subtype = subtype
        self.out_stages = out_stages
        self.output_stride = output_stride  # 8, 16, 32
        self.classifier = classifier
        self.backbone_path = backbone_path
        self.pretrained = pretrained

        self.width_coeff = self.params[subtype][0]
        self.depth_coeff = self.params[subtype][1]
        self.dropout_rate = self.params[subtype][3]
        self.depth_div = 8

        self.conv1 = ConvBNAct(3, self._calculate_width(32), kernel_size=3, stride=2)
        self.stage1 = self.make_layer(self._calculate_width(32), self._calculate_width(16), kernel_size=3, stride=1, block=self._calculate_depth(1))
        self.stage2 = self.make_layer(self._calculate_width(16), self._calculate_width(24), kernel_size=3, stride=2, block=self._calculate_depth(2))
        self.stage3 = self.make_layer(self._calculate_width(24), self._calculate_width(40), kernel_size=5, stride=2, block=self._calculate_depth(2))
        self.stage4 = self.make_layer(self._calculate_width(40), self._calculate_width(80), kernel_size=3, stride=2, block=self._calculate_depth(3))
        self.stage5 = self.make_layer(self._calculate_width(80), self._calculate_width(112), kernel_size=5, stride=1, block=self._calculate_depth(3))
        self.stage6 = self.make_layer(self._calculate_width(112), self._calculate_width(192), kernel_size=5, stride=2, block=self._calculate_depth(4))
        self.stage7 = self.make_layer(self._calculate_width(192), self._calculate_width(320), kernel_size=3, stride=1, block=self._calculate_depth(1))

        self.out_channels = [self._calculate_width(ch) for ch in [32, 16, 24, 40, 80, 112, 192, 320]]
        self.out_channels = [self.out_channels[ost] for ost in self.out_stages]

        if self.classifier:
            self.classifier = nn.Sequential(
                Conv1x1BNAct(320, 1280),
                nn.AdaptiveAvgPool2d(1),
                nn.Dropout2d(0.2),
                Flatten(),
                nn.Linear(1280, 1000)
            )
            self.out_channels = [1000]

        if self.pretrained:
            self.load_pretrained_weights()
        else:
            self.init_weights()

    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out")
            elif isinstance(m, nn.Linear):
                init_range = 1.0 / math.sqrt(m.weight.shape[1])
                nn.init.uniform_(m.weight, -init_range, init_range)

    def _calculate_width(self, x):
        x *= self.width_coeff
        new_x = max(self.depth_div, int(x + self.depth_div / 2) // self.depth_div * self.depth_div)
        if new_x < 0.9 * x:
            new_x += self.depth_div
        return int(new_x)

    def _calculate_depth(self, x):
        return int(math.ceil(x * self.depth_coeff))

    def make_layer(self, in_places, places, kernel_size, stride, block):
        layers = []
        layers.append(MBConvBlock(in_places, places, kernel_size, stride))
        for i in range(1, block):
            layers.append(MBConvBlock(places, places, kernel_size))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        output = []
        for i in range(1, 8):
            stage = getattr(self, 'stage{}'.format(i))
            x = stage(x)
            if i in self.out_stages and not self.classifier:
                output.append(x)
        if self.classifier:
            x = self.classifier(x)
            return x
        return output if len(self.out_stages) > 1 else output[0]

    def freeze_bn(self):
        for layer in self.modules():
            if isinstance(layer, nn.BatchNorm2d):
                layer.eval()


if __name__=='__main__':
    model = EfficientNet('efficientnet_b0')
    print(model)

    input = torch.randn(1, 3, 224, 224)
    out = model(input)
    print(out.shape)