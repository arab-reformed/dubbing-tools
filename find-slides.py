#!/usr/bin/env python3

import cv2
import fire
from dubbing_tools import *
import sys
import os
# from skimage.measure import compare_ssim as ssim
from skimage.metrics import structural_similarity as ssim
import json


def write_json(output_path: str, stills: list):
    with open(os.path.join(output_path, 'still-frames.json'), 'w') as file:
        json.dump({'stills': stills}, file, indent=2)


def cmd(video_file: str, output_path: str, debug: bool = False, skip: int = 20, similarity: float = 0.95):

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    capture = cv2.VideoCapture(video_file)

    frame_num = 0
    last_frame = None
    frame_start = None
    frame_end = None
    previous = {}
    current = {}
    stills = []
    write_json(output_path, stills)

    while (True):

        success, frame = capture.read()

        if not success:
            break

        current[frame_num] = frame

        if frame_num % skip == 0:
            # print(f'Frame: {frame_num}', file=sys.stderr)
            try:
                if last_frame is None:
                    last_frame = frame

                elif ssim(frame, last_frame, multichannel=True) > similarity:  #, gaussian_weights=True, win_size=None, sigma=1.5, use_sample_covariance=False) > 0.7:
                    if frame_start is None:
                        frame_start = frame_num
                        for n in previous:
                            if ssim(frame, previous[n], multichannel=True) > similarity:
                                frame_start = n
                                break
                        stills.append({
                            'frame_start': frame_start,
                            'frame_end': frame_start,
                        })

                    frame_end = frame_num
                    stills[-1]['frame_end'] = frame_end

                else:
                    if frame_start is not None and frame_end - frame_start >= skip:
                        for n in current:
                            if ssim(last_frame, current[n], multichannel=True) > similarity:
                                frame_end = n
                            else:
                                break

                        stills[-1]['frame_end'] = frame_end
                        stills[-1]['image_file'] = f'slide-{str(len(stills)).rjust(3, "0")}.jpg'
                        cv2.imwrite(os.path.join(output_path, stills[-1]['image_file']), last_frame)
                        write_json(output_path, stills)

                        frame_start = None
                        frame_end = None

            except Exception as exc:
                print(f'Frame number: {frame_num}')
                raise exc

            last_frame = frame
            previous = current
            current = {}

        frame_num += 1

        if debug and frame_num % 300 == 0:
            print(f'Frame: {frame_num}', file=sys.stderr)

    capture.release()


if __name__ == "__main__":
    fire.Fire(cmd)

