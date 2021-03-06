import requests
import urllib.request
from bs4 import BeautifulSoup
import re
import string
from string import digits
import json
from ModelRecipe import ModelRecipe
import os
import base64

debug = False

def saveRecipe(linkRecipeToDownload):
    soup = downloadPage(linkRecipeToDownload)
    title = findTitle(soup)
    ingredients = findIngredients(soup)
    description = findDescription(soup)
    category = findCategory(soup)
    imageBase64 = findImage(soup)

    modelRecipe = ModelRecipe()
    modelRecipe.title = title
    modelRecipe.ingredients = ingredients
    modelRecipe.description = description
    modelRecipe.category = category
    modelRecipe.imageBase64 = imageBase64

    createFileJson(modelRecipe.toDictionary(), modelRecipe.title)

def findTitle(soup):
    titleRecipe = ""
    for title in soup.find_all(attrs={'class' : 'gz-title-recipe gz-mBottom2x'}):
        titleRecipe = title.text
    return titleRecipe

def findIngredients(soup):
    allIngredients = []
    for tag in soup.find_all(attrs={'class' : 'gz-ingredient'}):
        link = tag.a.get('href')
        nameIngredient = tag.a.string
        contents = tag.span.contents[0]
        quantityProduct = re.sub(r"\s+", " ",  contents).strip()
        allIngredients.append([nameIngredient, quantityProduct])
    return allIngredients

def findDescription(soup):
    allDescription = ""
    for tag in soup.find_all(attrs={'class' : 'gz-content-recipe-step'}):
        removeNumbers = str.maketrans('', '', digits)
        description = tag.p.text.translate(removeNumbers)
        allDescription =  allDescription + description
    return allDescription

def findCategory(soup):
    for tag in soup.find_all(attrs={'class' : 'gz-breadcrumb'}):
        category = tag.li.a.string
        return category

def findImage(soup):
    for tag in soup.find_all(attrs={'class' : 'gz-featured-image'}):
        imageURL = tag.img.get('data-src')
        imageToBase64 = str(base64.b64encode(requests.get(imageURL).content))
        imageToBase64 = imageToBase64[2:len(imageToBase64)-1]
        return imageToBase64

def createFileJson(recipes, name):
    folderRecipes = "Recipes"
    if not os.path.exists(folderRecipes):
        os.makedirs(folderRecipes)
    with open(folderRecipes + '/' + name + '.txt', 'w') as file:
     file.write(json.dumps(recipes, ensure_ascii=False))

def downloadPage(linkToDownload):
    response = requests.get(linkToDownload)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def downloadAllRecipesFromGialloZafferano():
    for pageNumber in range(1,countTotalPages() + 1):
        linkList = 'https://www.giallozafferano.it/ricette-cat/page' + str(pageNumber)
        response = requests.get(linkList)
        soup= BeautifulSoup(response.text, 'html.parser')
        for tag in soup.find_all(attrs={'class' : 'gz-title'}):
            link = tag.a.get('href')
            saveRecipe(link)
            if debug :
                break

        if debug :
            break

def countTotalPages():
    numberOfPages = 0
    linkList = 'https://www.giallozafferano.it/ricette-cat'
    response = requests.get(linkList)
    soup= BeautifulSoup(response.text, 'html.parser')
    for tag in soup.find_all(attrs={'class' : 'disabled total-pages'}):
        numberOfPages = int(tag.text)
    return numberOfPages

if __name__ == '__main__' :
    downloadAllRecipesFromGialloZafferano()
