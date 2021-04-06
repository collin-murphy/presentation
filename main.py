"""
Presentation software video frontend that allows a user to update the screen on the fly
"""
import cv2 
import pyautogui
import numpy as np
import threading
import queue
import os
from datetime import datetime

SCREEN_HEIGHT = 480
SCREEN_WIDTH = 640

def show_webcam(mirror=False):
    #user input queue
    q = queue.Queue()
    user_input = None
    thread = None

    #set video capture
    cap = cv2.VideoCapture(0)

    #video codec and recording setup
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    #initialize extra image list
    extras = []

    #camera loop
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            #flip camera perspective
            if mirror:
                frame = cv2.flip(frame,1)
            

            addimages(frame, extras)
            out.write(frame)

            #display frame
            cv2.imshow('Frame',frame)
            
            #USER INPUT LOOP
            #get user input
            key = cv2.waitKey(25) & 0xFF

            #quit program
            if key == ord('q'):
                break
            
            #get filename from user
            elif key == ord("w") and thread == None:
                thread = threading.Thread(target=get_filename, args=(q,))
                thread.start()
            
            #commit filename and show image file
            elif key == ord("c") and thread != None:
                thread.join()
                filename = q.get()
                #put image in extras
                process_image(filename,frame, extras)
                
                thread = None
            #delete last image
            elif key == ord("d"):
                if len(extras) != 0:
                    extras.pop()
            #display help screen
            elif key == ord("h"):
                display_commands()
            #save screenshot of presentation
            elif key == ord("s"):
                save_screenshot(frame)

            
        else: 
            break

    out.release()
    cap.release()

    cv2.destroyAllWindows()

def save_screenshot(frame):
    directory = "screenshots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{directory}/screenshot({datetime.now()}).png"
    cv2.imwrite(filename, frame)
    print(f"\nScreenshot successfully saved at \"{filename}\"\n")
    

def process_image(filename, frame, extras):
    file_path = f"images/{filename}"
    #check if file path exists
    if not os.path.exists(file_path):
        print(f"\"{file_path}\" is not a valid file path. Try agian by pressing \"w\"\n")
        return
    
    image = cv2.imread(f"{file_path}")
    width, height, _ = image.shape

    #process image
    dim_height = SCREEN_HEIGHT//5
    dim_width = SCREEN_WIDTH//5
    dim = (dim_width, dim_height)

    correct_size_image = cv2.resize(image, dim)
    extras.append(correct_size_image)
    print(f"Displayed image #{len(extras)}")

def addimages(frame, extras):            
    start_x = 0
    start_y = 0
    for img in extras:
        height, width, _ = img.shape
        if start_y + height > SCREEN_WIDTH:
            print("Max image size achieved")
            return
        frame[0 + start_x:height + start_x, 0 + start_y:width+start_y] = img
        start_x += height
        if start_x + height > SCREEN_HEIGHT:
            start_x = 0
            start_y += width
        
def show_screen():
	image = pyautogui.screenshot()
	image = cv2.cvtColor(np.array(image),
				 cv2.COLOR_RGB2BGR)
	cv2.imshow("",image) 

def get_filename(q):
    user_input = input("Input an image filename here: ")
    q.put(user_input)



def display_commands():

    print("Type \"w\" to input a .png filename to display on screen\n" + 
        "Type \"c\" to display that image file to the screen\n" +
        "Type \"d\" to delete the last image from the screen\n" +
        "Type \"s\" to save screenshot of the current presentation\n" +
        "Type \"h\" to see these commands again\n" +
        "Type \"q\" to exit program\n")


def main():
    print("Welcome to OpenCV presentation software 1.0\n"+
                "All commands must be done with the window in focus.\n" +
                "Type \"h\" to view commands.\n")
    directory = "images"
    if not os.path.exists(directory):
        os.makedirs(directory)
    show_webcam(mirror=True)
	#show_screen()


if __name__ == '__main__':
    main()
