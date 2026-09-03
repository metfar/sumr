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
import re;
from .runtime import Runtime, c, data;
def _atom(text,rt):
    text=text.strip();
    if text.startswith('"') and text.endswith('"'): return text[1:-1];
    if re.match(r"^-?\d+(?:\.\d+)?$",text): return float(text) if "." in text else int(text);
    match=re.match(r"c\((.*)\)$",text);
    if match: return c(*[_atom(part,rt) for part in match.group(1).split(",") if part.strip()]);
    match=re.match(r"data\(([^)]+)\)$",text);
    if match: return data(match.group(1).strip().strip('"'));
    if text in rt.env: return rt.get(text);
    raise ValueError("Unsupported sumR expression: {}".format(text));
def execute(source,rt=None):
    rt=rt or Runtime(); output=[];
    for raw in source.splitlines():
        line=raw.strip().rstrip(";");
        if not line or line.startswith("#") or line.startswith("library("): continue;
        match=re.match(r"([A-Za-z_.][A-Za-z0-9_.]*)\s*(?:<-|=)\s*(.+)$",line);
        if match: rt.set(match.group(1),_atom(match.group(2),rt)); continue;
        match=re.match(r"print\((.+)\)$",line);
        if match: output.append(_atom(match.group(1),rt)); continue;
        output.append(_atom(line,rt));
    return output,rt;
def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("file",nargs="?"); parser.add_argument("-e","--expression"); args=parser.parse_args(argv); source=args.expression if args.expression is not None else open(args.file,encoding="utf-8").read(); out,_=execute(source); [print(value) for value in out]; return 0;
