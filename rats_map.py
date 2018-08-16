import pandas as pd
import numpy as np

from bokeh.io import curdoc

import yaml

from bokeh.io import (
    output_notebook,
    show
)

from bokeh.plotting import (
    Column,
    figure,
    gridplot,
    Row
)

from bokeh.themes import Theme
from bokeh.layouts import widgetbox
from bokeh.palettes import Blues9, OrRd9
from bokeh.transform import jitter
from bokeh.tile_providers import CARTODBPOSITRON

from bokeh.models import (
    BasicTicker, ColumnDataSource, ColorBar,
    ColorMapper, CustomJS, Div,
    HBar, HoverTool, LinearColorMapper,
    LogColorMapper, MultiSelect, PrintfTickFormatter,
    Select
)

def choro_map():

    df = pd.read_pickle("./data/Rat_Sightings.pkl")

    def make_map(var="postalCode", year="All", season="All"):

        def filter_years_seasons(df=df, season=season, year=year):

            if year == "All" and season =="All":

                #group dataframe by indicated column name and rename columns
                df = (df
                            )

            elif year != "All" and season == "All":

                #group dataframe by indicated column name and rename columns
                df = (df
                      .query("Year == '%s'" %year)
                     )

            elif year != "All" and season != "All":

                # select cases for user-selected year and season
                df = (df
                     .query("Year == '%s'" %year)
                     .query("Season == '%s'" %season)
                    )

            elif year == "All" and season != "All":

                # only extract cases for the user-selected season
                df = (df
                      .query("Season == '%s'" %season)
                     )

            else:

                # just set it to itself if user-error occurs
                df = df


            return df

        new_df = filter_years_seasons()

        if var=="postalCode":

            groupeddf = (new_df
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {"n":"Rat_Sightings"})
                         .merge(df[["postalCode", "Neighborhood",
                                    "Borough", "xs", "ys"
                                   ]])
                         .drop_duplicates(subset=[var])
                         .reset_index(drop=True)
                        )

        elif var == "Neighborhood":

            groupeddf = (new_df
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {"n":"Rat_Sightings"})
                         .merge(df[["Neighborhood", "Borough",
                                    "nhood_xs", "nhood_ys"
                                   ]])
                         .drop_duplicates(subset=[var])
                         .reset_index(drop=True)
                         .rename(columns={"nhood_xs":"xs", "nhood_ys":"ys"})
                        )

        elif var == "Borough":
            groupeddf = (new_df
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {"n":"Rat_Sightings"})
                         .merge(df[["Borough",
                                    "boro_xs", "boro_ys"
                                   ]])
                         .drop_duplicates(subset=[var])
                         .reset_index(drop=True)
                         .rename(columns={"boro_xs":"xs", "boro_ys":"ys"})
                        )
        else:

            var = "postalCode"

            groupeddf = (new_df
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {"n":"Rat_Sightings"})
                         .merge(df[["postalCode", "Neighborhood",
                                    "Borough", "xs", "ys"
                                   ]])
                         .drop_duplicates(subset=[var])
                         .reset_index(drop=True)
                        )


        # instantiate the color mapper
        color_mapper = LogColorMapper(
            palette=OrRd9[::-1]
        )

        p = figure(
            x_range=(-8400000,-8100000),
            y_range=(4950000, 5000000),
            x_axis_type = "mercator",
            y_axis_type="mercator",
            plot_height=1200,
            plot_width=1000
        )
        p.axis.visible = False
        p.grid.grid_line_color = None
        p.add_tile(CARTODBPOSITRON)

        p.grid.grid_line_color = None

        p.patches(
            "xs",
            "ys",
            source=ColumnDataSource(data=groupeddf),
            fill_color = {
                "field":"Rat_Sightings",
                "transform":color_mapper
            },
            fill_alpha=0.6
        )

        p.add_tools(HoverTool(tooltips=[
            ("Number of Rat Sightings: ", "@Rat_Sightings"),
            ("%s" %var, "@%s" %var)
        ]))

        return p

    year_select = Select(value="All",
                         options=[*df["Year"].unique()]+["All"],
                         title="Select a year to view: "
                        )

    season_select = Select(value="All",
                           options=[*df["Season"].unique()]+["All"],
                           title="Select a season to view: "
                          )

    agg_level_select = Select(value="postalCode",
                              options=["postalCode", "Neighborhood",
                                       "Borough"
                                      ],
                              title="Select a value to view the data by: "
                             )


    def update_plot(attr, old, new):

        layout.children[1] = make_map(year=year_select.value,
                                      season=season_select.value,
                                      var=agg_level_select.value

                                     )

    year_select.on_change("value", update_plot)
    season_select.on_change("value", update_plot)
    agg_level_select.on_change("value", update_plot)

    layout = Column(Column(agg_level_select,
                           year_select,
                           season_select
                          ),
                    make_map()
                   )

    return layout


curdoc().add_root(choro_map())
