import json
import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

import mysql.connector
import nltk
import requests
import spacy
import xmltodict as xmltodict
from mysql.connector import Error
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from text_to_num import text2num

import random_responses
from Python.Car import Car

newInput = ""
responseString = ""
nodejsUrl = 'http://localhost:3000'
global finishedSentence
global newInputFromUser
global sqlConnection

# semaphores to do syncronism between messages
chatSentenceSem = []
serverSem = []
inputSem = threading.Semaphore(value=1)
threadList = []
threadListId = []

nlp = spacy.load("en_core_web_lg")
url = "http://localhost:3000"


# Load JSON data
def loadJson(file):
    with open(file) as botResponses:
        print(f"Loaded '{file}' successfully!")
        return json.load(botResponses)


# Store JSON data
responseData = loadJson("./Data/basic_response.json")
carQuestions = loadJson("./Data/car_questions.json")
optionSearch = loadJson("./Data/option_search.json")


def sentimentAnalyse(inputText):
    score = SentimentIntensityAnalyzer().polarity_scores(inputText)
    print(score)


# connect to sql database
def create_server_connection(host_name, user_name, user_password, mydatabase):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=mydatabase
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


# handle response from user
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

    # sentimentAnalyse(inputFiltered)

    for tok in input.doc:
        print(tok.lemma_, tok.dep_)

    scoreList = []

    # search the best response
    for i in range(len(responseData)):
        response = responseData[i]
        tempScore = []
        for j in range(len(response["user_input"])):
            tempScore.insert(j, nlp(response["user_input"][j]).similarity(input))
        scoreList.insert(i, max(tempScore))
    bestResponse = max(scoreList)
    responseIndex = scoreList.index(bestResponse)

    # Check if input is empty
    if inputFiltered == "":
        return -2

    if bestResponse > 0.80:
        return responseIndex

    return -1


# handler from input from user
class Handler(BaseHTTPRequestHandler):
    global chatSentenceSem
    global responseString

    def do_POST(self):
        global newInputFromUser
        global newInput
        contentLength = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(contentLength))

        # Check if number id not in the list

        if data["messageID"] not in threadListId:
            # Create new semaphores
            thisSentenceSem = threading.Semaphore(value=0)
            thisServerSem = threading.Semaphore(value=0)

            # Append semaphores
            chatSentenceSem.append(thisSentenceSem)
            serverSem.append(thisServerSem)
            thread = threading.Thread(target=threaded_Chatbot,
                                      args=(data["messageID"], thisSentenceSem, thisServerSem))
            thread.start()

            threadList.append(thread)
            threadListId.append(data["messageID"])

            # Wait thread to start
            serverSem[threadListId.index(data["messageID"])].acquire()

        # Block new input
        inputSem.acquire()
        newInput = data["messagePost"]
        inputSem.release()

        chatSentenceSem[threadListId.index(data["messageID"])].release()


