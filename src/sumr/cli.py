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
import argparse;
import ast;
import re;
import sys;
from . import __version__;
from .runtime import RSymbol, Runtime, aes, after_stat, c, data, factor, geom_bar, geom_bar3d, geom_histogram, ggsave, ggplot, print_value, readRDS, saveRDS, system2;
from .screen import border, border_width, cols, configure_graphics, cursor, gcolors, gheight, gprint, gprintf, gwidth, paper, rows;
from sumplot import PlotSpec;

_TOKEN=re.compile(r'\s*(?:(?P<string>"(?:\\.|[^"\\])*")|(?P<number>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|(?P<assign><-)|(?P<name>[A-Za-z_.][A-Za-z0-9_.]*)|(?P<op>[(),+=]))');

def _strip_comment(line):
    output=[]; quote=False; escape=False;
    for char in line:
        if quote:
            output.append(char);
            if escape: escape=False;
            elif char=='\\': escape=True;
            elif char=='"': quote=False;
            continue;
        if char=='"': quote=True; output.append(char); continue;
        if char=='#': break;
        output.append(char);
    return ''.join(output);

def _statements(source):
    output=[]; buffer=[]; depth=0; quote=False; escape=False;
    source='\n'.join(_strip_comment(line) for line in str(source).splitlines());
    for char in source:
        if quote:
            buffer.append(char);
            if escape: escape=False;
            elif char=='\\': escape=True;
            elif char=='"': quote=False;
            continue;
        if char=='"': quote=True; buffer.append(char); continue;
        if char=='(': depth+=1;
        elif char==')': depth=max(0,depth-1);
        if char in (';','\n') and depth==0:
            text=''.join(buffer).strip();
            if text.endswith('+'): buffer.append(' '); continue;
            if text: output.append(text);
            buffer=[]; continue;
        buffer.append(char);
    text=''.join(buffer).strip();
    if text: output.append(text);
    return output;

def _top_assignment(text):
    depth=0; quote=False; escape=False; index=0;
    while index<len(text):
        char=text[index];
        if quote:
            if escape: escape=False;
            elif char=='\\': escape=True;
            elif char=='"': quote=False;
            index+=1; continue;
        if char=='"': quote=True; index+=1; continue;
        if char=='(': depth+=1; index+=1; continue;
        if char==')': depth=max(0,depth-1); index+=1; continue;
        if depth==0 and text[index:index+2]=='<-': return text[:index].strip(),text[index+2:].strip();
        if depth==0 and char=='=': return text[:index].strip(),text[index+1:].strip();
        index+=1;
    return None;

