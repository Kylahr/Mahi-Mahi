## OPTIONS ##

# Keybinds
fishing_key = 'up'           # Set keybind for fishing to up arrow
interact_key = 'down'        # Set interact key to down arrow
exit_key = "num9"            # Create /quit macro and bind to this key

# Button hold duration
button_hold1 = 0.3           # Minimum duration to hold a button (simulating human behavior)
button_hold2 = 0.7           # Maximum duration to hold a button (simulating human behavior)

# Run duration
duration = 4                 # Run WoW for at least 2 hours, time is set randomly

# Fishing rate
fishing_rate = 95           # Set percentage of catching fish. Best not to change it. Never make it 100
########################################################################################################

# Function to create ASCII art with dynamic text
def create_ascii_art(text):
    return f'''
       ,-.
    _n_  \\ {text}
   (---)  `-.___________________________________________________________
~^~^~|~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
     |
     |               }}<('>               }}-<#('c
     |
     |        <')"={{                             <><
     |                   }}-<#('c                           <')"={{
     |
     |                                 ><>                        
     J   
'''
import os
import random
import threading
import time
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import ImageGrab

# Global variables.
# Convert the total run duration into hours, minutes, and seconds
run_duration = random.uniform(3000, 3600) * duration
run_duration_hours = run_duration // 3600
run_duration_minutes = (run_duration % 3600) // 60
run_duration_seconds = run_duration % 60

hours = minutes = seconds = None
caught_fish = 0
failed_fish = 0
screen_width, screen_height = pyautogui.size()
handle = gw.getWindowsWithTitle('World of Warcraft')[0]
catching = True

# Define the size of the region you want to capture
width, height = 600, 150
window_width, window_height = 600, 150

# Calculate the bounding box coordinates
x = (screen_width - width) // 2
y = (screen_height - height) // 2

previous_y = None
fish_catching = False
contour_detected_time = None

# Initial HSV ranges for red
initial_lower_hue_1, initial_lower_saturation_1, initial_lower_value_1 = 166, 109, 0
initial_upper_hue_1, initial_upper_saturation_1, initial_upper_value_1 = 179, 255, 255
initial_lower_hue_2, initial_lower_saturation_2, initial_lower_value_2 = 0, 109, 0
initial_upper_hue_2, initial_upper_saturation_2, initial_upper_value_2 = 18, 255, 255

lower_hue_1, lower_saturation_1, lower_value_1 = initial_lower_hue_1, initial_lower_saturation_1, initial_lower_value_1
upper_hue_1, upper_saturation_1, upper_value_1 = initial_upper_hue_1, initial_upper_saturation_1, initial_upper_value_1
lower_hue_2, lower_saturation_2, lower_value_2 = initial_lower_hue_2, initial_lower_saturation_2, initial_lower_value_2
upper_hue_2, upper_saturation_2, upper_value_2 = initial_upper_hue_2, initial_upper_saturation_2, initial_upper_value_2

# Global stop event
global_stop_event = threading.Event()

# Function to generate random numbers
def rand_numb(x, y):
    lower_bound = x
    upper_bound = y
    random_bytes = os.urandom(4)
    random_number = int.from_bytes(random_bytes, byteorder="big")
    
    # Determine the scale factor to map the random number to the desired range
    scale_factor = (upper_bound - lower_bound) / (2**32 - 1)
    
    # Map the random integer to the range with decimals
    random_number_mapped = lower_bound + random_number * scale_factor
    return random_number_mapped

# Function to print status message
def print_status(message, length=None):
    # Get the length of the previous status message
    previous_length = len(print_status.previous_message) if hasattr(print_status, 'previous_message') else 0
    # If length is not specified, default to the length of the previous message
    if length is None:
        length = previous_length
    # Pad the new message with spaces to match the specified length
    padded_message = message.ljust(length)
    # Print the padded message with carriage return
    print("\r" + padded_message, end='', flush=True)
    # Update the length of the current message for the next iteration
    print_status.previous_message = message

