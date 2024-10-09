# importing necessary libraries
import cloudscraper
import bs4
import os, json
from tkinter import *
import tkinter as tk
from tkinter import ttk
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter.messagebox import showinfo

############################################################
#   Initialization
############################################################

# Creating a dictionary, lists to make a nested dictionary and the id, setting the limit not to scroll the entire list of notes
website_notes_dict = {}
brand_list = []
perfumes_list = []
# id to be used as an iterator for the dictionary
id = 1
limit = 20

############################################################
#   Scraping
############################################################

# scraping the website using cloudscraper to bypass the security
scraper = cloudscraper.create_scraper()
html = scraper.get("https://www.fragrantica.com/notes/").text

###########
# Scraping all urls of notes
###########

# parsing the html to retrieve all the links with notes
soup = bs4.BeautifulSoup(html, "lxml")
# this loop allows to retrieve all a tags
for link in soup.find_all("a"):
    # checking if a tags start with a specified url structure
    if link["href"].startswith("https://www.fragrantica.com/notes/"):
        # creating a nested dictionary to store previously retrieved links that comply with the previous condition
        website_notes_dict[id] = {}
        # storing links in the dictionary
        website_notes_dict[id]['website'] = link['href']

        # a limit added in order to optimize scraping and to avoid scraping more than 1000 notes
        if id == limit: break

        # incrementing the iterator to add new entries to the dictionary
        id += 1

###########
# Result: Entries with urls of notes
# The dictionary at this stage looks likes: {1: {website: www.SOMETHING.com}, 2:{website: www.SOMETHING.com}, ... }
###########

# resetting the iterator to use it on the next loop
id = 1

###########
# Scraping all notes names and associated perfumes (incl. perfumes names, brands, perfumes names urls)
###########

#  Accessing urls from the nested dictionary
for website_url in website_notes_dict:
     # "Extracting" a url to be scraped
     url = website_notes_dict[id]['website']
     # Parsing and scraping a url with notes to get notes names
     html = scraper.get(url).text
     soup = bs4.BeautifulSoup(html, "lxml")

    ####
    # Scraping the note name in a given url of a note within a h2 tag
    ####
     for note_name in soup.find_all("h2"):
        # transforming note_name into str to be able to manipulate it
        note_name = str(note_name)
        note_name = note_name.replace("Perfumes</h2>", "")
        note_name = note_name.replace('<h2 style="clear: left; margin: 2rem;">', "")
        # Storing notes in the dictionary
        website_notes_dict[id]['name'] = note_name.rstrip()

    ###########
    # Result: The dictionary at this stage looks likes: {1: {website: www.SOMETHING.com, name: note_name1}, ... }
    ###########

    ####
    # For a given url of a note scraping the perfume information (perfume name, brand, url of the perfume) and storing it into a list
    ####

    # getting perfumes information from notes urls
     for perfume_link in soup.find_all("a"):
        # checking if a tags start with a specified structure
        if perfume_link["href"].startswith("/perfume/"):
            # getting the perfumes names
            # getting all perfumes with brands (removing extra lines between perfumes names)
            perfumes = perfume_link.get_text().replace("\n", "").strip()

            # getting the name of the brand
            brand = perfume_link["href"]
            brand = brand.replace("/perfume/", "")
            separator = '/'
            # creating a list and retrieving only the brand name
            stripped = brand.split(separator, 1)[0]
            # removing unnecessary symbols from the brand names
            stripped = stripped.replace("-", " ")

            # getting perfumes urls
            perfume_link["href"] = "https://www.fragrantica.com" + perfume_link["href"]
            # perfume_link["href"] = str(perfume_link["href"])

            # appending a list with perfumes information (perfume name, brand, url of the perfume) to perfumes_list to create a nested list
            perfumes_list.append([perfumes,stripped,perfume_link["href"]])
            # storing perfumes_list into the dictionary
            website_notes_dict[id]['perfumes'] = perfumes_list

    ###########
    # Result: The dictionary at this stage looks likes:
    # {1: {website: www.SOMETHING.com, name: note_name1, perfumes: [[PerfumeName, Brand, PerfumeNameUrl],[PerfumeName, Brand, PerfumeNameUrl],...]}, ... }
    ###########

     # limit the code to a specified number of perfumes notes
     if id == limit: break

     # necessary to clean the list after finishing the current loop
     perfumes_list = []
     perfume_link = []

     # allow the incrementation of ID each time it loop
     id += 1

