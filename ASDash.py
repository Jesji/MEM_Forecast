# Script to read dfs and create graphics
import plotly.graph_objects as go
import pandas as pd

def get_df_plot(dfs,selection):
    df_gen = pd.concat([df for df in dfs])
    df_gen.columns = [word.strip() for word in df_gen.columns]
    day_time = pd.to_datetime(df_gen["Dia"], format="%d/%m/%Y")
    hour_delta = pd.to_timedelta(df_gen["Hora"], unit="h")
    df_gen["Date"] = day_time + hour_delta
    df_gen = df_gen.sort_values("Date").reset_index(drop=True)
    exclude_cols = ['Sistema', 'Dia', 'Hora', 'Date']
    columns_to_plot = [col for col in df_gen.columns if col not in exclude_cols]
    sel_resample = {"Daily":"D","Monthly":"M", "Yearly": "Y"}
    df_gen_res = df_gen.set_index('Date').resample(sel_resample[selection])[columns_to_plot].sum()

    return (df_gen_res, columns_to_plot)