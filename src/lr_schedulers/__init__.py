# !/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/12/18 19:00
# @Author : liumin
# @File : __init__.py

import math
from torch.optim.lr_scheduler import StepLR, MultiStepLR, ExponentialLR, ReduceLROnPlateau, CosineAnnealingLR, CosineAnnealingWarmRestarts, LambdaLR
from src.lr_schedulers.poly_lr import PolyLR

__all__ = ['StepLR', 'MultiStepLR', 'ReduceLROnPlateau', 'CosineAnnealingLR', 'CosineAnnealingWarmRestarts','ExponentialLR', 'PolyLR']



'''
        schedule_cfg = copy.deepcopy(self.cfg.schedule.lr_schedule)
        name = schedule_cfg.pop('name')
        Scheduler = getattr(torch.optim.lr_scheduler, name)
        self.lr_scheduler = Scheduler(optimizer=self.optimizer, **schedule_cfg)
'''

def build_lr_scheduler(cfg, iters_per_epoch, optimizer):
    max_iters = cfg.N_MAX_EPOCHS * iters_per_epoch

    if cfg.LR_SCHEDULER.TYPE == "StepLR":
        lr_scheduler_ft = StepLR(
            optimizer, step_size=cfg.LR_SCHEDULER.STEP, gamma=cfg.LR_SCHEDULER.GAMMA or 0.1
        )
    elif cfg.LR_SCHEDULER.TYPE == "MultiStepLR":
        lr_scheduler_ft = MultiStepLR(
            optimizer, cfg.LR_SCHEDULER.MILESTONES, gamma=cfg.LR_SCHEDULER.GAMMA or 0.1
        )
    elif cfg.LR_SCHEDULER.TYPE == "ExponentialLR":
        lr_scheduler_ft = ExponentialLR(
            optimizer, gamma=cfg.LR_SCHEDULER.GAMMA or 0.1
        )
    elif cfg.LR_SCHEDULER.TYPE == "ReduceLROnPlateau":
        lr_scheduler_ft = ReduceLROnPlateau(
            optimizer, factor=cfg.LR_SCHEDULER.GAMMA or 0.1, patience=cfg.LR_SCHEDULER.STEP
        )
    elif cfg.LR_SCHEDULER.TYPE == "CosineAnnealingLR":
        """
            \eta_t = \eta_{min} + \frac{1}{2}(\eta_{max} - \eta_{min})\left(1 + \cos\left(\frac{T_{cur}}{T_{max}}\pi\right)\right)
        """
        # copy from https://github.com/ultralytics/yolov5/blob/master/train.py
        # Scheduler https://arxiv.org/pdf/1812.01187.pdf
        # https://pytorch.org/docs/stable/_modules/torch/optim/lr_scheduler.html#OneCycleLR
        lf = lambda x: (((1 + math.cos(x * math.pi / cfg.N_MAX_EPOCHS)) / 2) ** 1.0) * 0.8 + 0.2  # cosine
        lr_scheduler_ft = LambdaLR(optimizer, lr_lambda=lf)

        # lr_scheduler_ft = CosineAnnealingLR(optimizer, T_max=cfg.N_MAX_EPOCHS, eta_min=0.02)

    elif cfg.LR_SCHEDULER.TYPE == "CosineAnnealingWarmRestarts":
        lr_scheduler_ft = CosineAnnealingWarmRestarts(optimizer, T_0=cfg.N_MAX_EPOCHS, T_mult=1, eta_min=0.02)
        # torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0, T_mult=1, eta_min=0.02, last_epoch=-1)
    elif cfg.LR_SCHEDULER.TYPE == "PolyLR":
        lr_scheduler_ft = PolyLR(optimizer, max_iters=max_iters, power=cfg.LR_SCHEDULER.POWER, min_lr=cfg.LR_SCHEDULER.MIN_LR if cfg.LR_SCHEDULER.MIN_LR is not None else 1e-6)
        # PolyLR(optimizer, max_iters, power=0.9, last_epoch=-1, min_lr=1e-6)
    else:
        raise ValueError("Unsupported lr_scheduler type: {}".format(cfg.LR_SCHEDULER.TYPE))

    return lr_scheduler_ft