# Function to catch fish
def catch_fish(stop_event):
    global fish_catching, previous_y, caught_fish, failed_fish, catching, fishing_rate
    handle = gw.getWindowsWithTitle('World of Warcraft')[0]
    # Check if the window is already active
    if gw.getActiveWindow() != handle:
        handle.activate()
    fish_catching = True
    rand_time = rand_numb(1, 3)
    
    if stop_event.wait(rand_time):
        fish_catching = False
        return
    
    if random.random() < fishing_rate / 100:  # X% chance of successful catch
        caught_fish += 1
        catching = False

        time.sleep(rand_numb(0.3, 0.7))  
        pyautogui.press(interact_key, interval=rand_numb(button_hold1, button_hold2))
        time.sleep(rand_numb(0.3, 0.9))
        
        if stop_event.wait(rand_time):
            fish_catching = False
            return
        
        time.sleep(rand_numb(0.7, 0.9)) 
        pyautogui.press(fishing_key, interval=rand_numb(button_hold1, button_hold2))
        time.sleep(rand_numb(0.05, 0.15))

        print_status("Fish caught: " + str(caught_fish) + "  Fish failed: " + str(failed_fish))
        catching = True
    else:
        failed_fish += 1
        
    fish_catching = False
    stop_event.set()  # Signal to stop the thread
    previous_y = None

def update_hsv_ranges(factor):
    global lower_hue_1, lower_saturation_1, lower_value_1
    global upper_hue_1, upper_saturation_1, upper_value_1
    global lower_hue_2, lower_saturation_2, lower_value_2
    global upper_hue_2, upper_saturation_2, upper_value_2

    lower_hue_1 = int(initial_lower_hue_1 * factor)
    lower_saturation_1 = int(initial_lower_saturation_1 * factor)
    lower_value_1 = int(initial_lower_value_1 * factor)
    upper_hue_1 = int(initial_upper_hue_1 * factor)
    upper_saturation_1 = int(initial_upper_saturation_1 * factor)
    upper_value_1 = int(initial_upper_value_1 * factor)
    lower_hue_2 = int(initial_lower_hue_2 * factor)
    lower_saturation_2 = int(initial_lower_saturation_2 * factor)
    lower_value_2 = int(initial_lower_value_2 * factor)
    upper_hue_2 = int(initial_upper_hue_2 * factor)
    upper_saturation_2 = int(initial_upper_saturation_2 * factor)
    upper_value_2 = int(initial_upper_value_2 * factor)

def on_trackbar(val):
    factor = val / 100
    update_hsv_ranges(factor)

