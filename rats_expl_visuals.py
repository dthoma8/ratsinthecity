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

from math import pi

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


def bar():

    df = pd.read_pickle("./data/Rat_Sightings.pkl")

    def bar_chart(var="Borough", year="All", season="All", month="All"):

        """ Takes in a dataframe and a column name in a string format as inputs
        and generates a simple bar chart with hover capability and color mapping
        the most intense categories.
        """

        if year == "All" and season =="All" and month=="All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                        )

        elif year != "All" and season == "All" and month=="All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                        )

        elif year != "All" and season != "All" and month == "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                        )
        elif year!="All" and season!="All" and month!="All":

            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .query("Season == '%s'" %season)
                         .query("Month == '%s'" %month)
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                         )

        elif year == "All" and season != "All" and month !="All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Season == '%s'" %season)
                         .query("Month == '%s'" %month)
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                        )
        elif year == "ALl" and season == "All" and month !="All":
            groupeddf = (df
                         .query("Month == '%s'" %month)
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                         )

        else:

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby(var)
                         .n
                         .count()
                         .reset_index()
                        )

        # add in the percentages
        groupeddf["perc"] = (groupeddf["n"]/groupeddf["n"].sum())*100

        # assign names of columns
        groupeddf.columns = [var, var+"_rat_sightings", "perc"]

        # keep names as list
        names = [*groupeddf.columns]

        # keep unique values of col_name
        uniq_vals = [*groupeddf[var].unique()]

        # instantiate color mapper
        mapper = LogColorMapper(palette=Blues9[::-1])

        # instantiate figure
        p = figure(
            y_range=uniq_vals,
            title = "Rat Sightings by %s" %var
        )

        # fill figure
        p.hbar(
            y = var,
            right=names[1],
            height=0.9,
            source=ColumnDataSource(data=groupeddf),
            alpha=0.6,
            hover_alpha=0.9,
            fill_color = {
                "field":names[1],
                "transform":mapper
            }
        )

        # add hover tool
        p.add_tools(HoverTool(
            tooltips =[
                ("%s" %var, "@%s" %var),
                ("%s" %names[1],"@%s"%(names[1])),
                ("Percentage of Sightings", "@perc %")
            ],
            point_policy="follow_mouse"
        ))

        return p

    # create a select for users
    var_select = Select(value="Borough",
                        options = ["Borough", "postalCode",
                                   "Neighborhood", "Location Type",
                                   "Year", "Season"
                                  ],
                        title = "Select the Variable to View: "
                       )
    year_select = Select(value="All",
                         options=[*df["Year"].unique()]+["All"],
                         title="Select a year to view: "
                        )
    season_select = Select(value="All",
                           options=[*df["Season"].unique()]+["All"],
                           title="Select a season to view: "
                          )
    month_select = Select(value="All",
                          options = [*df.Month.unique()]+["All"],
                          title = "Select a month to view: "
                          )

    # create interactivity component
    def update_plot(attr, old, new):

        layout.children[1] = bar_chart(var=var_select.value,
                                       year=year_select.value,
                                       season=season_select.value,
                                       month=month_select.value
                                      )

    # add in interactivity component
    var_select.on_change("value", update_plot)
    year_select.on_change("value", update_plot)
    season_select.on_change("value", update_plot)
    month_select.on_change("value", update_plot)

    # define layout
    layout = Column(
                 Column(var_select, year_select, season_select, month_select),
                 bar_chart()
                 )

    return layout

