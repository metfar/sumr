#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
from sumr import *;

def test_recycling(): assert list(RVector([1,2,3])+RVector([10]))==[11,12,13];
def test_one_based_index(): assert RVector([10,20]).r_index(1)==10;
def test_data_mtcars(): assert len(data("mtcars"))==32;
def test_data_catalog(): assert len(data(package="datasets"))==108;
def test_bare_aes_is_column(): assert isinstance(aes(x="mpg").get("x"),ColumnRef);
def test_execute_subset(): out,rt=execute("a <- c(1,2)\nprint(a)"); assert list(out[0])==[1,2];
