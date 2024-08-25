import streamlit as st
import pandas as pd
import io

def load_file(file):
    if file.name.endswith('.xls'):
        return pd.read_excel(file, engine='xlrd')
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file, engine='openpyxl')
    elif file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        st.error("Unsupported file type")
        return None

def main():
    st.title("Student Access Management")

    # Upload files
    active_file = st.file_uploader("Upload Active Students File", type=["xls", "xlsx", "csv"])
    access_file = st.file_uploader("Upload Students with Access File", type=["xls", "xlsx", "csv"])

    if active_file and access_file:
        # Load files
        active_df = load_file(active_file)
        access_df = load_file(access_file)

        if active_df is not None and access_df is not None:
            st.subheader("Raw Students Details")
            st.dataframe(active_df, height=200)  # Display with a fixed height for scrolling

            st.subheader("Students with vUWS Access")
            st.dataframe(access_df, height=200)  # Display with a fixed height for scrolling

            # Arrange columns for selections and multiselects
            col1, col2 = st.columns(2)
            
            with col1:
                # Select columns for campuses and study paths
                campus_column = st.selectbox("Select column for Campuses", active_df.columns)
                campuses_to_exclude = st.multiselect(
                    "Select Campuses to Exclude",
                    active_df[campus_column].unique()
                )
            with col2:
                study_path_column = st.selectbox("Select column for Study Paths", active_df.columns)
                study_paths_to_include = st.multiselect(
                    "Select Study Paths to Include",
                    active_df[study_path_column].unique()
                )

            # Apply filters
            if campuses_to_exclude:
                active_df = active_df[~active_df[campus_column].isin(campuses_to_exclude)]
            if study_paths_to_include:
                active_df = active_df[active_df[study_path_column].isin(study_paths_to_include)]

            st.subheader("Filtered Active Students File")
            st.dataframe(active_df, height=200)  # Display with a fixed height for scrolling

            # Select columns to match
            active_column = st.selectbox("Select column from Active Students file to match", active_df.columns)
            access_column = st.selectbox("Select column from Students with Access file to match", access_df.columns)

            # Arrange columns for buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Find Students to Add"):
                    # Determine which students need to be added
                    students_to_add = active_df[~active_df[active_column].isin(access_df[access_column])]

                    # Option to download the result as CSV with only the User Name column
                    csv_buffer = io.StringIO()
                    students_to_add[[active_column]].to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="Download Students to Add",
                        data=csv_buffer.getvalue(),
                        file_name='students_to_add.csv',
                        mime='text/csv'
                    )

                    # Option to download filtered students in the desired format
                    student_level_column = 'Student level'  # Assuming this column name
                    formatted_students = active_df[[student_level_column, active_column]].copy()
                    formatted_students.columns = ['Group Code', 'User Name']

                    csv_buffer_formatted = io.StringIO()
                    formatted_students.to_csv(csv_buffer_formatted, index=False)
                    st.download_button(
                        label="Download Group Members List",
                        data=csv_buffer_formatted.getvalue(),
                        file_name='groupmember.csv',
                        mime='text/csv'
                    )

                    # Option to download the groups.csv file
                    try:
                        groups_df = pd.read_csv('groups.csv')
                        csv_buffer_groups = io.StringIO()
                        groups_df.to_csv(csv_buffer_groups, index=False)
                        st.download_button(
                            label="Download Groups File",
                            data=csv_buffer_groups.getvalue(),
                            file_name='groups.csv',
                            mime='text/csv'
                        )
                    except FileNotFoundError:
                        st.error("groups.csv file not found.")

            with col2:
                if st.button("Find Students to Remove"):
                    # Determine which students need to be removed
                    students_to_remove = access_df[~access_df[access_column].isin(active_df[active_column])]

                    # Option to download the result as CSV with only the User Name column
                    csv_buffer_remove = io.StringIO()
                    students_to_remove[[access_column]].to_csv(csv_buffer_remove, index=False)
                    st.download_button(
                        label="Download Students to Remove",
                        data=csv_buffer_remove.getvalue(),
                        file_name='students_to_remove.csv',
                        mime='text/csv'
                    )

if __name__ == "__main__":
    main()