class Parser:
    def __init__(self,text,rt,output):
        self.tokens=[]; self.index=0; self.rt=rt; self.output=output; pos=0;
        while pos<len(text):
            match=_TOKEN.match(text,pos);
            if not match: raise SyntaxError("Unsupported sumR syntax near: {}".format(text[pos:pos+30]));
            kind=match.lastgroup; value=match.group(kind); self.tokens.append((kind,value)); pos=match.end();
    def peek(self,value=None,kind=None,offset=0):
        if self.index+offset>=len(self.tokens): return False;
        token=self.tokens[self.index+offset]; return (value is None or token[1]==value) and (kind is None or token[0]==kind);
    def pop(self,value=None):
        if self.index>=len(self.tokens): raise SyntaxError("Unexpected end of expression");
        token=self.tokens[self.index];
        if value is not None and token[1]!=value: raise SyntaxError("Expected {}, got {}".format(value,token[1]));
        self.index+=1; return token;
    def parse(self):
        value=self.add();
        if self.index!=len(self.tokens): raise SyntaxError("Unexpected token: {}".format(self.tokens[self.index][1]));
        return value;
    def add(self):
        value=self.primary();
        while self.peek('+'):
            self.pop('+'); right=self.primary(); value=self.value(value)+self.value(right);
        return value;
    def primary(self):
        kind,value=self.pop();
        if kind=='string': return ast.literal_eval(value);
        if kind=='number': return float(value) if any(ch in value for ch in '.eE') else int(value);
        if value=='(':
            result=self.add(); self.pop(')'); return result;
        if kind!='name': raise SyntaxError("Unexpected token: {}".format(value));
        if self.peek('('): return self.call(value);
        if value in self.rt.env and not callable(self.rt.env[value]): return self.rt.env[value];
        return RSymbol(value);
    def call(self,name):
        self.pop('('); args=[]; kwargs={};
        while not self.peek(')'):
            if self.peek(kind='name') and self.peek('=',offset=1): key=self.pop()[1]; self.pop('='); kwargs[key]=self.add();
            else: args.append(self.add());
            if self.peek(','): self.pop(','); continue;
            break;
        self.pop(')'); return self.invoke(name,args,kwargs);
    def value(self,value): return self.rt.resolve(value.name) if isinstance(value,RSymbol) else value;
    def values(self,values): return [self.value(value) for value in values];
    def invoke(self,name,args,kwargs):
        lname=name.lower();
        if lname=='library': return None;
        if lname=='after_stat': return after_stat(args[0]);
        if lname=='aes': return aes(*args,**kwargs);
        if lname=='ggplot': return ggplot(*self.values(args),**{key:self.value(value) for key,value in kwargs.items()});
        if lname=='geom_histogram': return geom_histogram(*self.values(args),**{key:self.value(value) for key,value in kwargs.items()});
        if lname=='geom_bar': return geom_bar(*self.values(args),**{key:self.value(value) for key,value in kwargs.items()});
        if lname=='geom_bar3d': return geom_bar3d(*self.values(args),**{key:self.value(value) for key,value in kwargs.items()});
        if lname=='c': return c(*self.values(args));
        if lname=='factor': return factor(self.value(args[0]));
        if lname=='data':
            item=args[0].name if args and isinstance(args[0],RSymbol) else self.value(args[0]) if args else None; package=self.value(kwargs['package']) if 'package' in kwargs else None; result=data(item,package=package);
            if item is not None: self.rt.set(str(item),result);
            return result;
        if lname=='print':
            value=self.value(args[0]); print_value(value);
            if not isinstance(value,PlotSpec): self.output.append(value);
            return value;
        if lname=='ggsave':
            values=self.values(args); filename=values[0] if values else self.value(kwargs.pop('filename')); params={key:self.value(value) for key,value in kwargs.items()}; return ggsave(filename,**params);
        if lname=='system2': return system2(*self.values(args),**{key:self.value(value) for key,value in kwargs.items()});
        if lname=='readrds': return readRDS(*self.values(args));
        if lname=='saverds': return saveRDS(*self.values(args));
        if lname in ('cursor','cols','rows','gwidth','gheight','gcolors','paper','border','border_width','gprint','gprintf'):
            fn={'cursor':cursor,'cols':cols,'rows':rows,'gwidth':gwidth,'gheight':gheight,'gcolors':gcolors,'paper':paper,'border':border,'border_width':border_width,'gprint':gprint,'gprintf':gprintf}[lname];
            return fn(*self.values(args),**{key:self.value(value) for key,value in kwargs.items()});
        raise ValueError("Unsupported sumR function: {}".format(name));

def _expression(text,rt,output): return Parser(text,rt,output).parse();
def execute(source,rt=None):
    rt=rt or Runtime(); output=[];
    for statement in _statements(source):
        assignment=_top_assignment(statement);
        if assignment:
            name,expression=assignment;
            if not re.match(r'^[A-Za-z_.][A-Za-z0-9_.]*$',name): raise SyntaxError("Unsupported assignment target: {}".format(name));
            rt.set(name,_expression(expression,rt,output));
        else: _expression(statement,rt,output);
    return output,rt;
def _print_values(values):
    for value in values: print(value);
def repl():
    rt=Runtime();
    while True:
        try: line=input("sumR> ");
        except (EOFError,KeyboardInterrupt): print(); return 0;
        command=line.strip();
        if command in ("q()","quit()","exit","exit()"): return 0;
        if not command: continue;
        try: out,rt=execute(line,rt); _print_values(out);
        except Exception as exc: print("Error: {}".format(exc),file=sys.stderr);
def main(argv=None):
    parser=argparse.ArgumentParser(prog="sumR",description="SUM R-compatible data-science runtime."); parser.add_argument("--version",action="version",version="sumR {}".format(__version__)); parser.add_argument("--gui",action="store_true",help="attach the optional sumGUI graphics device for gprint/gprintf and screen-plane commands"); parser.add_argument("file",nargs="?"); parser.add_argument("-e","--expression"); args=parser.parse_args(argv);
    window=None;
    if args.gui:
        try:
            from sumgui.graphics import GraphicsWindow;
            from sumui import basic_mode;
        except (ImportError,ModuleNotFoundError) as exc:
            parser.error("--gui requires sumGUI/Pygame")
        window=GraphicsWindow(title="sumR graphics",close_on_escape=True);
        window.handle(basic_mode(640,480));
        configure_graphics(size_provider=lambda: (window.surface.width,window.surface.height,16) if window.surface is not None else (640,480,16),handler=window.handle,fallback=(640,480,16));
    if args.expression is not None: source=args.expression;
    elif args.file is not None: source=open(args.file,encoding="utf-8").read();
    elif not sys.stdin.isatty():
        source=sys.stdin.read();
        if not source.strip(): parser.print_help(); return 0;
    else: return repl();
    out,_=execute(source); _print_values(out);
    if window is not None and window.screen is not None and not window.closed: window.finish(wait=True);
    return 0;