# Resetting the value
id = 1

############################################################
#   3. Data preparation for interface
############################################################

notes_dropdown = []
brand_dropdown = []

for id in website_notes_dict:
    # getting notes names from the dictionary and writing them in the dropdown list
    value = website_notes_dict[id]['name']
    notes_dropdown.append(value)

    # cleaning perfumes links by removing recurring links from the "Reviews" section depicted on the page
    uncleaned_length = len(website_notes_dict[id]['perfumes'])
    length = uncleaned_length - 15
    del website_notes_dict[id]['perfumes'][length:]

    # getting brands from the dictionary and writing them in the dropdown list
    for count in range(length):
        brand_dropdown.append(website_notes_dict[id]['perfumes'][count][1])

# removing duplicates in brand list
brand_dropdown = list(dict.fromkeys(brand_dropdown))

############################################################
#   Interface
############################################################

# interface creation
root = tk.Tk()

# configuring the root window
root.geometry('700x500')
root.resizable(False, False)
root.title("Fragrantica Perfumes")
root.config(bg='#FA8072')

frame = Frame(root, bg='#FA8072')
frame.pack(expand=True)

# creating a label
Label(
    frame,
    bg='#FA8072',
    font = ('Georgia',21,'bold','italic'),
    text='Please select notes:'
    ).pack(pady=15)

entry1 = AutocompleteCombobox(
    frame,
    width=30,
    font=('Times', 18),
    completevalues=notes_dropdown
    )
entry1.pack(pady=15)

entry2 = AutocompleteCombobox(
    frame,
    width=30,
    font=('Times', 18),
    completevalues=notes_dropdown
    )
entry2.pack(pady=15)

Label(
    frame,
    bg='#FA8072',
    font = ('Georgia',21,'bold','italic'),
    text='Please select the brand:'
    ).pack(pady=15)

entry3 = AutocompleteCombobox(
    frame,
    width=30,
    font=('Times', 18),
    completevalues=brand_dropdown
    )
entry3.pack(pady=15)

############################################################
#   Getting inputs & checking for results
############################################################

def save_entry(entry):
    save_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
    name_of_file = 'Perfume Search Result'
    input1 = entry1.get()
    input2 = entry2.get()
    input3 = entry3.get()

    perfume_list_entry1 = []
    perfume_list_entry2 = []
    brand_list_entry3 = []
    match_note = []
    result = []
    result_url = []

    # navigating into the dictionary
    for id in website_notes_dict:
        value = website_notes_dict[id]['name']
        # comparing the input and the notes to access perfumes lists
        if input1 == value:
            # for the selected note getting only the perfumes names
            for count in range(len(website_notes_dict[id]['perfumes'])):
                # storing the perfumes names in the list to be compared
                perfume_list_entry1.append(website_notes_dict[id]['perfumes'][count][0])

    # performing the same steps described above for the second entry
    for id in website_notes_dict:
        value = website_notes_dict[id]['name']
        if input2 == value:
            for count in range(len(website_notes_dict[id]['perfumes'])):
                perfume_list_entry2.append(website_notes_dict[id]['perfumes'][count][0])

    # performing the same steps for the third entry
    for id in website_notes_dict:
        for count in range(len(website_notes_dict[id]['perfumes'])):
            if input3 == website_notes_dict[id]['perfumes'][count][1]:
                brand_list_entry3.append(website_notes_dict[id]['perfumes'][count][0])
        # removing duplicates from the brand list
        brand_list_entry3 = list(dict.fromkeys(brand_list_entry3))

    # comparing two lists of perfumes and storing matches in a list
    for item in perfume_list_entry1:
        if item in perfume_list_entry2:
            match_note.append(item)

    # looking for brands inside the perfumes list
    if input3 != None:
        if len(perfume_list_entry2) != 0:
            for perfume in match_note:
                if input3 in perfume:
                    result.append(perfume)
        else:
            for perfume in perfume_list_entry1:
                if input3 in perfume:
                    result.append(perfume)

    # getting the perfumes urls based on brand
    if len(perfume_list_entry1) == 0:
        for perfume in brand_list_entry3:
            for id in website_notes_dict:
                for count in range(len(website_notes_dict[id]['perfumes'])):
                    if perfume == website_notes_dict[id]['perfumes'][count][0]:
                        result_url.append(website_notes_dict[id]['perfumes'][count][2])
    # getting the perfumes urls based on the entries
    else:
        for id in website_notes_dict:
            if input1 == website_notes_dict[id]['name']:
                for count in range(len(website_notes_dict[id]['perfumes'])):
                    for perfume in result:
                        if perfume == website_notes_dict[id]['perfumes'][count][0]:
                            result_url.append(website_notes_dict[id]['perfumes'][count][2])

