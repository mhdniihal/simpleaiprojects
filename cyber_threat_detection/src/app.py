import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from prediction import predict_network_flow


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Network Intrusion Detector",
    page_icon="🛡️",
    layout="wide"
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🛡️ Network Intrusion Detection System")

st.write(
    "Upload network-flow data to detect BENIGN and ATTACK traffic."
)

st.caption(
    "Machine Learning Model: Random Forest | "
    "Operational Threshold: 0.30"
)


# ---------------------------------------------------------
# File upload
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Network Flow CSV",
    type=["csv"]
)


# ---------------------------------------------------------
# Process uploaded file
# ---------------------------------------------------------

if uploaded_file is not None:

    try:

        data = pd.read_csv(uploaded_file)

        st.subheader("📄 Uploaded Data")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Records",
                f"{len(data):,}"
            )

        with col2:
            st.metric(
                "Input Features",
                data.shape[1]
            )

        with st.expander("Preview uploaded data"):

            st.dataframe(
                data.head(),
                use_container_width=True
            )


        # -------------------------------------------------
        # Analyze button
        # -------------------------------------------------

        if st.button(
            "🔍 Analyze Traffic",
            type="primary"
        ):

            with st.spinner(
                "Analyzing network traffic..."
            ):

                predictions, probabilities = (
                    predict_network_flow(data)
                )


            # -------------------------------------------------
            # Create results
            # -------------------------------------------------

            results = data.copy()

            results["Attack_Probability"] = (
                probabilities * 100
            ).round(2)

            results["Prediction"] = predictions


            # -------------------------------------------------
            # Statistics
            # -------------------------------------------------

            total_records = len(results)

            attack_count = (
                results["Prediction"] == "ATTACK"
            ).sum()

            benign_count = (
                results["Prediction"] == "BENIGN"
            ).sum()

            attack_rate = (
                attack_count / total_records
            ) * 100


            # -------------------------------------------------
            # Results header
            # -------------------------------------------------

            st.subheader("📊 Detection Results")


            # -------------------------------------------------
            # Metrics
            # -------------------------------------------------

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Total Flows",
                    f"{total_records:,}"
                )

            with col2:

                st.metric(
                    "🟢 BENIGN",
                    f"{benign_count:,}"
                )

            with col3:

                st.metric(
                    "🔴 ATTACK",
                    f"{attack_count:,}"
                )

            with col4:

                st.metric(
                    "Attack Rate",
                    f"{attack_rate:.2f}%"
                )


            # -------------------------------------------------
            # Detection status
            # -------------------------------------------------

            if attack_count > 0:

                st.error(
                    f"⚠️ {attack_count:,} suspicious "
                    f"network flow(s) detected."
                )

            else:

                st.success(
                    "✅ No attack traffic detected."
                )
            # -------------------------------------------------
            # Attack alerts
            # -------------------------------------------------

            st.subheader("🚨 Attack Alerts")

            attack_results = results[
                results["Prediction"] == "ATTACK"
            ].copy()

            if not attack_results.empty:

                st.warning(
                    f"{len(attack_results):,} suspicious "
                    "network flow(s) require attention."
                )

                # Create analyst-friendly alert information.
                attack_alerts = pd.DataFrame({
                    "Flow": attack_results.index + 1,
                    "Attack Probability": (
                        attack_results["Attack_Probability"]
                    ).map(
                        lambda x: f"{x:.2f}%"
                    ),
                    "Status": "🔴 ATTACK"
                })

                st.dataframe(
                    attack_alerts,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "🟢 No attack traffic detected."
                )

                st.info(
                    "All analyzed network flows are below "
                    "the operational attack threshold."
                )
            # -------------------------------------------------
            # Attack probability visualization
            # -------------------------------------------------

            st.subheader("📈 Attack Probability Analysis")

            flow_numbers = list(
                range(1, total_records + 1)
            )

            probability_percentages = (
                probabilities * 100
            )


            fig = go.Figure()


            # Attack probability line
            fig.add_trace(
                go.Scatter(
                    x=flow_numbers,
                    y=probability_percentages,
                    mode="lines+markers",
                    name="Attack Probability",
                    hovertemplate=(
                        "Flow: %{x}<br>"
                        "Attack Probability: %{y:.2f}%"
                        "<extra></extra>"
                    )
                )
            )


            # Operational threshold
            fig.add_hline(
                y=30,
                line_dash="dash",
                annotation_text="Attack Threshold: 30%",
                annotation_position="top right"
            )


            # Chart layout
            fig.update_layout(
                xaxis_title="Network Flow",
                yaxis_title="Attack Probability (%)",
                yaxis=dict(
                    range=[0, 100]
                ),
                hovermode="x unified",
                height=450
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


            st.caption(
                "Flows with attack probability ≥ 30% "
                "are classified as ATTACK."
            )

            # -------------------------------------------------
            # Results table
            # -------------------------------------------------

            st.subheader("📋 Detailed Predictions")

            display_results = results[
                [
                    "Attack_Probability",
                    "Prediction"
                ]
            ].copy()

            display_results[
                "Attack_Probability"
            ] = display_results[
                "Attack_Probability"
            ].map(
                lambda x: f"{x:.2f}%"
            )

            st.dataframe(
                display_results,
                use_container_width=True,
                hide_index=False
            )


            # -------------------------------------------------
            # Download results
            # -------------------------------------------------

            csv_output = results.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="📥 Download Prediction Results",
                data=csv_output,
                file_name="prediction_results.csv",
                mime="text/csv"
            )


    except Exception as error:

        st.error(
            f"❌ Unable to analyze the uploaded file:\n\n{error}"
        )