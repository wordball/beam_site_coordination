import streamlit as st
from classes import *
import pandas as pd
from main3 import *
import io


def excel_download_button(dfs: pd.DataFrame,
                          file_name: str) -> None:
    assert ".xlsx" in file_name, "File name must have the '.xlsx' extension"
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for i, df in enumerate(dfs):
            df.to_excel(writer,
                        sheet_name=f"Sheet{i+1}",
                        index=False)
        writer.close()

    download_button = st.download_button(
        "Download generated site maps as an Excel file",
        data=buffer, file_name=file_name)
    return download_button


st.write("# Instructions")
st.write(
    "1. Determine who you're trying to assign to sites.\n"
    "2. Upload your site map as an Excel file. It can either have people "
    "assigned already or it can be empty.\n"
    "At minimum, it must have the following columns: Site, District, Day, Time.\n"
    "Or you can include site maps where all the site leaders are assigned or all of staff has been "
    "assigned already. \n"
    "3. Upload all the relevant google form response spreadsheets as Excel files\n"
    "4. Hit the 'Generate Site Map' button and download the results.\n"
    "5. If you need more responses to completely fill out the site map "
    "(e.g. non-SL staff members, decal members), you will need to run this web app "
    "again. \nIn that case, you need to choose one of the generated site maps "
    "and feed it in as input the next time you run this program."
)


st.write("### ")
st.write("### Configuration")
options = ["Site Leaders", "Staff members (Excluding Site Leaders)",
           "Nonstaff/Decal Members"]
mappings = {options[0]: SiteLeader,
            options[1]: StaffMember,
            options[2]: DecalMember}
string_person_class = st.selectbox(
    "Who are you trying to assign to sites?", options=options)
int_number_trials = st.slider(
    "Desired number of generated site maps - No guarantees though :)",
    min_value=1, max_value=20, value=1, step=1)
int_time_tolerance = st.slider(
    "Time Tolerance", min_value=0, max_value=60, value=0, step=5)
person_class = mappings[string_person_class]




files = []
f_type = ".xlsx"
st.write("### ")
st.write("### File Uploads")
files.append(st.file_uploader(
    "Site Map", type=f_type))
files.append(st.file_uploader(
    "Site Leader Google Form Responses", type=f_type))
if person_class != SiteLeader:
    files.append(st.file_uploader(
        "Staff (Excluding Site Leaders) Google Form Responses", type=f_type))
if person_class == DecalMember:
    files.append(st.file_uploader(
        "Decal Member/Nonstaff Google Form Responses - "
        "Only include accepted decal members", type=".xlsx"))
st.write("### ")
st.write("### Warnings")
st.write(
    "1. Time tolerance should ideally be 0. This parameter represents how much "
    "leeway you have if there's not enough people signed up for a time (spoiler alert: "
    "you're going to have to assign some people who didn't sign up for it to that site).\n"
    "2. The number of generated site arrangements is not guaranteed to be what you want.\n"
    "3. This program relies on every single person filling out the google form (includes Site Coords)."
)


st.write("# ")
st.write("# Generate Site Maps")
counter = 0


if st.button("Run"):
    output_buffer = io.StringIO()
    sys.stdout = output_buffer

    counter+=1
    if counter > 0:
        eliminate_everything()

    if not all(file for file in files):
        st.error("You need to upload/reupload all the pertinent files!")
    else:
        dfs = [pd.read_excel(files[i]) if len(files) >= i+1 else None
                for i in range(4)]

        initial_read(*dfs, int_time_tolerance)
        outputs = master_func(person_class, int_number_trials)
        outputs_db = excel_download_button(outputs, "output_site_map.xlsx")

        log_contents = output_buffer.getvalue()
        sys.stdout = sys.__stdout__
        useful_details = st.download_button(
            label="Download Useful Details",
            data=log_contents,
            file_name="logs.txt",
            mime="text/plain")











