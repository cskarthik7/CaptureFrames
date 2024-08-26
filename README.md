# Frame Capture and Server Sent Events

The aim was to capture frames from webcam with a definitive frames per second and the frames are to be displayed at a set interval.


# How to Run?

Go to the main project where you're able to see client, server, docker folders. There run

> docker-compose -f docker/docker-compose.yml up --build

With this command, the front end server will be up, with the help of NGINX and backend flask docker container along with the mongo db container as well.

Visit http://localhost:3000, and please follow the below steps:

- First set frame interval
- Then set frame interval and hit the button else the API will give 400 response.
- Then click on the "start capturing" button.

The frames retrieved from the server will be displayed down along with the color data(the color data computed here is the average of RGB values of that frame which shows any variations in the intensity of the image) and the color difference.

Detailed doc: [Capturing frame and using SSE](https://docs.google.com/document/d/1RCGA6tDyI_UBDqnz7uvpHzWHJ5KgwkFyehr7FYhASb4/edit?usp=sharing).

P.S. : Pubslishing .env file with the repo, as it doesn't contain any tokens, and setting up will be easier.


