# Libraries
import RPi.GPIO as GPIO
import time
import boto3
import requests
import cv2

cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# set GPIO Pins
GPIO_TRIGGER = 23  # same wire at 16
GPIO_ECHO = 24  # samw wire at 18

# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


def distance():
    # set Trigger to HIGH
    print("before trig true")
    GPIO.output(GPIO_TRIGGER, True)
    print("after trig true")
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    print("after sleep")
    GPIO.output(GPIO_TRIGGER, False)
    print("after trig false")
    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    print("outside while echo GPIO_ECHO =" + str(GPIO_ECHO))
    while GPIO.input(GPIO_ECHO) == 0:
        print("inside echo GPIO_ECHO =" + str(GPIO_ECHO))
        print("inside echo=0")
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    print("near distance")
    return distance


if __name__ == '__main__':
    print("starting main function")
    status='closed'
    try:
        print("inside try")
        while (True):
            while (True):
                print("inside while 2nd")
                dist = distance()
                print("after distance")
                print("Measured Distance = %.1f cm" % dist)
                if (dist < 20 and status=='closed'):
                    print("in here")
                    status = 'open'
                    ret, frame = cam.read()
                    if not ret:
                        print("failed to grab frame")
                        break
                    cv2.imshow("test", frame)
                    if status == 'open':
                        # SPACE pressed
                        time.sleep(5)
                        img_name = "opencv_frame_0.png"
                        cv2.imwrite(img_name, frame)
                        print("{} written!".format(img_name))
                        status='closed'
                        break
            cam.release()
            cv2.destroyAllWindows()
            from botocore.client import Config

            ACCESS_KEY_ID = 'AKIAX3ZURLBX364GOWMB'
            ACCESS_SECRET_KEY = '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'
            BUCKET_NAME = 'inside-fridge'

            data = open('/home/pi/opencv_frame_0.png', 'rb')

            s3 = boto3.resource(
                's3',
                aws_access_key_id=ACCESS_KEY_ID,
                aws_secret_access_key=ACCESS_SECRET_KEY,
                config=Config(signature_version='s3v4')
            )
            s3.Bucket(BUCKET_NAME).put_object(Key='opencv_frame_0.png', Body=data, ACL='public-read')
            print("Done")

            insert = requests.get('http://smartfridge-env.eba-ya9mmfcm.us-east-2.elasticbeanstalk.com/insert')
            time.sleep(15)
            print(insert.status_code)
            insert = requests.get('http://smartfridge-env.eba-ya9mmfcm.us-east-2.elasticbeanstalk.com/filter')
            time.sleep(10)
            print(insert.status_code)
            insert = requests.get('http://smartfridge-env.eba-ya9mmfcm.us-east-2.elasticbeanstalk.com/filter')
            # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()