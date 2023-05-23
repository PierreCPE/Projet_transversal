from robotserver import RobotServer
import app
import multiprocessing
a = app.App()
a.sharedVariables['mode'] = 3
robotProcess = multiprocessing.Process(target=app.runRobotServer, args=(a.config, a.sharedVariables, a.sharedFrame))
robotProcess.start()