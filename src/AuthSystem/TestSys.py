#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sindre Wetjen.
# Distributed under a GPLv3 License.
# See top level directory for full license.
from AuthSys import AuthSys

if __name__ == '__main__':
    a = AuthSys('lol')
    a.recover_users()
    print(a.list_all_users())
