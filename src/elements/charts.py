import altair as alt
import polars as pl
import streamlit as st

from constants import COLUMN_APERTURE, COLUMN_CAMERA, COLUMN_ISO, COLUMN_DATETIME, COLUMN_LABEL, COLUMN_EXPOSURE, \
    COLUMN_FOCAL_LENGTH, COLUMN_LENS, COLUMN_EXPOSURE_PRETTY, COLUMN_APERTURE_PRETTY, COLUMN_FOCAL_LENGTH_PRETTY

def __generate_repartition(
        df: pl.DataFrame,
        col: str,
        col_ordering: str | None = None,
        as_percent_per_label: bool = False,
):
    col_percentage = 'Percentage'
    col_count = 'Count'
    col_aggregation = col_percentage if as_percent_per_label else col_count

    group_cols = [pl.col(COLUMN_LABEL), pl.col(col)]
    if col_ordering is not None:
        group_cols.append(pl.col(col_ordering))

    df = (
        df
          .group_by(*group_cols)
          .len(col_count)
            .with_columns(
                (pl.col(col_count) / pl.sum(col_count).over(COLUMN_LABEL) * 100)
                .round(2)
                .alias(col_percentage)
            )
    )
    st.text(f'{col} repartition ({col_aggregation})')
    if col_ordering is not None:
        df = df.sort(col_ordering)
        chart = alt.Chart(data=df.to_pandas()).mark_bar().encode(
            x=alt.X(f'{col}', title=col, sort=None, axis=alt.Axis(labelAngle=-75)),
            xOffset=alt.XOffset(field=COLUMN_LABEL),
            y=alt.Y(f'{col_aggregation}', stack=False),
            color=alt.Color(field=COLUMN_LABEL),
        ).configure_legend(
            orient='bottom',
            offset=5,
            titlePadding=5,
        )
        st.altair_chart(chart.interactive(), use_container_width=True)
    else:
        st.bar_chart(
            data=df.to_pandas(),
            x=col,
            y=col_aggregation,
            x_label=col,
            y_label=col_aggregation,
            color=COLUMN_LABEL,
            stack=False,
        )

def __generate_charts(df: pl.DataFrame, as_percent_per_label: bool):
    __generate_repartition(df, COLUMN_APERTURE_PRETTY, col_ordering=COLUMN_APERTURE, as_percent_per_label=as_percent_per_label)
    __generate_repartition(df, COLUMN_EXPOSURE_PRETTY, col_ordering=COLUMN_EXPOSURE, as_percent_per_label=as_percent_per_label)
    __generate_repartition(df, COLUMN_FOCAL_LENGTH_PRETTY, col_ordering=COLUMN_FOCAL_LENGTH, as_percent_per_label=as_percent_per_label)
    __generate_repartition(df, COLUMN_ISO, as_percent_per_label=as_percent_per_label)
    __generate_repartition(df, COLUMN_DATETIME, as_percent_per_label=as_percent_per_label)
    __generate_repartition(df, COLUMN_CAMERA, as_percent_per_label=as_percent_per_label)
    __generate_repartition(df, COLUMN_LENS, as_percent_per_label=as_percent_per_label)
    # Not ready at all
    # It would require to find which RAW belongs to which PROCESSED
    # __generate_repartition(df, COLUMN_DIRECTORY, as_percent_per_label=as_percent_per_label)


def charts(
        df: pl.DataFrame,
):
    st.title('Analysis of your pictures')
    st.text('You will find below charts representing the distribution of your RAW and your processed pictures. '
            'The percentage of distribution (right hand side) is among all of the picture in the same label (RAW or processed).')

    col_count, col_stats = st.columns(2)
    with col_count:
        __generate_charts(df, False)
    with col_stats:
        __generate_charts(df, True)
