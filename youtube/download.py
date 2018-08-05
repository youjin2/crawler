# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import os

import time

from collections import namedtuple

import tqdm

import argparse
from util import ExtractVideoList, DownloadSoundFile


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='channelURL', type=str)
    parsed = parser.parse_args()

    return parsed


if __name__ == '__main__':
    parsed = parseArgs()
    url = parsed.channelURL
    print(url)


