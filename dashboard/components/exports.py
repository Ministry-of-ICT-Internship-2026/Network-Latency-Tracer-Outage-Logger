import streamlit as st

from server.reports import ReportGenerator



def render_exports(analytics):
    """
    Display report export controls.
    """


    st.subheader(
        "Export Reports"
    )


    report_generator = ReportGenerator(
        analytics
    )


    col1, col2, col3, col4 = st.columns(4)



    # ---------------------------------
    # Latency CSV
    # ---------------------------------

    with col1:

        if st.button(
            "📡 Export Latency CSV"
        ):

            try:

                path = (
                    report_generator
                    .export_latency_csv()
                )


                with open(
                    path,
                    "rb"
                ) as file:


                    st.download_button(
                        label="Download latency.csv",
                        data=file,
                        file_name=path.name,
                        mime="text/csv"
                    )


            except Exception as e:

                st.error(
                    f"Latency export failed: {e}"
                )



    # ---------------------------------
    # Outage CSV
    # ---------------------------------

    with col2:

        if st.button(
            "🚨 Export Outage CSV"
        ):

            try:

                path = (
                    report_generator
                    .export_outage_csv()
                )


                with open(
                    path,
                    "rb"
                ) as file:


                    st.download_button(
                        label="Download outage.csv",
                        data=file,
                        file_name=path.name,
                        mime="text/csv"
                    )


            except Exception as e:

                st.error(
                    f"Outage export failed: {e}"
                )



    # ---------------------------------
    # Summary CSV
    # ---------------------------------

    with col3:

        if st.button(
            "📊 Export Summary CSV"
        ):

            try:

                path = (
                    report_generator
                    .export_summary_csv()
                )


                with open(
                    path,
                    "rb"
                ) as file:


                    st.download_button(
                        label="Download summary.csv",
                        data=file,
                        file_name=path.name,
                        mime="text/csv"
                    )


            except Exception as e:

                st.error(
                    f"Summary export failed: {e}"
                )



    # ---------------------------------
    # PDF Report
    # ---------------------------------

    with col4:

        if st.button(
            "📄 Generate PDF"
        ):

            try:

                path = (
                    report_generator
                    .export_pdf_report()
                )


                with open(
                    path,
                    "rb"
                ) as file:


                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name=path.name,
                        mime="application/pdf"
                    )


            except Exception as e:

                st.error(
                    f"PDF generation failed: {e}"
                )