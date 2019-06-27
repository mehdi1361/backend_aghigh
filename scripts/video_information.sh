#!/usr/bin/env bash

source="${1}"

ffprobe -v quiet -print_format json -show_format ${source}