def scatter():

    df = pd.read_pickle("./data/Rat_Sightings.pkl")


    def var_loc_scatter(var="Borough", loc_var = "Location Type", year="All", season="All"):

        """ This function takes in the dataframe, variable, and location
        type variable as inputs. The function will group the dataframe by
        the specified variable and location type to find the counts of various
        location types for each unique value of the variable. The function
        will then generate a scatter plot and return the resulting dataframe.
        """

        if year == "All" and season =="All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        elif year != "All" and season == "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        elif year != "All" and season != "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        elif year == "All" and season != "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        else:

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        # get total percentages
        groupeddf["total_perc"] = (groupeddf.rat_sightings/groupeddf.rat_sightings.sum())*100

        # get local percentages
        # use map?

        # create a list of the unique values
        uniq_vals = [*groupeddf[var].unique()]

        # create color mapper
        mapper = LogColorMapper(
            palette=Blues9[::-1]
        )

        # instantiate figure
        p = figure(
            y_range=uniq_vals
        )

        p.circle(
            x = "rat_sightings",
            y = jitter(var, width=0.6, range=p.y_range),
            source=ColumnDataSource(data=groupeddf),
            alpha=0.6,
            size=30,
            hover_alpha=0.9,
            fill_color = {
                "field":"rat_sightings",
                "transform":mapper
            }
        )

        p.add_tools(HoverTool(
            tooltips=[
                ("%s" %var, "@%s" %var),
                ("Location Type", "@loc_type"),
                ("Num. of Rat Sightings", "@rat_sightings"),
                ("Percentage of Rat Sightings within the %ss" %var,
                 "@total_perc %")
            ]
        ))

        return p

    # create a select for users
    var_select = Select(value="Borough",
                        options = ["Borough", "postalCode",
                                   "Neighborhood",
                                   "Year", "Season"
                                  ],
                        title = "Select the Variable to View: "
                       )
    year_select = Select(value="All",
                         options=[*df["Year"].unique()]+["All"],
                         title="Select a year to view: "
                        )
    season_select = Select(value="All",
                           options=[*df["Season"].unique()]+["All"],
                           title="Select a season to view: "
                          )

    # create interactivity components
    def update_plot(attr, old, new):

        layout.children[1] = var_loc_scatter(var=var_select.value,
                                             year=year_select.value,
                                             season=season_select.value
                                            )

    # add in interactivity component
    var_select.on_change('value', update_plot)
    year_select.on_change("value", update_plot)
    season_select.on_change("value", update_plot)

    layout = Column(Column(var_select, year_select, season_select), var_loc_scatter())

    return layout

def heatmap():

    df = pd.read_pickle("./data/Rat_Sightings.pkl")

    def var_loc_heatmap(df=df, var="Borough", loc_var="Location Type", year="All", season="All"):

        """
            Creates a heatmap for each class in var (Borough, Neighborhood, or Zip Code)
            and determines which location types are the of the highest
            intensity for each. Essentially a recreation of the scatter
            plot but with a heatmap instead of circles.
        """

        # group by
        if year == "All" and season =="All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        elif year != "All" and season == "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        elif year != "All" and season != "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        elif year == "All" and season != "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        else:

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby([var,loc_var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             loc_var:"loc_type","n":"rat_sightings"
                            })
                        )

        # get total percentages
        groupeddf["total_perc"] = (groupeddf.rat_sightings/groupeddf.rat_sightings.sum())*100


        # get unique value names
        loc_types = [*groupeddf["loc_type"].unique()]
        uniq_vals = [*groupeddf[var].unique()]

        # now add in percentages to give more information to user
        # get the total values

        sum_data = pd.DataFrame(
            groupeddf.groupby(var).rat_sightings.sum()
        )

        col_name = "total_%s_sights" %var
        sum_data.columns = [col_name]


        # merge the totals in to the dataframe
        """ Sure this can be applied to the dataframe in some fashion but opting
        for the conceptually easier solution here.
        """
        groupeddf = groupeddf.merge(sum_data.reset_index())

        # get percentages for each location type
        perc_name = "perc_sights"
        groupeddf[perc_name] = (
            groupeddf["rat_sightings"]/groupeddf[col_name])*100

        # instantiate color mapper
        mapper = LogColorMapper(palette=Blues9[::-1])

        # instantiate plot
        p = figure(y_range=uniq_vals, x_range=loc_types)

        # specify plot parameters
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size="7pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = pi/3

        # fill plot with data
        p.rect(
            x="loc_type",
            y=var,
            width=1,
            height=1,
            source=ColumnDataSource(data=groupeddf),
            alpha= 0.6,
            hover_alpha=0.9,
            fill_color = {
                "field":"rat_sightings",
                "transform":mapper
            }
        )

        p.add_tools(HoverTool(
            tooltips = [
                ("%s" %var, "@%s" %var),
                ("Location Type", "@loc_type"),
                ("Num. of Rat Sightings","@rat_sightings"),
                ("Perc. of Rat Sightings Across %ss" %var,"@perc_sights %")
            ],
            point_policy="follow_mouse"
        ))

        return p

    var_select = Select(value="Borough",
                            options=["Borough", "Neighborhood",
                                     "postalCode", "Year",
                                     "Season"
                                    ],
                            title="Select the Variable to View: "
                           )
    year_select = Select(value="All",
                         options=[*df["Year"].unique()]+["All"],
                         title="Select a year to view: "
                        )
    season_select = Select(value="All",
                           options=[*df["Season"].unique()]+["All"],
                           title="Select a season to view: "
                          )

    # create interactivity components
    def update_plot(attr, old, new):

        layout.children[1] = var_loc_heatmap(var=var_select.value,
                                             year=year_select.value,
                                             season=season_select.value
                                            )

    # add in interactivity component
    var_select.on_change('value', update_plot)
    year_select.on_change("value", update_plot)
    season_select.on_change("value", update_plot)

    layout = Column(Column(var_select, year_select, season_select), var_loc_heatmap())

    return layout

