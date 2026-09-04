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
    assert exc.value.code==0; assert "sumR 0.1.0a3" in capsys.readouterr().out;

def test_cli_stdin_no_file(monkeypatch,capsys):
    from sumr.cli import main;
    import io,sys;
    monkeypatch.setattr(sys,"stdin",io.StringIO("a <- 2\nprint(a)\n"));
    assert main([])==0; assert "2" in capsys.readouterr().out;


def test_ggplot_histogram_acceptance(tmp_path,monkeypatch):
    monkeypatch.setenv("MPLBACKEND","Agg"); monkeypatch.chdir(tmp_path);
    source='library(ggplot2);\ndatacamp_light_blue = "#51A8C9";\np = ggplot(mtcars, aes(mpg, after_stat(density))) + geom_histogram(binwidth = 1, fill = datacamp_light_blue);\nprint(p);\nggsave("mtcars_mpg_density_blue.png", plot = p, width = 8, height = 6, dpi = 150);';
    out,rt=execute(source); target=tmp_path/"mtcars_mpg_density_blue.png"; assert target.exists(); assert target.read_bytes()[:8]==bytes.fromhex("89504e470d0a1a0a"); assert rt.get("p").layers[0].stat=="bin";