def threaded_Chatbot(id, localChatSem, serverSem):
    global newInput
    global responseString
    global t1
    responseIndex = 0
    car = Car(optionSearch)

    serverSem.release()

    # until user says bye
    while responseIndex != 1:

        localChatSem.acquire()

        # semaphore used to protect the variable from other threads
        inputSem.acquire()
        userInput = newInput
        inputSem.release()
        # userInput = input("You: ")

        responseIndex = getResponse(userInput)
        responseString = ""

        if responseIndex < -1: # empty string
            responseString = "Please type something so we can chat :("
        elif responseIndex == -1: # did not understand
            responseString = random_responses.random_string()
        elif responseIndex >= 0: # answer
            responseString = responseData[responseIndex]["bot_response"]

        if responseIndex < 6:
            print("MyCar:", responseString)
            requests.post(nodejsUrl, json={'messagePython': responseString, "idPython": id})

        # Set a certain delay to emulate a human talking
        time.sleep(0.5)

        # If the index is 3 then start asking car questions
        if responseIndex == 3:
            # Create car object
            car = Car(optionSearch)
            questionIndex = 0
            for questions in carQuestions:

                # Print question in terminal and post in web
                print(questions["bot_input"])
                requests.post(nodejsUrl, json={'messagePython': questions["bot_input"], "idPython": id})

                localChatSem.acquire()

                # Get the answer
                inputSem.acquire()
                userInput = newInput
                inputSem.release()

                # userInput = input("You: ")

                # separate sentence and handle each of them individually
                listSentences = list(
                    nlp(userInput.replace(",", ".").replace("and", ".").replace("or", ".").replace("nor", ".")).sents)

                for sentence in listSentences:
                    scoreList = [[]]
                    tempList = []
                    tempListIndex = []
                    for i in range(len(questions["user_input"])):
                        tempScore = []
                        for j in range(len(questions["user_input"][i])):
                            tempScore.insert(j, sentence.as_doc().similarity(nlp(questions["user_input"][i][j])))
                        tempList.insert(i, max(tempScore))
                        tempListIndex.insert(i, tempScore.index(max(tempScore)))
                    scoreList.insert(0, tempList)
                    scoreList.insert(1, tempListIndex)

                    bestScore = max(scoreList[0])
                    bestIndex = [scoreList[0].index(max(scoreList[0]))][0]

                    print("Best Score:", bestScore)
                    print("Best Index:", bestIndex)

                    if questionIndex == 2:
                        if bestIndex == 2:
                            # calculate auxiliary responses
                            print("My Car:", "How many members are you in the family?")
                            requests.post(nodejsUrl, json={'messagePython': "How many members are you in the family?",
                                                           "idPython": id})

                            localChatSem.acquire()

                            # Get the answer
                            inputSem.acquire()
                            userInput = newInput
                            inputSem.release()

                            # userInput = input("You: ")

                            sentenceFam = nlp(userInput)

                            numberPeople = []
                            for ent in sentenceFam.ents:
                                if ent.label_ == "CARDINAL":
                                    if ent.text.isdigit():
                                        numberPeople.append(int(ent.text))
                                    else:
                                        numberPeople.append(text2num(ent.text.lower(), "en"))

                            print("My Car:", "Will you use the car with your family?")
                            requests.post(nodejsUrl, json={'messagePython': "Will you use the car with your family?",
                                                           "idPython": id})

                            localChatSem.acquire()

                            # Get the answer
                            inputSem.acquire()
                            userInput = newInput
                            inputSem.release()

                            # userInput = input("You: ")

                            questionsFamily = [["no", "sometimes", "don't know"], ["yes", "maybe", "often", "for sure"]]
                            tempScoreFamEnd = []
                            sentenceFam = nlp(userInput)

                            for questionFam in questionsFamily:
                                tempScoreFam = []
                                for i in range(len(questionFam)):
                                    tempScoreFam.insert(i, sentenceFam.similarity(nlp(questionFam[i])))

                                tempScoreFamEnd.append(max(tempScoreFam))

                            if tempScoreFamEnd.index(max(tempScoreFamEnd)) == 1 and max(numberPeople) > 2:
                                # Add the value of door numbers to 4
                                car.setCharacteristic(questionIndex, 4)
                    else:
                        # if best index > 0.80, process information
                        if bestIndex > 0 and bestScore > 0.90:
                            car.setCharacteristic(questionIndex, bestIndex)

                questionIndex += 1

            # Respond the user with suggestion if list belows 10000
            print("My Car:", "Perfect, we have here your recommendation!")
            requests.post(nodejsUrl,
                          json={'messagePython': "Perfect, we have here your recommendation!", "idPython": id})

            # query from database to get a recommendation
            sqlQuery = "select car.brand, car.model, car.year, car.engine, car.cylinders, car.transmissionType, car.drivenWheels, car.doors, car.size, car.style, car.MSRP from car where car.year >= 2010"

            # add info to car skeleton
            if not car.isEmpty():
                for size in car.size:
                    sqlQuery += " and"
                    sqlQuery += (" car.size = \"" + size + "\"")

                for brand in car.brand:
                    sqlQuery += " and"
                    sqlQuery += (" car.brand = \"" + brand + "\"")

                if car.numberDoors is not None:
                    sqlQuery += " and"
                    sqlQuery += (" car.doors = " + str(car.numberDoors))

                for extraUrbanMileage in car.extraUrbanMileage:
                    sqlQuery += " and"
                    sqlQuery += (" car.extraUrbanMileage >= " + str(extraUrbanMileage))

                for urbanMileage in car.urbanMileage:
                    sqlQuery += " and"
                    sqlQuery += (" car.urbanMileage >= " + str(urbanMileage))

            sqlQuery += " order by car.MSRP asc;"

            mycursor = sqlConnection.cursor(buffered=True)
            # execute query
            mycursor.execute(sqlQuery)

            myresult = mycursor.fetchone()

            if bool(myresult):
                carName = myresult[0] + " " + myresult[1] + " " + str(myresult[2])
                enginePower = myresult[3]
                engineCylinders = myresult[4]
                transmission = myresult[5]
                drivenWheel = myresult[6]
                doors = myresult[7]
                carSize = myresult[8]
                carStyle = myresult[9]
                price = myresult[10]

                # Finish with the result (image API call)
                carUrl = "http://www.carimagery.com/api.asmx/GetImageUrl"
                params = {"searchTerm": carName}
                response = requests.get(carUrl, params=params)
                imageUrl = xmltodict.parse(response.text)["string"]["#text"]

                # Create the string name
                file = carName + ".jpg"
                filename = "./Images/" + file

                # Retreive the value
                urllib.request.urlretrieve(imageUrl, filename)

                # Post the image to the Whatsapp
                requests.post(nodejsUrl, json={"messageImageFile": filename,
                                               "messageImageName": file,
                                               "messageImageCaption":
                                                   ("Check this out! What do you think about it? *" + carName + "*\n\n"
                                                    + "·Engine Power:" + str(enginePower)
                                                    + "\n·Cylinders:" + str(engineCylinders)
                                                    + "\n·Transmission:" + transmission
                                                    + "\n·Driven Wheel:" + drivenWheel
                                                    + "\n·Doors:" + str(doors)
                                                    + "\n·Size:" + carSize
                                                    + "\n·Style:" + carStyle
                                                    + "\n·MSRP:" + str(price)),
                                               "idPython": id})

                # Removing the image after usage
                os.remove(filename)

                # create a new object again
                car = Car(optionSearch)

            else:
                time.sleep(0.5)
                requests.post(nodejsUrl,
                              json={'messagePython': "Sorry, we could not find a car specific to your preferences :(",
                                    "idPython": id})


if __name__ == '__main__':
    sqlConnection = create_server_connection("localhost", "root", "", "mycar_database")
    # t1 = threading.Thread(target=threaded_Chatbot)
    # t1.start()
    with HTTPServer(("localhost", 3030), Handler) as server:
        server.serve_forever()
