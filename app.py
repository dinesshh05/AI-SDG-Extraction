import os

import streamlit as st #type:ignore


from main import run_pipeline


st.set_page_config(
    page_title="AI Sustainability Initiative Extractor",
    page_icon="🌎",
    layout="wide"
)

st.title(
    "🌎 AI Sustainability Initiative Extractor"
)

st.markdown(
    """
Upload an Annual Report PDF and automatically extract
Sustainability and ESG initiatives mapped to UN SDGs.
"""
)

uploaded_file = st.file_uploader(
    "Upload a single Annual Report PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Only one PDF can be processed at a time."
)

if uploaded_file:

    os.makedirs(
        "input",
        exist_ok=True
    )

    pdf_path = os.path.join(
        "input",
        uploaded_file.name
    )

    with open(
        pdf_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "🚀 Run Extraction"
    ):

        try:

            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(step, total_steps, label):
                progress_bar.progress(step / total_steps)
                status_text.text(f"[{step}/{total_steps}] {label}")

            cache_db = "cache/embeddings.db"

            if os.path.exists(
                cache_db
            ):
                os.remove(
                    cache_db
                )

            output_file, validation_errors = run_pipeline(
                pdf_path,
                progress_callback=update_progress
            )

            progress_bar.progress(1.0)
            status_text.text("Done.")

            st.success(
                "✅ Extraction Completed Successfully!"
            )

            if validation_errors:

                st.warning(
                    f"⚠️ {len(validation_errors)} extracted record(s) "
                    f"failed validation and were excluded from the report."
                )

                with st.expander("Show validation error details"):

                    for err in validation_errors:
                        st.text(err["reason"])

            if os.path.exists(
                output_file
            ):

                with open(
                    output_file,
                    "rb"
                ) as file:

                    st.download_button(
                        label="📥 Download Excel Report",
                        data=file,
                        file_name="sustainability_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        except Exception as e:

            st.error(
                f" Error: {str(e)}"
            )