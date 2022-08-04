#!/bin/bash

find /Users/admin/Library/Developer/Xcode/Archives/* -type d -maxdepth 0 -mtime +0 -exec rm -rf {} \;
