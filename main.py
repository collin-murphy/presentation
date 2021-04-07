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

#GLOBAL VARIABLES
SCREEN_HEIGHT = 480
SCREEN_WIDTH = 640
SMALL_SCREEN_HEIGHT = SCREEN_HEIGHT // 5
SMALL_SCREEN_WIDTH = SCREEN_WIDTH // 5
BLACK_SCREEN = np.zeros((SCREEN_HEIGHT,SCREEN_WIDTH,3), np.uint8)

def show_webcam(mirror=False):
    #user input queue
    q = queue.Queue()
    string_q = queue.Queue()
    user_input = None
    thread = None
    mirror = True
    #set video capture
    cap = cv2.VideoCapture(0)

    directory = "videos"
    if not os.path.exists(directory):
        os.makedirs(directory)
    #video codec and recording setup
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_out_filename = f"videos/recording({datetime.now()}).avi"
    out = cv2.VideoWriter(video_out_filename, fourcc, 20.0, (SCREEN_WIDTH, SCREEN_HEIGHT))


    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    #initialize extra image list
    extras = []
    last_image = BLACK_SCREEN
    screen = BLACK_SCREEN
    camera = True
    picture = False
    string = ""

    #camera loop
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            #flip camera perspective
            if mirror: 
                cam = cv2.flip(frame,1)
            else:
                cam = frame
            if camera == False:
                small_cam = cv2.resize(cam, (SMALL_SCREEN_WIDTH, SMALL_SCREEN_HEIGHT))
                frame = screen
                frame[0:SMALL_SCREEN_HEIGHT, SCREEN_WIDTH - SMALL_SCREEN_WIDTH:SCREEN_WIDTH] = small_cam

            elif picture == True:
                small_cam = cv2.resize(cam, (SMALL_SCREEN_WIDTH, SMALL_SCREEN_HEIGHT))
                frame = last_image
                frame[0 : SMALL_SCREEN_HEIGHT, SCREEN_WIDTH - SMALL_SCREEN_WIDTH:SCREEN_WIDTH] = small_cam
            elif mirror:
                frame = cam

            add_images(frame, extras)
            display_text(frame, string)
            out.write(frame)

            #display frame
            cv2.imshow('Frame',frame)
            
            #USER INPUT LOOP
            #get user input
            key = cv2.waitKey(25) & 0xFF

            #quit program
            if key == ord('q'):
                save_video(out,cap, video_out_filename)
                break
            
            #get filename from user
            elif key == ord("w") and thread == None:
                thread = threading.Thread(target=get_filename, args=(q,))
                thread.start()
            
            #commit filename and show image file
            elif key == ord("c") and thread != None:
                thread.join()
                #put image in extras
                process_image(q.get(),frame, extras)
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
            elif key == ord("m"):
                screen = cv2.resize(show_screen(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                camera = not camera
            elif key == ord("i"):
                if thread != None:
                    thread.join()
                    last_image = get_last_image(q.get())
                    thread = None
                picture = not picture
            elif key == ord("r"):
                #reset logic
                save_video(out, cap, video_out_filename)
                main()
            elif key == ord("t"):
                if thread != None:
                    thread.join()
                thread = threading.Thread(target = get_string, args=(q,))
                thread.start()
            elif key == ord("p") and thread != None:
                thread.join()
                thread = None
                string = q.get()
            elif key == ord("f"):
                mirror = not mirror
                
        else: 
            break


def save_video(out, cap, video_out_filename):
    out.release()
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nVideo successfully saved at \"{video_out_filename}\"\n")

def save_screenshot(frame):
    directory = "screenshots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{directory}/screenshot({datetime.now()}).png"
    cv2.imwrite(filename, frame)
    print(f"\nScreenshot successfully saved at \"{filename}\"\n")
    

def get_last_image(filename):
    file_path = f"images/{filename}"
    #check if file path exists
    if not os.path.exists(file_path):
        print(f"\"{file_path}\" is not a valid file path. Try agian by pressing \"w\"\n")
        return BLACK_SCREEN
    
    image = cv2.imread(f"{file_path}")
    width, height, _ = image.shape

    return cv2.resize(image, (SCREEN_WIDTH,SCREEN_HEIGHT))

def process_image(filename, frame, extras):
    file_path = f"images/{filename}"
    #check if file path exists
    if not os.path.exists(file_path):
        print(f"\"{file_path}\" is not a valid file path. Try agian by pressing \"w\"\n")
        return
    
    image = cv2.imread(f"{file_path}")
    width, height, _ = image.shape

    #process image
    dim = (SMALL_SCREEN_WIDTH, SMALL_SCREEN_HEIGHT)
    correct_size_image = cv2.resize(image, dim)
    extras.append(correct_size_image)
    print(f"Displayed image #{len(extras)}")

def add_images(frame, extras):            
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

def display_text(frame, text = ""):
    # font
    font = cv2.FONT_HERSHEY_SIMPLEX

    # origin
    textsize = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = (SCREEN_WIDTH - textsize[0]) // 2 
    text_y = (SCREEN_HEIGHT - textsize[1]) // 2 + int(0.4 * SCREEN_HEIGHT)
    org = (text_x, text_y)
    
    # fontScale
    fontScale = 1
    
    # Red color in BGR
    color = (0, 0, 255)
    
    # Line thickness of 2 px
    thickness = 2
    
    # Using cv2.putText() method
    frame = cv2.putText(frame, text, org, font, fontScale, 
                    color, thickness, cv2.LINE_AA, False)
        
def show_screen():
	screenshot = pyautogui.screenshot()
	screenshot = cv2.cvtColor(np.array(screenshot),
				 cv2.COLOR_RGB2BGR)
	return screenshot

def get_filename(q):
    user_input = input("Input an image filename here: ")
    q.put(user_input)

def get_string(q):
    user_input = input("Input string: ")
    q.put(user_input)


def display_commands():

    print("Type \"w\" to input a .png filename to be used with other commands\n" + 
        "Type \"c\" to display a small version of that image on the left side of the screen\n" +
        "Type \"i\" to toggle camera with last image inputted\n" +
        "Type \"d\" to delete the last image from the screen\n" +
        "Type \"s\" to save screenshot of the current presentation\n" +
        "Type \"m\" to toggle monitor screencap instead of camera\n" +
        "Type \"t\" to type text to be displayed on screen\n" +
        "Type \"p\" to display text\n" +
        "Type \"f\" flip camera\n" +
        "Type \"r\" to restart program and save video\n" +
        "Type \"h\" to display these commands again\n" +
        "Type \"q\" to exit program\n")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Welcome to OPS 1.0 (OpenCV Presentation Software) \n"+
                "All commands must be done with the window in focus.\n" +
                "Type \"h\" to view commands.\n")
    directory = "images"
    if not os.path.exists(directory):
        os.makedirs(directory)
    show_webcam()

if __name__ == '__main__':
    main()
