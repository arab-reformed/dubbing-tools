#!/usr/bin/env python3

import cv2
import fire
from dubbing_tools import *
import sys
import os
# from skimage.measure import compare_ssim as ssim
from skimage.metrics import structural_similarity as ssim


def cmd(video_file: str, output_path: str, debug: bool = False, exact: bool = False):
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    capture = cv2.VideoCapture(video_file)
    
    frame_num = 0
    last_frame = None
    frame_start = None
    frame_end = None

    while (True):

        success, frame = capture.read()

        if not success:
            break

        if frame_num % 20 == 0:
            # print(f'Frame: {frame_num}', file=sys.stderr)
            try:
                if last_frame is None:
                    last_frame = frame

                elif ssim(frame, last_frame, multichannel=True) > 0.90:  #, gaussian_weights=True, win_size=None, sigma=1.5, use_sample_covariance=False) > 0.7:
                    if frame_start is None:
                        frame_start = frame_num
                    frame_end = frame_num
                
                else:
                    if frame_start is not None and frame_end - frame_start >= 20:
                        cv2.imwrite(f'{output_path}/{frame_start}-{frame_end}.jpg', last_frame)
                        frame_start = None
                        frame_end = None

            except Exception as exc:
                print(f'Frame number: {frame_num}')
                raise exc

            last_frame = frame

        frame_num += 1

        if debug and frame_num % 300 == 0:
            print(f'Frame: {frame_num}', file=sys.stderr)

    capture.release()


if __name__ == "__main__":
    fire.Fire(cmd)

