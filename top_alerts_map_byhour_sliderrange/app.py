from shiny import App, ui, render, reactive
import pandas as pd
import altair as alt
import json

# File paths
collapsed_file_path = "/Users/mengyuting/Documents/GitHub/ps6/top_alerts_map_byhour/top_alerts_map_byhour.csv"
geojson_filepath = "/Users/mengyuting/Documents/GitHub/ps6/chicago_neighborhoods.geojson"

# Load the collapsed data
collapsed_df = pd.read_csv(collapsed_file_path)
collapsed_df['hour'] = pd.to_datetime(collapsed_df['hour']).dt.tz_localize(None).dt.floor('H')

# Load GeoJSON data
with open(geojson_filepath) as f:
    chicago_geojson = json.load(f)

# Define UI with Switch Button
app_ui = ui.page_sidebar(
    title="Top Alerts by Hour",
    sidebar=ui.panel_sidebar(
        ui.h2("Filter Options"),
        ui.input_switch(
            id="switch_button",
            label="Toggle to switch to range of hours",
            value=True  # Default to range slider
        ),
        ui.input_select(
            id="alert_type",
            label="Select Alert Type and Subtype:",
            choices={
                f"{row['type']} - {row['subtype']}": f"{row['type']}|{row['subtype']}"
                for _, row in collapsed_df[['type', 'subtype']].drop_duplicates().iterrows()
            },
            selected="JAM|JAM_HEAVY_TRAFFIC"
        ),
        ui.output_ui("dynamic_slider")  # Placeholder for the slider
    ),
    main=ui.panel_main(
        ui.output_plot("alert_plot")
    )
)

# Define server logic
def server(input, output, session):
    # Dynamic UI for slider
    @output
    @render.ui
    def dynamic_slider():
        if input.switch_button():
            # Range slider
            return ui.input_slider(
                id="hour_range",
                label="Select Hour Range:",
                min=0,
                max=23,
                value=[6, 9]
            )
        else:
            # Single hour slider
            return ui.input_slider(
                id="single_hour",
                label="Select Single Hour:",
                min=0,
                max=23,
                value=6
            )

    # Placeholder for filtered data and plot generation logic

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()



