"""Streamlit presentation for the synthetic product-feedback explorer."""

from __future__ import annotations

import streamlit as st

from feedback import (
    FixtureError,
    aggregate_by_product,
    filter_feedback,
    load_feedback,
    parse_uploaded_feedback,
    to_csv,
)


st.set_page_config(page_title="Product feedback explorer", page_icon="📝")
st.title("Product feedback explorer")
st.write("Explore synthetic product feedback by product. The fixture is bundled with this app and stays local.")

try:
    records = load_feedback()
except FixtureError as error:
    st.error(str(error))
    st.stop()

uploaded_file = st.file_uploader(
    "Add more feedback (CSV, same columns as the bundled fixture)",
    type="csv",
    help="Kept only for this browser session; nothing is written to disk.",
)
if uploaded_file is not None:
    try:
        records = records + parse_uploaded_feedback(uploaded_file)
    except FixtureError as error:
        st.error(str(error))

products = sorted({str(record["product"]) for record in records})
selected_products = st.multiselect(
    "Products",
    options=products,
    default=products,
    help="Choose one or more products to update the table and chart.",
)
filtered_records = filter_feedback(records, selected_products)

total = len(filtered_records)
average_rating = (
    sum(int(record["rating"]) for record in filtered_records) / total if total else 0
)
metric_columns = st.columns(2)
metric_columns[0].metric("Feedback", total)
metric_columns[1].metric("Average rating", f"{average_rating:.1f}/5" if total else "—")

st.subheader("Feedback count by product")
if filtered_records:
    st.bar_chart(aggregate_by_product(filtered_records), y_label="Feedback", x_label="Product")
    st.subheader("Feedback details")
    st.dataframe(filtered_records, width="stretch", hide_index=True)
    st.download_button(
        "Download filtered feedback (CSV)",
        data=to_csv(filtered_records),
        file_name="filtered_feedback.csv",
        mime="text/csv",
    )
else:
    st.info("No feedback matches the selected products. Choose a product to repopulate the table and chart.")
    st.dataframe([], width="stretch", hide_index=True)
