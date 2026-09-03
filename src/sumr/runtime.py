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
import re;
from sumdata import NA, dataset, dataset_names, read_rds, save_rds;
from sumplot import AesSpec, ColumnRef, PlotSpec, LayerSpec, to_chart_spec;
class RVector(list):
    def _bin(self,other,fn):
        right=list(other) if isinstance(other,(list,tuple,RVector)) else [other]; n=max(len(self),len(right)); return RVector(fn(self[i%len(self)],right[i%len(right)]) for i in range(n));
    def __add__(self,o): return self._bin(o,lambda a,b:a+b);
    def __sub__(self,o): return self._bin(o,lambda a,b:a-b);
    def __mul__(self,o): return self._bin(o,lambda a,b:a*b);
    def __truediv__(self,o): return self._bin(o,lambda a,b:a/b);
    def r_index(self,index):
        if isinstance(index,int): return self[index-1] if index>0 else RVector(v for i,v in enumerate(self,1) if i != -index);
        return RVector(self[i-1] for i in index if i>0);
def c(*values): return RVector(values);
def factor(values): return RVector(values);
def data(name=None, package=None):
    if package=="datasets" and name is None: return dataset_names(display=True);
    return dataset(name);
def readRDS(path): return read_rds(path);
def saveRDS(value,path): return save_rds(path,value);
def aes(**kwargs): return AesSpec(tuple((key,ColumnRef(value) if isinstance(value,str) else value) for key,value in kwargs.items()));
def ggplot(data_value=None,mapping=None): return PlotSpec(data_value,mapping or AesSpec());
def geom_bar(mapping=None,position="stack",stat="identity",**kwargs): return LayerSpec("bar",mapping or AesSpec(),stat=stat,position=position,params=tuple(kwargs.items()));
def geom_bar3d(mapping=None,position="stack",stat="identity",**kwargs): return LayerSpec("bar3d",mapping or AesSpec(),stat=stat,position=position,params=tuple(kwargs.items()));
def lower_chart(plot,layer): return to_chart_spec(plot.add(layer));
class Runtime:
    def __init__(self): self.env={"NA":NA,"c":c,"factor":factor,"data":data,"readRDS":readRDS,"saveRDS":saveRDS};
    def set(self,name,value): self.env[str(name)]=value; return value;
    def get(self,name): return self.env[str(name)];
