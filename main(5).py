from final_project_classes import Camera, NemaMotor, API
from final_project_classes import metal_display, plastic_display, paper_display, trash_display, rotate_display, \
    detect_display
import RPi.GPIO as GPIO
import datetime
import threading
import time

angle_EA = 72
angle_AB = 72
angle_BC = 64.8
angle_CD = 79.2
angle_DE = 64.8
"""GPIO Settings"""
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
"""PWM_A,PWM_B,StandBy need to be set to high value"""
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, True)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, True)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, True)
"""4 GPIO to control motor"""
A11 = 19
A12 = 26
B11 = 21
B12 = 13
GpioPins = [A11, B11, A12, B12]
"""2 GPIO to control distance sensor"""
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
cur_position = 'E'
spiral = 0  # Index indicate the spiral of the ultra sensor wire on the central motor axis, left minus, right plus


class MyThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        if self.threadID == 'rotating':
            rotate_display()
        if self.threadID == 'detecting':
            detect_display()


def Get_Distance():
    """Get the distance from sensor to trash, return a float"""
    start, end = 0, 0
    GPIO.output(TRIG, True)
    time.sleep(0.0001)
    GPIO.output(TRIG, False)
    while not GPIO.input(ECHO):
        start = time.time()
    while GPIO.input(ECHO):
        end = time.time()
    sig_time = end - start
    distance = sig_time / 0.000058  # cm
    return distance


def Get_Volume():
    """Get the volume of 4 different area, return a list with a length of 4"""
    thread_detect = MyThread('detecting')
    thread_detect.start()
    global cur_position, spiral
    step_list = [int(angle_EA / 7.2),
                 int(angle_AB / 7.2),
                 int(angle_BC / 7.2),
                 int(angle_CD / 7.2)]
    Reset_Position()
    time.sleep(1)
    spiral -= 1
    avg_depth = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for i in ['A', 'B', 'C', 'D']:
        if i == 'A':
            section_total_depth = 15
        elif i == 'D':
            section_total_depth = 30
        else:
            section_total_depth = 0
        valid_num = 0
        print("start detecting {0}".format(i))
        for j in range(step_list[list(avg_depth.keys()).index(i)]):
            if 2 < j < 8 and j % 2 == 1:
                time.sleep(0.2)
                distance = Get_Distance()
                # distance = max(distance, Get_Distance())
                if distance < 50:
                    valid_num += 1
                    section_total_depth += distance
                    print('{0} cm'.format(distance))
            Clockwise(angle=7.2, wait=0.05, initdelay=0.8, steptype="half")
        avg_depth[i] += section_total_depth / valid_num
    cur_position = 'D'
    Reset_Position()
    Rotate_to_D()
    for key in avg_depth.keys():
        avg_depth_result = min(1, max(0, (42.5 - avg_depth[key]) / 42.5))
        avg_depth[key] = float("%.2f" % avg_depth_result)
    thread_detect.join()
    return avg_depth


def Counter_Clockwise(angle, wait=0.018, initdelay=1, steptype="half"):
    """Rotate motor by certain angle clockwise"""
    # thread_rotate = MyThread('rotating')
    # thread_rotate.start()
    steps = int(angle / 7.2)  # angle should be a multiple of 7.2
    ccwise = False
    verbose = True
    Nema17.motor_run(GpioPins, wait, steps, ccwise, verbose, steptype, initdelay)
    # thread_rotate.join()


def Clockwise(angle, wait=0.018, initdelay=1, steptype="half"):
    """Rotate motor by certain angle counterclockwise"""
    # thread_rotate = MyThread('rotating')
    # thread_rotate.start()
    steps = int(angle / 7.2)  # angle should be a multiple of 7.2
    ccwise = True
    verbose = True
    Nema17.motor_run(GpioPins, wait, steps, ccwise, verbose, steptype, initdelay)
    # thread_rotate.join()


def Rotate_to_A():
    """Rotate the trash can lid to area A"""
    global cur_position, spiral
    print('Rotating to A')
    if cur_position == 'B':
        Counter_Clockwise(angle_AB)
    if cur_position == 'C':
        Counter_Clockwise(angle_BC)
        Counter_Clockwise(angle_AB)
    if cur_position == 'D':
        Counter_Clockwise(angle_CD)
        Counter_Clockwise(angle_BC)
        Counter_Clockwise(angle_AB)
    if cur_position == 'E':
        Clockwise(angle_DE)
        spiral -= 1
    cur_position = 'A'
    print('Rotated to A')


def Rotate_to_B():
    """Rotate the trash can lid to area B"""
    global cur_position, spiral
    print('Rotating to B')
    if cur_position == 'A':
        Clockwise(angle_AB)
    if cur_position == 'C':
        Counter_Clockwise(angle_BC)
    if cur_position == 'D':
        Counter_Clockwise(angle_CD)
        Counter_Clockwise(angle_BC)
    if cur_position == 'E':
        Clockwise(angle_EA)
        Clockwise(angle_AB)
        spiral -= 1
    cur_position = 'B'
    print('Rotated to B')


def Rotate_to_C():
    """Rotate the trash can lid to area C"""
    global cur_position, spiral
    print('Rotating to C')
    if cur_position == 'A':
        Clockwise(angle_DE)
        Clockwise(angle_CD)
    if cur_position == 'B':
        Clockwise(angle_BC)
    if cur_position == 'D':
        Counter_Clockwise(angle_CD)
    if cur_position == 'E':
        Counter_Clockwise(angle_DE)
        Counter_Clockwise(angle_CD)
        spiral += 1
    cur_position = 'C'
    print('Rotated to C')


