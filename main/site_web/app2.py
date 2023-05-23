from robotserver import RobotServer
import app
import multiprocessing
a = app.App()

robotProcess = multiprocessing.Process(target=app.runRobotServer, args=(a.config, a.sharedVariables, a.sharedFrame))
robotProcess.start()