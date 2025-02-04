# -*- coding: utf-8 -*-
# pyright: reportUnknownMemberType=false
import qi
import random
import time
from io import BytesIO
import monotonic
from PIL import Image
# import vision_definitions
from datetime import date
from babel.dates import format_date
from util import get_statements_speech
from tactile_gesture import TactileGesture
# import cv2


class HumanGreeter(object):

    def tac_gesture_handler(self, gesture):
        # type: (list[str]) -> None
        """
        gesture: See http://doc.aldebaran.com/2-8/naoqi/sensors/altactilegesture.html
                 Is: list[str]. Elements are strings of length 3, containing values of front, middle, back sensor as "0" or "1".
                     ex.: pat-pat gesture (called "DoubleTap") = ["000", "111", "000", "111", "000"]
        """
        if gesture in (TactileGesture.CaressFtoR, TactileGesture.CaressRtoF):
            laugh = [] # type: list[str]
            if self.posture_service.getPosture() == "Stand":
                laugh = ["animations/Stand/Emotions/Positive/Laugh_1",
                         "animations/Stand/Emotions/Positive/Laugh_2"]
            else:
                laugh = ["animations/Sit/Emotions/Positive/Laugh_1",
                         "animations/Sit/Emotions/Positive/Laugh_2"]
            self.behavior.runBehavior(random.choice(laugh), _async=True)

    def __init_laugh(self):
        self.tg.onGesture.connect(self.tac_gesture_handler)

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection
        """
        super(HumanGreeter, self).__init__()
        app.start()
        session = app.session # type: qi.Session
        self.showcase_num = 8

        self.dict_master = {
            "de": get_statements_speech("_global", "de"),
            "en": get_statements_speech("_global", "en")
        }
        # Get the service ALMemory and ALTexttoSpeech.
        self.tts = session.service("ALTextToSpeech")  # actually used
        # self.tts.setLanguage("German")
        # self.speak_move_service = session.service("ALSpeakingMovement")
        # self.anim_speech_service = session.service("ALAnimatedSpeech")
        self.bm_service = session.service("ALBackgroundMovement")
        self.ba_service = session.service("ALBasicAwareness")
        self.motion_service = session.service("ALMotion")
        self.tg = session.service("ALTactileGesture")
        self.posture_service = session.service("ALRobotPosture")
        self.behavior = session.service("ALBehaviorManager")
        self.animation_player_service = session.service(
            "ALAnimationPlayer")  # actually used
        self.video_service = session.service("ALVideoDevice")
        # self.subscribe_video_service= self.video_service.subscribeCamera("name_test", 0, 3, 13, 1)
        print("Starting UI2Speech Interaction")
        self.bm_service.setEnabled(True)
        self.motion_service.wakeUp()
        print("Starting BasicAwareness")
        self.ba_service.startAwareness()
        self.__init_laugh()

    def showNaoImage(self):
        resolution = 2    # VGA
        colorSpace = 11   # RGB
        videoClient = self.video_service.subscribeCamera(
            "python_client", 0, resolution, colorSpace, 5)

        t0 = monotonic.monotonic()

        naoImage = self.video_service.getImageRemote(videoClient)

        t1 = monotonic.monotonic()

        # Time the image transfer.
        print("acquisition delay "), t1 - t0

        self.video_service.unsubscribe(videoClient)
        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

        # Save the image.
        data = BytesIO()
        im.save(data, "jpeg")
        return data

    def _get_context(self, language):
        # type: (str) -> dict[str, int | str]
        now = time.localtime()
        ctx = { # type: dict[str, int | str]
            "showcase_num": self.showcase_num,
            "hour": now.tm_hour,
            "min": now.tm_min
        }
        if language == "en":
            ctx.update(date=date.today().strftime("%B %d"))
        elif language == "de":
            ctx.update(date=format_date(
                date.today(), format="full", locale='de_DE'))
        return ctx

    def speak(self, language, prompt, action):
        # type: (str, str, str) -> None
        # TODO move this into configuration
        FORMATTABLE_PROMPTS = ["OMR", "Date", "Time"]
        print(u"Language used: {language}. Prompt: {prompt}. Action: {action}".format(
            language=language, prompt=prompt, action=action))
        if action == "speech" or action == "NaoChat":
            if language == "en":
                self.tts.setLanguage("English")
            elif language == "de":
                self.tts.setLanguage("German")
            responses = get_statements_speech(
                '_global', language)[prompt]
            if prompt in FORMATTABLE_PROMPTS:
                ctx = self._get_context(language)
                responses = list(map(lambda s: s.format(**ctx), responses))
            self.tts.say(random.choice(responses))

    def move(self, prompt):
        # type: (str) -> None
        # TODO make sure the service stays connected... else RuntimeError
        self.animation_player_service.run("animations/" + prompt)
        # ("animations/Stand/Gestures/Applause_1", "animations/Stand/Gestures/Applause_1", "animations/Stand/Gestures/Salute1", "animations/Stand/Gestures/Stretch_1, "animations/Stand/Reactions/SeeSomething_1", "animations/Stand/Reactions/AirJuggle_1", "Systems/animations/Stand/Waiting/Fitness_3", "animations/Stand/Waiting/AirGuitar_1", "animations/Stand/Waiting/DriveCar_1", "animations/Stand/Waiting/HappyBirthday_1", "animations/Stand/Waiting/LoveYou_1", "animations/Stand/Waiting/TakePicture_1", "animations/Stand/Gestures/Hey_3)
        # self.posture_service.goToPosture(prompt, 1.0)
        # time.sleep(1)
        # self.posture_service.goToPosture("StandInit", 0.8)

        if prompt == "Stand/Waiting/TakePicture_1":
            return ("image/jpeg", self.showNaoImage())

        self.posture_service.goToPosture("Stand", 1.0)
