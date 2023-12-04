#!/bin/sh
echo -ne '\033c\033]0;handscanner\a'
base_path="$(dirname "$(realpath "$0")")"
"$base_path/handscanner.x86_64" "$@"
