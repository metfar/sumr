# sumR r20.2: shared aliases, text grid, cursor and graphics plane.
print(TRUE);
print(True);
print(true);
print(FALSE);
print(false);
print(NULL);
print(nil);
print(none);

print(cols());
print(rows());
cursor(FALSE);
cursor(TRUE);
cursor("block");
cursor(TRUE);

print(gwidth());
print(gheight());
print(gcolors());
paper(0);
border(1);
border_width(24);
gprint(20, 30, "sumR graphics text");
gprintf(20, 60, "size=%dx%d", gwidth(), gheight());