def new_scatter():

    df = pd.read_pickle("./data/Rat_Sightings.pkl")

    def var_var_scatter(df=df, var1="Borough", var2="Neighborhood", year="All", season="All"):

        """
            Allows the user to select whichever variables
            from the dataset for comparison in the form
            of a scatter plot.
        """

        # we want the var1 to be the least granular variable
        name1, name2 = var1,var2

        # get the number of classes
        n_classes1 = df[var1].nunique()
        n_classes2 = df[var2].nunique()

        # if the num of classes in var2 is less then reassign variables
        if n_classes2 < n_classes1:
            var1 = name2
            var2 = name1

        # group by
        if year == "All" and season =="All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby([var1, var2])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             "n":"rat_sightings"
                            })
                        )

        elif year != "All" and season == "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .assign(n=0)
                         .groupby([var1, var2])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             "n":"rat_sightings"
                            })
                        )

        elif year != "All" and season != "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Year == '%s'" %year)
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby([var1, var2])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             "n":"rat_sightings"
                            })
                        )

        elif year == "All" and season != "All":

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .query("Season == '%s'" %season)
                         .assign(n=0)
                         .groupby([var1, var2])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             "n":"rat_sightings"
                            })
                        )

        else:

            #group dataframe by indicated column name and rename columns
            groupeddf = (df
                         .assign(n=0)
                         .groupby([var1, var2])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {
                             "n":"rat_sightings"
                            })
                        )

        # get unique values for both vars
        uniq_vals1 = [*groupeddf[var1].unique()]
        uniq_vals2 = [*groupeddf[var2].unique()]

        # now add in percentages to give more information to user
        # get the total values

        sum_data = pd.DataFrame(
            groupeddf.groupby(var1)["rat_sightings"].sum()
        )

        col_name = "total_%s_sights" %var1
        sum_data.columns = [col_name]


        # merge the totals in to the dataframe
        """ Sure this can be applied to the dataframe in some fashion but opting
        for the conceptually easier solution here.
        """
        groupeddf = groupeddf.merge(sum_data.reset_index())

        # get percentages for each location type
        perc_name = "perc_sights"
        groupeddf[perc_name] = (
            groupeddf["rat_sightings"]/groupeddf[col_name])*100

        # create color mapper
        mapper = LogColorMapper(
            palette=Blues9[::-1]
        )

        # instantiate figure
        p = figure(
            plot_width=800,
            plot_height=600,
            y_range=uniq_vals1
        )

        p.circle(
            x = "rat_sightings",
            y = jitter(var1, width=0.6, range=p.y_range),
            source=ColumnDataSource(data=groupeddf),
            alpha=0.6,
            size=30,
            hover_alpha=0.9,
            fill_color = {
                "field":"rat_sightings",
                "transform":mapper
            }
        )

        p.add_tools(HoverTool(
            tooltips=[
                ("%s" %var1, "@%s" %var1),
                ("%s" %var2, "@%s" %var2),
                ("Num. of Rat Sightings", "@rat_sightings"),
                ("Percentage of Rat Sightings within the %ss" %var1,
                 "@perc_sights %")
            ]
        ))

        return p

    # define variable selects
    var1_select = Select(value="Borough",
                         options=[*df.columns],
                         title="Select a variable: "
                        )
    var2_select = Select(value="Neighborhood",
                         options=[*df.columns],
                         title="Select a variable: "
                        )
    year_select = Select(value="All",
                         options=[*df["Year"].unique()]+["All"],
                         title="Select a year to view: "
                        )
    season_select = Select(value="All",
                           options=[*df["Season"].unique()]+["All"],
                           title="Select a season to view: "
                          )

    # define interactivity
    def update_plot(attr, old, new):

        layout.children[1] = var_var_scatter(var1=var1_select.value,
                                             var2=var2_select.value,
                                             year=year_select.value,
                                             season=season_select.value
                                            )

    # inc interactivity
    var1_select.on_change("value", update_plot)
    var2_select.on_change("value", update_plot)
    year_select.on_change("value", update_plot)
    season_select.on_change("value", update_plot)

    layout=Column(
        Row(
            Column(var1_select, var2_select),
            Column(year_select, season_select)
        ),
        var_var_scatter()
    )
    return layout

from bokeh.models.widgets import Panel, Tabs

layout = Tabs(tabs = [Panel(child=bar(), title="Bar Plot"),
              Panel(child=scatter(), title="Scatter Plot"),
              Panel(child=heatmap(), title="Heatmap"),
              Panel(child=new_scatter(), title="Scatter - User Select")
              ])

curdoc().add_root(layout)
