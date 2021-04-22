# !/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/12/11 14:51
# @Author : liumin
# @File : nanodet-main.py

import torch
import torch.nn as nn
from .ext.nanodet.nanodet.model.backbone import ShuffleNetV2
from .ext.nanodet.nanodet.model.fpn import PAN
from .ext.nanodet.nanodet.model.head import NanoDetHead


class NANODET(nn.Module):
    def __init__(self, dictionary=None):
        super(NANODET, self).__init__()
        self.dictionary = dictionary
        self.dummy_input = torch.zeros(1, 3, 800, 600)

        self.num_classes = len(self.dictionary)
        self._category = [v for d in self.dictionary for v in d.keys()]
        self.weight = [d[v] for d in self.dictionary for v in d.keys() if v in self._category]

        backbone_cfg={'model_size': '1.0x','out_stages': [2, 3, 4],'activation': 'LeakyReLU'}
        fpn_cfg = {'in_channels': [116, 232, 464],'out_channels': 96,'start_level': 0,'num_outs': 3}
        head_cfg = {'num_classes': 80,'input_channel': 96,'feat_channels': 96,'stacked_convs': 2,'share_cls_reg': True,
                    'octave_base_scale': 5,'scales_per_octave': 1,'strides': [8, 16, 32],'reg_max': 7,
                    'loss':
                        {'loss_qfl':
                             {'name': 'QualityFocalLoss','use_sigmoid': True,'beta': 2.0,'loss_weight': 1.0},
                        'loss_dfl':{'name': 'DistributionFocalLoss','loss_weight': 0.25},
                        'loss_bbox':{'name': 'GIoULoss','loss_weight': 2.0}
                         }
                    }
        self.backbone = ShuffleNetV2(**backbone_cfg)
        self.fpn = PAN(**fpn_cfg)
        self.head = NanoDetHead(**head_cfg)

    def forward(self, imgs, targets=None, mode='infer', **kwargs):
        '''
        inputs
        [training] list  batch_imgs,batch_boxes,batch_classes
        [inference] img
        '''

        if mode == 'infer':
            '''
                for inference mode, img should preprocessed before feeding in net 
            '''

            return
        else:
            losses = {}
            x = self.backbone(imgs)
            x = self.fpn(x)
            x = self.head(x)
            preds = tuple(x)

            loss, loss_states = self.head.loss(preds, targets)

            losses['qfl_loss'] = loss_states['loss_qfl']
            losses['bbox_loss'] = loss_states['loss_bbox']
            losses['dfl_loss'] = loss_states['loss_dfl']
            losses['loss'] = loss.mean()

            if mode == 'val':
                dets = self.head.post_process(preds, targets)
                return losses, dets
            else:
                return losses