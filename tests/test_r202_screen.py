from sumui import GraphicsCommand, TextScreen;
from sumr.cli import execute;
from sumr.runtime import Runtime;
from sumr.screen import configure_graphics, set_text_screen;


def test_r_aliases_are_transparent_without_collapsing_na():
    rt=Runtime();
    for name in ("TRUE","True","true"): assert rt.resolve(name) is True;
    for name in ("FALSE","False","false"): assert rt.resolve(name) is False;
    for name in ("NULL","Null","null","NIL","Nil","nil","None","none"): assert rt.resolve(name) is None;
    assert rt.resolve("NA") is not None;


def test_r_cursor_grid_and_graphics_functions_through_parser():
    size=[80,25]; states=[]; commands=[];
    set_text_screen(TextScreen(size_provider=lambda: tuple(size), cursor_setter=states.append));
    configure_graphics(lambda:(320,200,16), commands.append);
    out,rt=execute('''print(cols()); print(rows()); cursor(FALSE); cursor(TRUE); cursor("block"); gprintf(10,20,"x=%d",7); print(gwidth()); print(gheight()); print(gcolors());''');
    assert out == [80,25,320,200,16];
    assert commands[-1].operation=="text" and commands[-1].arguments==(10,20,"x=7");
    size[:]=[39,17]; out,_=execute('print(cols()); print(rows());',rt); assert out==[39,17];


def test_r2021_border_width_and_parser_support():
    import sumr.screen as screen;
    from sumr.cli import execute;
    seen=[]; screen.configure_graphics(handler=seen.append);
    output,unused_rt=execute('paper(0); border(1); border_width(20); print(border_width());');
    assert output[-1] == 20;
    assert any(item.operation == "border_width" and item.arguments == (20,) for item in seen);
    assert [item.operation for item in seen[:2]] == ["paper","border"];