def Rotate_to_D():
    """Rotate the trash can lid to area D"""
    global cur_position, spiral
    print('Rotating to D')
    if cur_position == 'A':
        Clockwise(angle_AB)
        Clockwise(angle_BC)
        Clockwise(angle_CD)
    if cur_position == 'B':
        Clockwise(angle_BC)
        Clockwise(angle_CD)
    if cur_position == 'C':
        Clockwise(angle_CD)
    if cur_position == 'E':
        Counter_Clockwise(angle_DE)
        spiral += 1
    cur_position = 'D'
    print('Rotated to D')


def Rotate_to_E():
    """Rotate the trash can lid to area E, offset spiral"""
    global cur_position, spiral
    print('Rotating to E')
    if spiral > 0:
        if cur_position == 'A':
            for angle in [angle_AB, angle_BC, angle_CD, angle_DE]:
                Clockwise(angle)
        if cur_position == 'B':
            for angle in [angle_BC, angle_CD, angle_DE]:
                Clockwise(angle)
        if cur_position == 'C':
            for angle in [angle_CD, angle_DE]:
                Clockwise(angle)
        if cur_position == 'D':
            Clockwise(angle_DE)
    if spiral < 0:
        if cur_position == 'A':
            Counter_Clockwise(angle_EA)
        if cur_position == 'B':
            for angle in [angle_AB, angle_EA]:
                Counter_Clockwise(angle)
        if cur_position == 'C':
            for angle in [angle_BC, angle_AB, angle_EA]:
                Counter_Clockwise(angle)
        if cur_position == 'D':
            for angle in [angle_CD, angle_BC, angle_AB, angle_EA]:
                Counter_Clockwise(angle)
    cur_position = 'E'
    print('Rotated to E')


def Reset_Position():
    """Reset the trash can lid to original position"""
    global spiral
    Rotate_to_E()
    spiral = 0
    print("Start precise reset position...")
    fst_distance = Get_Distance()
    print(fst_distance)
    if fst_distance <= 5:
        Clockwise(7.2, wait=0.05, initdelay=1, steptype="half")
        while Get_Distance() < 5:
            Clockwise(7.2, wait=0.05, initdelay=1, steptype="half")
        while Get_Distance() > 5:
            Counter_Clockwise(7.2, wait=0.05, initdelay=1, steptype="half")
    if fst_distance > 5:
        Counter_Clockwise(7.2, wait=0.05, initdelay=1, steptype="half")
        while Get_Distance() > 5:
            Counter_Clockwise(7.2, wait=0.05, initdelay=1, steptype="half")
        Clockwise(7.2, wait=0.05, initdelay=1, steptype="half")
    print('Precise reset position finished!!!')


def Rotate2Trash(type_of_trash):
    """
    Rotate trash can lid according to the predict_list, finally rotate to the "other" trash can, get volume, reset.
    :param predict_list:
    :return: Volume of all the part i.e. A,B,C,D of the trash can
    """
    global camera
    section2move = default_type_bind[type_of_trash]
    if section2move == 'A':
        Rotate_to_A()
    elif section2move == 'B':
        Rotate_to_B()
    elif section2move == 'C':
        Rotate_to_C()
    elif section2move == 'D':
        Rotate_to_D()
    else:
        print('invalid trash type')
    if type_of_trash == 'metal':
        metal_display()
    elif type_of_trash == 'plastic':
        plastic_display()
    elif type_of_trash == 'paper':
        paper_display()
    elif type_of_trash == 'other':
        trash_display()
    else:
        print('invalid trash type')
    print('please throw your trash in 5 seconds')
    stay_timer = time.time()
    while time.time() - stay_timer<=5:
        camera.read(show=True)


def get_key(dictionary, val):
    for key, value in dictionary.items():
        if val == value:
            return key
    return "key doesn't exist"

# ===================MAIN===============================
if __name__ == '__main__':
    # Initialization--------------------------------------
    Nema17 = NemaMotor()
    camera = Camera('http://192.168.0.242:5000/')
    camera.initialize()
    appearance = 1
    waiting = False
    # ---------------------------------------------------
    default_type_seq = ['metal', 'paper', 'plastic', 'other']
    default_type_bind = {'metal': 'A', 'paper': 'B', 'plastic': 'C', 'other': 'D'}
    section_volume_seq = {'0': 'A', '1': 'B', '2': 'C', '3': 'D'}
    # ---------------------------------------------------
    api_location = API("http://ip-api.com/json")
    location = api_location.post()
    lat, lon = location['lat'], location['lon']
    camera.send_location({1: {'location': [lat, lon]}})
    print('Trash can started!!!')
    while True:
        trash_index = 1
        picture, Flag = camera.read(show=True)
        prediction = camera.get(picture)
        print(prediction['results'])
        if len(prediction['results']) > 0:
            appearance += 1
            if appearance > 10:
                # trash_index *= -1
                for _ in range(len(prediction['results'])):
                    type_of_trash = prediction['results'].pop()[0]
                    Rotate2Trash(type_of_trash)
                wait_timer = time.time()
                waiting = True
                appearance = 0
        if len(prediction['results']) == 0:
            appearance -= 1
            appearance = max(0, appearance)
        if waiting == True and appearance == 0 and time.time() - wait_timer > 8:  # Start volume detection!
            volume_dict = Get_Volume()
            volume_send_dict = {1: {'volume': [[datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")] +
                                              [volume_dict[default_type_bind[trash_type]] for trash_type in
                                               default_type_seq]]}}
            print(volume_send_dict)
            camera.send_volume(volume_send_dict)
            updated_type_binding = camera.reset(id=1)
            for key in default_type_bind.keys():
                default_type_bind[key] = section_volume_seq[get_key(updated_type_binding, key)]
            waiting = False
            time.sleep(5)
        if not Flag:
            break  # get esc button to close

    GPIO.cleanup()
    camera.close()

