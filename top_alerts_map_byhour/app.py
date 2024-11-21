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

# Define UI
app_ui = ui.page_sidebar(
    ui.panel_sidebar(
        ui.h2("Top Alerts by Range of Hours"),
        ui.input_select(
            id="alert_type",
            label="Select Alert Type and Subtype:",
            choices={
                f"{row['type']} - {row['subtype']}": f"{row['type']}|{row['subtype']}"
                for _, row in collapsed_df[['type', 'subtype']].drop_duplicates().iterrows()
            },
            selected="JAM|JAM_HEAVY_TRAFFIC"
        ),
        ui.input_slider(
            id="hour_range",
            label="Select Hour Range:",
            min=0,
            max=23,
            value=[6, 9]
        )
    ),
    ui.panel_main(
        ui.output_plot("alert_plot")
    )
)

# Define server logic
def server(input, output, session):
    @reactive.Calc
    def filtered_data():
        # Extract selected type and subtype
        selected_type, selected_subtype = input.alert_type().split("|")
        
        # Filter for selected type, subtype, and hour range
        filtered = collapsed_df[
            (collapsed_df['type'] == selected_type) &
            (collapsed_df['subtype'] == selected_subtype) &
            (collapsed_df['hour'].dt.hour >= input.hour_range()[0]) &
            (collapsed_df['hour'].dt.hour < input.hour_range()[1])
        ]

        if filtered.empty:
            return pd.DataFrame(columns=['binned_latitude', 'binned_longitude', 'alert_count'])

        # Aggregate the data and find top 10 locations
        top_10 = (
            filtered.groupby(['binned_latitude', 'binned_longitude'])
            .agg({'alert_count': 'sum'})
            .reset_index()
            .nlargest(10, 'alert_count')
        )
        return top_10

    @output
    @render.plot
    def alert_plot():
        top_10_df = filtered_data()
        if top_10_df.empty:
            return alt.Chart(pd.DataFrame({'message': ['No data available']})).mark_text().encode(
                text='message'
            ).properties(
                width=600,
                height=400
            )
        
        # Prepare the map layer
        geo_data = alt.Data(values=chicago_geojson["features"])
        chicago_map = alt.Chart(geo_data).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(
            width=600,
            height=400
        ).project('mercator')

        # Create the scatter plot
        scatter_plot = alt.Chart(top_10_df).mark_circle().encode(
            longitude='binned_longitude:Q',
            latitude='binned_latitude:Q',
            size=alt.Size('alert_count:Q', title='Number of Alerts', scale=alt.Scale(range=[100, 1000])),
            color=alt.value("red"),
            tooltip=['binned_latitude', 'binned_longitude', 'alert_count']
        ).properties(
            title="Top 10 Locations for Selected Alerts and Time Range",
            width=600,
            height=400
        )

        return chicago_map + scatter_plot

# Create and run the app
app = App(app_ui, server)



