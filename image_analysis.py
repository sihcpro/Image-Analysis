import cv2
import numpy as np
from queue import Queue

# Edit this info
acceptable_color_error = 3
acceptable_near_error = 30

img_name = "quynh"
img_path = "img1.png"

destination_color = np.array([0, 0, 0])

# Don't edit below
origin_img = cv2.imread(img_path)

img_x = len(origin_img)
img_y = len(origin_img[0])
print("img size:", (img_y, img_x))

search_queue = Queue(img_x * img_y)
unchecked_matix = [[True] * img_y for i in range(img_x)]
print("img size:", (len(unchecked_matix), len(unchecked_matix[0])))

mouseX = 0
mouseY = 0

target_pixel = (0, 0)


def generate_upper_and_lower_bound(target_color, acceptable_error):
    upper_bound_color = [color + acceptable_error for color in target_color]
    lower_bound_color = [color - acceptable_error for color in target_color]
    return upper_bound_color, lower_bound_color


def compare_pixel_with_error(pixel, upper_bound, lower_bound):
    global acceptable_error
    return all(pixel <= upper_bound) and all(pixel >= lower_bound)


def check_and_push_search_queue(img, current_color, next_pos):
    global unchecked_matix, search_queue, acceptable_near_error, destination_color

    upper_bound, lower_bound = generate_upper_and_lower_bound(
        current_color, acceptable_near_error
    )
    next_color = img[next_pos]

    if compare_pixel_with_error(next_color, upper_bound, lower_bound):
        img[next_pos] = destination_color
        unchecked_matix[next_pos[0]][next_pos[1]] = False
        search_queue.put((next_pos, next_color))


def push_around_pixel(img, current_position, current_color):
    global unchecked_matix, img_x, img_y, search_queue, acceptable_near_error, destination_color
    x = current_position[0]
    y = current_position[1]
    # print("push_around_pixel: xy:", current_position)

    unchecked_matix[x][y] = False
    if x + 1 < img_x and unchecked_matix[x + 1][y]:
        next_pos = (x + 1, y)
        check_and_push_search_queue(img, current_color, next_pos)
    if x - 1 >= 0 and unchecked_matix[x - 1][y]:
        next_pos = (x - 1, y)
        check_and_push_search_queue(img, current_color, next_pos)
    if y + 1 < img_y and unchecked_matix[x][y + 1]:
        next_pos = (x, y + 1)
        check_and_push_search_queue(img, current_color, next_pos)
    if y - 1 < img_y and unchecked_matix[x][y - 1]:
        next_pos = (x, y - 1)
        check_and_push_search_queue(img, current_color, next_pos)


def track_and_set_color(img, current_position, current_color):
    global acceptable_near_error, destination_color, search_queue, unchecked_matix

    push_around_pixel(img, current_position, current_color)
    while not search_queue.empty():
        next_one = search_queue.get()
        push_around_pixel(img, next_one[0], next_one[1])


def set_img_color(img):
    global target_pixel, acceptable_color_error, destination_color
    print("destination pixel:", target_pixel)
    target_color = img[target_pixel[1]][target_pixel[0]].copy()
    upper_bound, lower_bound = generate_upper_and_lower_bound(
        target_color, acceptable_color_error
    )
    print("target_color", target_color)
    for x in range(len(img)):
        for y in range(len(img[x])):
            if compare_pixel_with_error(img[x, y], upper_bound, lower_bound):
                track_and_set_color(img, (x, y), img[x, y])
                img[x, y] = destination_color
    return img


def draw_circle(event, x, y, flags, param):
    global mouseX, mouseY, target_pixel
    mouseX, mouseY = x, y
    img = origin_img.copy()
    if event == cv2.EVENT_LBUTTONDBLCLK:
        target_pixel = (x, y)

    cv2.circle(img, (x, y), 1, (255, 0, 0), -1)
    cv2.circle(img, target_pixel, 2, (0, 0, 255), -1)
    cv2.imshow(img_name, img)


def set_event_listener(target_img, img_name="user_image"):
    cv2.imshow(img_name, target_img)
    cv2.namedWindow(img_name)
    cv2.setMouseCallback(img_name, draw_circle)


if __name__ == "__main__":
    img = origin_img.copy()
    set_event_listener(img, img_name)
    cv2.imshow(img_name, img)
    while True:
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
        elif k == ord("a"):
            print(mouseX, mouseY)
        elif k == ord("s"):
            destination_img = set_img_color(origin_img.copy())
            cv2.imshow("destination image", destination_img)

    cv2.destroyAllWindows()
