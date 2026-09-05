# sumr

R-compatible data-science subset for the Sum ecosystem.


## r20.1 graphical acceptance example

Run the ggplot2-compatible histogram example directly with SUM R:

```bash
sumr examples/mtcars_mpg_density_blue.R
```

It renders `print(p)`, writes `mtcars_mpg_density_blue.png` through `ggsave()`, and demonstrates non-blocking `system2("xdg-open", ...)`.

<p align=center><b>- oOo -</b></p>

## Graphical acceptance example

`examples/mtcars_mpg_density_blue.R` exercises `library(ggplot2)`, `geom_histogram()`, `after_stat(density)`, `print()`, `ggsave()` and non-blocking `system2()`.


## r20.1 graphical acceptance example

Run the ggplot2-compatible histogram example directly with SUM R:

```bash
sumr examples/mtcars_mpg_density_blue.R
```

It renders `print(p)`, writes `mtcars_mpg_density_blue.png` through `ggsave()`, and demonstrates non-blocking `system2("xdg-open", ...)`.

## Shared audio

```r
beep(0.25, 12);
sound(440, 18.2);
play("T180O5cdefgabC");
play("O4c", hold=TRUE, timeout=3);
stopAudio();
```

The functions delegate to `sumCore`; sumR does not duplicate synthesis.

<p align=center><b>- oOo -</b></p>
