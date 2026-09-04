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
import subprocess;
from dataclasses import dataclass;
from sumdata import NA, dataset, dataset_names, read_rds, save_rds;
from .screen import clear_layer, cols, configure_graphics, cursor, gcolors, gheight, gprint, gprintf, gwidth, rows, sort_layers;
from sumplot import AesSpec, ColumnRef, PlotSpec, after_stat as plot_after_stat, geom_bar as plot_geom_bar, geom_bar3d as plot_geom_bar3d, geom_histogram as plot_geom_histogram, ggplot as plot_ggplot, ggsave as plot_ggsave, show_plot, to_chart_spec;

@dataclass(frozen=True)
class RSymbol: name: str;

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
def data(name=None,package=None):
    if package=="datasets" and name is None: return dataset_names(display=True);
    return dataset(name);
def readRDS(path): return read_rds(path);
def saveRDS(value,path): return save_rds(path,value);
def after_stat(name): return plot_after_stat(name.name if isinstance(name,RSymbol) else name);
def aes(*args,**kwargs):
    mappings={};
    if len(args)>2: raise TypeError("aes() accepts at most x and y positional aesthetics");
    if len(args)>=1: mappings["x"]=args[0];
    if len(args)>=2: mappings["y"]=args[1];
    mappings.update(kwargs); normalized=[];
    for key,value in mappings.items():
        if isinstance(value,RSymbol): value=ColumnRef(value.name);
        elif isinstance(value,str): value=ColumnRef(value);
        normalized.append((key,value));
    return AesSpec(tuple(normalized));
def ggplot(data_value=None,mapping=None): return plot_ggplot(data_value,mapping);
def geom_bar(mapping=None,position="stack",stat="identity",**kwargs): return plot_geom_bar(mapping,position=position,stat=stat,**kwargs);
def geom_bar3d(mapping=None,position="stack",stat="identity",**kwargs): return plot_geom_bar3d(mapping,position=position,stat=stat,**kwargs);
def geom_histogram(mapping=None,binwidth=None,bins=None,**kwargs): return plot_geom_histogram(mapping,binwidth=binwidth,bins=bins,**kwargs);
def ggsave(filename,plot,width=8,height=6,dpi=100,**kwargs): return plot_ggsave(filename,plot,width=width,height=height,dpi=dpi,**kwargs);
def print_value(value):
    if isinstance(value,PlotSpec): show_plot(value,block=False); return value;
    return value;
def system2(command,args=None,stdout=None,stderr=None,wait=True):
    argv=[str(command)];
    if args is not None:
        if isinstance(args,(list,tuple,RVector)): argv.extend(str(item) for item in args);
        else: argv.append(str(args));
    out=subprocess.DEVNULL if stdout is False else None; err=subprocess.DEVNULL if stderr is False else None;
    if wait: return subprocess.run(argv,stdout=out,stderr=err,check=False).returncode;
    subprocess.Popen(argv,stdout=out,stderr=err,start_new_session=True); return 0;
def lower_chart(plot,layer): return to_chart_spec(plot.add(layer));

class Runtime:
    def __init__(self):
        self.env={"NA":NA,"NULL":None,"Null":None,"null":None,"NIL":None,"Nil":None,"nil":None,"None":None,"none":None,"TRUE":True,"True":True,"true":True,"FALSE":False,"False":False,"false":False,"c":c,"factor":factor,"data":data,"readRDS":readRDS,"saveRDS":saveRDS,"cursor":cursor,"cols":cols,"rows":rows,"gwidth":gwidth,"gheight":gheight,"gcolors":gcolors,"gprint":gprint,"gprintf":gprintf};
    def set(self,name,value): self.env[str(name)]=value; return value;
    def get(self,name): return self.env[str(name)];
    def resolve(self,name):
        text=str(name);
        if text in self.env: return self.env[text];
        try: value=dataset(text); self.env[text]=value; return value;
        except (KeyError,FileNotFoundError): raise NameError("object '{}' not found".format(text));
