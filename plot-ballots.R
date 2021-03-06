library(tidyverse)
library(ggtext)

sa_members = c(
    "MATT HANEY" = "Matt Haney",
    "DAVID CAMPOS" = "David Campos",
    "BILAL MAHMOOD" = "Bilal Mahmood",
    "THEA SELBY" = "Thea Selby"
)

ballots <- read_csv("ballots.csv") %>%
    rename(sa_member = state_assembly_member_district_17) %>%
    filter(sa_member != "Write-in") %>%
    mutate(sa_member = recode(sa_member, !!! sa_members)) %>%
    mutate(sa_member = fct_relevel(sa_member, rev(sa_members)))

plot_recall <- function(
    df,
    boe_member,
    no_color = "#f5ae52",
    yes_color = "#ae52f5"
) {
    df %>%
        group_by(sa_member) %>%
        count(recall) %>%
        filter(!is.na(sa_member), !is.na(recall)) %>%
        mutate(n = if_else(recall == "NO", -n, n)) %>%
        ggplot(aes(n, sa_member, fill = recall)) +
        geom_col(width = 0.7) +
        scale_fill_manual(values = c(no_color, yes_color)) +
        guides(fill = "none") +
        lims(x = c(-13000, 19000)) +
        labs(
            title = glue::glue("Recall <b>{boe_member}</b>? "),
            subtitle = glue::glue(
                "<span style='color:{no_color}'>No</span> or ",
                "<span style='color:{yes_color}'>Yes</span> " ,
                "by choice for State Assembly Member District 17"
            ),
            y = NULL,
            x = NULL
        ) +
        theme_minimal(base_size = 18) +
        theme(
            plot.title = element_markdown(size = 24),
            plot.title.position = "plot",
            plot.subtitle = element_markdown(size = 16),
            plot.background = element_rect(fill = "white", color = "white"),
            plot.margin = margin(1.5, 1.5, 1, 1.5, unit = "line"),
            panel.grid.major.y = element_blank(),
            panel.grid.major.x = element_blank(),
            panel.grid.minor.x = element_blank(),
            axis.text.y = element_text(size = 18),
            axis.text.x = element_blank()
        )
}

ballots %>%
    rename(recall = recall_measure_regarding_alison_collins) %>%
    plot_recall("Alison Collins")

ggsave("collins.png", width = 7, height = 4)

ballots %>%
    rename(recall = recall_measure_regarding_gabriela_lópez) %>%
    plot_recall("Gabriela López")

ggsave("lopez.png", width = 7, height = 4)

ballots %>%
    rename(recall = recall_measure_regarding_faauuga_moliga) %>%
    plot_recall("Faauuga Moliga")

ggsave("moliga.png", width = 7, height = 4)