############################################################
#   Writing outputs, if any
############################################################

    # creating a txt file to write the results
    completeName = os.path.join(save_path, name_of_file + ".txt")
    with open(completeName, "w", encoding='utf-8') as f:
        # writing results if entry 1 is selected and entry 2 is empty
        if len(perfume_list_entry1) != 0 and len(perfume_list_entry2) == 0:
            # writing results if entry 3 is also selected
            if input3 != None:
                f.write("We found ")
                f.write(str(len(result)))
                f.write(" perfume(s) that match your search:")
                f.write("\n")
                for count in range(len(result)):
                    f.write("\n")
                    f.write(result[count])
                    f.write("\n")
                    f.write(result_url[count])
                    f.write("\n")
            # writing results if entry 3 is not selected
            else:
                f.write("We found ")
                f.write(str(len(perfume_list_entry1)))
                f.write(" perfume(s) that match your search:")
                f.write("\n")
                for count in range(len(perfume_list_entry1)):
                    f.write("\n")
                    f.write(perfume_list_entry1[count])
                    f.write("\n")
                    f.write(result_url[count])
                    f.write("\n")
        # writing results if entry 1 is empty and entry 2 is selected
        elif len(perfume_list_entry1) == 0 and len(perfume_list_entry2) != 0:
            f.write('Please, go to the first input field!')
        # writing results if entry 1 is empty and entry 2 is empty
        elif len(perfume_list_entry1) == 0 and len(perfume_list_entry2) == 0:
            if len(input3) != 0:
                f.write("We found ")
                f.write(str(len(brand_list_entry3)))
                f.write(" perfume(s) that match your search:")
                f.write("\n")
                for count in range(len(brand_list_entry3)):
                    f.write("\n")
                    f.write(brand_list_entry3[count])
                    f.write("\n")
                    f.write(result_url[count])
                    f.write("\n")
            # writing the result if no entry is selected
            else:
                f.write('Please make your choice')
        # writing results if entry 1 is selected and entry 2 is selected
        elif len(perfume_list_entry1) != 0 and len(perfume_list_entry2) != 0:
            # writing the result if entry 3 is empty
            if input3 == None:
                # writing the result (no result) if there is no match from entry 1 and entry 2
                if len(match_note) == 0:
                    f.write("There is no result")
                # writing the result if there are matches from entry 1 and entry 2
                else:
                    f.write("We found ")
                    f.write(str(len(match_note)))
                    f.write(" perfume(s) that match your search:")
                    f.write("\n")
                    for count in range(len(match_note)):
                        f.write("\n")
                        f.write(match_note[count])
                        f.write("\n")
                        f.write(result_url[count])
                        f.write("\n")
            # writing the result if entry 3 is selected
            else:
                # writing no result if there is no match between 3 entries
                if len(result) == 0:
                    f.write("There is no result")
                # writing the result if there is a match between 3 entries
                else:
                    f.write("We found ")
                    f.write(str(len(result)))
                    f.write(" perfume(s) that match your search:")
                    f.write("\n")
                    for count in range(len(result)):
                        f.write("\n")
                        f.write(result[count])
                        f.write("\n")
                        f.write(result_url[count])
                        f.write("\n")
        f.close()

list_of_results = [entry1, entry2, entry3]
button_save = tk.Button(root, text = "Select and proceed",
                        command = (lambda : save_entry(list_of_results))).pack(pady=15)
root.mainloop()
