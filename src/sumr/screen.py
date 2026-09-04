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
"""sumR facade for Sum's text-grid and graphics-plane contracts.""";

from sumui import CursorState, GraphicsCommand, TextScreen, coerce_cursor_state;
try:
    from sumtui import TerminalTextScreen;
except Exception:
    TerminalTextScreen = None;

_MISSING = object();
_text_screen = TerminalTextScreen() if TerminalTextScreen is not None else TextScreen();
_graphics_size_provider = None;
_graphics_handler = None;
_graphics_fallback = (640,480,16);


def set_text_screen(screen):
    global _text_screen;
    if not isinstance(screen, TextScreen): raise TypeError("screen must implement sumUI TextScreen");
    _text_screen=screen; return screen;

def text_screen(): return _text_screen;
def cols(): return _text_screen.cols;
def rows(): return _text_screen.rows;

def _cursor_code(state):
    state=coerce_cursor_state(state);
    if state==CursorState.HIDDEN: return 0;
    if state==CursorState.BLOCK: return 2;
    return 1;

def cursor(value=_MISSING):
    if value is _MISSING: return _cursor_code(_text_screen.cursor());
    return _cursor_code(_text_screen.cursor(value));

def configure_graphics(size_provider=None,handler=None,fallback=(640,480,16)):
    global _graphics_size_provider,_graphics_handler,_graphics_fallback;
    _graphics_size_provider=size_provider if callable(size_provider) else None;
    _graphics_handler=handler if callable(handler) else None;
    _graphics_fallback=tuple(fallback); return (_graphics_size_provider,_graphics_handler);

def _graphics_size():
    value=None;
    if _graphics_size_provider is not None:
        try: value=_graphics_size_provider();
        except Exception: value=None;
    if value is None: value=_graphics_fallback;
    if len(value)==2: value=(value[0],value[1],_graphics_fallback[2]);
    return max(1,int(value[0])),max(1,int(value[1])),max(1,int(value[2]));

def gwidth(): return _graphics_size()[0];
def gheight(): return _graphics_size()[1];
def gcolors(): return _graphics_size()[2];

def _emit(operation,arguments=(),**options):
    command=GraphicsCommand(str(operation),tuple(arguments),tuple(options.items()));
    if _graphics_handler is not None: _graphics_handler(command);
    return command;

def gprint(x,y,text,color=None,size=None,font_name=None):
    options={};
    if color is not None: options["color"]=color;
    if size is not None: options["size"]=int(size);
    if font_name is not None: options["font_name"]=str(font_name);
    return _emit("text",(x,y,str(text)),**options);

def gprintf(x,y,format_text,*values):
    rendered=str(format_text) % (values[0] if len(values)==1 else tuple(values)) if values else str(format_text);
    return gprint(x,y,rendered);

def sort_layers(*names,direction="ASC"): return _emit("sort_layers",(tuple(str(n) for n in names),str(direction).upper()));
def clear_layer(name): return _emit("clear_layer",(str(name),));

__all__=["set_text_screen","text_screen","cols","rows","cursor","configure_graphics","gwidth","gheight","gcolors","gprint","gprintf","sort_layers","clear_layer"];
