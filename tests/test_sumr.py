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

def test_cli_version(capsys):
    from sumr.cli import main;
    import pytest;
    with pytest.raises(SystemExit) as exc: main(["--version"]);
    assert exc.value.code==0; assert "sumR 0.1.0a6" in capsys.readouterr().out;

def test_cli_stdin_no_file(monkeypatch,capsys):
    from sumr.cli import main;
    import io,sys;
    monkeypatch.setattr(sys,"stdin",io.StringIO("a <- 2\nprint(a)\n"));
    assert main([])==0; assert "2" in capsys.readouterr().out;


def test_ggplot_histogram_acceptance(tmp_path,monkeypatch):
    monkeypatch.setenv("MPLBACKEND","Agg"); monkeypatch.chdir(tmp_path);
    source='library(ggplot2);\ndatacamp_light_blue = "#51A8C9";\np = ggplot(mtcars, aes(mpg, after_stat(density))) + geom_histogram(binwidth = 1, fill = datacamp_light_blue);\nprint(p);\nggsave("mtcars_mpg_density_blue.png", plot = p, width = 8, height = 6, dpi = 150);';
    out,rt=execute(source); target=tmp_path/"mtcars_mpg_density_blue.png"; assert target.exists(); assert target.read_bytes()[:8]==bytes.fromhex("89504e470d0a1a0a"); assert rt.get("p").layers[0].stat=="bin";

def test_r2021_cli_gui_attaches_graphics_device(monkeypatch):
    import sys,types;
    from sumr.cli import main;
    seen=[];
    class Surface:
        width=640; height=480;
    class Window:
        def __init__(self,**unused): self.surface=None; self.screen=None; self.closed=False; self.finished=False;
        def handle(self,item):
            seen.append(item);
            if hasattr(item,"logical_width"):
                self.surface=Surface(); self.screen=object();
            return item;
        def finish(self,wait=False): self.finished=bool(wait); self.closed=True; return 0;
    package=types.ModuleType("sumgui"); graphics=types.ModuleType("sumgui.graphics"); graphics.GraphicsWindow=Window;
    monkeypatch.setitem(sys.modules,"sumgui",package); monkeypatch.setitem(sys.modules,"sumgui.graphics",graphics);
    assert main(["--gui","-e",'paper(0); border(1); border_width(12); gprint(10,20,"R GUI")']) == 0;
    operations=[getattr(item,"operation",None) for item in seen];
    assert "border_width" in operations and "text" in operations;


def test_audio_facade_is_shared_sumcore_contract():
    from sumcore import audio_api;
    rt=Runtime();
    assert rt.resolve("beep") is audio_api.beep;
    assert rt.resolve("sound") is audio_api.sound;
    assert rt.resolve("play") is audio_api.play;
