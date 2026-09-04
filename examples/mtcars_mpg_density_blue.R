library(ggplot2);

datacamp_light_blue = "#51A8C9";

p = ggplot(
  mtcars,
  aes(mpg, after_stat(density))
) +
  geom_histogram(
    binwidth = 1,
    fill = datacamp_light_blue
  );

print(p);

ggsave(
  "mtcars_mpg_density_blue.png",
  plot = p,
  width = 8,
  height = 6,
  dpi = 150
);

system2(
  "xdg-open",
  "mtcars_mpg_density_blue.png",
  stdout = FALSE,
  stderr = FALSE,
  wait = FALSE
);
