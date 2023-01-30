from scripts.site_assignments import *
#Reused
complete_this_stage_later = lambda x: \
    "If you need more time to complete these instructions before proceeding, press Ctrl-C and then the 'Enter' button to exit. The next time you run this program, you need to start from Stage {}\n".format(x)
google_form_instructions = lambda url, person, new_name: "Copy-paste the following url: {}This links to a premade google form. Copy the google form and add any extra ".format(url) + \
    "questions if necessary but do not alter what is already there. Once {} have finished entering their responses, open the responses in google sheets ".format(person) + \
    "and then download it as an Excel file into the data subfolder. Rename the excel file as {}. Once you are done, type in 'done'".format(new_name)
site_assignments_context = "After each set of site assignments is displayed, you will have the opportunity to either keep it or get a new one by either typing " + \
    "'yes' or 'no', respectively. Although the script does work, make sure to check the results just in case."

# Intro
intro_text = "There are a few stages in this process but I promise you that this will take less time than actually doing this by hand.\n" + \
    "There are four stages. Start at Stage 1. It is expected that you will complete one stage and cannot move onto the next stage until " + \
    "you collect data or need some extra time. That is okay because you can just go to the stage which you have not completed without " + \
    "having to redo everything. Just make sure you do not delete any files that were already existing. If you realize that you need to change some of the spreadsheets that you put into the data subfolder, that's fine.\n\n" + \
    "Here are the four stages:\nStage 1: Collect school availability data & site leader availability data\nStage 2: Create sites\nStage 3: " + \
    "Collect availabilities from the rest of decal\nStage 4: Collect results\n\nWhich stage are you on? Enter a number from 0 to 4\n"
stage_number_error = 'The stage number must be an integer ranging from 0 to 4(inclusive). Try again.'


# Stage 1
stage1a = "Let's get started on Stage 1. There is a pre-made excel spreadsheet in the templates subfolder titled 'school_availabilities.xlsx'. Copy it into the data subfolder and fill the copied spreadsheet with availabilities from each school. \n" + \
    "\nThe spreadsheet will have columns for the school name, each day of the week, the ideal number of sites, and any extra notes you want to write in. Note that times should be written in the same format(capitalization, spacing, etc.) as '11:00AM" + \
    "-12:00PM' in the event that the site time crosses from morning to afternoon or similar to '2:00-3:00PM' if the time of day is the same. If there are multiple sites that can operate at the same school, separate each time with commas and if more than " + \
    "one site can operate at the same location during the same time, you will need to write out the given time for as many sites that have that time. Also, please ensure that the spellings of the school are also correct. Once you have finished populating the spreadsheet with the necessary details, " + \
    "type in 'done'.\n"

url1 = "[INSERT URL1]"
stage1b = "Excellent! Now, we need to collect responses from site leaders to get their availabilities and confirm our sites. " + google_form_instructions(url1, 'all site leaders', 'site_leader_availabilities.xlsx') + "\n"

#Stage 2
stage2 = "We are now on Stage 2. A script is going to show you the various sites and the site leaders who are assigned." + site_assignments_context + complete_this_stage_later(2)
no_approval = "Oof. Let's try again."
does_this_work = "Do these site assignments work? Type either 'yes' or 'no'.\n\n"

#Stage 3
url2 = "[INSERT URL2]"
stage3 = "Excellent! The spreadsheet containing the confirmed site leaders will be saved as 'confirmed_sites.xlsx' under the data subfolder. We are now onto stage 3. Now you need to collect availabilities from the rest of decal(not including site leaders). " + \
    google_form_instructions(url2, 'the other decal members', 'confirmed_sites.xlsx') + "\n" + complete_this_stage_later(3)

#Stage 4
stage4 = "We are now on Stage 4!!! You are almost done! You will now be shown site assignments for everyone in decal.\n" + site_assignments_context + "\n" + complete_this_stage_later(4)

#Done
end_text = "Excellent! You can now see the results in the data subfolder. The excel spreadsheet should be titled as 'confirmed_sites.xlsx'. Congrats on getting your site assignments. Hope y'all have a great semester!"

#Errors
yes_no_error = "The only acceptable answers are either 'yes' or 'no'. Try again."
done_error = "In order to advance, you must type 'done'. Try again."


#Functions
def get_input_from_user(text, error_message, accepted_values, return_type = str):
    user_input = input(text).lower()
    while user_input not in accepted_values:
        user_input = input(error_message).lower()
    return return_type(user_input)

def get_site_assignments_approval(text):
    print(text)
    #run code
    user_approval = get_input_from_user(does_this_work, yes_no_error, ['yes', 'no'])
    #run code
    while user_approval != 'yes':
        print(no_approval + "\n\n")
        #run code
        user_approval = get_input_from_user(does_this_work, yes_no_error, ['yes', 'no'])

def split_at_80_characters(text):
    pass
def separate_stages():
    print("\n\n-----------------------------------------------------------\n\n")

if __name__ == "__main__":
    stage_number = get_input_from_user(intro_text, stage_number_error, ['1', '2', '3', '4'], int)
    separate_stages()
    if stage_number == 1:
        finished = get_input_from_user(stage1a, done_error, ['done'])
        print("\n\n")
        finished = get_input_from_user(stage1b, done_error, ['done'])
        stage_number += 1
        separate_stages()
    if stage_number == 2:
        get_site_assignments_approval(stage2)
        stage_number += 1
        separate_stages()
    if stage_number == 3:
        finished = get_input_from_user(stage3, done_error, ['done'])
        stage_number += 1
        separate_stages()
    if stage_number == 4:
        get_site_assignments_approval(stage4)
        print(end_text)


    