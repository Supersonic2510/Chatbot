import json
import re
import random_responses
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet

nlp = spacy.load("en_core_web_lg")


# Load JSON data
def loadJson(file):
    with open(file) as botResponses:
        print(f"Loaded '{file}' successfully!")
        return json.load(botResponses)

# Store JSON data
responseData = loadJson("basic_response.json")
carQuestions = loadJson("car_questions.json")


def getResponse(inputString):
    messageUnfiltered = nltk.word_tokenize(inputString.lower())
    # stopWords = set(stopwords.words("english"))
    filteredMessageArray = []

    # Algorithm to get the most relevant information
    for word in messageUnfiltered:
        if word.isalnum():
            filteredMessageArray.append(word)

    inputFiltered = " ".join(filteredMessageArray)
    input = nlp(inputFiltered)
    scoreList = []

    for i in range(len(responseData)):
        response = responseData[i]
        tempScore = []
        for j in range(len(response["user_input"])):
            tempScore.insert(j, nlp(response["user_input"][j]).similarity(input))
        scoreList.insert(i, max(tempScore))

    print(scoreList)
    bestResponse = max(scoreList)
    responseIndex = scoreList.index(bestResponse)

    # score_list = []
    #
    # # Check all the responses in api
    # for response in response_data:
    #     response_score = 0
    #     required_score = 0
    #     required_words = response["required_words"]
    #
    #     # Check if there are any required words
    #     if required_words:
    #         for word in filteredMessage:
    #             if word in required_words:
    #                 required_score += 1
    #
    #     # Amount of required words should match the required score
    #     if required_score == len(required_words):
    #         # Check each word the user has typed
    #         for word in filteredMessage:
    #             # If the word is in the response, add to the score
    #             if word in response["user_input"]:
    #                 response_score += 1
    #
    #     # Add score to list
    #     score_list.append(response_score)
    #     # Debugging: Find the best phrase
    #     # print(response_score, response["user_input"])
    #
    # # Find the best response and return it if they're not all 0
    # best_response = max(score_list)
    # response_index = score_list.index(best_response)

    # Check if input is empty
    if inputFiltered == "":
        return -2

    if bestResponse > 0.80:
        return responseIndex

    return -1


responseIndex = 0

while responseIndex != 1:
    userInput = input("You: ")

    responseIndex = getResponse(userInput)
    responseString = ""

    if responseIndex < -1:
        responseString = "Please type something so we can chat :("
    elif responseIndex == -1:
        responseString = random_responses.random_string()
    elif responseIndex >= 0:
        responseString = responseData[responseIndex]["bot_response"]

    print("MyCar:", responseString)

    # # If the index is 3 then start asking car questions
    # if responseIndex == 3:
    #     #Create a car object
    #
    #     for questions in car_questions:
