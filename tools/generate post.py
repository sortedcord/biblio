from random import randint
from datetime import datetime


def generate_good_string(_list):
    good_string = ""
    for i in range(len(_list)):
        good_string += "    - " + _list[i] + "\n"
    return good_string


def main():

    sharing_link = input("Enter the sharing link: ")
    
    # # Use a dummy google drive sharing link for sharing_link
    # sharing_link = "https://drive.google.com/file/d/1cYeRzGqVQQJ2kCiBw_Np2vAKliuh89dX/view?usp=sharing"

    direct_link = sharing_link
    book_name = input("Enter the book name: ")
    # Set book_name as a random book name
    # book_name = "Book " + str(randint(1, 100))

    image_link = input("Enter the image link: ")
    # Use a dummy image link for image_link
    # image_link = "https://images-na.ssl-images-amazon.com/images/I/51-Q-q-qQL._SX331_BO1,204,203,200_.jpg"

    # Generate a random paraghraph of text for dummy text
    # discription = "naidfadfadfadf adfad fadf adsf ad f\nafdasfadf ads fadsf adsfadf asfadsf \n $n$"
    description = ""
    while True:
        try:
            description += input("Enter the description: ")
        except EOFError:
            break
        if "$n$" in description:
            break
    
    # get all the tags of book from user
    # and store in a list

    tags = []
    # create dummy tags
    # tags = ["tag1", "tag2", "tag3"]
    while True:
        tag = input("Enter the tag: ")
        if tag == "":
            break
        tags.append(tag)
    
    # do the same for categories
    categories = []
    # categories = ["category1", "category2", "category3"]
    while True:
        category = input("Enter the category: ")
        if category == "":
            break
        
        # If the category contains more than one word then enclose it within a pair of single quotes
        if " " in category:
            category = "'" + category + "'"

        categories.append(category)


    markdown_text = f"""---
id: {randint(1, 1000)}
title: '{book_name}'
date: '{datetime.now().strftime("%Y-%m-%d %H:%M:%S +0530")}'
author: sortedcord
layout: post
permalink: /{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/{book_name.replace(' ','-')}/
image: '{image_link}'
categories:\n"""  + generate_good_string(categories) + f"""
tags:\n"""+ generate_good_string(tags) + f"""
---



{description}

[Download PDF]({direct_link})
"""

    # write the markdown text to a file called post.md
    with open(f"{datetime.now().strftime('%Y-%m-%d')}-{book_name.replace(' ','-')}.md", "w") as f:
        f.write(markdown_text)

# define a function that takes the google drive sharing link as input as returns the direct download link as output
def generate_direct_link(sharing_link):
    direct_link = sharing_link.replace("https://drive.google.com/file/d/", "https://drive.google.com/uc?export=download&id=")
    return direct_link.split("/view")[0]

if __name__=="__main__":
    main()



