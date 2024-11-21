import pandas as pd
from shiny import App, ui, reactive, render
import matplotlib.pyplot as plt

top_alerts_df = pd.read_csv("top_alerts_map.csv")
top_alerts_df['type_subtype'] = top_alerts_df['type'] + " - " + top_alerts_df['subtype']

unique_combinations = top_alerts_df[['type', 'subtype']].drop_duplicates()
unique_combinations['type_subtype'] = unique_combinations['type'] + " - " + unique_combinations['subtype']
type_subtype_options = unique_combinations['type_subtype'].tolist()

app_ui = ui.page_fluid(
    ui.h1("Top Alert Locations in Chicago"),
    ui.input_select(
        id="type_subtype",
        label="Select Alert Type and Subtype:",
        choices=type_subtype_options,
    ),
    ui.output_plot("alert_map"),
)

def server(input, output, session):
    @reactive.Calc
    def filtered_data():
        selected_type_subtype = input.type_subtype()
        filtered_df = top_alerts_df[top_alerts_df['type_subtype'] == selected_type_subtype]
        top_10_df = filtered_df.nlargest(10, 'alert_count')
        return top_10_df

    @output
    @render.plot
    def alert_map():
        data = filtered_data()
        fig, ax = plt.subplots()
        scatter = ax.scatter(
            data['binned_longitude'], 
            data['binned_latitude'],
            s=data['alert_count'] / 10, 
            alpha=0.6, 
            color="red"
        )
        ax.set_title(f"Top 10 Locations for {input.type_subtype()}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.colorbar(scatter, ax=ax, label="Alert Count")
        return fig

app = App(app_ui, server)



