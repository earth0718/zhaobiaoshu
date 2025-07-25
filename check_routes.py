#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from main import app

print('Available routes:')
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        print(f'{route.methods} {route.path}')
    elif hasattr(route, 'path'):
        print(f'Static: {route.path}')