try: 
    
    ascii_art = create_ascii_art(f"Your cousin will play for {int(run_duration_hours)} hours, "
      f"{int(run_duration_minutes)} minutes, and "
      f"{int(run_duration_seconds)} seconds.")
    print(ascii_art)
    time.sleep(2)
    start_time = time.time()
    # Create a named window
    cv2.namedWindow("League of Legends", cv2.WINDOW_NORMAL)
    # Create a trackbar for adjusting the HSV range factor
    cv2.createTrackbar('Red Range', 'League of Legends', 100, 200, on_trackbar)
    
    while True:
        time_elapsed = time.time() - start_time
        hours = int(time_elapsed // 3600)
        minutes = int((time_elapsed % 3600) // 60)
        seconds = int(time_elapsed % 60) 
        
        if time_elapsed >= run_duration:
            # Check if the window is already active
            if gw.getActiveWindow() != handle:
                handle.activate()
            print(f"Reached {run_duration_hours:.2f} hours. Stopping WoW.")
            pyautogui.press(exit_key, interval=rand_numb(button_hold1, button_hold2))
            break
        
        if global_stop_event.is_set():
            break

        if not catching:
            print_status("Waiting to settle...")
            time.sleep(2)
            continue
        stop_event = threading.Event()
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Convert the frame to the HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds for the red color in HSV (adjust these values as needed)
        lower_red1 = np.array([lower_hue_1, lower_saturation_1, lower_value_1])
        upper_red1 = np.array([upper_hue_1, upper_saturation_1, upper_value_1])
        lower_red2 = np.array([lower_hue_2, lower_saturation_2, lower_value_2])
        upper_red2 = np.array([upper_hue_2, upper_saturation_2, upper_value_2])

        # Create masks for red color within the specified ranges
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        # Combine masks
        mask = cv2.bitwise_or(mask1, mask2)

        # Apply morphological operations to reduce noise and refine the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            contour_detected_time = time.time()
            largest_contour = max(contours, key=cv2.contourArea)

            # Create a mask for the largest contour
            mask_largest_contour = np.zeros_like(mask)
            cv2.drawContours(mask_largest_contour, [largest_contour], -1, 255, thickness=cv2.FILLED)

            # Create a green overlay for the largest contour
            green_overlay = np.zeros_like(frame)
            green_overlay[mask_largest_contour != 0] = (0, 255, 0)  # Green color

            # Combine the original frame with the green overlay
            frame = cv2.addWeighted(frame, 1, green_overlay, 0.5, 0)

            x_contour, y_contour, w, h = cv2.boundingRect(largest_contour)

            current_y = y + y_contour + h // 2

            # Define static rectangle size
            static_rect_width = 60
            static_rect_height = 60

            # Calculate static rectangle position
            static_rect_x = x_contour + 20 + (w - static_rect_width) // 2
            static_rect_y = y_contour + 20 + (h - static_rect_height) // 2

            # Draw static rectangle corners
            corner_thickness = 2
            corner_size = 10
            # Top-left corner
            cv2.line(frame, (static_rect_x, static_rect_y), 
                    (static_rect_x + corner_size, static_rect_y), (0, 0, 255), corner_thickness)
            cv2.line(frame, (static_rect_x, static_rect_y), 
                    (static_rect_x, static_rect_y + corner_size), (0, 0, 255), corner_thickness)
            # Top-right corner
            cv2.line(frame, (static_rect_x + static_rect_width, static_rect_y), 
                    (static_rect_x + static_rect_width - corner_size, static_rect_y), (0, 0, 255), corner_thickness)
            cv2.line(frame, (static_rect_x + static_rect_width, static_rect_y), 
                    (static_rect_x + static_rect_width, static_rect_y + corner_size), (0, 0, 255), corner_thickness)
            # Bottom-left corner
            cv2.line(frame, (static_rect_x, static_rect_y + static_rect_height), 
                    (static_rect_x + corner_size, static_rect_y + static_rect_height), (0, 0, 255), corner_thickness)
            cv2.line(frame, (static_rect_x, static_rect_y + static_rect_height), 
                    (static_rect_x, static_rect_y + static_rect_height - corner_size), (0, 0, 255), corner_thickness)
            # Bottom-right corner
            cv2.line(frame, (static_rect_x + static_rect_width, static_rect_y + static_rect_height), 
                    (static_rect_x + static_rect_width - corner_size, static_rect_y + static_rect_height), (0, 0, 255), corner_thickness)
            cv2.line(frame, (static_rect_x + static_rect_width, static_rect_y + static_rect_height), 
                    (static_rect_x + static_rect_width, static_rect_y + static_rect_height - corner_size), (0, 0, 255), corner_thickness)
            
            if previous_y is not None and not fish_catching:
                motion = current_y - previous_y
                if motion > 4:
                    stop_event = threading.Event()
                    stop_event.clear()
                    
                    thread = threading.Thread(target=catch_fish, args=(stop_event,))
                    thread.start()

            previous_y = current_y

        else:
            if contour_detected_time is None:
                contour_detected_time = time.time()
            elif time.time() - contour_detected_time > 8 and not fish_catching:
                handle = gw.getWindowsWithTitle('World of Warcraft')[0]
                # Check if the window is already active
                if gw.getActiveWindow() != handle:
                    handle.activate()
 
                pyautogui.press(fishing_key, interval=rand_numb(button_hold1, button_hold2))
                print_status("Fishing...")
                
                previous_y = None
                contour_detected_time = None
                
        cv2.setWindowProperty("League of Legends", cv2.WND_PROP_TOPMOST, 1)
        cv2.resizeWindow("League of Legends", 600, 150)
        cv2.imshow("League of Legends", frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()

except Exception as e:
    print(e)
finally:
    global_stop_event.set()
    print_status("Cousin is done fishing")
    print(f"\nTime elapsed: {hours} hours, {minutes} minutes, {seconds} seconds")
    print("Caught fish: ", caught_fish)
    print("Failed catches: ", failed_fish)